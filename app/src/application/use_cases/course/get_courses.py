from src.domain.entities import Course
from src.domain.interfaces.repositories import ICourseRepository


class GetCoursesUseCase:
    def __init__(self, course_repository: ICourseRepository):
        self._course_repository = course_repository
    
    async def execute(self, center_id: int | None = None) -> list[Course]:
        if center_id:
            return await self._course_repository.get_by_center_id(center_id)
        return await self._course_repository.get_all()
