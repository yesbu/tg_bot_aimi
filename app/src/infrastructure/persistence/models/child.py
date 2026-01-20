from sqlalchemy import Integer, String, BigInteger, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

from src.infrastructure.persistence.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from src.infrastructure.persistence.models.user import User


class Child(TimestampMixin, Base):
    __tablename__ = "children"
    
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )
    
    parent_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.telegram_id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    name: Mapped[str] = mapped_column(
        String(128),
        nullable=False
    )
    
    age: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )
    
    parent: Mapped["User"] = relationship(
        "User",
        back_populates="children",
        lazy="selectin"
    )

