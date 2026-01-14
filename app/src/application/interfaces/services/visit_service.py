from abc import ABC, abstractmethod
from typing import Sequence

from src.domain.entities import Visit


class IVisitService(ABC):
    @abstractmethod
    async def get_subscription_visits(self, subscription_id: int) -> Sequence[Visit]:
        pass
    
    @abstractmethod
    async def register_visit(
        self,
        qr_code: str,
        center_id: int,
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
