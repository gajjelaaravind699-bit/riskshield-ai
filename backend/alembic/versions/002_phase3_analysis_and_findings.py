"""Phase 3 schema: analysis_runs, findings, finding_entities, and finding_transactions

Revision ID: 002_phase3_schema
Revises: 001_phase2_schema
Create Date: 2026-08-28 01:00:00.000000 UTC

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "002_phase3_schema"
down_revision: Union[str, None] = "001_phase2_schema"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create analysis_runs table
    op.create_table(
        "analysis_runs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("run_id", sa.String(length=100), nullable=False),
        sa.Column("status", sa.String(length=30), server_default="COMPLETED", nullable=False),
        sa.Column("total_transactions_analyzed", sa.Integer(), server_default="0", nullable=False),
        sa.Column("findings_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("config_hash", sa.String(length=64), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("run_id", name="uq_analysis_runs_run_id"),
    )
    op.create_index("ix_analysis_runs_run_id", "analysis_runs", ["run_id"])
    op.create_index("ix_analysis_runs_config_hash", "analysis_runs", ["config_hash"])

    # 2. Create findings table
    op.create_table(
        "findings",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("finding_id", sa.String(length=100), nullable=False),
        sa.Column("analysis_run_id", sa.Integer(), nullable=False),
        sa.Column("finding_type", sa.String(length=50), nullable=False),
        sa.Column("severity", sa.String(length=20), server_default="MEDIUM", nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("explanation", sa.Text(), nullable=False),
        sa.Column("fingerprint", sa.String(length=64), nullable=False),
        sa.Column("evidence_payload", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["analysis_run_id"], ["analysis_runs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("finding_id", name="uq_findings_finding_id"),
    )
    op.create_index("ix_findings_finding_id", "findings", ["finding_id"])
    op.create_index("ix_findings_analysis_run_id", "findings", ["analysis_run_id"])
    op.create_index("ix_findings_finding_type", "findings", ["finding_type"])
    op.create_index("ix_findings_severity", "findings", ["severity"])
    op.create_index("ix_findings_fingerprint", "findings", ["fingerprint"])

    # 3. Create finding_entities table
    op.create_table(
        "finding_entities",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("finding_id", sa.Integer(), nullable=False),
        sa.Column("entity_id", sa.Integer(), nullable=False),
        sa.Column("role", sa.String(length=50), server_default="ASSOCIATED_ENTITY", nullable=False),
        sa.ForeignKeyConstraint(["entity_id"], ["entities.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["finding_id"], ["findings.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("finding_id", "entity_id", "role", name="uq_finding_entity_role"),
    )
    op.create_index("ix_finding_entities_finding_id", "finding_entities", ["finding_id"])
    op.create_index("ix_finding_entities_entity_id", "finding_entities", ["entity_id"])

    # 4. Create finding_transactions table
    op.create_table(
        "finding_transactions",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("finding_id", sa.Integer(), nullable=False),
        sa.Column("transaction_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["finding_id"], ["findings.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["transaction_id"], ["transactions.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("finding_id", "transaction_id", name="uq_finding_transaction"),
    )
    op.create_index("ix_finding_transactions_finding_id", "finding_transactions", ["finding_id"])
    op.create_index("ix_finding_transactions_transaction_id", "finding_transactions", ["transaction_id"])


def downgrade() -> None:
    op.drop_table("finding_transactions")
    op.drop_table("finding_entities")
    op.drop_table("findings")
    op.drop_table("analysis_runs")
