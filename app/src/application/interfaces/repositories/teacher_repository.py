from abc import ABC, abstractmethod
from typing import Sequence

from src.domain.entities import Teacher


class ITeacherRepository(ABC):
    @abstractmethod
    async def get_by_id(self, id: int) -> Teacher | None:
        pass
    
    @abstractmethod
    async def get_by_center_id(self, center_id: int) -> Sequence[Teacher]:
        pass
    
    @abstractmethod
    async def create(
        self,
        center_id: int,
        name: str,
        description: str | None = None,
    ) -> Teacher:
        pass
    
    @abstractmethod
    async def update(self, teacher: Teacher) -> Teacher:
        pass
    
    @abstractmethod
    async def delete(self, id: int) -> bool:
        pass
