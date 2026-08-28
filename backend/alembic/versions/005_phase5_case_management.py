"""Phase 5 schema: cases, case_notes, and case_audit_events tables

Revision ID: 005_phase5_case_management
Revises: 004_phase4_assessments
Create Date: 2026-08-28 03:00:00.000000 UTC

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "005_phase5_case_management"
down_revision: Union[str, None] = "004_phase4_assessments"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create cases table
    op.create_table(
        "cases",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("case_id", sa.String(length=100), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("priority", sa.String(length=20), nullable=False),
        sa.Column("assigned_to", sa.String(length=100), nullable=True),
        sa.Column("transaction_id", sa.Integer(), nullable=False),
        sa.Column("assessment_id", sa.Integer(), nullable=True),
        sa.Column("disposition", sa.String(length=50), nullable=True),
        sa.Column("disposition_rationale", sa.Text(), nullable=True),
        sa.Column("disposition_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("disposition_by", sa.String(length=100), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["transaction_id"],
            ["transactions.id"],
            name="fk_cases_transaction_id_transactions",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["assessment_id"],
            ["assessments.id"],
            name="fk_cases_assessment_id_assessments",
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_cases"),
    )
    op.create_index("ix_cases_case_id", "cases", ["case_id"], unique=True)
    op.create_index("ix_cases_status", "cases", ["status"], unique=False)
    op.create_index("ix_cases_priority", "cases", ["priority"], unique=False)
    op.create_index("ix_cases_assigned_to", "cases", ["assigned_to"], unique=False)
    op.create_index("ix_cases_transaction_id", "cases", ["transaction_id"], unique=False)
    op.create_index("ix_cases_assessment_id", "cases", ["assessment_id"], unique=False)
    op.create_index("ix_cases_disposition", "cases", ["disposition"], unique=False)

    # 2. Create case_notes table
    op.create_table(
        "case_notes",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("note_id", sa.String(length=100), nullable=False),
        sa.Column("case_id", sa.Integer(), nullable=False),
        sa.Column("author", sa.String(length=100), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["case_id"],
            ["cases.id"],
            name="fk_case_notes_case_id_cases",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_case_notes"),
    )
    op.create_index("ix_case_notes_note_id", "case_notes", ["note_id"], unique=True)
    op.create_index("ix_case_notes_case_id", "case_notes", ["case_id"], unique=False)

    # 3. Create case_audit_events table
    op.create_table(
        "case_audit_events",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("event_id", sa.String(length=100), nullable=False),
        sa.Column("case_id", sa.Integer(), nullable=False),
        sa.Column("event_type", sa.String(length=50), nullable=False),
        sa.Column("actor", sa.String(length=100), nullable=False),
        sa.Column("from_state", sa.String(length=100), nullable=True),
        sa.Column("to_state", sa.String(length=100), nullable=True),
        sa.Column("event_details", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["case_id"],
            ["cases.id"],
            name="fk_case_audit_events_case_id_cases",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_case_audit_events"),
    )
    op.create_index("ix_case_audit_events_event_id", "case_audit_events", ["event_id"], unique=True)
    op.create_index("ix_case_audit_events_case_id", "case_audit_events", ["case_id"], unique=False)
    op.create_index("ix_case_audit_events_event_type", "case_audit_events", ["event_type"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_case_audit_events_event_type", table_name="case_audit_events")
    op.drop_index("ix_case_audit_events_case_id", table_name="case_audit_events")
    op.drop_index("ix_case_audit_events_event_id", table_name="case_audit_events")
    op.drop_table("case_audit_events")

    op.drop_index("ix_case_notes_case_id", table_name="case_notes")
    op.drop_index("ix_case_notes_note_id", table_name="case_notes")
    op.drop_table("case_notes")

    op.drop_index("ix_cases_disposition", table_name="cases")
    op.drop_index("ix_cases_assessment_id", table_name="cases")
    op.drop_index("ix_cases_transaction_id", table_name="cases")
    op.drop_index("ix_cases_assigned_to", table_name="cases")
    op.drop_index("ix_cases_priority", table_name="cases")
    op.drop_index("ix_cases_status", table_name="cases")
    op.drop_index("ix_cases_case_id", table_name="cases")
    op.drop_table("cases")
