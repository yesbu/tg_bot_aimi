from typing import Sequence
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from src.domain.interfaces.repositories import IReviewRepository
from src.domain.entities import Review
from src.infrastructure.persistence.models.review import Review as ReviewModel
from src.infrastructure.persistence.mappers import ReviewMapper


class ReviewRepository(IReviewRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
    
    async def get_by_id(self, id: int) -> Review | None:
        logger.debug(f"Getting review by id={id}")
        result = await self._session.execute(
            select(ReviewModel).where(ReviewModel.id == id)
        )
        model = result.scalar_one_or_none()
        return ReviewMapper.to_entity(model) if model else None
    
    async def get_by_course_id(
        self,
        course_id: int,
        limit: int | None = 20
    ) -> Sequence[Review]:
        logger.debug(f"Getting reviews for course_id={course_id}, limit={limit}")
        query = (
            select(ReviewModel)
            .where(ReviewModel.course_id == course_id)
            .order_by(ReviewModel.created_at.desc())
        )
        
        if limit:
            query = query.limit(limit)
        
        result = await self._session.execute(query)
        models = result.scalars().all()
        return [ReviewMapper.to_entity(model) for model in models]
    
    async def get_user_review(self, course_id: int, user_id: int) -> Review | None:
        logger.debug(f"Getting review for course_id={course_id}, user_id={user_id}")
        result = await self._session.execute(
            select(ReviewModel)
            .where(ReviewModel.course_id == course_id)
            .where(ReviewModel.user_id == user_id)
        )
        model = result.scalar_one_or_none()
        return ReviewMapper.to_entity(model) if model else None
    
    async def create(
        self,
        course_id: int,
        user_id: int,
        rating: int,
        comment: str | None = None,
    ) -> Review:
        logger.debug(f"Creating review for course_id={course_id}")
        entity = Review(
            course_id=course_id,
            user_id=user_id,
            rating=rating,
            comment=comment,
        )
        model = ReviewMapper.to_model(entity)
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return ReviewMapper.to_entity(model)
    
    async def calculate_average_rating(self, course_id: int) -> float | None:
        logger.debug(f"Calculating average rating for course_id={course_id}")
        result = await self._session.execute(
            select(func.avg(ReviewModel.rating))
            .where(ReviewModel.course_id == course_id)
        )
        avg_rating = result.scalar_one()
        return round(avg_rating, 1) if avg_rating else None
    
    async def exists_user_review(self, course_id: int, user_id: int) -> bool:
        logger.debug(f"Checking if review exists for course_id={course_id}, user_id={user_id}")
        result = await self._session.execute(
            select(func.count())
            .select_from(ReviewModel)
            .where(ReviewModel.course_id == course_id)
            .where(ReviewModel.user_id == user_id)
        )
        count = result.scalar_one()
        return count > 0
