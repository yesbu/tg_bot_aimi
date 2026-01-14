from abc import ABC, abstractmethod
from typing import Sequence

from src.domain.entities import SubscriptionTemplate, Subscription


class ISubscriptionRepository(ABC):
    @abstractmethod
    async def get_template_by_id(self, id: int) -> SubscriptionTemplate | None:
        pass
    
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
    async def update_template(self, template: SubscriptionTemplate) -> SubscriptionTemplate:
        pass
    
    @abstractmethod
    async def deactivate_template(self, id: int) -> bool:
        pass
    
    @abstractmethod
    async def get_subscription_by_id(self, id: int) -> Subscription | None:
        pass
    
    @abstractmethod
    async def get_subscription_by_qr_code(self, qr_code: str) -> Subscription | None:
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
        qr_code: str,
        child_id: int | None = None,
    ) -> Subscription:
        pass
    
    @abstractmethod
    async def update_subscription(self, subscription: Subscription) -> Subscription:
        pass
    
    @abstractmethod
    async def deactivate_subscription(self, id: int) -> bool:
        pass
