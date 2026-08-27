"""
Automated tests for Graph & Pattern Analysis Layer, Detectors, Idempotency, and REST API.
"""

from datetime import datetime, timezone, timedelta
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_shared_payment_instrument_detector(async_client: AsyncClient):
    """
    Test detection of a payment instrument shared across distinct customer accounts.
    """
    # 1. Ingest transactions from 2 different customers sharing a card token
    t1 = {
        "transaction_id": "txn_shared_card_1",
        "customer_id": "cust_alice",
        "amount": "100.00",
        "payment_method": "card",
        "instrument_token": "tok_shared_card_999",
    }
    t2 = {
        "transaction_id": "txn_shared_card_2",
        "customer_id": "cust_bob",
        "amount": "150.00",
        "payment_method": "card",
        "instrument_token": "tok_shared_card_999",
    }
    assert (await async_client.post("/api/v1/transactions", json=t1)).status_code == 201
    assert (await async_client.post("/api/v1/transactions", json=t2)).status_code == 201

    # 2. Trigger analysis
    res = await async_client.post("/api/v1/analysis/run")
    assert res.status_code == 201, res.text
    run_data = res.json()

    assert run_data["status"] == "COMPLETED"
    assert run_data["total_transactions_analyzed"] == 2
    assert run_data["findings_count"] >= 1

    # Find the SHARED_PAYMENT_INSTRUMENT finding
    findings = [f for f in run_data["findings"] if f["finding_type"] == "SHARED_PAYMENT_INSTRUMENT"]
    assert len(findings) == 1
    finding = findings[0]

    assert "Shared Payment Instrument" in finding["title"]
    assert "cust_alice" in finding["explanation"]
    assert "cust_bob" in finding["explanation"]
    assert finding["evidence_payload"]["customer_count"] == 2
    assert set(finding["evidence_payload"]["customer_ids"]) == {"cust_alice", "cust_bob"}
    assert set(finding["evidence_payload"]["transaction_ids"]) == {"txn_shared_card_1", "txn_shared_card_2"}

    # Verify entity associations
    roles = {re["role"]: re["entity"]["entity_value"] for re in finding["related_entities"]}
    assert "PRIMARY_SHARED_ENTITY" in roles
    assert roles["PRIMARY_SHARED_ENTITY"] == "tok_shared_card_999"


@pytest.mark.asyncio
async def test_shared_device_detector(async_client: AsyncClient):
    """
    Test detection of a device shared across multiple distinct customer accounts.
    """
    t1 = {
        "transaction_id": "txn_dev_1",
        "customer_id": "cust_user_1",
        "amount": "50.00",
        "payment_method": "card",
        "device_id": "dev_shared_hw_01",
    }
    t2 = {
        "transaction_id": "txn_dev_2",
        "customer_id": "cust_user_2",
        "amount": "75.00",
        "payment_method": "upi",
        "device_id": "dev_shared_hw_01",
    }
    assert (await async_client.post("/api/v1/transactions", json=t1)).status_code == 201
    assert (await async_client.post("/api/v1/transactions", json=t2)).status_code == 201

    res = await async_client.post("/api/v1/analysis/run")
    assert res.status_code == 201
    run_data = res.json()

    findings = [f for f in run_data["findings"] if f["finding_type"] == "SHARED_DEVICE"]
    assert len(findings) == 1
    f = findings[0]
    assert f["evidence_payload"]["device_id"] == "dev_shared_hw_01"
    assert f["evidence_payload"]["customer_count"] == 2


@pytest.mark.asyncio
async def test_shared_ip_cluster_detector(async_client: AsyncClient):
    """
    Test detection of an IP address shared across 3 distinct customer accounts.
    """
    shared_ip = "198.51.100.222"
    for i in range(3):
        t = {
            "transaction_id": f"txn_ip_{i}",
            "customer_id": f"cust_ip_user_{i}",
            "amount": "100.00",
            "payment_method": "card",
            "ip_address": shared_ip,
        }
        res = await async_client.post("/api/v1/transactions", json=t)
        assert res.status_code == 201

    res = await async_client.post("/api/v1/analysis/run")
    assert res.status_code == 201
    run_data = res.json()

    findings = [f for f in run_data["findings"] if f["finding_type"] == "SHARED_IP_CLUSTER"]
    assert len(findings) == 1
    assert findings[0]["evidence_payload"]["ip_address"] == shared_ip
    assert findings[0]["evidence_payload"]["customer_count"] == 3


@pytest.mark.asyncio
async def test_velocity_burst_detector(async_client: AsyncClient):
    """
    Test detection of rapid transaction bursts on a single user within the time window.
    """
    base_time = datetime.now(timezone.utc)
    for i in range(3):
        t = {
            "transaction_id": f"txn_burst_{i}",
            "customer_id": "cust_burst_target",
            "amount": "30.00",
            "payment_method": "card",
            "transacted_at": (base_time + timedelta(seconds=i * 30)).isoformat(),
        }
        res = await async_client.post("/api/v1/transactions", json=t)
        assert res.status_code == 201

    res = await async_client.post("/api/v1/analysis/run")
    assert res.status_code == 201
    run_data = res.json()

    findings = [f for f in run_data["findings"] if f["finding_type"] == "VELOCITY_BURST"]
    assert len(findings) >= 1
    burst_f = findings[0]
    assert burst_f["evidence_payload"]["transaction_count"] >= 3
    assert burst_f["evidence_payload"]["entity_value"] == "cust_burst_target"


@pytest.mark.asyncio
async def test_rapid_failure_burst_detector(async_client: AsyncClient):
    """
    Test detection of rapid payment failures within the failure window.
    """
    base_time = datetime.now(timezone.utc)
    for i in range(3):
        t = {
            "transaction_id": f"txn_fail_{i}",
            "customer_id": "cust_fail_target",
            "amount": "20.00",
            "currency": "USD",
            "status": "FAILED",
            "payment_method": "card",
            "transacted_at": (base_time + timedelta(seconds=i * 45)).isoformat(),
        }
        res = await async_client.post("/api/v1/transactions", json=t)
        assert res.status_code == 201

    res = await async_client.post("/api/v1/analysis/run")
    assert res.status_code == 201
    run_data = res.json()

    findings = [f for f in run_data["findings"] if f["finding_type"] == "RAPID_FAILURE_BURST"]
    assert len(findings) >= 1
    fail_f = findings[0]
    assert fail_f["evidence_payload"]["failed_transaction_count"] >= 3
    assert fail_f["evidence_payload"]["entity_value"] == "cust_fail_target"


@pytest.mark.asyncio
async def test_negative_baseline_independent_transactions(async_client: AsyncClient):
    """
    Verify that normal independent transactions with unique entities produce zero findings.
    """
    base_time = datetime.now(timezone.utc)
    t1 = {
        "transaction_id": "txn_normal_1",
        "customer_id": "cust_normal_1",
        "amount": "49.99",
        "payment_method": "card",
        "instrument_token": "tok_unique_1",
        "device_id": "dev_unique_1",
        "ip_address": "198.51.100.1",
        "transacted_at": (base_time - timedelta(hours=5)).isoformat(),
    }
    t2 = {
        "transaction_id": "txn_normal_2",
        "customer_id": "cust_normal_2",
        "amount": "89.99",
        "payment_method": "card",
        "instrument_token": "tok_unique_2",
        "device_id": "dev_unique_2",
        "ip_address": "198.51.100.2",
        "transacted_at": (base_time - timedelta(hours=1)).isoformat(),
    }
    assert (await async_client.post("/api/v1/transactions", json=t1)).status_code == 201
    assert (await async_client.post("/api/v1/transactions", json=t2)).status_code == 201

    res = await async_client.post("/api/v1/analysis/run")
    assert res.status_code == 201
    run_data = res.json()
    assert run_data["findings_count"] == 0
    assert len(run_data["findings"]) == 0


@pytest.mark.asyncio
async def test_deterministic_idempotent_analysis(async_client: AsyncClient):
    """
    Verify that repeated analysis on identical data produces identical, deterministic findings.
    """
    t1 = {
        "transaction_id": "txn_idem_1",
        "customer_id": "cust_idem_1",
        "amount": "100.00",
        "payment_method": "card",
        "device_id": "dev_idem_token",
    }
    t2 = {
        "transaction_id": "txn_idem_2",
        "customer_id": "cust_idem_2",
        "amount": "120.00",
        "payment_method": "card",
        "device_id": "dev_idem_token",
    }
    assert (await async_client.post("/api/v1/transactions", json=t1)).status_code == 201
    assert (await async_client.post("/api/v1/transactions", json=t2)).status_code == 201

    # Run 1
    res1 = await async_client.post("/api/v1/analysis/run")
    assert res1.status_code == 201
    run1 = res1.json()

    # Run 2
    res2 = await async_client.post("/api/v1/analysis/run")
    assert res2.status_code == 201
    run2 = res2.json()

    # Both runs should yield the exact same finding types and fingerprints
    fps1 = [f["fingerprint"] for f in run1["findings"]]
    fps2 = [f["fingerprint"] for f in run2["findings"]]
    assert fps1 == fps2
    assert len(fps1) == 1


@pytest.mark.asyncio
async def test_findings_and_runs_retrieval_endpoints(async_client: AsyncClient):
    """
    Test listing findings and querying single finding/run details.
    """
    t1 = {
        "transaction_id": "txn_lookup_rel_1",
        "customer_id": "cust_lookup_rel_1",
        "amount": "50.00",
        "payment_method": "card",
        "instrument_token": "tok_lookup_rel",
    }
    t2 = {
        "transaction_id": "txn_lookup_rel_2",
        "customer_id": "cust_lookup_rel_2",
        "amount": "60.00",
        "payment_method": "card",
        "instrument_token": "tok_lookup_rel",
    }
    await async_client.post("/api/v1/transactions", json=t1)
    await async_client.post("/api/v1/transactions", json=t2)

    run_res = await async_client.post("/api/v1/analysis/run")
    run_id = run_res.json()["run_id"]
    finding_id = run_res.json()["findings"][0]["finding_id"]

    # 1. Get run by ID
    get_run = await async_client.get(f"/api/v1/analysis/runs/{run_id}")
    assert get_run.status_code == 200
    assert get_run.json()["run_id"] == run_id

    # 2. List runs
    list_runs = await async_client.get("/api/v1/analysis/runs")
    assert list_runs.status_code == 200
    assert list_runs.json()["total"] >= 1

    # 3. Get finding by ID
    get_finding = await async_client.get(f"/api/v1/analysis/findings/{finding_id}")
    assert get_finding.status_code == 200
    assert get_finding.json()["finding_id"] == finding_id
    assert len(get_finding.json()["related_entities"]) >= 1
    assert len(get_finding.json()["related_transactions"]) >= 1

    # 4. List findings with filter
    list_findings = await async_client.get("/api/v1/analysis/findings?finding_type=SHARED_PAYMENT_INSTRUMENT")
    assert list_findings.status_code == 200
    assert list_findings.json()["total"] >= 1

    # 5. 404 on missing finding
    not_found = await async_client.get("/api/v1/analysis/findings/find_missing_99999")
    assert not_found.status_code == 404
