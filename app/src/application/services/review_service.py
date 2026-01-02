from typing import Sequence
from loguru import logger

from src.application.interfaces.services import IReviewService
from src.application.interfaces.repositories import IReviewRepository, ICourseRepository
from src.domain.entities import Review


class ReviewService(IReviewService):
    def __init__(
        self,
        review_repository: IReviewRepository,
        course_repository: ICourseRepository,
    ) -> None:
        self._review_repo = review_repository
        self._course_repo = course_repository
    
    async def get_course_reviews(
        self,
        course_id: int,
        limit: int | None = 20
    ) -> Sequence[Review]:
        logger.info(f"Getting reviews for course_id={course_id}")
        return await self._review_repo.get_by_course_id(course_id, limit)
    
    async def create_review(
        self,
        course_id: int,
        user_id: int,
        rating: int,
        comment: str | None = None,
    ) -> Review:
        logger.info(f"Creating review for course_id={course_id}, user_id={user_id}")
        
        exists = await self._review_repo.exists_user_review(course_id, user_id)
        if exists:
            raise ValueError(f"User {user_id} already reviewed course {course_id}")
        
        review = await self._review_repo.create(
            course_id=course_id,
            user_id=user_id,
            rating=rating,
            comment=comment,
        )
        
        avg_rating = await self._review_repo.calculate_average_rating(course_id)
        if avg_rating:
            course = await self._course_repo.get_by_id(course_id)
            if course:
                course.update_rating(avg_rating)
                await self._course_repo.update(course)
                logger.info(f"Updated course {course_id} rating to {avg_rating}")
        
        return review
    
    async def get_user_review(self, course_id: int, user_id: int) -> Review | None:
        logger.info(f"Getting review for course_id={course_id}, user_id={user_id}")
        return await self._review_repo.get_user_review(course_id, user_id)
    
    async def user_can_review(self, course_id: int, user_id: int) -> bool:
        exists = await self._review_repo.exists_user_review(course_id, user_id)
        return not exists
