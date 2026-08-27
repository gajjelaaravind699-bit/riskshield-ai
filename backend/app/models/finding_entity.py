"""
FindingEntity join model linking a Finding to an Entity.
"""

from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

if TYPE_CHECKING:
    from app.models.finding import Finding
    from app.models.entity import Entity


class FindingEntity(Base):
    """
    Relational link between a Finding and an associated Entity.
    """
    __tablename__ = "finding_entities"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    finding_id: Mapped[int] = mapped_column(
        ForeignKey("findings.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    entity_id: Mapped[int] = mapped_column(
        ForeignKey("entities.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    role: Mapped[str] = mapped_column(
        String(50),
        default="ASSOCIATED_ENTITY",
        nullable=False,
    )

    # Relationships
    finding: Mapped["Finding"] = relationship("Finding", back_populates="related_entities")
    entity: Mapped["Entity"] = relationship("Entity", lazy="selectin")

    __table_args__ = (
        UniqueConstraint("finding_id", "entity_id", "role", name="uq_finding_entity_role"),
    )

    def __repr__(self) -> str:
        return f"<FindingEntity(finding_id={self.finding_id}, entity_id={self.entity_id}, role='{self.role}')>"
