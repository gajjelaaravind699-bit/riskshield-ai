"""
Test suite for Phase 4: Deterministic Risk Scoring, Decision-Support Recommendations, and Advisory Audit Traces.
"""

from datetime import datetime, timedelta, timezone
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_assessment_allow_recommendation_clean_transaction(async_client: AsyncClient):
    """
    Verify that an isolated, legitimate transaction with no pattern findings receives an ALLOW recommendation (Score 0, LOW).
    """
    tx = {
        "transaction_id": "txn_clean_001",
        "customer_id": "cust_clean_001",
        "amount": "99.99",
        "payment_method": "card",
        "card_bin": "400000",
        "card_last4": "0001",
        "instrument_token": "tok_clean_001",
        "device_id": "dev_clean_001",
        "ip_address": "192.0.2.1",
    }
    ingest_res = await async_client.post("/api/v1/transactions", json=tx)
    assert ingest_res.status_code == 201
    assert ingest_res.json()["status"] == "SUCCESS"

    # Run analysis (should yield 0 findings)
    await async_client.post("/api/v1/analysis/run")

    # Evaluate risk assessment
    asmt_res = await async_client.post(f"/api/v1/assessments/evaluate/{tx['transaction_id']}")
    assert asmt_res.status_code == 201
    data = asmt_res.json()

    assert data["score"] == 0
    assert data["risk_level"] == "LOW"
    assert data["recommendation"] == "ALLOW"
    assert data["action_executed"] is False
    assert "ALLOW" in data["explanation"]
    assert "Advisory" in data["action_disclaimer"] or "Decision-support" in data["action_disclaimer"]
    assert data["ruleset_version"] == "rs_v1.0.0"
    assert data["decision_policy_version"] == "dp_v1.0.0"

    # Verify underlying transaction status is UNTOUCHED
    tx_check = await async_client.get(f"/api/v1/transactions/{tx['transaction_id']}")
    assert tx_check.json()["status"] == "SUCCESS"


@pytest.mark.asyncio
async def test_assessment_review_recommendation(async_client: AsyncClient):
    """
    Verify that a transaction associated with a moderate anomaly (e.g. shared IP cluster or velocity) receives REVIEW.
    """
    # Create 3 transactions sharing an IP cluster across 3 accounts (triggers SHARED_IP_CLUSTER: +25 pts)
    base_time = datetime.now(timezone.utc)
    for i in range(1, 4):
        tx = {
            "transaction_id": f"txn_rev_ip_{i}",
            "customer_id": f"cust_rev_ip_{i}",
            "amount": "150.00",
            "payment_method": "upi",
            "upi_vpa": f"user{i}@upi",
            "ip_address": "198.51.100.99",
            "transacted_at": (base_time - timedelta(minutes=i)).isoformat(),
        }
        assert (await async_client.post("/api/v1/transactions", json=tx)).status_code == 201

    # Run analysis
    analysis_res = await async_client.post("/api/v1/analysis/run")
    assert analysis_res.status_code == 201
    assert analysis_res.json()["findings_count"] >= 1

    # Evaluate with review_threshold=25 so +25 points maps to REVIEW
    eval_req = {
        "policy": {
            "review_threshold": 25,
            "block_threshold": 60,
            "decision_policy_version": "dp_v1.0.0",
        }
    }
    asmt_res = await async_client.post(
        "/api/v1/assessments/evaluate/txn_rev_ip_1",
        json=eval_req,
    )
    assert asmt_res.status_code == 201
    data = asmt_res.json()

    assert data["score"] >= 25
    assert data["recommendation"] == "REVIEW"
    assert data["action_executed"] is False

    # Verify underlying transaction status is UNTOUCHED
    tx_check = await async_client.get("/api/v1/transactions/txn_rev_ip_1")
    assert tx_check.json()["status"] == "SUCCESS"


@pytest.mark.asyncio
async def test_assessment_block_recommendation_and_non_action_guarantee(async_client: AsyncClient):
    """
    Verify that transactions with high-risk coordinated abuse signals receive BLOCK recommendation (Score >= 60),
    and explicitly confirm that NO transaction status modification or financial action is executed.
    """
    # Multi-account ring sharing both card instrument (+40) and device token (+35) -> 75 pts (BLOCK)
    t1 = {
        "transaction_id": "txn_ring_alpha_01",
        "customer_id": "cust_ring_alpha",
        "amount": "500.00",
        "payment_method": "card",
        "instrument_token": "tok_shared_ring_card",
        "device_id": "dev_shared_ring_hw",
    }
    t2 = {
        "transaction_id": "txn_ring_beta_01",
        "customer_id": "cust_ring_beta",
        "amount": "650.00",
        "payment_method": "card",
        "instrument_token": "tok_shared_ring_card",
        "device_id": "dev_shared_ring_hw",
    }
    assert (await async_client.post("/api/v1/transactions", json=t1)).status_code == 201
    assert (await async_client.post("/api/v1/transactions", json=t2)).status_code == 201

    # Run analysis
    analysis_res = await async_client.post("/api/v1/analysis/run")
    assert analysis_res.status_code == 201
    assert analysis_res.json()["findings_count"] >= 2

    # Evaluate risk assessment
    asmt_res = await async_client.post("/api/v1/assessments/evaluate/txn_ring_alpha_01")
    assert asmt_res.status_code == 201
    data = asmt_res.json()

    # Rule contributions check: 40 (instrument) + 35 (device) = 75 points
    assert data["score"] >= 60
    assert data["risk_level"] in ["HIGH", "CRITICAL"]
    assert data["recommendation"] == "BLOCK"
    assert data["action_executed"] is False
    assert "BLOCK" in data["explanation"]
    assert "Decision-support recommendation only" in data["action_disclaimer"]

    # Check rule contributions breakdown
    rule_map = {rc["finding_type"]: rc for rc in data["rule_contributions"]}
    assert rule_map["SHARED_PAYMENT_INSTRUMENT"]["triggered"] is True
    assert rule_map["SHARED_PAYMENT_INSTRUMENT"]["points_contributed"] == 40
    assert rule_map["SHARED_DEVICE"]["triggered"] is True
    assert rule_map["SHARED_DEVICE"]["points_contributed"] == 35

    # CRITICAL NON-ACTION GUARANTEE:
    # Transaction status must remain SUCCESS (not CANCELLED, BLOCKED, REJECTED, or MODIFIED)
    tx_check = await async_client.get("/api/v1/transactions/txn_ring_alpha_01")
    assert tx_check.status_code == 200
    assert tx_check.json()["status"] == "SUCCESS"


@pytest.mark.asyncio
async def test_assessment_deterministic_repeatability(async_client: AsyncClient):
    """
    Verify that evaluating identical transaction/findings/ruleset/policy inputs produces deterministic equivalent results.
    """
    t1 = {
        "transaction_id": "txn_idem_asmt_1",
        "customer_id": "cust_idem_asmt_1",
        "amount": "120.00",
        "payment_method": "card",
        "instrument_token": "tok_repeat_asmt",
    }
    t2 = {
        "transaction_id": "txn_idem_asmt_2",
        "customer_id": "cust_idem_asmt_2",
        "amount": "130.00",
        "payment_method": "card",
        "instrument_token": "tok_repeat_asmt",
    }
    await async_client.post("/api/v1/transactions", json=t1)
    await async_client.post("/api/v1/transactions", json=t2)
    await async_client.post("/api/v1/analysis/run")

    # Evaluate 1st time
    res1 = await async_client.post("/api/v1/assessments/evaluate/txn_idem_asmt_1")
    assert res1.status_code == 201
    asmt1 = res1.json()

    # Evaluate 2nd time
    res2 = await async_client.post("/api/v1/assessments/evaluate/txn_idem_asmt_1")
    assert res2.status_code == 201
    asmt2 = res2.json()

    # Verify score, risk level, recommendation, rule contributions are 100% deterministic
    assert asmt1["score"] == asmt2["score"]
    assert asmt1["risk_level"] == asmt2["risk_level"]
    assert asmt1["recommendation"] == asmt2["recommendation"]
    assert asmt1["rule_contributions"] == asmt2["rule_contributions"]


@pytest.mark.asyncio
async def test_assessment_custom_ruleset_and_policy_overrides(async_client: AsyncClient):
    """
    Verify that custom ruleset weights and decision policy thresholds correctly alter score calculation.
    """
    t1 = {
        "transaction_id": "txn_custom_cfg_1",
        "customer_id": "cust_custom_cfg_1",
        "amount": "200.00",
        "payment_method": "card",
        "device_id": "dev_custom_cfg",
    }
    t2 = {
        "transaction_id": "txn_custom_cfg_2",
        "customer_id": "cust_custom_cfg_2",
        "amount": "210.00",
        "payment_method": "card",
        "device_id": "dev_custom_cfg",
    }
    await async_client.post("/api/v1/transactions", json=t1)
    await async_client.post("/api/v1/transactions", json=t2)
    await async_client.post("/api/v1/analysis/run")

    custom_payload = {
        "ruleset": {
            "ruleset_version": "rs_v2.0.0_custom",
            "shared_device_weight": 90,
            "shared_instrument_weight": 10,
        },
        "policy": {
            "decision_policy_version": "dp_v2.0.0_custom",
            "review_threshold": 40,
            "block_threshold": 80,
        },
    }

    res = await async_client.post(
        "/api/v1/assessments/evaluate/txn_custom_cfg_1",
        json=custom_payload,
    )
    assert res.status_code == 201
    data = res.json()

    assert data["score"] == 90
    assert data["recommendation"] == "BLOCK"
    assert data["ruleset_version"] == "rs_v2.0.0_custom"
    assert data["decision_policy_version"] == "dp_v2.0.0_custom"


@pytest.mark.asyncio
async def test_assessment_endpoints_and_batch_evaluation(async_client: AsyncClient):
    """
    Verify batch evaluation and retrieval endpoints (GET /assessments, GET /assessments/{id}, GET /assessments/transaction/{tx_id}).
    """
    t1 = {
        "transaction_id": "txn_batch_asmt_1",
        "customer_id": "cust_batch_asmt_1",
        "amount": "50.00",
        "payment_method": "card",
    }
    await async_client.post("/api/v1/transactions", json=t1)

    # 1. Batch evaluate all transactions
    batch_res = await async_client.post("/api/v1/assessments/evaluate-all")
    assert batch_res.status_code == 201
    batch_data = batch_res.json()
    assert batch_data["total_evaluated"] >= 1
    assert "items" in batch_data
    asmt_id = batch_data["items"][0]["assessment_id"]

    # 2. Get assessment by ID
    get_by_id = await async_client.get(f"/api/v1/assessments/{asmt_id}")
    assert get_by_id.status_code == 200
    assert get_by_id.json()["assessment_id"] == asmt_id

    # 3. Get assessment by transaction ID
    get_by_tx = await async_client.get("/api/v1/assessments/transaction/txn_batch_asmt_1")
    assert get_by_tx.status_code == 200
    assert get_by_tx.json()["assessment_id"] == asmt_id

    # 4. List assessments with filter
    list_res = await async_client.get("/api/v1/assessments?recommendation=ALLOW")
    assert list_res.status_code == 200
    assert list_res.json()["total"] >= 1

    # 5. 404 on missing assessment
    missing_res = await async_client.get("/api/v1/assessments/asmt_missing_999")
    assert missing_res.status_code == 404
