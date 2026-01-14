from sqlalchemy import Integer, BigInteger, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING
from datetime import datetime

from src.infrastructure.persistence.models.base import Base

if TYPE_CHECKING:
    from src.infrastructure.persistence.models.subscription import Subscription
    from src.infrastructure.persistence.models.user import User
    from src.infrastructure.persistence.models.child import Child
    from src.infrastructure.persistence.models.center import Center
    from src.infrastructure.persistence.models.lesson import Lesson


class Visit(Base):
    __tablename__ = "visits"
    
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )
    
    subscription_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("subscriptions.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.telegram_id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    child_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("children.id", ondelete="CASCADE"),
        nullable=True,
        index=True
    )
    
    center_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("centers.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    lesson_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("lessons.id", ondelete="SET NULL"),
        nullable=True
    )
    
    visited_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        index=True
    )
    
    subscription: Mapped["Subscription"] = relationship(
        "Subscription",
        back_populates="visits",
        lazy="selectin"
    )
    
    user: Mapped["User"] = relationship(
        "User",
        back_populates="visits",
        lazy="selectin"
    )
    
    child: Mapped["Child | None"] = relationship(
        "Child",
        lazy="selectin"
    )
    
    center: Mapped["Center"] = relationship(
        "Center",
        lazy="selectin"
    )
    
    lesson: Mapped["Lesson | None"] = relationship(
        "Lesson",
        back_populates="visits",
        lazy="selectin"
    )
