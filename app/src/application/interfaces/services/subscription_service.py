from abc import ABC, abstractmethod
from typing import Sequence

from src.domain.entities import SubscriptionTemplate, Subscription


class ISubscriptionService(ABC):
    @abstractmethod
    async def get_active_templates(self) -> Sequence[SubscriptionTemplate]:
        pass
    
    @abstractmethod
    async def create_template(
        self,
        name: str,
        tariff: str,
        price: float,
        description: str | None = None,
        lessons_total: int | None = None,
        created_by: int | None = None,
    ) -> SubscriptionTemplate:
        pass
    
    @abstractmethod
    async def get_subscription_by_qr(self, qr_code: str) -> Subscription | None:
        pass
    
    @abstractmethod
    async def get_user_subscriptions(
        self,
        user_id: int,
        child_id: int | None = None
    ) -> Sequence[Subscription]:
        pass
    
    @abstractmethod
    async def create_subscription(
        self,
        user_id: int,
        template_id: int,
        child_id: int | None = None,
    ) -> Subscription:
        pass
    
    @abstractmethod
    async def use_subscription_lesson(self, subscription_id: int) -> Subscription:
        pass
