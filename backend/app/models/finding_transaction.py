"""
FindingTransaction join model linking a Finding to a Transaction.
"""

from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

if TYPE_CHECKING:
    from app.models.finding import Finding
    from app.models.transaction import Transaction


class FindingTransaction(Base):
    """
    Relational link between a Finding and an involved Transaction.
    """
    __tablename__ = "finding_transactions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    finding_id: Mapped[int] = mapped_column(
        ForeignKey("findings.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    transaction_id: Mapped[int] = mapped_column(
        ForeignKey("transactions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Relationships
    finding: Mapped["Finding"] = relationship("Finding", back_populates="related_transactions")
    transaction: Mapped["Transaction"] = relationship("Transaction", lazy="selectin")

    __table_args__ = (
        UniqueConstraint("finding_id", "transaction_id", name="uq_finding_transaction"),
    )

    def __repr__(self) -> str:
        return f"<FindingTransaction(finding_id={self.finding_id}, transaction_id={self.transaction_id})>"
