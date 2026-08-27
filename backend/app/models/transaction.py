"""
Transaction model representing financial transactions for abuse ring analysis.
"""

from decimal import Decimal
from datetime import datetime, timezone
from typing import List, TYPE_CHECKING
from sqlalchemy import DateTime, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.models.base import TimestampMixin

if TYPE_CHECKING:
    from app.models.transaction_entity import TransactionEntity


class Transaction(Base, TimestampMixin):
    """
    Transaction record storing normalized payment event attributes and entity relationships.
    """
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    transaction_id: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        index=True,
        nullable=False,
    )
    customer_id: Mapped[str] = mapped_column(
        String(100),
        index=True,
        nullable=False,
    )
    amount: Mapped[Decimal] = mapped_column(
        Numeric(precision=18, scale=2),
        nullable=False,
    )
    currency: Mapped[str] = mapped_column(
        String(3),
        default="USD",
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(30),
        default="SUCCESS",
        nullable=False,
    )
    payment_method: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    # Safe payment instrument references (NO PAN, NO CVV)
    card_bin: Mapped[str | None] = mapped_column(
        String(8),
        nullable=True,
    )
    card_last4: Mapped[str | None] = mapped_column(
        String(4),
        nullable=True,
    )
    instrument_token: Mapped[str | None] = mapped_column(
        String(128),
        nullable=True,
        index=True,
    )
    upi_vpa: Mapped[str | None] = mapped_column(
        String(128),
        nullable=True,
    )

    # Device & Network signals
    device_id: Mapped[str | None] = mapped_column(
        String(128),
        nullable=True,
        index=True,
    )
    ip_address: Mapped[str | None] = mapped_column(
        String(45),
        nullable=True,
        index=True,
    )
    user_agent: Mapped[str | None] = mapped_column(
        String(512),
        nullable=True,
    )
    location_city: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )
    location_country: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    # Timestamp
    transacted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relational entity associations
    entities: Mapped[List["TransactionEntity"]] = relationship(
        "TransactionEntity",
        back_populates="transaction",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return (
            f"<Transaction(id={self.id}, txn_id='{self.transaction_id}', "
            f"cust='{self.customer_id}', amount={self.amount} {self.currency})>"
        )
