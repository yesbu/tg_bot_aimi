from abc import ABC, abstractmethod
from typing import Sequence

from src.domain.entities import Course


class ICourseRepository(ABC):
    @abstractmethod
    async def get_by_id(self, id: int) -> Course | None:
        pass
    
    @abstractmethod
    async def get_by_center_id(self, center_id: int) -> Sequence[Course]:
        pass
    
    @abstractmethod
    async def get_by_filters(
        self,
        city: str | None = None,
        category: str | None = None,
        age: int | None = None,
        limit: int | None = None,
        offset: int | None = None
    ) -> Sequence[Course]:
        pass
    
    @abstractmethod
    async def create(
        self,
        center_id: int,
        name: str,
        description: str | None = None,
        category: str | None = None,
        age_min: int | None = None,
        age_max: int | None = None,
        requirements: str | None = None,
        schedule: str | None = None,
        price_4: int | None = None,
        price_8: int | None = None,
        price_unlimited: int | None = None,
        photo: str | None = None,
    ) -> Course:
        pass
    
    @abstractmethod
    async def update(self, course: Course) -> Course:
        pass
    
    @abstractmethod
    async def delete(self, id: int) -> bool:
        pass
