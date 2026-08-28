"""
API Endpoints for Phase 5 Analyst Case Review, Notes, Dispositions, and Audit Trails.
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.case import (
    CaseCreate,
    CaseFromAssessmentCreate,
    CaseStatusUpdate,
    CaseAssignmentUpdate,
    CasePriorityUpdate,
    CaseNoteCreate,
    CaseDispositionCreate,
    CaseNoteRead,
    CaseRead,
    CaseListResponse,
)
from app.services.case_service import CaseService

router = APIRouter(prefix="/cases", tags=["Analyst Case Management"])


@router.post(
    "",
    response_model=CaseRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create Analyst Investigation Case",
    description="Create a new case attached to a transaction for human compliance review.",
)
async def create_case(
    payload: CaseCreate,
    db: AsyncSession = Depends(get_db),
) -> CaseRead:
    try:
        case = await CaseService.create_case(
            db=db,
            transaction_lookup=payload.transaction_id,
            title=payload.title,
            description=payload.description,
            priority=payload.priority or "MEDIUM",
            assigned_to=payload.assigned_to,
            actor=payload.actor or "analyst",
        )
        return CaseRead.model_validate(case)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post(
    "/from-assessment/{assessment_id}",
    response_model=CaseRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create Case from Flagged Assessment",
    description="Instantiate an investigation case directly from an existing risk assessment.",
)
async def create_case_from_assessment(
    assessment_id: str,
    payload: Optional[CaseFromAssessmentCreate] = None,
    db: AsyncSession = Depends(get_db),
) -> CaseRead:
    try:
        case = await CaseService.create_case_from_assessment(
            db=db,
            assessment_lookup=assessment_id,
            title=payload.title if payload else None,
            description=payload.description if payload else None,
            priority=payload.priority if payload else None,
            assigned_to=payload.assigned_to if payload else None,
            actor=payload.actor if payload else "analyst",
        )
        return CaseRead.model_validate(case)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get(
    "",
    response_model=CaseListResponse,
    status_code=status.HTTP_200_OK,
    summary="List Cases in Queue",
    description="Retrieve paginated cases with status, priority, assignee, and disposition filtering.",
)
async def list_cases(
    skip: int = Query(0, ge=0, description="Pagination offset skip"),
    limit: int = Query(50, ge=1, le=100, description="Page limit"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by case status"),
    priority_filter: Optional[str] = Query(None, alias="priority", description="Filter by case priority"),
    assigned_to: Optional[str] = Query(None, description="Filter by assigned analyst"),
    disposition: Optional[str] = Query(None, description="Filter by analyst disposition"),
    transaction_id: Optional[str] = Query(None, description="Filter by transaction reference ID"),
    db: AsyncSession = Depends(get_db),
) -> CaseListResponse:
    items, total = await CaseService.get_cases(
        db=db,
        skip=skip,
        limit=limit,
        status=status_filter,
        priority=priority_filter,
        assigned_to=assigned_to,
        disposition=disposition,
        transaction_id=transaction_id,
    )
    validated_items = [CaseRead.model_validate(c) for c in items]
    page = (skip // limit) + 1
    return CaseListResponse(
        items=validated_items,
        total=total,
        page=page,
        page_size=limit,
    )


@router.get(
    "/{case_id}",
    response_model=CaseRead,
    status_code=status.HTTP_200_OK,
    summary="Get Case Details by ID",
    description="Retrieve full case details including transaction, assessment, notes, and audit events.",
)
async def get_case(
    case_id: str,
    db: AsyncSession = Depends(get_db),
) -> CaseRead:
    case = await CaseService.get_case_by_id(db=db, case_lookup=case_id)
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Case '{case_id}' not found.",
        )
    return CaseRead.model_validate(case)


@router.patch(
    "/{case_id}/status",
    response_model=CaseRead,
    status_code=status.HTTP_200_OK,
    summary="Update Case Status",
    description="Transition case status according to state machine rules with audit trail.",
)
async def update_case_status(
    case_id: str,
    payload: CaseStatusUpdate,
    db: AsyncSession = Depends(get_db),
) -> CaseRead:
    try:
        case = await CaseService.update_case_status(
            db=db,
            case_lookup=case_id,
            new_status=payload.status,
            actor=payload.actor,
            reason=payload.reason,
        )
        return CaseRead.model_validate(case)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.patch(
    "/{case_id}/assignment",
    response_model=CaseRead,
    status_code=status.HTTP_200_OK,
    summary="Assign Case to Analyst",
    description="Assign or reassign an analyst to handle this case.",
)
async def update_case_assignment(
    case_id: str,
    payload: CaseAssignmentUpdate,
    db: AsyncSession = Depends(get_db),
) -> CaseRead:
    try:
        case = await CaseService.update_case_assignment(
            db=db,
            case_lookup=case_id,
            assigned_to=payload.assigned_to,
            actor=payload.actor,
        )
        return CaseRead.model_validate(case)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.patch(
    "/{case_id}/priority",
    response_model=CaseRead,
    status_code=status.HTTP_200_OK,
    summary="Update Case Priority",
    description="Change the priority level of a case.",
)
async def update_case_priority(
    case_id: str,
    payload: CasePriorityUpdate,
    db: AsyncSession = Depends(get_db),
) -> CaseRead:
    try:
        case = await CaseService.update_case_priority(
            db=db,
            case_lookup=case_id,
            new_priority=payload.priority,
            actor=payload.actor,
        )
        return CaseRead.model_validate(case)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post(
    "/{case_id}/notes",
    response_model=CaseNoteRead,
    status_code=status.HTTP_201_CREATED,
    summary="Add Append-Only Analyst Note",
    description="Append a new investigation note to the case history.",
)
async def add_case_note(
    case_id: str,
    payload: CaseNoteCreate,
    db: AsyncSession = Depends(get_db),
) -> CaseNoteRead:
    try:
        note = await CaseService.add_case_note(
            db=db,
            case_lookup=case_id,
            author=payload.author,
            content=payload.content,
        )
        return CaseNoteRead.model_validate(note)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post(
    "/{case_id}/disposition",
    response_model=CaseRead,
    status_code=status.HTTP_200_OK,
    summary="Record Analyst Review Disposition",
    description=(
        "Record analyst human review outcome (NO_ACTION, FALSE_POSITIVE, CONFIRMED_SUSPICIOUS, ESCALATED). "
        "Strictly advisory outcome — never executes payment blocks or modifies transaction data."
    ),
)
async def record_case_disposition(
    case_id: str,
    payload: CaseDispositionCreate,
    db: AsyncSession = Depends(get_db),
) -> CaseRead:
    try:
        case = await CaseService.record_case_disposition(
            db=db,
            case_lookup=case_id,
            disposition=payload.disposition,
            rationale=payload.rationale,
            actor=payload.actor,
        )
        return CaseRead.model_validate(case)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
