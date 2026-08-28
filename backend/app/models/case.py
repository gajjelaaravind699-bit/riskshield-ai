"""
Case management, analyst notes, and audit event models for Phase 5.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, TYPE_CHECKING
from sqlalchemy import DateTime, ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.models.base import TimestampMixin

if TYPE_CHECKING:
    from app.models.transaction import Transaction
    from app.models.assessment import Assessment


class CaseStatus:
    NEW = "NEW"
    ASSIGNED = "ASSIGNED"
    IN_REVIEW = "IN_REVIEW"
    PENDING_INFO = "PENDING_INFO"
    CLOSED = "CLOSED"
    ARCHIVED = "ARCHIVED"

    ALL = [NEW, ASSIGNED, IN_REVIEW, PENDING_INFO, CLOSED, ARCHIVED]

    # Valid transitions from each status
    ALLOWED_TRANSITIONS = {
        NEW: [ASSIGNED, IN_REVIEW, CLOSED, ARCHIVED],
        ASSIGNED: [IN_REVIEW, PENDING_INFO, CLOSED, ARCHIVED, NEW],
        IN_REVIEW: [PENDING_INFO, CLOSED, ARCHIVED, ASSIGNED],
        PENDING_INFO: [IN_REVIEW, CLOSED, ARCHIVED],
        CLOSED: [IN_REVIEW, ARCHIVED],
        ARCHIVED: [NEW, IN_REVIEW],
    }


class CasePriority:
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

    ALL = [LOW, MEDIUM, HIGH, CRITICAL]


class CaseDisposition:
    NO_ACTION = "NO_ACTION"
    FALSE_POSITIVE = "FALSE_POSITIVE"
    CONFIRMED_SUSPICIOUS = "CONFIRMED_SUSPICIOUS"
    ESCALATED = "ESCALATED"

    ALL = [NO_ACTION, FALSE_POSITIVE, CONFIRMED_SUSPICIOUS, ESCALATED]


class CaseAuditEventType:
    CASE_CREATED = "CASE_CREATED"
    STATUS_CHANGED = "STATUS_CHANGED"
    ASSIGNED = "ASSIGNED"
    PRIORITY_CHANGED = "PRIORITY_CHANGED"
    NOTE_ADDED = "NOTE_ADDED"
    DISPOSITION_RECORDED = "DISPOSITION_RECORDED"

    ALL = [
        CASE_CREATED,
        STATUS_CHANGED,
        ASSIGNED,
        PRIORITY_CHANGED,
        NOTE_ADDED,
        DISPOSITION_RECORDED,
    ]


class Case(Base, TimestampMixin):
    """
    Analyst case review tracking entity for investigating flagged transactions and risk assessments.
    """
    __tablename__ = "cases"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    case_id: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        index=True,
        nullable=False,
    )
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    status: Mapped[str] = mapped_column(
        String(30),
        default=CaseStatus.NEW,
        nullable=False,
        index=True,
    )
    priority: Mapped[str] = mapped_column(
        String(20),
        default=CasePriority.MEDIUM,
        nullable=False,
        index=True,
    )
    assigned_to: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        index=True,
    )
    transaction_id: Mapped[int] = mapped_column(
        ForeignKey("transactions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    assessment_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("assessments.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Analyst Review Disposition (Review outcome only, NOT financial/payment action)
    disposition: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        index=True,
    )
    disposition_rationale: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    disposition_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    disposition_by: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )

    # Relationships
    transaction: Mapped["Transaction"] = relationship(
        "Transaction",
        lazy="selectin",
    )
    assessment: Mapped[Optional["Assessment"]] = relationship(
        "Assessment",
        lazy="selectin",
    )
    notes: Mapped[List["CaseNote"]] = relationship(
        "CaseNote",
        back_populates="case",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="CaseNote.created_at.asc()",
    )
    audit_events: Mapped[List["CaseAuditEvent"]] = relationship(
        "CaseAuditEvent",
        back_populates="case",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="CaseAuditEvent.created_at.asc()",
    )

    def __repr__(self) -> str:
        return f"<Case(id='{self.case_id}', status='{self.status}', priority='{self.priority}')>"


class CaseNote(Base):
    """
    Append-only analyst notes attached to an investigation case.
    """
    __tablename__ = "case_notes"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    note_id: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        index=True,
        nullable=False,
    )
    case_id: Mapped[int] = mapped_column(
        ForeignKey("cases.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    author: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationship
    case: Mapped["Case"] = relationship("Case", back_populates="notes")

    def __repr__(self) -> str:
        return f"<CaseNote(id='{self.note_id}', author='{self.author}')>"


class CaseAuditEvent(Base):
    """
    Immutable audit log event for all lifecycle actions on a case.
    """
    __tablename__ = "case_audit_events"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    event_id: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        index=True,
        nullable=False,
    )
    case_id: Mapped[int] = mapped_column(
        ForeignKey("cases.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    event_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )
    actor: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    from_state: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )
    to_state: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )
    event_details: Mapped[Dict[str, Any]] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationship
    case: Mapped["Case"] = relationship("Case", back_populates="audit_events")

    def __repr__(self) -> str:
        return f"<CaseAuditEvent(id='{self.event_id}', type='{self.event_type}', actor='{self.actor}')>"
