from typing import Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from src.application.interfaces.repositories import ICourseRepository
from src.domain.entities import Course
from src.infrastructure.persistence.models.course import Course as CourseModel
from src.infrastructure.persistence.models.center import Center as CenterModel
from src.infrastructure.persistence.mappers import CourseMapper
from src.domain.enums import CenterStatus


class CourseRepository(ICourseRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
    
    async def get_by_id(self, id: int) -> Course | None:
        logger.debug(f"Getting course by id={id}")
        result = await self._session.execute(
            select(CourseModel).where(CourseModel.id == id)
        )
        model = result.scalar_one_or_none()
        return CourseMapper.to_entity(model) if model else None
    
    async def get_by_center_id(self, center_id: int) -> Sequence[Course]:
        logger.debug(f"Getting courses by center_id={center_id}")
        result = await self._session.execute(
            select(CourseModel).where(CourseModel.center_id == center_id)
        )
        models = result.scalars().all()
        return [CourseMapper.to_entity(model) for model in models]
    
    async def get_by_filters(
        self,
        city: str | None = None,
        category: str | None = None,
        age: int | None = None,
        limit: int | None = None,
        offset: int | None = None
    ) -> Sequence[Course]:
        logger.debug(f"Getting courses with filters")
        query = (
            select(CourseModel)
            .join(CenterModel, CourseModel.center_id == CenterModel.id)
            .where(CenterModel.status == CenterStatus.APPROVED)
        )
        
        if city:
            query = query.where(CenterModel.city == city)
        if category:
            query = query.where(CourseModel.category == category)
        if age:
            query = query.where(
                (CourseModel.age_min.is_(None) | (CourseModel.age_min <= age)) &
                (CourseModel.age_max.is_(None) | (CourseModel.age_max >= age))
            )
        
        if offset:
            query = query.offset(offset)
        if limit:
            query = query.limit(limit)
        
        result = await self._session.execute(query)
        models = result.scalars().all()
        return [CourseMapper.to_entity(model) for model in models]
    
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
        logger.debug(f"Creating course for center_id={center_id}")
        entity = Course(
            center_id=center_id,
            name=name,
            description=description,
            category=category,
            age_min=age_min,
            age_max=age_max,
            requirements=requirements,
            schedule=schedule,
            price_4=price_4,
            price_8=price_8,
            price_unlimited=price_unlimited,
            photo=photo,
        )
        model = CourseMapper.to_model(entity)
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return CourseMapper.to_entity(model)
    
    async def update(self, course: Course) -> Course:
        logger.debug(f"Updating course id={course.id}")
        result = await self._session.execute(
            select(CourseModel).where(CourseModel.id == course.id)
        )
        model = result.scalar_one()
        CourseMapper.update_model(model, course)
        await self._session.flush()
        await self._session.refresh(model)
        return CourseMapper.to_entity(model)
    
    async def delete(self, id: int) -> bool:
        logger.debug(f"Deleting course id={id}")
        result = await self._session.execute(
            select(CourseModel).where(CourseModel.id == id)
        )
        model = result.scalar_one_or_none()
        
        if model:
            await self._session.delete(model)
            await self._session.flush()
            return True
        return False
