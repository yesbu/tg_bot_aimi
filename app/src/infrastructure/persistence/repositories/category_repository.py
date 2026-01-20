from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.persistence.models import CourseCategory, CourseCategoryTranslation


class CategoryRepository:
    def __init__(self, session: AsyncSession):
        self._session = session
    
    async def get_all_categories(self, language_id: int = 1) -> list[tuple[int, str]]:
        query = (
            select(CourseCategory.id, CourseCategoryTranslation.name)
            .join(CourseCategoryTranslation, CourseCategory.id == CourseCategoryTranslation.category_id)
            .where(
                CourseCategoryTranslation.language_id == language_id,
                CourseCategory.is_active == True
            )
            .order_by(CourseCategoryTranslation.name)
        )
        result = await self._session.execute(query)
        categories = result.all()
        
        return [(row[0], row[1]) for row in categories]
