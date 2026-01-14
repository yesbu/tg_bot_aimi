from sqlalchemy import Integer, String, BigInteger, ForeignKey, Enum, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

from src.infrastructure.persistence.models.base import Base, TimestampMixin
from src.domain.enums import CenterStatus

if TYPE_CHECKING:
    from src.infrastructure.persistence.models.user import User
    from src.infrastructure.persistence.models.course import Course
    from src.infrastructure.persistence.models.teacher import Teacher
    from src.infrastructure.persistence.models.lesson import Lesson


class Center(TimestampMixin, Base):
    __tablename__ = "centers"
    
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )
    
    partner_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.telegram_id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    name: Mapped[str] = mapped_column(
        String(256),
        nullable=False
    )
    
    city: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
        index=True
    )
    
    address: Mapped[str | None] = mapped_column(
        String(512),
        nullable=True
    )
    
    phone: Mapped[str | None] = mapped_column(
        String(32),
        nullable=True
    )
    
    category: Mapped[str | None] = mapped_column(
        String(128),
        nullable=True,
        index=True
    )
    
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )
    
    logo: Mapped[str | None] = mapped_column(
        String(512),
        nullable=True
    )
    
    status: Mapped[CenterStatus] = mapped_column(
        Enum(CenterStatus, native_enum=False),
        nullable=False,
        default=CenterStatus.PENDING,
        server_default=CenterStatus.PENDING.value,
        index=True
    )
    
    partner: Mapped["User"] = relationship(
        "User",
        back_populates="centers",
        lazy="selectin"
    )
    
    courses: Mapped[list["Course"]] = relationship(
        "Course",
        back_populates="center",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    
    teachers: Mapped[list["Teacher"]] = relationship(
        "Teacher",
        back_populates="center",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    
    lessons: Mapped[list["Lesson"]] = relationship(
        "Lesson",
        back_populates="center",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
