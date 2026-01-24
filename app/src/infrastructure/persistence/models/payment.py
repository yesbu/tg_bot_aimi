from sqlalchemy import Integer, String, Float, ForeignKey, Text, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

from src.infrastructure.persistence.models.base import Base, TimestampMixin
from src.domain.enums import PaymentStatus

if TYPE_CHECKING:
    from src.infrastructure.persistence.models.user import User


class Payment(Base, TimestampMixin):
    __tablename__ = "payments"
    
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
    
    amount: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        comment="Payment amount in cents"
    )
    
    currency: Mapped[str] = mapped_column(
        String(8),
        nullable=False,
        default="KZT",
        server_default="KZT"
    )
    
    status: Mapped[PaymentStatus] = mapped_column(
        Enum(PaymentStatus, native_enum=False),
        nullable=False,
        default=PaymentStatus.NEW,
        server_default=PaymentStatus.NEW.value,
        index=True
    )

    payment_id: Mapped[str | None] = mapped_column(
        String(128),
        nullable=True,
        unique=True,
        index=True,
        comment="External payment gateway payment ID"
    )
    
    invoice_id: Mapped[str | None] = mapped_column(
        String(128),
        nullable=True,
        index=True,
        comment="Invoice ID from payment gateway"
    )
    
    user: Mapped["User"] = relationship(
        "User",
        back_populates="payments"
    )
    
