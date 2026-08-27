"""Initial Phase 2 schema: transactions, entities, and transaction_entities

Revision ID: 001_phase2_schema
Revises: 
Create Date: 2026-08-28 00:00:00.000000 UTC

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "001_phase2_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create transactions table
    op.create_table(
        "transactions",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("transaction_id", sa.String(length=100), nullable=False),
        sa.Column("customer_id", sa.String(length=100), nullable=False),
        sa.Column("amount", sa.Numeric(precision=18, scale=2), nullable=False),
        sa.Column("currency", sa.String(length=3), server_default="USD", nullable=False),
        sa.Column("status", sa.String(length=30), server_default="SUCCESS", nullable=False),
        sa.Column("payment_method", sa.String(length=50), nullable=False),
        sa.Column("card_bin", sa.String(length=8), nullable=True),
        sa.Column("card_last4", sa.String(length=4), nullable=True),
        sa.Column("instrument_token", sa.String(length=128), nullable=True),
        sa.Column("upi_vpa", sa.String(length=128), nullable=True),
        sa.Column("device_id", sa.String(length=128), nullable=True),
        sa.Column("ip_address", sa.String(length=45), nullable=True),
        sa.Column("user_agent", sa.String(length=512), nullable=True),
        sa.Column("location_city", sa.String(length=100), nullable=True),
        sa.Column("location_country", sa.String(length=100), nullable=True),
        sa.Column("transacted_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("transaction_id", name="uq_transactions_transaction_id"),
    )
    op.create_index("ix_transactions_transaction_id", "transactions", ["transaction_id"])
    op.create_index("ix_transactions_customer_id", "transactions", ["customer_id"])
    op.create_index("ix_transactions_instrument_token", "transactions", ["instrument_token"])
    op.create_index("ix_transactions_device_id", "transactions", ["device_id"])
    op.create_index("ix_transactions_ip_address", "transactions", ["ip_address"])

    # 2. Create entities table
    op.create_table(
        "entities",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("entity_type", sa.String(length=50), nullable=False),
        sa.Column("entity_value", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("entity_type", "entity_value", name="uq_entity_type_value"),
    )
    op.create_index("ix_entities_entity_type", "entities", ["entity_type"])
    op.create_index("ix_entities_entity_value", "entities", ["entity_value"])

    # 3. Create transaction_entities table
    op.create_table(
        "transaction_entities",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("transaction_id", sa.Integer(), nullable=False),
        sa.Column("entity_id", sa.Integer(), nullable=False),
        sa.Column("relationship_type", sa.String(length=50), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["entity_id"], ["entities.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["transaction_id"], ["transactions.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("transaction_id", "entity_id", "relationship_type", name="uq_transaction_entity_rel"),
    )
    op.create_index("ix_transaction_entities_transaction_id", "transaction_entities", ["transaction_id"])
    op.create_index("ix_transaction_entities_entity_id", "transaction_entities", ["entity_id"])
    op.create_index("ix_transaction_entities_relationship_type", "transaction_entities", ["relationship_type"])


def downgrade() -> None:
    op.drop_table("transaction_entities")
    op.drop_table("entities")
    op.drop_table("transactions")
