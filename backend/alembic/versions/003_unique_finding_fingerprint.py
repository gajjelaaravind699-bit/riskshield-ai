"""Add unique constraint to findings fingerprint and clean duplicate verification records

Revision ID: 003_unique_finding_fingerprint
Revises: 002_phase3_schema
Create Date: 2026-08-28 02:00:00.000000 UTC

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "003_unique_finding_fingerprint"
down_revision: Union[str, None] = "002_phase3_schema"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Safely remove duplicate verification rows retaining the earliest row per fingerprint
    op.execute(
        sa.text(
            """
            DELETE FROM findings
            WHERE id NOT IN (
                SELECT MIN(id)
                FROM findings
                GROUP BY fingerprint
            )
            """
        )
    )

    # 2. Add database-level unique constraint on findings.fingerprint using batch_alter_table
    with op.batch_alter_table("findings", schema=None) as batch_op:
        batch_op.create_unique_constraint("uq_findings_fingerprint", ["fingerprint"])


def downgrade() -> None:
    with op.batch_alter_table("findings", schema=None) as batch_op:
        batch_op.drop_constraint("uq_findings_fingerprint", type_="unique")
