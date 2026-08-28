"""
Test suite for Phase 6: Production Hardening, Security Controls, Authentication/RBAC,
Error Sanitization, Logging Redaction, and Observability.
"""

import pytest
from httpx import AsyncClient
from pydantic import ValidationError
from app.core.config import Settings
from app.core.logging import redact_sensitive_data
from app.core.database import check_database_connection
from app.main import app


@pytest.mark.asyncio
async def test_authentication_enforcement_missing_and_invalid_key(unauthenticated_client: AsyncClient):
    """
    Verify protected endpoints reject unauthenticated requests (401 Unauthorized) and invalid keys.
    """
    # 1. Missing API Key -> 401 Unauthorized
    res_missing = await unauthenticated_client.get("/api/v1/transactions")
    assert res_missing.status_code == 401
    assert "error" in res_missing.json()
    assert res_missing.json()["error"]["code"] == "UNAUTHORIZED"

    # 2. Invalid API Key -> 401 Unauthorized
    res_invalid = await unauthenticated_client.get(
        "/api/v1/transactions",
        headers={"X-API-Key": "invalid_fake_key_999"},
    )
    assert res_invalid.status_code == 401
    assert res_invalid.json()["error"]["code"] == "UNAUTHORIZED"


@pytest.mark.asyncio
async def test_role_based_access_control(unauthenticated_client: AsyncClient):
    """
    Verify role-based authorization (ingest role vs analyst role vs admin role).
    """
    # Ingest key can POST transactions
    tx = {
        "transaction_id": "txn_rbac_001",
        "customer_id": "cust_rbac_001",
        "amount": "150.00",
        "payment_method": "card",
    }
    res_ingest = await unauthenticated_client.post(
        "/api/v1/transactions",
        json=tx,
        headers={"X-API-Key": "rs_ingest_key_dev"},
    )
    assert res_ingest.status_code == 201

    # Ingest key CANNOT run analysis (requires analyst role) -> 403 Forbidden
    res_forbidden = await unauthenticated_client.post(
        "/api/v1/analysis/run",
        headers={"X-API-Key": "rs_ingest_key_dev"},
    )
    assert res_forbidden.status_code == 403
    assert res_forbidden.json()["error"]["code"] == "FORBIDDEN"

    # Analyst key CAN run analysis -> 201 Created
    res_analyst = await unauthenticated_client.post(
        "/api/v1/analysis/run",
        headers={"X-API-Key": "rs_analyst_key_dev"},
    )
    assert res_analyst.status_code in [200, 201]


@pytest.mark.asyncio
async def test_correlation_id_and_timing_headers(async_client: AsyncClient):
    """
    Verify X-Correlation-ID is generated or passed through, and X-Process-Time is attached.
    """
    custom_corr_id = "custom_test_correlation_id_12345"
    response = await async_client.get(
        "/api/v1/health/liveness",
        headers={"X-Correlation-ID": custom_corr_id},
    )
    assert response.status_code == 200
    assert response.headers.get("X-Correlation-ID") == custom_corr_id
    assert "X-Process-Time" in response.headers
    assert response.headers["X-Process-Time"].endswith("ms")


@pytest.mark.asyncio
async def test_security_headers_presence(async_client: AsyncClient):
    """
    Verify mandatory security headers are attached to API responses.
    """
    response = await async_client.get("/api/v1/health/liveness")
    assert response.status_code == 200
    assert response.headers.get("X-Content-Type-Options") == "nosniff"
    assert response.headers.get("X-Frame-Options") == "DENY"
    assert response.headers.get("X-XSS-Protection") == "1; mode=block"
    assert response.headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"
    assert "default-src 'self'" in response.headers.get("Content-Security-Policy", "")


@pytest.mark.asyncio
async def test_liveness_and_readiness_probes(async_client: AsyncClient):
    """
    Verify separation of liveness probe (200) and readiness probe (200 connected / 503 disconnected).
    """
    # 1. Liveness Probe
    res_live = await async_client.get("/api/v1/health/liveness")
    assert res_live.status_code == 200
    assert res_live.json()["status"] == "alive"
    assert "version" in res_live.json()

    # 2. Readiness Probe (connected state)
    res_ready = await async_client.get("/api/v1/health/readiness")
    assert res_ready.status_code == 200
    assert res_ready.json()["status"] == "ready"
    assert res_ready.json()["database"]["status"] == "connected"


@pytest.mark.asyncio
async def test_readiness_probe_disconnected_db(async_client: AsyncClient, monkeypatch):
    """
    Verify readiness probe returns HTTP 503 when the database is unreachable without exposing secrets.
    """
    async def mock_disconnected():
        return {"status": "disconnected", "error": "Connection timed out"}

    monkeypatch.setattr("app.api.v1.endpoints.health.check_database_connection", mock_disconnected)

    res = await async_client.get("/api/v1/health/readiness")
    assert res.status_code == 503
    data = res.json()
    assert data["status"] == "not_ready"
    assert data["database"]["status"] == "disconnected"
    assert "password" not in str(data).lower()
    assert "postgresql" not in str(data).lower()


@pytest.mark.asyncio
async def test_unhandled_error_sanitization_masks_stack_traces(async_client: AsyncClient, monkeypatch):
    """
    Verify unhandled exceptions return sanitized HTTP 500 error envelopes without internal stack traces.
    """
    from app.services.transaction_service import TransactionService

    async def mock_broken_service(*args, **kwargs):
        raise RuntimeError("Internal critical secret core failure with internal schema details")

    monkeypatch.setattr(TransactionService, "get_transactions", mock_broken_service)

    response = await async_client.get("/api/v1/transactions")
    assert response.status_code == 500
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == "INTERNAL_SERVER_ERROR"
    assert "correlation_id" in data["error"]
    # Ensure raw runtime traceback was sanitized
    assert "Traceback" not in data["error"]["message"]
    assert "mock_broken_service" not in data["error"]["message"]


def test_sensitive_data_redaction():
    """
    Verify sensitive keys and values (PANs, passwords, API keys, CVVs) are redacted.
    """
    sensitive_dict = {
        "customer_id": "cust_123",
        "password": "super_secret_password_999",
        "api_key": "rs_live_secret_key_abc",
        "nested": {
            "card_number": "4111 2222 3333 4444",
            "cvv": "123",
            "normal_field": "safe_value",
        },
    }
    redacted = redact_sensitive_data(sensitive_dict)
    assert redacted["customer_id"] == "cust_123"
    assert redacted["password"] == "[REDACTED]"
    assert redacted["api_key"] == "[REDACTED]"
    assert redacted["nested"]["card_number"] == "[REDACTED]"
    assert redacted["nested"]["cvv"] == "[REDACTED]"
    assert redacted["nested"]["normal_field"] == "safe_value"

    # Test raw string with PAN and Bearer token
    raw_str = "User Authorization: Bearer eyJhbGciOiJIUzI1Ni... with card 4111222233334444"
    scrubbed_str = redact_sensitive_data(raw_str)
    assert "eyJhbGciOiJIUzI1Ni" not in scrubbed_str
    assert "4111222233334444" not in scrubbed_str


def test_production_environment_validation_rejects_insecure_settings():
    """
    Verify production mode rejects weak/default SECRET_KEY and weak POSTGRES_PASSWORD.
    """
    # 1. Rejects default weak SECRET_KEY in production
    with pytest.raises(ValueError, match="SECRET_KEY must be a cryptographically strong secret"):
        Settings(
            ENVIRONMENT="production",
            SECRET_KEY="dev-short-key",
            POSTGRES_PASSWORD="secure_prod_password_12345!",
            API_KEYS={"prod_key": {"role": "analyst"}},
        )

    # 2. Rejects default weak POSTGRES_PASSWORD in production
    with pytest.raises(ValueError, match="POSTGRES_PASSWORD cannot use default or weak password"):
        Settings(
            ENVIRONMENT="production",
            SECRET_KEY="a_very_long_secure_production_secret_key_exceeding_32_chars!",
            POSTGRES_PASSWORD="riskshield_password",
            API_KEYS={"prod_key": {"role": "analyst"}},
        )

    # 3. Accepts valid production settings
    valid_prod = Settings(
        ENVIRONMENT="production",
        SECRET_KEY="a_very_long_secure_production_secret_key_exceeding_32_chars!",
        POSTGRES_PASSWORD="a_strong_production_postgres_password_98765!",
        API_KEYS={"prod_key_12345": {"role": "analyst"}},
    )
    assert valid_prod.ENVIRONMENT == "production"
    assert valid_prod.DEBUG is False
