"""
Pydantic schemas for deterministic risk scoring, decision-support assessment, and audit traces.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field
from app.schemas.analysis import TransactionSummaryRead


class RulesetConfig(BaseModel):
    """
    Configurable rule weights for deterministic risk factor scoring.
    """
    ruleset_version: str = Field(
        default="rs_v1.0.0",
        description="Semantic version tag for this ruleset specification.",
    )
    shared_instrument_weight: int = Field(
        default=40,
        ge=0,
        le=100,
        description="Risk score points for SHARED_PAYMENT_INSTRUMENT finding.",
    )
    shared_device_weight: int = Field(
        default=35,
        ge=0,
        le=100,
        description="Risk score points for SHARED_DEVICE finding.",
    )
    shared_ip_weight: int = Field(
        default=25,
        ge=0,
        le=100,
        description="Risk score points for SHARED_IP_CLUSTER finding.",
    )
    velocity_burst_weight: int = Field(
        default=20,
        ge=0,
        le=100,
        description="Risk score points for VELOCITY_BURST finding.",
    )
    failure_burst_weight: int = Field(
        default=25,
        ge=0,
        le=100,
        description="Risk score points for RAPID_FAILURE_BURST finding.",
    )
    base_score: int = Field(
        default=0,
        ge=0,
        le=100,
        description="Initial base risk score.",
    )
    max_score: int = Field(
        default=100,
        ge=1,
        le=100,
        description="Upper bound ceiling for total risk score.",
    )


class DecisionPolicyConfig(BaseModel):
    """
    Configurable decision-support policy thresholds mapping risk scores to recommendations.
    """
    decision_policy_version: str = Field(
        default="dp_v1.0.0",
        description="Semantic version tag for this decision policy specification.",
    )
    review_threshold: int = Field(
        default=30,
        ge=1,
        le=100,
        description="Minimum risk score required to trigger a REVIEW recommendation.",
    )
    block_threshold: int = Field(
        default=60,
        ge=1,
        le=100,
        description="Minimum risk score required to trigger a BLOCK recommendation.",
    )


class AssessmentEvaluationRequest(BaseModel):
    """
    Optional configuration overrides when triggering assessment evaluation.
    """
    ruleset: Optional[RulesetConfig] = Field(
        default=None,
        description="Custom ruleset configuration. Default is used if omitted.",
    )
    policy: Optional[DecisionPolicyConfig] = Field(
        default=None,
        description="Custom decision policy configuration. Default is used if omitted.",
    )


class RuleContributionRead(BaseModel):
    """
    Explainable breakdown of a single rule's contribution to the final risk score.
    """
    rule_name: str
    finding_type: str
    weight: int
    triggered: bool
    points_contributed: int
    description: str
    finding_ids: List[str] = Field(default=[])


class AssessmentRead(BaseModel):
    """
    Output schema for a completed decision-support assessment.
    """
    model_config = ConfigDict(from_attributes=True)

    id: int
    assessment_id: str
    transaction_id: int
    score: int
    risk_level: str
    recommendation: str
    explanation: str
    ruleset_version: str
    decision_policy_version: str
    rule_contributions: List[Dict[str, Any]]
    evidence_summary: Dict[str, Any]
    action_executed: bool
    action_disclaimer: str
    created_at: datetime
    transaction: Optional[TransactionSummaryRead] = None


class AssessmentListResponse(BaseModel):
    """
    Paginated list response for assessments.
    """
    items: List[AssessmentRead]
    total: int
    page: int
    page_size: int


class AssessmentBatchResponse(BaseModel):
    """
    Summary response for a batch assessment execution.
    """
    total_evaluated: int
    allow_count: int
    review_count: int
    block_count: int
    ruleset_version: str
    decision_policy_version: str
    action_disclaimer: str
    items: List[AssessmentRead]
