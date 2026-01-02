from abc import ABC, abstractmethod
from typing import Sequence

from src.domain.entities import Center
from src.domain.enums import CenterStatus


class ICenterService(ABC):
    @abstractmethod
    async def get_center_by_id(self, id: int) -> Center | None:
        pass
    
    @abstractmethod
    async def get_partner_center(self, partner_id: int) -> Center | None:
        pass
    
    @abstractmethod
    async def search_centers(
        self,
        city: str | None = None,
        category: str | None = None,
        limit: int | None = None,
        offset: int | None = None
    ) -> Sequence[Center]:
        pass
    
    @abstractmethod
    async def create_center(
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
    async def update_center(self, center: Center) -> Center:
        pass
    
    @abstractmethod
    async def approve_center(self, center_id: int) -> Center:
        pass
    
    @abstractmethod
    async def reject_center(self, center_id: int) -> Center:
        pass
    
    @abstractmethod
    async def get_pending_centers(self) -> Sequence[Center]:
        pass
