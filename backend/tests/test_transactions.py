"""
Automated tests for Transaction models, validation, persistence, and REST endpoints.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_ingest_single_transaction(async_client: AsyncClient):
    """
    Test successful ingestion of a single valid transaction with Decimal precision and entity linking.
    """
    payload = {
        "transaction_id": "txn_test_001",
        "customer_id": "cust_alpha_101",
        "amount": "149.99",
        "currency": "USD",
        "status": "SUCCESS",
        "payment_method": "card",
        "card_bin": "411111",
        "card_last4": "1111",
        "instrument_token": "tok_safe_fp_9a8b7c",
        "device_id": "dev_token_x99",
        "ip_address": "198.51.100.42",
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "location_city": "New York",
        "location_country": "US",
    }

    response = await async_client.post("/api/v1/transactions", json=payload)
    assert response.status_code == 201, response.text
    data = response.json()

    # Verify transaction data
    assert data["transaction_id"] == "txn_test_001"
    assert data["customer_id"] == "cust_alpha_101"
    assert data["amount"] == "149.99"
    assert data["currency"] == "USD"
    assert data["status"] == "SUCCESS"
    assert data["payment_method"] == "card"
    assert data["card_bin"] == "411111"
    assert data["card_last4"] == "1111"
    assert data["instrument_token"] == "tok_safe_fp_9a8b7c"
    assert data["device_id"] == "dev_token_x99"
    assert data["ip_address"] == "198.51.100.42"

    # Verify normalized entity linking
    entities = data.get("entities", [])
    assert len(entities) == 4

    entity_types = {e["entity"]["entity_type"]: e for e in entities}
    assert "USER" in entity_types
    assert entity_types["USER"]["entity"]["entity_value"] == "cust_alpha_101"
    assert entity_types["USER"]["relationship_type"] == "ACCOUNT_HOLDER"

    assert "PAYMENT_INSTRUMENT" in entity_types
    assert entity_types["PAYMENT_INSTRUMENT"]["entity"]["entity_value"] == "tok_safe_fp_9a8b7c"
    assert entity_types["PAYMENT_INSTRUMENT"]["relationship_type"] == "PAYMENT_SOURCE"

    assert "DEVICE" in entity_types
    assert entity_types["DEVICE"]["entity"]["entity_value"] == "dev_token_x99"
    assert entity_types["DEVICE"]["relationship_type"] == "DEVICE_ORIGIN"

    assert "IP" in entity_types
    assert entity_types["IP"]["entity"]["entity_value"] == "198.51.100.42"
    assert entity_types["IP"]["relationship_type"] == "IP_ORIGIN"


@pytest.mark.asyncio
async def test_ingest_batch_transactions(async_client: AsyncClient):
    """
    Test atomic batch ingestion of multiple transactions.
    """
    batch_payload = {
        "transactions": [
            {
                "transaction_id": "txn_batch_001",
                "customer_id": "cust_101",
                "amount": "50.00",
                "currency": "USD",
                "status": "SUCCESS",
                "payment_method": "card",
                "card_bin": "424242",
                "card_last4": "4242",
            },
            {
                "transaction_id": "txn_batch_002",
                "customer_id": "cust_102",
                "amount": "1200.50",
                "currency": "USD",
                "status": "FAILED",
                "payment_method": "upi",
                "upi_vpa": "payer@okhdfcbank",
            },
            {
                "transaction_id": "txn_batch_003",
                "customer_id": "cust_103",
                "amount": "25.75",
                "currency": "USD",
                "status": "SUCCESS",
                "payment_method": "card",
            },
        ]
    }

    response = await async_client.post("/api/v1/transactions/batch", json=batch_payload)
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["ingested_count"] == 3
    assert len(data["items"]) == 3
    assert data["items"][0]["transaction_id"] == "txn_batch_001"
    assert data["items"][1]["transaction_id"] == "txn_batch_002"
    assert data["items"][2]["transaction_id"] == "txn_batch_003"


@pytest.mark.asyncio
async def test_get_transaction_by_id(async_client: AsyncClient):
    """
    Test retrieval of a single transaction by its unique external transaction ID.
    """
    payload = {
        "transaction_id": "txn_lookup_001",
        "customer_id": "cust_lookup_99",
        "amount": "99.00",
        "currency": "USD",
        "payment_method": "card",
        "device_id": "dev_lookup_node_1",
    }
    ingest_res = await async_client.post("/api/v1/transactions", json=payload)
    assert ingest_res.status_code == 201

    get_res = await async_client.get("/api/v1/transactions/txn_lookup_001")
    assert get_res.status_code == 200
    data = get_res.json()
    assert data["transaction_id"] == "txn_lookup_001"
    assert data["customer_id"] == "cust_lookup_99"
    assert data["amount"] == "99.00"
    assert len(data["entities"]) == 2  # USER and DEVICE


@pytest.mark.asyncio
async def test_get_transaction_not_found(async_client: AsyncClient):
    """
    Test 404 response for non-existent transaction lookup.
    """
    res = await async_client.get("/api/v1/transactions/non_existent_txn_99999")
    assert res.status_code == 404
    assert "not found" in res.json()["detail"].lower()


@pytest.mark.asyncio
async def test_list_transactions_with_filters_and_pagination(async_client: AsyncClient):
    """
    Test listing transactions with pagination and query filtering.
    """
    # Ingest 3 transactions
    txns = [
        {
            "transaction_id": f"txn_list_{i}",
            "customer_id": f"cust_target" if i < 2 else f"cust_other",
            "amount": f"{10 * (i + 1)}.00",
            "status": "SUCCESS" if i % 2 == 0 else "FAILED",
            "payment_method": "card" if i == 0 else "upi",
        }
        for i in range(3)
    ]
    for tx in txns:
        res = await async_client.post("/api/v1/transactions", json=tx)
        assert res.status_code == 201

    # 1. Total list
    res_all = await async_client.get("/api/v1/transactions?limit=10")
    assert res_all.status_code == 200
    data_all = res_all.json()
    assert data_all["total"] == 3
    assert len(data_all["items"]) == 3

    # 2. Filter by customer_id
    res_cust = await async_client.get("/api/v1/transactions?customer_id=cust_target")
    assert res_cust.status_code == 200
    data_cust = res_cust.json()
    assert data_cust["total"] == 2
    assert all(item["customer_id"] == "cust_target" for item in data_cust["items"])

    # 3. Filter by status
    res_status = await async_client.get("/api/v1/transactions?status=FAILED")
    assert res_status.status_code == 200
    data_status = res_status.json()
    assert data_status["total"] == 1
    assert data_status["items"][0]["status"] == "FAILED"


@pytest.mark.asyncio
async def test_duplicate_transaction_id_rejected(async_client: AsyncClient):
    """
    Test that ingesting a duplicate transaction_id returns a 409 Conflict.
    """
    payload = {
        "transaction_id": "txn_duplicate_001",
        "customer_id": "cust_dup",
        "amount": "75.00",
        "payment_method": "card",
    }
    first_res = await async_client.post("/api/v1/transactions", json=payload)
    assert first_res.status_code == 201

    dup_res = await async_client.post("/api/v1/transactions", json=payload)
    assert dup_res.status_code == 409
    assert "already exists" in dup_res.json()["detail"].lower()


@pytest.mark.asyncio
async def test_validation_rejected_non_positive_amount(async_client: AsyncClient):
    """
    Test that negative or zero monetary amounts are rejected with 422 Unprocessable Entity.
    """
    payload_zero = {
        "transaction_id": "txn_zero",
        "customer_id": "cust_invalid",
        "amount": "0.00",
        "payment_method": "card",
    }
    res_zero = await async_client.post("/api/v1/transactions", json=payload_zero)
    assert res_zero.status_code == 422

    payload_neg = {
        "transaction_id": "txn_neg",
        "customer_id": "cust_invalid",
        "amount": "-50.00",
        "payment_method": "card",
    }
    res_neg = await async_client.post("/api/v1/transactions", json=payload_neg)
    assert res_neg.status_code == 422


@pytest.mark.asyncio
async def test_validation_rejected_raw_pan(async_client: AsyncClient):
    """
    Test zero-trust safety: raw card numbers (16-digit PAN) are strictly rejected.
    """
    payload_pan = {
        "transaction_id": "txn_pan_leak",
        "customer_id": "cust_unsafe",
        "amount": "250.00",
        "payment_method": "card",
        "instrument_token": "4111111111111111",  # Raw 16-digit card number!
    }
    res = await async_client.post("/api/v1/transactions", json=payload_pan)
    assert res.status_code == 422
    assert "raw card numbers" in res.text.lower() or "forbidden sensitive data" in res.text.lower()


@pytest.mark.asyncio
async def test_card_bin_and_last4_validation(async_client: AsyncClient):
    """
    Test card_bin must be 6-8 digits and card_last4 must be 4 digits.
    """
    payload_bad_bin = {
        "transaction_id": "txn_bad_bin",
        "customer_id": "cust_bad",
        "amount": "10.00",
        "payment_method": "card",
        "card_bin": "123",  # Less than 6 digits
        "card_last4": "1234",
    }
    res_bin = await async_client.post("/api/v1/transactions", json=payload_bad_bin)
    assert res_bin.status_code == 422

    payload_bad_last4 = {
        "transaction_id": "txn_bad_last4",
        "customer_id": "cust_bad",
        "amount": "10.00",
        "payment_method": "card",
        "card_bin": "411111",
        "card_last4": "12",  # Less than 4 digits
    }
    res_last4 = await async_client.post("/api/v1/transactions", json=payload_bad_last4)
    assert res_last4.status_code == 422
