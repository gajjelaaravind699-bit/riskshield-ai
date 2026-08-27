"""
API Endpoints for Graph & Pattern Analysis and Explainable Findings.
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.analysis import (
    AnalysisRunRequest,
    AnalysisRunRead,
    AnalysisRunListResponse,
    FindingRead,
    FindingListResponse,
)
from app.services.analysis_service import AnalysisService

router = APIRouter(prefix="/analysis", tags=["Analysis & Findings"])


@router.post(
    "/run",
    response_model=AnalysisRunRead,
    status_code=status.HTTP_201_CREATED,
    summary="Trigger Pattern & Graph Analysis",
    description=(
        "Executes deterministic rule-based relationship and frequency anomaly detectors "
        "across all persisted transactions and normalized entities. Produces explainable findings "
        "with supporting evidence traces and deterministic deduplication."
    ),
)
async def trigger_analysis_run(
    request: Optional[AnalysisRunRequest] = None,
    db: AsyncSession = Depends(get_db),
) -> AnalysisRunRead:
    config = request.config if request else None
    run = await AnalysisService.run_analysis(db=db, config=config)
    return AnalysisRunRead.model_validate(run)


@router.get(
    "/runs",
    response_model=AnalysisRunListResponse,
    status_code=status.HTTP_200_OK,
    summary="List Analysis Runs",
    description="Retrieve a paginated history of pattern analysis execution runs.",
)
async def list_analysis_runs(
    skip: int = Query(0, ge=0, description="Offset for pagination"),
    limit: int = Query(20, ge=1, le=100, description="Page size limit"),
    db: AsyncSession = Depends(get_db),
) -> AnalysisRunListResponse:
    runs, total = await AnalysisService.get_analysis_runs(db=db, skip=skip, limit=limit)
    items = [AnalysisRunRead.model_validate(r) for r in runs]
    page = (skip // limit) + 1 if limit > 0 else 1

    return AnalysisRunListResponse(
        items=items,
        total=total,
        page=page,
        page_size=limit,
    )


@router.get(
    "/runs/{run_id}",
    response_model=AnalysisRunRead,
    status_code=status.HTTP_200_OK,
    summary="Get Analysis Run By ID",
    description="Retrieve an analysis run along with all findings generated during that run.",
)
async def get_analysis_run(
    run_id: str,
    db: AsyncSession = Depends(get_db),
) -> AnalysisRunRead:
    run = await AnalysisService.get_analysis_run_by_id(db=db, run_id=run_id)
    if not run:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Analysis run '{run_id}' not found.",
        )
    return AnalysisRunRead.model_validate(run)


@router.get(
    "/findings",
    response_model=FindingListResponse,
    status_code=status.HTTP_200_OK,
    summary="List Explainable Findings",
    description="Retrieve a paginated list of relationship findings with optional type and severity filters.",
)
async def list_findings(
    skip: int = Query(0, ge=0, description="Offset for pagination"),
    limit: int = Query(50, ge=1, le=100, description="Page size limit"),
    finding_type: Optional[str] = Query(None, description="Filter by finding type"),
    severity: Optional[str] = Query(None, description="Filter by severity level"),
    run_id: Optional[str] = Query(None, description="Filter by analysis run ID"),
    db: AsyncSession = Depends(get_db),
) -> FindingListResponse:
    findings, total = await AnalysisService.get_findings(
        db=db,
        skip=skip,
        limit=limit,
        finding_type=finding_type,
        severity=severity,
        run_id=run_id,
    )
    items = [FindingRead.model_validate(f) for f in findings]
    page = (skip // limit) + 1 if limit > 0 else 1

    return FindingListResponse(
        items=items,
        total=total,
        page=page,
        page_size=limit,
    )


@router.get(
    "/findings/{finding_id}",
    response_model=FindingRead,
    status_code=status.HTTP_200_OK,
    summary="Get Finding By ID",
    description="Retrieve a single finding with complete explainability, structured evidence payload, and involved entities/transactions.",
)
async def get_finding(
    finding_id: str,
    db: AsyncSession = Depends(get_db),
) -> FindingRead:
    finding = await AnalysisService.get_finding_by_id(db=db, finding_id=finding_id)
    if not finding:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Finding '{finding_id}' not found.",
        )
    return FindingRead.model_validate(finding)
