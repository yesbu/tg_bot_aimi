from src.domain.entities import Course
from src.domain.interfaces.repositories import ICourseRepository


class CreateCourseUseCase:
    def __init__(self, course_repository: ICourseRepository):
        self._course_repository = course_repository
    
    async def execute(
        self,
        name: str,
        description: str,
        center_id: int,
        teacher_id: int | None = None,
    ) -> Course:
        course = Course(
            name=name,
            description=description,
            center_id=center_id,
            teacher_id=teacher_id,
        )
        
        return await self._course_repository.create(course)
