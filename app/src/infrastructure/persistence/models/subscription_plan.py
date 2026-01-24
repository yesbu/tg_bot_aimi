from sqlalchemy import Integer, String, Text, Float, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

from src.infrastructure.persistence.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from src.infrastructure.persistence.models.subscription import Subscription


class SubscriptionPlan(TimestampMixin, Base):
    __tablename__ = "subscription_plans"
    
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )
    
    name: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        unique=True,
        comment="BASIC, SMART, PRO"
    )
    
    duration_months: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="3, 6, 12"
    )
    
    price: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        comment="195000, 300000, 516000"
    )
    
    visits_limit: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="20, 30, 40"
    )
    
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Для знакомства с форматом"
    )
    
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true"
    )
    
    display_order: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="Порядок отображения"
    )
    
    subscriptions: Mapped[list["Subscription"]] = relationship(
        "Subscription",
        back_populates="subscription_plan"
    )

