"""
Entity model representing graph nodes (USER, DEVICE, IP, PAYMENT_INSTRUMENT).
"""

from typing import List, TYPE_CHECKING
from sqlalchemy import String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.models.base import TimestampMixin

if TYPE_CHECKING:
    from app.models.transaction_entity import TransactionEntity


class EntityType:
    USER = "USER"
    DEVICE = "DEVICE"
    IP = "IP"
    PAYMENT_INSTRUMENT = "PAYMENT_INSTRUMENT"

    ALL = [USER, DEVICE, IP, PAYMENT_INSTRUMENT]


class Entity(Base, TimestampMixin):
    """
    Normalized entity representing a distinct participant or instrument in the payment network.
    """
    __tablename__ = "entities"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    entity_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )
    entity_value: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )

    # Relationships
    transaction_links: Mapped[List["TransactionEntity"]] = relationship(
        "TransactionEntity",
        back_populates="entity",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        UniqueConstraint("entity_type", "entity_value", name="uq_entity_type_value"),
    )

    def __repr__(self) -> str:
        return f"<Entity(id={self.id}, type='{self.entity_type}', value='{self.entity_value}')>"
