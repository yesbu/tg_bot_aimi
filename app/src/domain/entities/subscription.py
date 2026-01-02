from dataclasses import dataclass
from datetime import datetime

from src.domain.enums import SubscriptionStatus


@dataclass
class SubscriptionTemplate:
    name: str
    tariff: str
    price: float
    description: str | None = None
    lessons_total: int | None = None
    is_active: bool = True
    created_by: int | None = None
    id: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    
    def __post_init__(self):
        self.validate()
    
    def validate(self) -> None:
        if not self.name or len(self.name.strip()) == 0:
            raise ValueError("Template name cannot be empty")
        
        if not self.tariff or len(self.tariff.strip()) == 0:
            raise ValueError("Tariff cannot be empty")
        
        if self.price < 0:
            raise ValueError("Price cannot be negative")
        
        if self.lessons_total is not None and self.lessons_total <= 0:
            raise ValueError("Lessons total must be positive")
    
    def deactivate(self) -> None:
        self.is_active = False
    
    def activate(self) -> None:
        self.is_active = True


@dataclass
class Subscription:
    user_id: int
    tariff: str
    qr_code: str
    template_id: int | None = None
    child_id: int | None = None
    lessons_total: int | None = None
    lessons_remaining: int | None = None
    status: SubscriptionStatus = SubscriptionStatus.ACTIVE
    id: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    
    def __post_init__(self):
        self.validate()
    
    def validate(self) -> None:
        if not self.qr_code or len(self.qr_code.strip()) == 0:
            raise ValueError("QR code cannot be empty")
        
        if self.lessons_total is not None and self.lessons_total <= 0:
            raise ValueError("Lessons total must be positive")
        
        if self.lessons_remaining is not None and self.lessons_remaining < 0:
            raise ValueError("Lessons remaining cannot be negative")
    
    @property
    def is_active(self) -> bool:
        return self.status == SubscriptionStatus.ACTIVE
    
    @property
    def is_expired(self) -> bool:
        return self.status == SubscriptionStatus.EXPIRED
    
    @property
    def has_lessons_remaining(self) -> bool:
        if self.lessons_remaining is None:
            return True
        return self.lessons_remaining > 0
    
    def use_lesson(self) -> None:
        if not self.is_active:
            raise ValueError("Cannot use lesson from inactive subscription")
        
        if self.lessons_remaining is None:
            return
        
        if self.lessons_remaining <= 0:
            raise ValueError("No lessons remaining")
        
        self.lessons_remaining -= 1
        
        if self.lessons_remaining == 0:
            self.expire()
    
    def expire(self) -> None:
        self.status = SubscriptionStatus.EXPIRED
    
    def cancel(self) -> None:
        self.status = SubscriptionStatus.CANCELLED
