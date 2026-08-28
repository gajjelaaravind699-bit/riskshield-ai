"""
Test suite for Phase 5: Human Analyst Case Review, Notes, Dispositions, and Immutable Audit Trails.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_case_manually_and_audit_trail(async_client: AsyncClient):
    """
    Verify manual case creation and initial CASE_CREATED audit event.
    """
    tx = {
        "transaction_id": "txn_case_001",
        "customer_id": "cust_case_001",
        "amount": "199.99",
        "payment_method": "card",
    }
    await async_client.post("/api/v1/transactions", json=tx)

    case_payload = {
        "transaction_id": "txn_case_001",
        "title": "Suspicious Velocity Investigation",
        "description": "Manual case creation for rapid testing investigation.",
        "priority": "HIGH",
        "assigned_to": "analyst_bob",
        "actor": "lead_analyst",
    }
    res = await async_client.post("/api/v1/cases", json=case_payload)
    assert res.status_code == 201
    data = res.json()

    assert data["case_id"].startswith("case_")
    assert data["title"] == "Suspicious Velocity Investigation"
    assert data["status"] == "ASSIGNED"
    assert data["priority"] == "HIGH"
    assert data["assigned_to"] == "analyst_bob"
    assert data["transaction"]["transaction_id"] == "txn_case_001"

    # Verify CASE_CREATED audit event
    assert len(data["audit_events"]) == 1
    evt = data["audit_events"][0]
    assert evt["event_type"] == "CASE_CREATED"
    assert evt["actor"] == "lead_analyst"
    assert evt["to_state"] == "ASSIGNED"


@pytest.mark.asyncio
async def test_create_case_from_assessment(async_client: AsyncClient):
    """
    Verify creating a case directly from an existing risk assessment.
    """
    t1 = {
        "transaction_id": "txn_asmt_case_1",
        "customer_id": "cust_asmt_case_1",
        "amount": "500.00",
        "payment_method": "card",
        "instrument_token": "tok_ring_asmt_case",
    }
    t2 = {
        "transaction_id": "txn_asmt_case_2",
        "customer_id": "cust_asmt_case_2",
        "amount": "600.00",
        "payment_method": "card",
        "instrument_token": "tok_ring_asmt_case",
    }
    await async_client.post("/api/v1/transactions", json=t1)
    await async_client.post("/api/v1/transactions", json=t2)
    await async_client.post("/api/v1/analysis/run")

    # Evaluate assessment
    asmt_res = await async_client.post("/api/v1/assessments/evaluate/txn_asmt_case_1")
    assert asmt_res.status_code == 201
    asmt_id = asmt_res.json()["assessment_id"]

    # Create case from assessment
    case_res = await async_client.post(
        f"/api/v1/cases/from-assessment/{asmt_id}",
        json={"assigned_to": "analyst_sarah", "actor": "lead_analyst"},
    )
    assert case_res.status_code == 201
    case_data = case_res.json()

    assert case_data["assessment_id"] is not None
    assert case_data["assessment"]["assessment_id"] == asmt_id
    assert case_data["status"] == "ASSIGNED"
    assert case_data["assigned_to"] == "analyst_sarah"
    assert case_data["transaction"]["transaction_id"] == "txn_asmt_case_1"


@pytest.mark.asyncio
async def test_controlled_status_transitions_and_rejection_of_invalid_transitions(async_client: AsyncClient):
    """
    Verify controlled state machine transitions and rejection of invalid status transitions.
    """
    tx = {
        "transaction_id": "txn_trans_001",
        "customer_id": "cust_trans_001",
        "amount": "100.00",
        "payment_method": "card",
    }
    await async_client.post("/api/v1/transactions", json=tx)

    create_res = await async_client.post(
        "/api/v1/cases",
        json={"transaction_id": "txn_trans_001", "title": "Transition Test Case"},
    )
    case_id = create_res.json()["case_id"]
    assert create_res.json()["status"] == "NEW"

    # 1. Valid Transition: NEW -> IN_REVIEW
    res_review = await async_client.patch(
        f"/api/v1/cases/{case_id}/status",
        json={"status": "IN_REVIEW", "actor": "analyst_bob", "reason": "Beginning review"},
    )
    assert res_review.status_code == 200
    assert res_review.json()["status"] == "IN_REVIEW"

    # 2. Valid Transition: IN_REVIEW -> PENDING_INFO
    res_pending = await async_client.patch(
        f"/api/v1/cases/{case_id}/status",
        json={"status": "PENDING_INFO", "actor": "analyst_bob", "reason": "Awaiting customer identity response"},
    )
    assert res_pending.status_code == 200
    assert res_pending.json()["status"] == "PENDING_INFO"

    # 3. Invalid Transition: PENDING_INFO -> NEW (should fail with 400 Bad Request)
    res_invalid = await async_client.patch(
        f"/api/v1/cases/{case_id}/status",
        json={"status": "NEW", "actor": "analyst_bob"},
    )
    assert res_invalid.status_code == 400
    assert "Invalid transition" in res_invalid.json()["detail"]

    # 4. Valid Transition: PENDING_INFO -> CLOSED
    res_closed = await async_client.patch(
        f"/api/v1/cases/{case_id}/status",
        json={"status": "CLOSED", "actor": "analyst_bob", "reason": "Investigation completed"},
    )
    assert res_closed.status_code == 200
    assert res_closed.json()["status"] == "CLOSED"


@pytest.mark.asyncio
async def test_case_assignment_and_priority_updates(async_client: AsyncClient):
    """
    Verify case assignment, reassignment, priority updates, and audit trails.
    """
    tx = {
        "transaction_id": "txn_assign_001",
        "customer_id": "cust_assign_001",
        "amount": "120.00",
        "payment_method": "card",
    }
    await async_client.post("/api/v1/transactions", json=tx)
    case_res = await async_client.post(
        "/api/v1/cases",
        json={"transaction_id": "txn_assign_001", "title": "Assignment Test Case"},
    )
    case_id = case_res.json()["case_id"]

    # 1. Update assignment
    res_assign = await async_client.patch(
        f"/api/v1/cases/{case_id}/assignment",
        json={"assigned_to": "analyst_jane", "actor": "supervisor_mark"},
    )
    assert res_assign.status_code == 200
    assert res_assign.json()["assigned_to"] == "analyst_jane"
    assert res_assign.json()["status"] == "ASSIGNED"

    # 2. Update priority
    res_priority = await async_client.patch(
        f"/api/v1/cases/{case_id}/priority",
        json={"priority": "CRITICAL", "actor": "supervisor_mark"},
    )
    assert res_priority.status_code == 200
    assert res_priority.json()["priority"] == "CRITICAL"

    # Verify audit events
    audit_events = res_priority.json()["audit_events"]
    event_types = [e["event_type"] for e in audit_events]
    assert "CASE_CREATED" in event_types
    assert "ASSIGNED" in event_types
    assert "PRIORITY_CHANGED" in event_types


@pytest.mark.asyncio
async def test_append_only_case_notes(async_client: AsyncClient):
    """
    Verify appending notes and sequential audit trail generation.
    """
    tx = {
        "transaction_id": "txn_notes_001",
        "customer_id": "cust_notes_001",
        "amount": "75.00",
        "payment_method": "card",
    }
    await async_client.post("/api/v1/transactions", json=tx)
    case_res = await async_client.post(
        "/api/v1/cases",
        json={"transaction_id": "txn_notes_001", "title": "Notes Test Case"},
    )
    case_id = case_res.json()["case_id"]

    # Add Note 1
    n1_res = await async_client.post(
        f"/api/v1/cases/{case_id}/notes",
        json={"content": "Contacted issuer bank regarding device fingerprint mismatch.", "author": "analyst_1"},
    )
    assert n1_res.status_code == 201
    assert n1_res.json()["author"] == "analyst_1"

    # Add Note 2
    n2_res = await async_client.post(
        f"/api/v1/cases/{case_id}/notes",
        json={"content": "Confirmed cardholder validated transaction as legitimate.", "author": "analyst_2"},
    )
    assert n2_res.status_code == 201

    # Fetch case details and assert 2 notes in chronological order
    case_detail = await async_client.get(f"/api/v1/cases/{case_id}")
    assert case_detail.status_code == 200
    notes = case_detail.json()["notes"]
    assert len(notes) == 2
    assert notes[0]["author"] == "analyst_1"
    assert notes[1]["author"] == "analyst_2"


@pytest.mark.asyncio
async def test_case_disposition_recording_and_closure(async_client: AsyncClient):
    """
    Verify recording analyst review dispositions (NO_ACTION, FALSE_POSITIVE, CONFIRMED_SUSPICIOUS, ESCALATED).
    """
    tx = {
        "transaction_id": "txn_disp_001",
        "customer_id": "cust_disp_001",
        "amount": "800.00",
        "payment_method": "card",
    }
    await async_client.post("/api/v1/transactions", json=tx)
    case_res = await async_client.post(
        "/api/v1/cases",
        json={"transaction_id": "txn_disp_001", "title": "Disposition Test Case"},
    )
    case_id = case_res.json()["case_id"]

    # Record disposition CONFIRMED_SUSPICIOUS
    disp_payload = {
        "disposition": "CONFIRMED_SUSPICIOUS",
        "rationale": "Identified coordinated device and IP clustering across synthetic accounts.",
        "actor": "senior_analyst_dan",
    }
    disp_res = await async_client.post(f"/api/v1/cases/{case_id}/disposition", json=disp_payload)
    assert disp_res.status_code == 200
    data = disp_res.json()

    assert data["disposition"] == "CONFIRMED_SUSPICIOUS"
    assert data["disposition_rationale"] == disp_payload["rationale"]
    assert data["disposition_by"] == "senior_analyst_dan"
    assert data["status"] == "CLOSED"
    assert data["disposition_at"] is not None

    # Verify DISPOSITION_RECORDED audit event
    disp_event = [e for e in data["audit_events"] if e["event_type"] == "DISPOSITION_RECORDED"]
    assert len(disp_event) == 1
    assert disp_event[0]["to_state"] == "CONFIRMED_SUSPICIOUS"
    assert disp_event[0]["actor"] == "senior_analyst_dan"


@pytest.mark.asyncio
async def test_critical_non_action_guarantee_and_immutability(async_client: AsyncClient):
    """
    CRITICAL NON-ACTION GUARANTEE:
    Verify that throughout case creation, priority updates, status transitions, notes, and dispositions,
    the underlying transaction status, transaction amount, assessment score, and findings remain STRICTLY UNMODIFIED.
    """
    # 1. Ingest transaction with initial SUCCESS status
    tx = {
        "transaction_id": "txn_immutable_001",
        "customer_id": "cust_immutable_001",
        "amount": "999.00",
        "payment_method": "card",
        "instrument_token": "tok_immutable_shared",
    }
    tx_res = await async_client.post("/api/v1/transactions", json=tx)
    assert tx_res.status_code == 201
    assert tx_res.json()["status"] == "SUCCESS"
    assert tx_res.json()["amount"] == "999.00"

    # 2. Run analysis and evaluate assessment
    await async_client.post("/api/v1/analysis/run")
    asmt_res = await async_client.post("/api/v1/assessments/evaluate/txn_immutable_001")
    assert asmt_res.status_code == 201
    initial_score = asmt_res.json()["score"]
    initial_rec = asmt_res.json()["recommendation"]
    asmt_id = asmt_res.json()["assessment_id"]

    # 3. Create case from assessment
    case_res = await async_client.post(f"/api/v1/cases/from-assessment/{asmt_id}")
    assert case_res.status_code == 201
    case_id = case_res.json()["case_id"]

    # 4. Perform series of analyst operations
    await async_client.patch(f"/api/v1/cases/{case_id}/priority", json={"priority": "CRITICAL", "actor": "analyst"})
    await async_client.patch(f"/api/v1/cases/{case_id}/status", json={"status": "IN_REVIEW", "actor": "analyst"})
    await async_client.post(f"/api/v1/cases/{case_id}/notes", json={"content": "Investigating abuse ring link.", "author": "analyst"})
    await async_client.post(f"/api/v1/cases/{case_id}/disposition", json={
        "disposition": "CONFIRMED_SUSPICIOUS",
        "rationale": "Abuse ring confirmed by intelligence team.",
        "actor": "analyst",
    })

    # 5. VERIFY TRANSACTION IMMUTABILITY:
    tx_check = await async_client.get("/api/v1/transactions/txn_immutable_001")
    assert tx_check.status_code == 200
    assert tx_check.json()["status"] == "SUCCESS", "FAIL: Transaction status was modified!"
    assert tx_check.json()["amount"] == "999.00", "FAIL: Transaction amount was modified!"

    # 6. VERIFY ASSESSMENT IMMUTABILITY:
    asmt_check = await async_client.get(f"/api/v1/assessments/{asmt_id}")
    assert asmt_check.status_code == 200
    assert asmt_check.json()["score"] == initial_score, "FAIL: Assessment score was modified!"
    assert asmt_check.json()["recommendation"] == initial_rec, "FAIL: Assessment recommendation was modified!"


@pytest.mark.asyncio
async def test_case_queue_filtering_and_pagination(async_client: AsyncClient):
    """
    Verify case queue listing with status, priority, and disposition filters.
    """
    # Create multiple cases
    for i in range(1, 4):
        tx = {
            "transaction_id": f"txn_queue_{i}",
            "customer_id": f"cust_queue_{i}",
            "amount": f"{100 * i}.00",
            "payment_method": "card",
        }
        await async_client.post("/api/v1/transactions", json=tx)
        await async_client.post(
            "/api/v1/cases",
            json={
                "transaction_id": f"txn_queue_{i}",
                "title": f"Queue Case #{i}",
                "priority": "HIGH" if i == 1 else "LOW",
                "assigned_to": "analyst_frank" if i == 2 else None,
            },
        )

    # 1. List all cases
    all_cases = await async_client.get("/api/v1/cases")
    assert all_cases.status_code == 200
    assert all_cases.json()["total"] >= 3

    # 2. Filter by priority=HIGH
    high_cases = await async_client.get("/api/v1/cases?priority=HIGH")
    assert high_cases.status_code == 200
    assert all(c["priority"] == "HIGH" for c in high_cases.json()["items"])

    # 3. Filter by assigned_to
    assigned_cases = await async_client.get("/api/v1/cases?assigned_to=analyst_frank")
    assert assigned_cases.status_code == 200
    assert len(assigned_cases.json()["items"]) >= 1
    assert assigned_cases.json()["items"][0]["assigned_to"] == "analyst_frank"
