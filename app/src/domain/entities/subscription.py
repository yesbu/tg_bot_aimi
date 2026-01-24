from dataclasses import dataclass
from datetime import datetime, timedelta

from src.domain.enums import SubscriptionStatus


@dataclass
class Subscription:
    user_id: int
    subscription_plan_id: int
    status: SubscriptionStatus
    starts_at: datetime
    expires_at: datetime
    payment_id: int | None = None
    id: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    
    @property
    def is_active(self) -> bool:
        if self.status != SubscriptionStatus.ACTIVE:
            return False
        return datetime.utcnow() < self.expires_at
    
    @property
    def is_expired(self) -> bool:
        return datetime.utcnow() >= self.expires_at
    
    @property
    def days_remaining(self) -> int:
        if self.is_expired:
            return 0
        delta = self.expires_at - datetime.utcnow()
        return max(0, delta.days)
    
    def cancel(self) -> None:
        if self.status == SubscriptionStatus.CANCELLED:
            return
        self.status = SubscriptionStatus.CANCELLED
    
    def activate(self) -> None:
        if self.status == SubscriptionStatus.ACTIVE:
            return
        if self.is_expired:
            raise ValueError("Cannot activate expired subscription")
        self.status = SubscriptionStatus.ACTIVE
    
    def extend(self, months: int) -> None:
        if not self.is_active:
            raise ValueError("Cannot extend inactive subscription")
        self.expires_at = self.expires_at + timedelta(days=months * 30)
    
    def check_and_update_status(self) -> None:
        if self.is_expired and self.status == SubscriptionStatus.ACTIVE:
            self.status = SubscriptionStatus.EXPIRED
