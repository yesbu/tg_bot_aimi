from src.domain.entities import Course
from src.domain.interfaces.repositories import ICourseRepository


class GetCourseByIdUseCase:
    def __init__(self, course_repository: ICourseRepository):
        self._course_repository = course_repository
    
    async def execute(self, course_id: int) -> Course | None:
        return await self._course_repository.get_by_id(course_id)
