from sqlalchemy import Integer, String, BigInteger, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

from src.infrastructure.persistence.models.base import Base, TimestampMixin, SoftDeleteMixin
from src.domain.enums import Role

if TYPE_CHECKING:
    from src.infrastructure.persistence.models.child import Child
    from src.infrastructure.persistence.models.center import Center
    from src.infrastructure.persistence.models.subscription import Subscription
    from src.infrastructure.persistence.models.visit import Visit
    from src.infrastructure.persistence.models.payment import Payment
    from src.infrastructure.persistence.models.review import Review


class User(TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(
        Integer, 
        primary_key=True, 
        autoincrement=True
    )

    telegram_id: Mapped[int] = mapped_column(
        BigInteger, 
        nullable=False, 
        unique=True,
        index=True  
    )

    username: Mapped[str | None] = mapped_column(
        String(32), 
        nullable=True,
    )
    
    first_name: Mapped[str | None] = mapped_column(
        String(64), 
        nullable=True,
    )
    
    last_name: Mapped[str | None] = mapped_column(
        String(64), 
        nullable=True,
    )
    
    phone: Mapped[str | None] = mapped_column(
        String(32),
        nullable=True
    )
    
    city: Mapped[str | None] = mapped_column(
        String(128),
        nullable=True
    )
    
    role: Mapped[Role] = mapped_column(
        Enum(Role, native_enum=False),  
        nullable=False, 
        default=Role.USER,
        server_default=Role.USER.value,
        index=True
    )
    
    children: Mapped[list["Child"]] = relationship(
        "Child",
        back_populates="parent",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    
    centers: Mapped[list["Center"]] = relationship(
        "Center",
        back_populates="partner",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    
    subscriptions: Mapped[list["Subscription"]] = relationship(
        "Subscription",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    
    visits: Mapped[list["Visit"]] = relationship(
        "Visit",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    
    payments: Mapped[list["Payment"]] = relationship(
        "Payment",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    
    reviews: Mapped[list["Review"]] = relationship(
        "Review",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin"
    )




    