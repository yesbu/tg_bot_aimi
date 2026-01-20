from src.domain.entities import Review
from src.domain.interfaces.repositories import IReviewRepository


class GetCourseReviewsUseCase:
    def __init__(self, review_repository: IReviewRepository):
        self._review_repository = review_repository
    
    async def execute(self, course_id: int) -> list[Review]:
        return await self._review_repository.get_by_course_id(course_id)
