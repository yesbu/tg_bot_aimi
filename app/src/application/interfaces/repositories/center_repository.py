from abc import ABC, abstractmethod
from typing import Sequence

from src.domain.entities import Center
from src.domain.enums import CenterStatus


class ICenterRepository(ABC):
    @abstractmethod
    async def get_by_id(self, id: int) -> Center | None:
        pass
    
    @abstractmethod
    async def get_by_partner_id(self, partner_id: int) -> Center | None:
        pass
    
    @abstractmethod
    async def get_by_filters(
        self,
        city: str | None = None,
        category: str | None = None,
        status: CenterStatus | None = None,
        limit: int | None = None,
        offset: int | None = None
    ) -> Sequence[Center]:
        pass
    
    @abstractmethod
    async def get_pending_centers(self) -> Sequence[Center]:
        pass
    
    @abstractmethod
    async def create(
        self,
        partner_id: int,
        name: str,
        city: str,
        address: str | None = None,
        phone: str | None = None,
        category: str | None = None,
        description: str | None = None,
        logo: str | None = None,
    ) -> Center:
        pass
    
    @abstractmethod
    async def update(self, center: Center) -> Center:
        pass
    
    @abstractmethod
    async def delete(self, id: int) -> bool:
        pass
