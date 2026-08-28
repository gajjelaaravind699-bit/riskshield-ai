"""
Pydantic schemas for Phase 5 analyst case review, status transitions, notes, dispositions, and audit traces.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field
from app.schemas.analysis import TransactionSummaryRead
from app.schemas.assessment import AssessmentRead


class CaseCreate(BaseModel):
    """
    Schema for creating a case manually for a transaction.
    """
    transaction_id: str = Field(..., description="Transaction ID to attach this investigation case to.")
    title: str = Field(..., min_length=3, max_length=255, description="Short summary title for the case.")
    description: Optional[str] = Field(default=None, description="Detailed context or rationale for case creation.")
    priority: Optional[str] = Field(default="MEDIUM", description="Case priority (LOW, MEDIUM, HIGH, CRITICAL).")
    assigned_to: Optional[str] = Field(default=None, description="Analyst identifier assigned to handle case.")
    actor: Optional[str] = Field(default="analyst", description="Analyst or system actor creating the case.")


class CaseFromAssessmentCreate(BaseModel):
    """
    Schema for creating a case directly from an existing flagged assessment.
    """
    title: Optional[str] = Field(default=None, description="Optional custom title. Auto-generated if omitted.")
    description: Optional[str] = Field(default=None, description="Optional custom description.")
    priority: Optional[str] = Field(default=None, description="Optional priority override. Mapped from risk level if omitted.")
    assigned_to: Optional[str] = Field(default=None, description="Analyst identifier to assign immediately.")
    actor: Optional[str] = Field(default="analyst", description="Actor creating the case.")


class CaseStatusUpdate(BaseModel):
    """
    Schema for updating case status with audit trail.
    """
    status: str = Field(..., description="Target status (NEW, ASSIGNED, IN_REVIEW, PENDING_INFO, CLOSED, ARCHIVED).")
    actor: str = Field(default="analyst", description="Analyst performing the status transition.")
    reason: Optional[str] = Field(default=None, description="Explanation or justification for status change.")


class CaseAssignmentUpdate(BaseModel):
    """
    Schema for assigning or reassigning a case to an analyst.
    """
    assigned_to: Optional[str] = Field(default=None, description="Target analyst identifier (or null to unassign).")
    actor: str = Field(default="analyst", description="Analyst performing the assignment.")


class CasePriorityUpdate(BaseModel):
    """
    Schema for changing case priority level.
    """
    priority: str = Field(..., description="Target priority (LOW, MEDIUM, HIGH, CRITICAL).")
    actor: str = Field(default="analyst", description="Analyst changing the priority.")


class CaseNoteCreate(BaseModel):
    """
    Schema for adding an append-only note to a case.
    """
    content: str = Field(..., min_length=1, max_length=5000, description="Note text content.")
    author: str = Field(default="analyst", description="Analyst authoring this note.")


class CaseDispositionCreate(BaseModel):
    """
    Schema for recording an analyst review disposition (human review outcome, NOT financial/payment action).
    """
    disposition: str = Field(
        ...,
        description="Analyst disposition outcome (NO_ACTION, FALSE_POSITIVE, CONFIRMED_SUSPICIOUS, ESCALATED).",
    )
    rationale: str = Field(
        ...,
        min_length=3,
        max_length=5000,
        description="Detailed justification and findings summary supporting this disposition.",
    )
    actor: str = Field(default="analyst", description="Analyst recording the disposition.")


class CaseNoteRead(BaseModel):
    """
    Output schema for an append-only case note.
    """
    model_config = ConfigDict(from_attributes=True)

    id: int
    note_id: str
    author: str
    content: str
    created_at: datetime


class CaseAuditEventRead(BaseModel):
    """
    Output schema for an immutable case audit log event.
    """
    model_config = ConfigDict(from_attributes=True)

    id: int
    event_id: str
    event_type: str
    actor: str
    from_state: Optional[str] = None
    to_state: Optional[str] = None
    event_details: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime


class CaseRead(BaseModel):
    """
    Full output schema for an analyst case with notes, audit events, transaction, and assessment links.
    """
    model_config = ConfigDict(from_attributes=True)

    id: int
    case_id: str
    title: str
    description: Optional[str] = None
    status: str
    priority: str
    assigned_to: Optional[str] = None
    transaction_id: int
    assessment_id: Optional[int] = None
    disposition: Optional[str] = None
    disposition_rationale: Optional[str] = None
    disposition_at: Optional[datetime] = None
    disposition_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    transaction: Optional[TransactionSummaryRead] = None
    assessment: Optional[AssessmentRead] = None
    notes: List[CaseNoteRead] = Field(default=[])
    audit_events: List[CaseAuditEventRead] = Field(default=[])


class CaseListResponse(BaseModel):
    """
    Paginated list response for cases in queue.
    """
    items: List[CaseRead]
    total: int
    page: int
    page_size: int
