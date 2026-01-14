from abc import ABC, abstractmethod
from typing import Sequence

from src.domain.entities import Visit


class IVisitRepository(ABC):
    @abstractmethod
    async def get_by_id(self, id: int) -> Visit | None:
        pass
    
    @abstractmethod
    async def get_by_subscription_id(self, subscription_id: int) -> Sequence[Visit]:
        pass
    
    @abstractmethod
    async def check_recent_visit(
        self,
        subscription_id: int,
        center_id: int,
        minutes: int = 5
    ) -> bool:
        pass
    
    @abstractmethod
    async def create(
        self,
        subscription_id: int,
        user_id: int,
        center_id: int,
        child_id: int | None = None,
        lesson_id: int | None = None,
    ) -> Visit:
        pass
    
    @abstractmethod
    async def get_visit_count(
        self,
        user_id: int | None = None,
        child_id: int | None = None,
        center_id: int | None = None
    ) -> int:
        pass
