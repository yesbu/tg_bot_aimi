from sqlalchemy import Integer, String, BigInteger, ForeignKey, Enum, Text, Float, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

from src.infrastructure.persistence.models.base import Base, TimestampMixin
from src.domain.enums import SubscriptionStatus

if TYPE_CHECKING:
    from src.infrastructure.persistence.models.user import User
    from src.infrastructure.persistence.models.child import Child
    from src.infrastructure.persistence.models.visit import Visit
    from src.infrastructure.persistence.models.payment import Payment


class SubscriptionTemplate(TimestampMixin, Base):
    __tablename__ = "subscription_templates"
    
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )
    
    name: Mapped[str] = mapped_column(
        String(256),
        nullable=False
    )
    
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )
    
    tariff: Mapped[str] = mapped_column(
        String(64),
        nullable=False
    )
    
    lessons_total: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )
    
    price: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )
    
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true"
    )
    
    created_by: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("users.telegram_id", ondelete="SET NULL"),
        nullable=True
    )
    
    subscriptions: Mapped[list["Subscription"]] = relationship(
        "Subscription",
        back_populates="template",
        lazy="selectin"
    )


class Subscription(TimestampMixin, Base):
    __tablename__ = "subscriptions"
    
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
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
    
    template_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("subscription_templates.id", ondelete="SET NULL"),
        nullable=True
    )
    
    tariff: Mapped[str] = mapped_column(
        String(64),
        nullable=False
    )
    
    lessons_total: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )
    
    lessons_remaining: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )
    
    qr_code: Mapped[str] = mapped_column(
        String(256),
        nullable=False,
        unique=True,
        index=True
    )
    
    status: Mapped[SubscriptionStatus] = mapped_column(
        Enum(SubscriptionStatus, native_enum=False),
        nullable=False,
        default=SubscriptionStatus.ACTIVE,
        server_default=SubscriptionStatus.ACTIVE.value,
        index=True
    )
    
    user: Mapped["User"] = relationship(
        "User",
        back_populates="subscriptions",
        lazy="selectin"
    )
    
    child: Mapped["Child | None"] = relationship(
        "Child",
        lazy="selectin"
    )
    
    template: Mapped["SubscriptionTemplate | None"] = relationship(
        "SubscriptionTemplate",
        back_populates="subscriptions",
        lazy="selectin"
    )
    
    visits: Mapped[list["Visit"]] = relationship(
        "Visit",
        back_populates="subscription",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    
    payments: Mapped[list["Payment"]] = relationship(
        "Payment",
        back_populates="subscription",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
