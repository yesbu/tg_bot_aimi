from abc import ABC, abstractmethod
from typing import Sequence

from src.domain.entities import SubscriptionPlan


class ISubscriptionPlanRepository(ABC):
    @abstractmethod
    async def get_by_id(self, id: int) -> SubscriptionPlan | None:
        pass
    
    @abstractmethod
    async def get_by_name(self, name: str) -> SubscriptionPlan | None:
        pass
    
    @abstractmethod
    async def get_all(self) -> Sequence[SubscriptionPlan]:
        pass
    
    @abstractmethod
    async def get_active(self) -> Sequence[SubscriptionPlan]:
        pass
    
    @abstractmethod
    async def create(
        self,
        name: str,
        duration_months: int,
        price: float,
        visits_limit: int,
        description: str | None = None,
        display_order: int = 0,
    ) -> SubscriptionPlan:
        pass
    
    @abstractmethod
    async def update(self, plan: SubscriptionPlan) -> SubscriptionPlan:
        pass
    
    @abstractmethod
    async def deactivate(self, id: int) -> bool:
        pass
    
    @abstractmethod
    async def activate(self, id: int) -> bool:
        pass
