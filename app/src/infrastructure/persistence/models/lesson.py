from sqlalchemy import Integer, String, ForeignKey, Text, Date, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING
from datetime import date, time

from src.infrastructure.persistence.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from src.infrastructure.persistence.models.center import Center
    from src.infrastructure.persistence.models.course import Course
    from src.infrastructure.persistence.models.teacher import Teacher
    from src.infrastructure.persistence.models.visit import Visit


class Lesson(TimestampMixin, Base):
    __tablename__ = "lessons"
    
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
    
    course_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("courses.id", ondelete="CASCADE"),
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
    
    date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        index=True
    )
    
    time: Mapped[time] = mapped_column(
        Time,
        nullable=False
    )
    
    duration: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )
    
    teacher_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("teachers.id", ondelete="SET NULL"),
        nullable=True
    )
    
    max_students: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )
    
    current_students: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0"
    )
    
    center: Mapped["Center"] = relationship(
        "Center",
        back_populates="lessons",
        lazy="selectin"
    )
    
    course: Mapped["Course"] = relationship(
        "Course",
        back_populates="lessons",
        lazy="selectin"
    )
    
    teacher: Mapped["Teacher | None"] = relationship(
        "Teacher",
        back_populates="lessons",
        lazy="selectin"
    )
    
    visits: Mapped[list["Visit"]] = relationship(
        "Visit",
        back_populates="lesson",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
