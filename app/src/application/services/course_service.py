from typing import Sequence
from loguru import logger

from src.application.interfaces.services import ICourseService
from src.application.interfaces.repositories import ICourseRepository, IReviewRepository
from src.domain.entities import Course


class CourseService(ICourseService):
    def __init__(
        self,
        course_repository: ICourseRepository,
        review_repository: IReviewRepository,
    ) -> None:
        self._course_repo = course_repository
        self._review_repo = review_repository
    
    async def get_course_by_id(self, id: int) -> Course | None:
        logger.info(f"Getting course by id={id}")
        return await self._course_repo.get_by_id(id)
    
    async def get_center_courses(self, center_id: int) -> Sequence[Course]:
        logger.info(f"Getting courses for center_id={center_id}")
        return await self._course_repo.get_by_center_id(center_id)
    
    async def search_courses(
        self,
        city: str | None = None,
        category: str | None = None,
        age: int | None = None,
        limit: int | None = None,
        offset: int | None = None
    ) -> Sequence[Course]:
        logger.info(f"Searching courses: city={city}, category={category}, age={age}")
        return await self._course_repo.get_by_filters(
            city=city,
            category=category,
            age=age,
            limit=limit,
            offset=offset,
        )
    
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
        logger.info(f"Creating course for center_id={center_id}")
        return await self._course_repo.create(
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
    
    async def update_course(self, course: Course) -> Course:
        logger.info(f"Updating course id={course.id}")
        return await self._course_repo.update(course)
    
    async def recalculate_course_rating(self, course_id: int) -> Course:
        logger.info(f"Recalculating rating for course_id={course_id}")
        course = await self._course_repo.get_by_id(course_id)
        if not course:
            raise ValueError(f"Course {course_id} not found")
        
        avg_rating = await self._review_repo.calculate_average_rating(course_id)
        if avg_rating is not None:
            course.update_rating(avg_rating)
            return await self._course_repo.update(course)
        
        return course
