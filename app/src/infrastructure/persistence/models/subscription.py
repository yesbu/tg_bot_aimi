from datetime import datetime
from sqlalchemy import Integer, String, ForeignKey, Boolean, DateTime, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

from src.infrastructure.persistence.models.base import Base, TimestampMixin
from src.domain.enums import SubscriptionStatus

if TYPE_CHECKING:
    from src.infrastructure.persistence.models.user import User
    from src.infrastructure.persistence.models.subscription_plan import SubscriptionPlan
    from src.infrastructure.persistence.models.payment import Payment


class Subscription(Base, TimestampMixin):
    __tablename__ = "subscriptions"
    
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )
    
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    subscription_plan_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("subscription_plans.id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )
    
    status: Mapped[SubscriptionStatus] = mapped_column(
        Enum(SubscriptionStatus, native_enum=False),
        nullable=False,
        default=SubscriptionStatus.ACTIVE,
        server_default=SubscriptionStatus.ACTIVE.value,
        index=True
    )
    
    starts_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        comment="Subscription start date"
    )
    
    expires_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        index=True,
        comment="Subscription expiration date"
    )
               
    payment_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("payments.id", ondelete="SET NULL"),
        nullable=True,
        comment="Associated payment"
    )
    
    user: Mapped["User"] = relationship(
        "User",
        back_populates="subscriptions"
    )
    
    subscription_plan: Mapped["SubscriptionPlan"] = relationship(
        "SubscriptionPlan",
        back_populates="subscriptions"
    )
    
    payment: Mapped["Payment"] = relationship(
        "Payment"
    )
    

    

