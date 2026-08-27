"""
TransactionEntity model representing relationship links between Transactions and Entities.
"""

from datetime import datetime, timezone
from typing import TYPE_CHECKING
from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

if TYPE_CHECKING:
    from app.models.transaction import Transaction
    from app.models.entity import Entity


class RelationshipType:
    ACCOUNT_HOLDER = "ACCOUNT_HOLDER"
    DEVICE_ORIGIN = "DEVICE_ORIGIN"
    IP_ORIGIN = "IP_ORIGIN"
    PAYMENT_SOURCE = "PAYMENT_SOURCE"

    ALL = [ACCOUNT_HOLDER, DEVICE_ORIGIN, IP_ORIGIN, PAYMENT_SOURCE]


class TransactionEntity(Base):
    """
    Relational link connecting a Transaction to an Entity with a specified relationship role.
    """
    __tablename__ = "transaction_entities"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    transaction_id: Mapped[int] = mapped_column(
        ForeignKey("transactions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    entity_id: Mapped[int] = mapped_column(
        ForeignKey("entities.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    relationship_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    transaction: Mapped["Transaction"] = relationship("Transaction", back_populates="entities")
    entity: Mapped["Entity"] = relationship("Entity", back_populates="transaction_links")

    __table_args__ = (
        UniqueConstraint(
            "transaction_id",
            "entity_id",
            "relationship_type",
            name="uq_transaction_entity_rel",
        ),
    )

    def __repr__(self) -> str:
        return (
            f"<TransactionEntity(transaction_id={self.transaction_id}, "
            f"entity_id={self.entity_id}, rel='{self.relationship_type}')>"
        )
