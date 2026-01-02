from abc import ABC, abstractmethod
from typing import Sequence

from src.domain.entities import Course


class ICourseService(ABC):
    @abstractmethod
    async def get_course_by_id(self, id: int) -> Course | None:
        pass
    
    @abstractmethod
    async def get_center_courses(self, center_id: int) -> Sequence[Course]:
        pass
    
    @abstractmethod
    async def search_courses(
        self,
        city: str | None = None,
        category: str | None = None,
        age: int | None = None,
        limit: int | None = None,
        offset: int | None = None
    ) -> Sequence[Course]:
        pass
    
    @abstractmethod
    async def create_course(
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
    async def update_course(self, course: Course) -> Course:
        pass
    
    @abstractmethod
    async def recalculate_course_rating(self, course_id: int) -> Course:
        pass
