"""
Finding model representing an observed graph or pattern anomaly finding.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, TYPE_CHECKING
from sqlalchemy import DateTime, ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

if TYPE_CHECKING:
    from app.models.analysis_run import AnalysisRun
    from app.models.finding_entity import FindingEntity
    from app.models.finding_transaction import FindingTransaction


class FindingType:
    SHARED_PAYMENT_INSTRUMENT = "SHARED_PAYMENT_INSTRUMENT"
    SHARED_DEVICE = "SHARED_DEVICE"
    SHARED_IP_CLUSTER = "SHARED_IP_CLUSTER"
    VELOCITY_BURST = "VELOCITY_BURST"
    RAPID_FAILURE_BURST = "RAPID_FAILURE_BURST"

    ALL = [
        SHARED_PAYMENT_INSTRUMENT,
        SHARED_DEVICE,
        SHARED_IP_CLUSTER,
        VELOCITY_BURST,
        RAPID_FAILURE_BURST,
    ]


class FindingSeverity:
    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"

    ALL = [INFO, LOW, MEDIUM, HIGH]


class Finding(Base):
    """
    Observed pattern or relationship finding with explainable evidence traces.
    """
    __tablename__ = "findings"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    finding_id: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        index=True,
        nullable=False,
    )
    analysis_run_id: Mapped[int] = mapped_column(
        ForeignKey("analysis_runs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    finding_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )
    severity: Mapped[str] = mapped_column(
        String(20),
        default=FindingSeverity.MEDIUM,
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    explanation: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    fingerprint: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        index=True,
    )
    evidence_payload: Mapped[Dict[str, Any]] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    analysis_run: Mapped["AnalysisRun"] = relationship(
        "AnalysisRun",
        back_populates="findings",
    )
    related_entities: Mapped[List["FindingEntity"]] = relationship(
        "FindingEntity",
        back_populates="finding",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    related_transactions: Mapped[List["FindingTransaction"]] = relationship(
        "FindingTransaction",
        back_populates="finding",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Finding(id='{self.finding_id}', type='{self.finding_type}', severity='{self.severity}')>"
