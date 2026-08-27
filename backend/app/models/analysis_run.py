"""
AnalysisRun model representing a graph/pattern analysis execution batch.
"""

from datetime import datetime, timezone
from typing import List, TYPE_CHECKING
from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.models.base import TimestampMixin

if TYPE_CHECKING:
    from app.models.finding import Finding


class AnalysisRunStatus:
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class AnalysisRun(Base, TimestampMixin):
    """
    Record representing an execution run of the pattern and graph analysis engine.
    """
    __tablename__ = "analysis_runs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    run_id: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        index=True,
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(30),
        default=AnalysisRunStatus.COMPLETED,
        nullable=False,
    )
    total_transactions_analyzed: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    findings_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    config_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        index=True,
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Relationships
    findings: Mapped[List["Finding"]] = relationship(
        "Finding",
        back_populates="analysis_run",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<AnalysisRun(run_id='{self.run_id}', status='{self.status}', findings={self.findings_count})>"
