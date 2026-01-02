from abc import ABC, abstractmethod
from typing import Sequence

from src.domain.entities import Child


class IChildRepository(ABC):
    @abstractmethod
    async def get_by_id(self, id: int) -> Child | None:
        pass
    
    @abstractmethod
    async def get_by_parent_id(self, parent_id: int) -> Sequence[Child]:
        pass
    
    @abstractmethod
    async def create(
        self,
        parent_id: int,
        name: str,
        age: int,
    ) -> Child:
        pass
    
    @abstractmethod
    async def update(self, child: Child) -> Child:
        pass
    
    @abstractmethod
    async def delete(self, id: int) -> bool:
        pass
