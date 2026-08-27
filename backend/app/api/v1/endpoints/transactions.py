"""
API Endpoints for Transaction ingestion, querying, and retrieval.
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.transaction import (
    TransactionCreate,
    TransactionRead,
    TransactionListResponse,
    TransactionBatchCreate,
    TransactionBatchResponse,
)
from app.services.transaction_service import (
    TransactionService,
    DuplicateTransactionError,
)

router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.post(
    "",
    response_model=TransactionRead,
    status_code=status.HTTP_201_CREATED,
    summary="Ingest Single Transaction",
    description=(
        "Ingest a single payment transaction with zero-trust validation. "
        "Automatically resolves and links normalized graph entities (USER, PAYMENT_INSTRUMENT, DEVICE, IP)."
    ),
)
async def ingest_transaction(
    transaction_in: TransactionCreate,
    db: AsyncSession = Depends(get_db),
) -> TransactionRead:
    try:
        transaction = await TransactionService.ingest_transaction(
            db=db,
            transaction_in=transaction_in,
        )
        return TransactionRead.model_validate(transaction)
    except DuplicateTransactionError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )


@router.post(
    "/batch",
    response_model=TransactionBatchResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Ingest Transaction Batch",
    description="Ingest a batch of up to 500 payment transactions atomically.",
)
async def ingest_transactions_batch(
    batch_in: TransactionBatchCreate,
    db: AsyncSession = Depends(get_db),
) -> TransactionBatchResponse:
    try:
        transactions = await TransactionService.ingest_transactions_batch(
            db=db,
            batch_in=batch_in,
        )
        items = [TransactionRead.model_validate(tx) for tx in transactions]
        return TransactionBatchResponse(
            ingested_count=len(items),
            items=items,
        )
    except DuplicateTransactionError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )


@router.get(
    "",
    response_model=TransactionListResponse,
    status_code=status.HTTP_200_OK,
    summary="List Transactions",
    description="Retrieve a paginated list of ingested transactions with optional filtering.",
)
async def list_transactions(
    skip: int = Query(0, ge=0, description="Offset for pagination"),
    limit: int = Query(50, ge=1, le=100, description="Page size limit"),
    customer_id: Optional[str] = Query(None, description="Filter by customer identifier"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by transaction status"),
    payment_method: Optional[str] = Query(None, description="Filter by payment method"),
    db: AsyncSession = Depends(get_db),
) -> TransactionListResponse:
    items, total = await TransactionService.get_transactions(
        db=db,
        skip=skip,
        limit=limit,
        customer_id=customer_id,
        status=status_filter,
        payment_method=payment_method,
    )
    validated_items = [TransactionRead.model_validate(tx) for tx in items]
    page = (skip // limit) + 1 if limit > 0 else 1

    return TransactionListResponse(
        items=validated_items,
        total=total,
        page=page,
        page_size=limit,
    )


@router.get(
    "/{transaction_id}",
    response_model=TransactionRead,
    status_code=status.HTTP_200_OK,
    summary="Get Transaction By ID",
    description="Retrieve a single transaction and its linked normalized entity relationships.",
)
async def get_transaction(
    transaction_id: str,
    db: AsyncSession = Depends(get_db),
) -> TransactionRead:
    transaction = await TransactionService.get_transaction_by_id(
        db=db,
        transaction_id=transaction_id,
    )
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction with ID '{transaction_id}' not found.",
        )
    return TransactionRead.model_validate(transaction)
