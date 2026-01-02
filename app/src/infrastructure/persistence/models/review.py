from sqlalchemy import Integer, BigInteger, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

from src.infrastructure.persistence.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from src.infrastructure.persistence.models.course import Course
    from src.infrastructure.persistence.models.user import User


class Review(TimestampMixin, Base):
    __tablename__ = "reviews"
    
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )
    
    course_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("courses.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.telegram_id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    rating: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )
    
    comment: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )
    
    course: Mapped["Course"] = relationship(
        "Course",
        back_populates="reviews",
        lazy="selectin"
    )
    
    user: Mapped["User"] = relationship(
        "User",
        back_populates="reviews",
        lazy="selectin"
    )
