from sqlalchemy import Integer, String, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

from src.infrastructure.persistence.models.base import Base

if TYPE_CHECKING:
    from src.infrastructure.persistence.models.center import Center
    from src.infrastructure.persistence.models.lesson import Lesson


class Teacher(Base):
    __tablename__ = "teachers"
    
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
    
    center: Mapped["Center"] = relationship(
        "Center",
        back_populates="teachers",
        lazy="selectin"
    )
    
    lessons: Mapped[list["Lesson"]] = relationship(
        "Lesson",
        back_populates="teacher",
        lazy="selectin"
    )
