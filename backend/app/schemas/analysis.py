"""
Pydantic schemas for graph/pattern analysis runs and explainable findings.
"""

from decimal import Decimal
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field
from app.schemas.transaction import EntityRead


class AnalysisConfig(BaseModel):
    """
    Configurable detection threshold parameters for rule-based analysis.
    """
    shared_instrument_threshold: int = Field(
        default=2,
        ge=2,
        le=50,
        description="Minimum distinct customer accounts sharing a payment instrument to trigger finding.",
    )
    shared_device_threshold: int = Field(
        default=2,
        ge=2,
        le=50,
        description="Minimum distinct customer accounts sharing a device to trigger finding.",
    )
    shared_ip_threshold: int = Field(
        default=3,
        ge=2,
        le=100,
        description="Minimum distinct customer accounts sharing an IP address to trigger finding.",
    )
    velocity_burst_count: int = Field(
        default=3,
        ge=2,
        le=100,
        description="Minimum transactions within sliding window to trigger velocity burst.",
    )
    velocity_window_minutes: int = Field(
        default=10,
        ge=1,
        le=1440,
        description="Sliding window duration in minutes for velocity burst detection.",
    )
    failure_burst_count: int = Field(
        default=3,
        ge=2,
        le=100,
        description="Minimum failed transactions within sliding window to trigger failure burst.",
    )
    failure_window_minutes: int = Field(
        default=15,
        ge=1,
        le=1440,
        description="Sliding window duration in minutes for failure burst detection.",
    )


class AnalysisRunRequest(BaseModel):
    """
    Request payload to trigger a pattern/graph analysis execution.
    """
    config: Optional[AnalysisConfig] = Field(
        default=None,
        description="Custom threshold configurations. Uses default thresholds if omitted.",
    )


class FindingEntityRead(BaseModel):
    """
    Output schema for an entity linked to a finding.
    """
    model_config = ConfigDict(from_attributes=True)

    id: int
    role: str
    entity: EntityRead


class TransactionSummaryRead(BaseModel):
    """
    Summary representation of a transaction linked to a finding.
    """
    model_config = ConfigDict(from_attributes=True)

    id: int
    transaction_id: str
    customer_id: str
    amount: Decimal
    currency: str
    status: str
    payment_method: str
    card_bin: Optional[str] = None
    card_last4: Optional[str] = None
    instrument_token: Optional[str] = None
    upi_vpa: Optional[str] = None
    device_id: Optional[str] = None
    ip_address: Optional[str] = None
    transacted_at: datetime


class FindingTransactionRead(BaseModel):
    """
    Output schema for a transaction linked to a finding.
    """
    model_config = ConfigDict(from_attributes=True)

    id: int
    transaction: TransactionSummaryRead


class FindingRead(BaseModel):
    """
    Output schema for an explainable relationship/pattern finding.
    """
    model_config = ConfigDict(from_attributes=True)

    id: int
    finding_id: str
    analysis_run_id: int
    finding_type: str
    severity: str
    title: str
    explanation: str
    fingerprint: str
    evidence_payload: Dict[str, Any]
    created_at: datetime
    related_entities: List[FindingEntityRead] = Field(
        default=[],
        description="Entities participating in this finding.",
    )
    related_transactions: List[FindingTransactionRead] = Field(
        default=[],
        description="Transactions participating in this finding.",
    )


class FindingListResponse(BaseModel):
    """
    Paginated response for findings.
    """
    items: List[FindingRead]
    total: int
    page: int
    page_size: int


class AnalysisRunRead(BaseModel):
    """
    Output schema for an analysis execution run.
    """
    model_config = ConfigDict(from_attributes=True)

    id: int
    run_id: str
    status: str
    total_transactions_analyzed: int
    findings_count: int
    config_hash: str
    completed_at: Optional[datetime] = None
    created_at: datetime
    findings: List[FindingRead] = Field(
        default=[],
        description="Findings detected during this analysis run.",
    )


class AnalysisRunListResponse(BaseModel):
    """
    Paginated response for analysis runs.
    """
    items: List[AnalysisRunRead]
    total: int
    page: int
    page_size: int
