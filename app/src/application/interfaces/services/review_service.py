from abc import ABC, abstractmethod
from typing import Sequence

from src.domain.entities import Review


class IReviewService(ABC):
    @abstractmethod
    async def get_course_reviews(
        self,
        course_id: int,
        limit: int | None = 20
    ) -> Sequence[Review]:
        pass
    
    @abstractmethod
    async def create_review(
        self,
        course_id: int,
        user_id: int,
        rating: int,
        comment: str | None = None,
    ) -> Review:
        pass
    
    @abstractmethod
    async def get_user_review(self, course_id: int, user_id: int) -> Review | None:
        pass
    
    @abstractmethod
    async def user_can_review(self, course_id: int, user_id: int) -> bool:
        pass
