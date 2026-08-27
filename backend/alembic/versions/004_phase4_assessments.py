"""Phase 4 schema: assessments table with unique constraint and indexes

Revision ID: 004_phase4_assessments
Revises: 003_unique_finding_fingerprint
Create Date: 2026-08-28 02:30:00.000000 UTC

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "004_phase4_assessments"
down_revision: Union[str, None] = "003_unique_finding_fingerprint"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "assessments",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("assessment_id", sa.String(length=100), nullable=False),
        sa.Column("transaction_id", sa.Integer(), nullable=False),
        sa.Column("score", sa.Integer(), nullable=False),
        sa.Column("risk_level", sa.String(length=20), nullable=False),
        sa.Column("recommendation", sa.String(length=20), nullable=False),
        sa.Column("explanation", sa.Text(), nullable=False),
        sa.Column("ruleset_version", sa.String(length=50), nullable=False),
        sa.Column("decision_policy_version", sa.String(length=50), nullable=False),
        sa.Column("rule_contributions", sa.JSON(), nullable=False),
        sa.Column("evidence_summary", sa.JSON(), nullable=False),
        sa.Column("action_executed", sa.Boolean(), nullable=False, server_default=sa.text("0")),
        sa.Column("action_disclaimer", sa.String(length=500), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["transaction_id"],
            ["transactions.id"],
            name="fk_assessments_transaction_id_transactions",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_assessments"),
        sa.UniqueConstraint(
            "transaction_id",
            "ruleset_version",
            "decision_policy_version",
            name="uq_assessment_txn_ruleset_policy",
        ),
    )
    op.create_index("ix_assessments_assessment_id", "assessments", ["assessment_id"], unique=True)
    op.create_index("ix_assessments_transaction_id", "assessments", ["transaction_id"], unique=False)
    op.create_index("ix_assessments_score", "assessments", ["score"], unique=False)
    op.create_index("ix_assessments_risk_level", "assessments", ["risk_level"], unique=False)
    op.create_index("ix_assessments_recommendation", "assessments", ["recommendation"], unique=False)
    op.create_index("ix_assessments_ruleset_version", "assessments", ["ruleset_version"], unique=False)
    op.create_index("ix_assessments_decision_policy_version", "assessments", ["decision_policy_version"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_assessments_decision_policy_version", table_name="assessments")
    op.drop_index("ix_assessments_ruleset_version", table_name="assessments")
    op.drop_index("ix_assessments_recommendation", table_name="assessments")
    op.drop_index("ix_assessments_risk_level", table_name="assessments")
    op.drop_index("ix_assessments_score", table_name="assessments")
    op.drop_index("ix_assessments_transaction_id", table_name="assessments")
    op.drop_index("ix_assessments_assessment_id", table_name="assessments")
    op.drop_table("assessments")
