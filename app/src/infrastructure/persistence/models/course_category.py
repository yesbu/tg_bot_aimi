from sqlalchemy import Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

from src.infrastructure.persistence.models.base import Base

if TYPE_CHECKING:
    from src.infrastructure.persistence.models.language import Language


class CourseCategory(Base):
    __tablename__ = "course_categories"
    
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )
    
    code: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        unique=True,
        index=True
    )
    
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true"
    )
    
    translations: Mapped[list["CourseCategoryTranslation"]] = relationship(
        "CourseCategoryTranslation",
        back_populates="category",
        cascade="all, delete-orphan",
        lazy="selectin"
    )


class CourseCategoryTranslation(Base):
    __tablename__ = "course_category_translations"
    
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )
    
    category_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("course_categories.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    language_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("languages.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    name: Mapped[str] = mapped_column(
        String(128),
        nullable=False
    )
    
    category: Mapped["CourseCategory"] = relationship(
        "CourseCategory",
        back_populates="translations",
        lazy="selectin"
    )
    
    language: Mapped["Language"] = relationship(
        "Language",
        lazy="selectin"
    )
