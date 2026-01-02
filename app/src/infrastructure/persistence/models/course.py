from sqlalchemy import Integer, String, ForeignKey, Text, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

from src.infrastructure.persistence.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from src.infrastructure.persistence.models.center import Center
    from src.infrastructure.persistence.models.lesson import Lesson
    from src.infrastructure.persistence.models.review import Review


class Course(TimestampMixin, Base):
    __tablename__ = "courses"
    
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )
    
    center_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("centers.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    name: Mapped[str] = mapped_column(
        String(256),
        nullable=False
    )
    
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )
    
    category: Mapped[str | None] = mapped_column(
        String(128),
        nullable=True,
        index=True
    )
    
    age_min: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )
    
    age_max: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )
    
    requirements: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )
    
    schedule: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )
    
    rating: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
        server_default="0.0"
    )
    
    price_4: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )
    
    price_8: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )
    
    price_unlimited: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )
    
    photo: Mapped[str | None] = mapped_column(
        String(512),
        nullable=True
    )
    
    center: Mapped["Center"] = relationship(
        "Center",
        back_populates="courses",
        lazy="selectin"
    )
    
    lessons: Mapped[list["Lesson"]] = relationship(
        "Lesson",
        back_populates="course",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    
    reviews: Mapped[list["Review"]] = relationship(
        "Review",
        back_populates="course",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
