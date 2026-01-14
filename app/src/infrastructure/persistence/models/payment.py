from sqlalchemy import Integer, String, BigInteger, ForeignKey, Enum, Text, Float, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING
from datetime import datetime

from src.infrastructure.persistence.models.base import Base, TimestampMixin
from src.domain.enums import PaymentStatus

if TYPE_CHECKING:
    from src.infrastructure.persistence.models.subscription import Subscription
    from src.infrastructure.persistence.models.user import User


class Payment(TimestampMixin, Base):
    __tablename__ = "payments"
    
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )
    
    subscription_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("subscriptions.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.telegram_id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    amount: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )
    
    currency: Mapped[str] = mapped_column(
        String(8),
        nullable=False,
        default="KZT",
        server_default="KZT"
    )
    
    method: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True
    )
    
    status: Mapped[PaymentStatus] = mapped_column(
        Enum(PaymentStatus, native_enum=False),
        nullable=False,
        default=PaymentStatus.PENDING,
        server_default=PaymentStatus.PENDING.value,
        index=True
    )
    
    transaction_id: Mapped[str | None] = mapped_column(
        String(256),
        nullable=True,
        unique=True,
        index=True
    )
    
    invoice_id: Mapped[str | None] = mapped_column(
        String(256),
        nullable=True,
        index=True
    )
    
    airba_payment_id: Mapped[str | None] = mapped_column(
        String(256),
        nullable=True,
        index=True
    )
    
    redirect_url: Mapped[str | None] = mapped_column(
        String(512),
        nullable=True
    )
    
    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )
    
    processed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    
    subscription: Mapped["Subscription | None"] = relationship(
        "Subscription",
        back_populates="payments",
        lazy="selectin"
    )
    
    user: Mapped["User"] = relationship(
        "User",
        back_populates="payments",
        lazy="selectin"
    )
    
    refunds: Mapped[list["PaymentRefund"]] = relationship(
        "PaymentRefund",
        back_populates="payment",
        cascade="all, delete-orphan",
        lazy="selectin"
    )


class PaymentRefund(Base):
    __tablename__ = "payment_refunds"
    
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )
    
    payment_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("payments.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    airba_refund_id: Mapped[str | None] = mapped_column(
        String(256),
        nullable=True,
        index=True
    )
    
    ext_id: Mapped[str | None] = mapped_column(
        String(256),
        nullable=True
    )
    
    amount: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )
    
    reason: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )
    
    status: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True
    )
    
    processed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow
    )
    
    payment: Mapped["Payment"] = relationship(
        "Payment",
        back_populates="refunds",
        lazy="selectin"
    )
