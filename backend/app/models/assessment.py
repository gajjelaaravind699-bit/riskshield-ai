"""
Assessment model representing an explainable, deterministic risk scoring and decision-support assessment.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, TYPE_CHECKING
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, JSON, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

if TYPE_CHECKING:
    from app.models.transaction import Transaction


class RiskLevel:
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

    ALL = [LOW, MEDIUM, HIGH, CRITICAL]


class Recommendation:
    ALLOW = "ALLOW"
    REVIEW = "REVIEW"
    BLOCK = "BLOCK"

    ALL = [ALLOW, REVIEW, BLOCK]


class Assessment(Base):
    """
    Immutable, explainable risk assessment for a transaction.
    Provides decision-support recommendations (ALLOW / REVIEW / BLOCK) without executing autonomous financial actions.
    """
    __tablename__ = "assessments"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    assessment_id: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        index=True,
        nullable=False,
    )
    transaction_id: Mapped[int] = mapped_column(
        ForeignKey("transactions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    score: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        index=True,
    )
    risk_level: Mapped[str] = mapped_column(
        String(20),
        default=RiskLevel.LOW,
        nullable=False,
        index=True,
    )
    recommendation: Mapped[str] = mapped_column(
        String(20),
        default=Recommendation.ALLOW,
        nullable=False,
        index=True,
    )
    explanation: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    ruleset_version: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )
    decision_policy_version: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )
    rule_contributions: Mapped[List[Dict[str, Any]]] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )
    evidence_summary: Mapped[Dict[str, Any]] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
    )
    action_executed: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    action_disclaimer: Mapped[str] = mapped_column(
        String(500),
        default=(
            "Decision-support recommendation only. RiskShield AI is an advisory sentinel "
            "and does not execute autonomous transaction blocks or financial interventions."
        ),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    transaction: Mapped["Transaction"] = relationship(
        "Transaction",
        lazy="selectin",
    )

    __table_args__ = (
        UniqueConstraint(
            "transaction_id",
            "ruleset_version",
            "decision_policy_version",
            name="uq_assessment_txn_ruleset_policy",
        ),
    )

    def __repr__(self) -> str:
        return (
            f"<Assessment(id='{self.assessment_id}', txn_id={self.transaction_id}, "
            f"score={self.score}, rec='{self.recommendation}')>"
        )
