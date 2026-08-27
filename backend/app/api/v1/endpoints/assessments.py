"""
API Endpoints for Deterministic Risk Assessment and Decision-Support Recommendations.
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.assessment import (
    AssessmentEvaluationRequest,
    AssessmentRead,
    AssessmentListResponse,
    AssessmentBatchResponse,
)
from app.services.assessment_service import AssessmentService

router = APIRouter(prefix="/assessments", tags=["Risk Assessments & Decision Support"])


@router.post(
    "/evaluate/{transaction_id}",
    response_model=AssessmentRead,
    status_code=status.HTTP_201_CREATED,
    summary="Evaluate Risk Assessment for a Transaction",
    description=(
        "Performs deterministic risk scoring and decision-support recommendation (ALLOW / REVIEW / BLOCK) "
        "for a transaction based on persisted abuse ring findings. "
        "Advisory only — never alters underlying transaction status or executes financial blocks."
    ),
)
async def evaluate_transaction(
    transaction_id: str,
    payload: Optional[AssessmentEvaluationRequest] = None,
    db: AsyncSession = Depends(get_db),
) -> AssessmentRead:
    ruleset = payload.ruleset if payload else None
    policy = payload.policy if payload else None
    try:
        assessment = await AssessmentService.evaluate_transaction(
            db=db,
            transaction_lookup=transaction_id,
            ruleset=ruleset,
            policy=policy,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    
    # Reload with relationships loaded for clean validation
    reloaded = await AssessmentService.get_assessment_by_id(db=db, assessment_id=assessment.assessment_id)
    return AssessmentRead.model_validate(reloaded)


@router.post(
    "/evaluate-all",
    response_model=AssessmentBatchResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Evaluate All Persisted Transactions",
    description=(
        "Executes batch risk scoring across all persisted transactions using the active ruleset and decision policy. "
        "Produces auditable decision-support recommendations."
    ),
)
async def evaluate_all_transactions(
    payload: Optional[AssessmentEvaluationRequest] = None,
    db: AsyncSession = Depends(get_db),
) -> AssessmentBatchResponse:
    ruleset = payload.ruleset if payload else None
    policy = payload.policy if payload else None
    return await AssessmentService.evaluate_all_transactions(
        db=db,
        ruleset=ruleset,
        policy=policy,
    )


@router.get(
    "",
    response_model=AssessmentListResponse,
    status_code=status.HTTP_200_OK,
    summary="List Assessments",
    description="Retrieve paginated list of risk assessments with optional recommendation and risk level filters.",
)
async def list_assessments(
    skip: int = Query(0, ge=0, description="Offset pagination skip"),
    limit: int = Query(50, ge=1, le=100, description="Page limit"),
    recommendation: Optional[str] = Query(None, description="Filter by recommendation (ALLOW, REVIEW, BLOCK)"),
    risk_level: Optional[str] = Query(None, description="Filter by risk level (LOW, MEDIUM, HIGH, CRITICAL)"),
    customer_id: Optional[str] = Query(None, description="Filter by customer account ID"),
    transaction_id: Optional[str] = Query(None, description="Filter by transaction reference ID"),
    db: AsyncSession = Depends(get_db),
) -> AssessmentListResponse:
    items, total = await AssessmentService.get_assessments(
        db=db,
        skip=skip,
        limit=limit,
        recommendation=recommendation,
        risk_level=risk_level,
        customer_id=customer_id,
        transaction_id=transaction_id,
    )
    validated_items = [AssessmentRead.model_validate(asmt) for asmt in items]
    page = (skip // limit) + 1
    return AssessmentListResponse(
        items=validated_items,
        total=total,
        page=page,
        page_size=limit,
    )


@router.get(
    "/{assessment_id}",
    response_model=AssessmentRead,
    status_code=status.HTTP_200_OK,
    summary="Get Assessment by ID",
    description="Retrieve a single assessment report with full rule contribution and evidence breakdown.",
)
async def get_assessment(
    assessment_id: str,
    db: AsyncSession = Depends(get_db),
) -> AssessmentRead:
    assessment = await AssessmentService.get_assessment_by_id(db=db, assessment_id=assessment_id)
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Assessment '{assessment_id}' not found",
        )
    return AssessmentRead.model_validate(assessment)


@router.get(
    "/transaction/{transaction_id}",
    response_model=AssessmentRead,
    status_code=status.HTTP_200_OK,
    summary="Get Assessment for a Transaction",
    description="Retrieve the latest risk assessment evaluated for a specific transaction ID.",
)
async def get_assessment_by_transaction(
    transaction_id: str,
    db: AsyncSession = Depends(get_db),
) -> AssessmentRead:
    assessment = await AssessmentService.get_assessment_by_transaction_id(
        db=db,
        transaction_id=transaction_id,
    )
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No assessment found for transaction '{transaction_id}'",
        )
    return AssessmentRead.model_validate(assessment)
