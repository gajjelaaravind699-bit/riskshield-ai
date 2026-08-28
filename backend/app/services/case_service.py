"""
Service layer for Phase 5 analyst case review, status transitions, notes, dispositions, and audit events.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from uuid import uuid4
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.case import (
    Case,
    CaseNote,
    CaseAuditEvent,
    CaseStatus,
    CasePriority,
    CaseDisposition,
    CaseAuditEventType,
)
from app.models.transaction import Transaction
from app.models.assessment import Assessment


class CaseService:
    @classmethod
    async def create_case(
        cls,
        db: AsyncSession,
        transaction_lookup: int | str,
        title: str,
        description: Optional[str] = None,
        priority: str = CasePriority.MEDIUM,
        assigned_to: Optional[str] = None,
        assessment_id: Optional[int] = None,
        actor: str = "analyst",
    ) -> Case:
        """
        Create a new analyst review case for a transaction.
        Generates initial immutable CASE_CREATED audit event.
        """
        # Validate priority
        if priority not in CasePriority.ALL:
            raise ValueError(f"Invalid priority '{priority}'. Must be one of: {', '.join(CasePriority.ALL)}")

        # Fetch transaction
        tx_stmt = select(Transaction)
        if isinstance(transaction_lookup, int):
            tx_stmt = tx_stmt.where(Transaction.id == transaction_lookup)
        else:
            tx_stmt = tx_stmt.where(Transaction.transaction_id == str(transaction_lookup))

        tx = (await db.execute(tx_stmt)).scalars().first()
        if not tx:
            raise ValueError(f"Transaction '{transaction_lookup}' not found.")

        # If assessment_id not provided, look for latest assessment for this transaction
        if not assessment_id:
            asmt_stmt = (
                select(Assessment.id)
                .where(Assessment.transaction_id == tx.id)
                .order_by(Assessment.created_at.desc())
            )
            assessment_id = (await db.execute(asmt_stmt)).scalars().first()

        case_id = f"case_{uuid4().hex[:10]}"
        initial_status = CaseStatus.ASSIGNED if assigned_to else CaseStatus.NEW

        case = Case(
            case_id=case_id,
            title=title,
            description=description,
            status=initial_status,
            priority=priority,
            assigned_to=assigned_to,
            transaction_id=tx.id,
            assessment_id=assessment_id,
        )
        db.add(case)
        await db.flush()

        # Record CASE_CREATED audit event
        audit_event = CaseAuditEvent(
            event_id=f"evt_{uuid4().hex[:10]}",
            case_id=case.id,
            event_type=CaseAuditEventType.CASE_CREATED,
            actor=actor,
            from_state=None,
            to_state=initial_status,
            event_details={
                "transaction_id": tx.transaction_id,
                "assessment_id": assessment_id,
                "priority": priority,
                "assigned_to": assigned_to,
                "title": title,
            },
        )
        db.add(audit_event)
        await db.flush()

        return await cls.get_case_by_id(db=db, case_lookup=case.id)  # type: ignore

    @classmethod
    async def create_case_from_assessment(
        cls,
        db: AsyncSession,
        assessment_lookup: int | str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        priority: Optional[str] = None,
        assigned_to: Optional[str] = None,
        actor: str = "analyst",
    ) -> Case:
        """
        Convenience method to instantiate a case directly from an assessment.
        """
        asmt_stmt = (
            select(Assessment)
            .options(selectinload(Assessment.transaction))
        )
        if isinstance(assessment_lookup, int):
            asmt_stmt = asmt_stmt.where(Assessment.id == assessment_lookup)
        else:
            asmt_stmt = asmt_stmt.where(Assessment.assessment_id == str(assessment_lookup))

        asmt = (await db.execute(asmt_stmt)).scalars().first()
        if not asmt:
            raise ValueError(f"Assessment '{assessment_lookup}' not found.")

        # Determine priority from assessment risk level if not explicitly provided
        if not priority:
            if asmt.risk_level == "CRITICAL":
                priority = CasePriority.CRITICAL
            elif asmt.risk_level == "HIGH":
                priority = CasePriority.HIGH
            elif asmt.risk_level == "MEDIUM":
                priority = CasePriority.MEDIUM
            else:
                priority = CasePriority.LOW

        case_title = title or f"Investigation Case: {asmt.recommendation} ({asmt.risk_level}) on {asmt.transaction.transaction_id}"
        case_desc = description or asmt.explanation

        return await cls.create_case(
            db=db,
            transaction_lookup=asmt.transaction_id,
            title=case_title,
            description=case_desc,
            priority=priority,
            assigned_to=assigned_to,
            assessment_id=asmt.id,
            actor=actor,
        )

    @classmethod
    async def get_cases(
        cls,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 50,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        assigned_to: Optional[str] = None,
        disposition: Optional[str] = None,
        transaction_id: Optional[str] = None,
    ) -> Tuple[List[Case], int]:
        """
        Retrieve paginated list of cases with filtering for case queue.
        """
        filters = []
        if status:
            filters.append(Case.status == status)
        if priority:
            filters.append(Case.priority == priority)
        if assigned_to:
            filters.append(Case.assigned_to == assigned_to)
        if disposition:
            filters.append(Case.disposition == disposition)
        if transaction_id:
            tx_subq = select(Transaction.id).where(Transaction.transaction_id == transaction_id)
            filters.append(Case.transaction_id.in_(tx_subq))

        count_stmt = select(func.count()).select_from(Case)
        if filters:
            count_stmt = count_stmt.where(*filters)
        total = (await db.execute(count_stmt)).scalar() or 0

        stmt = (
            select(Case)
            .options(
                selectinload(Case.transaction),
                selectinload(Case.assessment),
                selectinload(Case.notes),
                selectinload(Case.audit_events),
            )
            .order_by(Case.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        if filters:
            stmt = stmt.where(*filters)

        items = list((await db.execute(stmt)).scalars().all())
        return items, total

    @classmethod
    async def get_case_by_id(
        cls,
        db: AsyncSession,
        case_lookup: int | str,
    ) -> Optional[Case]:
        """
        Retrieve full case details including transaction, assessment, notes, and audit events.
        """
        stmt = (
            select(Case)
            .options(
                selectinload(Case.transaction),
                selectinload(Case.assessment),
                selectinload(Case.notes),
                selectinload(Case.audit_events),
            )
        )
        if isinstance(case_lookup, int):
            stmt = stmt.where(Case.id == case_lookup)
        else:
            stmt = stmt.where(Case.case_id == str(case_lookup))

        return (await db.execute(stmt)).scalars().first()

    @classmethod
    async def update_case_status(
        cls,
        db: AsyncSession,
        case_lookup: int | str,
        new_status: str,
        actor: str = "analyst",
        reason: Optional[str] = None,
    ) -> Case:
        """
        Transition case status according to controlled state machine rules.
        Records STATUS_CHANGED audit event.
        """
        case = await cls.get_case_by_id(db=db, case_lookup=case_lookup)
        if not case:
            raise ValueError(f"Case '{case_lookup}' not found.")

        if new_status not in CaseStatus.ALL:
            raise ValueError(f"Invalid status '{new_status}'. Allowed values: {', '.join(CaseStatus.ALL)}")

        if new_status == case.status:
            return case

        allowed_next = CaseStatus.ALLOWED_TRANSITIONS.get(case.status, [])
        if new_status not in allowed_next:
            raise ValueError(
                f"Invalid transition from '{case.status}' to '{new_status}'. "
                f"Allowed transitions: {', '.join(allowed_next)}"
            )

        prev_status = case.status
        case.status = new_status
        case.updated_at = datetime.now(timezone.utc)

        # Record audit event
        audit_event = CaseAuditEvent(
            event_id=f"evt_{uuid4().hex[:10]}",
            case_id=case.id,
            event_type=CaseAuditEventType.STATUS_CHANGED,
            actor=actor,
            from_state=prev_status,
            to_state=new_status,
            event_details={"reason": reason or "Status transition"},
        )
        db.add(audit_event)
        await db.flush()
        db.expire(case, ["audit_events", "notes"])

        return await cls.get_case_by_id(db=db, case_lookup=case.id)  # type: ignore

    @classmethod
    async def update_case_assignment(
        cls,
        db: AsyncSession,
        case_lookup: int | str,
        assigned_to: Optional[str],
        actor: str = "analyst",
    ) -> Case:
        """
        Assign or reassign a case to an analyst.
        Records ASSIGNED audit event.
        """
        case = await cls.get_case_by_id(db=db, case_lookup=case_lookup)
        if not case:
            raise ValueError(f"Case '{case_lookup}' not found.")

        prev_assignee = case.assigned_to
        case.assigned_to = assigned_to
        case.updated_at = datetime.now(timezone.utc)

        # If case was NEW and is now assigned, transition to ASSIGNED
        if case.status == CaseStatus.NEW and assigned_to:
            case.status = CaseStatus.ASSIGNED

        # Record audit event
        audit_event = CaseAuditEvent(
            event_id=f"evt_{uuid4().hex[:10]}",
            case_id=case.id,
            event_type=CaseAuditEventType.ASSIGNED,
            actor=actor,
            from_state=prev_assignee,
            to_state=assigned_to,
            event_details={"previous_assignee": prev_assignee, "new_assignee": assigned_to},
        )
        db.add(audit_event)
        await db.flush()
        db.expire(case, ["audit_events", "notes"])

        return await cls.get_case_by_id(db=db, case_lookup=case.id)  # type: ignore

    @classmethod
    async def update_case_priority(
        cls,
        db: AsyncSession,
        case_lookup: int | str,
        new_priority: str,
        actor: str = "analyst",
    ) -> Case:
        """
        Change priority level of a case.
        Records PRIORITY_CHANGED audit event.
        """
        case = await cls.get_case_by_id(db=db, case_lookup=case_lookup)
        if not case:
            raise ValueError(f"Case '{case_lookup}' not found.")

        if new_priority not in CasePriority.ALL:
            raise ValueError(f"Invalid priority '{new_priority}'. Must be one of: {', '.join(CasePriority.ALL)}")

        prev_priority = case.priority
        case.priority = new_priority
        case.updated_at = datetime.now(timezone.utc)

        audit_event = CaseAuditEvent(
            event_id=f"evt_{uuid4().hex[:10]}",
            case_id=case.id,
            event_type=CaseAuditEventType.PRIORITY_CHANGED,
            actor=actor,
            from_state=prev_priority,
            to_state=new_priority,
            event_details={"previous_priority": prev_priority, "new_priority": new_priority},
        )
        db.add(audit_event)
        await db.flush()
        db.expire(case, ["audit_events", "notes"])

        return await cls.get_case_by_id(db=db, case_lookup=case.id)  # type: ignore

    @classmethod
    async def add_case_note(
        cls,
        db: AsyncSession,
        case_lookup: int | str,
        author: str,
        content: str,
    ) -> CaseNote:
        """
        Append a new note to a case.
        Notes are append-only. Generates NOTE_ADDED audit event.
        """
        case = await cls.get_case_by_id(db=db, case_lookup=case_lookup)
        if not case:
            raise ValueError(f"Case '{case_lookup}' not found.")

        note_id = f"note_{uuid4().hex[:10]}"
        note = CaseNote(
            note_id=note_id,
            case_id=case.id,
            author=author,
            content=content,
        )
        db.add(note)
        case.updated_at = datetime.now(timezone.utc)
        await db.flush()

        # Record NOTE_ADDED audit event
        audit_event = CaseAuditEvent(
            event_id=f"evt_{uuid4().hex[:10]}",
            case_id=case.id,
            event_type=CaseAuditEventType.NOTE_ADDED,
            actor=author,
            from_state=None,
            to_state=None,
            event_details={
                "note_id": note.note_id,
                "content_preview": content[:120] + ("..." if len(content) > 120 else ""),
            },
        )
        db.add(audit_event)
        await db.flush()
        db.expire(case, ["audit_events", "notes"])

        return note

    @classmethod
    async def record_case_disposition(
        cls,
        db: AsyncSession,
        case_lookup: int | str,
        disposition: str,
        rationale: str,
        actor: str = "analyst",
    ) -> Case:
        """
        Record analyst review disposition (human review outcome, NOT financial/payment execution).
        Transitions case to CLOSED status and records DISPOSITION_RECORDED audit event.
        Underlying transaction and assessment records are strictly UNTOUCHED.
        """
        case = await cls.get_case_by_id(db=db, case_lookup=case_lookup)
        if not case:
            raise ValueError(f"Case '{case_lookup}' not found.")

        if disposition not in CaseDisposition.ALL:
            raise ValueError(
                f"Invalid disposition '{disposition}'. Must be one of: {', '.join(CaseDisposition.ALL)}"
            )

        prev_disp = case.disposition
        prev_status = case.status

        case.disposition = disposition
        case.disposition_rationale = rationale
        case.disposition_at = datetime.now(timezone.utc)
        case.disposition_by = actor
        case.status = CaseStatus.CLOSED
        case.updated_at = datetime.now(timezone.utc)

        # Record DISPOSITION_RECORDED audit event
        audit_event = CaseAuditEvent(
            event_id=f"evt_{uuid4().hex[:10]}",
            case_id=case.id,
            event_type=CaseAuditEventType.DISPOSITION_RECORDED,
            actor=actor,
            from_state=prev_disp,
            to_state=disposition,
            event_details={
                "disposition": disposition,
                "rationale": rationale,
                "previous_status": prev_status,
                "new_status": CaseStatus.CLOSED,
            },
        )
        db.add(audit_event)
        await db.flush()
        db.expire(case, ["audit_events", "notes"])

        return await cls.get_case_by_id(db=db, case_lookup=case.id)  # type: ignore
