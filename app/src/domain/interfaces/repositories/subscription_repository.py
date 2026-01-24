from abc import ABC, abstractmethod
from datetime import datetime
from typing import Sequence

from src.domain.entities import Subscription
from src.domain.enums import SubscriptionStatus


class ISubscriptionRepository(ABC):
    @abstractmethod
    async def get_by_id(self, id: int) -> Subscription | None:
        pass
    
    @abstractmethod
    async def get_active_by_user_id(self, user_id: int) -> Subscription | None:
        pass
    
    @abstractmethod
    async def get_all_by_user_id(
        self,
        user_id: int,
        limit: int | None = None,
        offset: int | None = None,
    ) -> Sequence[Subscription]:
        pass
    
    @abstractmethod
    async def get_expiring_soon(
        self,
        days: int = 7,
        limit: int | None = None,
    ) -> Sequence[Subscription]:
        pass
    
    @abstractmethod
    async def get_by_status(
        self,
        status: SubscriptionStatus,
        limit: int | None = None,
        offset: int | None = None,
    ) -> Sequence[Subscription]:
        pass
    
    @abstractmethod
    async def create(
        self,
        user_id: int,
        subscription_plan_id: int,
        starts_at: datetime,
        expires_at: datetime,
        payment_id: int | None = None,
    ) -> Subscription:
        pass
    
    @abstractmethod
    async def update(self, subscription: Subscription) -> Subscription:
        pass
    
    @abstractmethod
    async def has_active_subscription(self, user_id: int) -> bool:
        pass
