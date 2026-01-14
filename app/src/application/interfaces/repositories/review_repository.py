from abc import ABC, abstractmethod
from typing import Sequence

from src.domain.entities import Review


class IReviewRepository(ABC):
    @abstractmethod
    async def get_by_id(self, id: int) -> Review | None:
        pass
    
    @abstractmethod
    async def get_by_course_id(
        self,
        course_id: int,
        limit: int | None = 20
    ) -> Sequence[Review]:
        pass
    
    @abstractmethod
    async def get_user_review(self, course_id: int, user_id: int) -> Review | None:
        pass
    
    @abstractmethod
    async def create(
        self,
        course_id: int,
        user_id: int,
        rating: int,
        comment: str | None = None,
    ) -> Review:
        pass
    
    @abstractmethod
    async def calculate_average_rating(self, course_id: int) -> float | None:
        pass
    
    @abstractmethod
    async def exists_user_review(self, course_id: int, user_id: int) -> bool:
        pass
