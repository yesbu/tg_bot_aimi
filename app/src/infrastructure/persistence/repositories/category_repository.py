from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.interfaces.repositories.category_repository import ICategoryRepository
from src.domain.entities.category import Category as CategoryEntity
from src.infrastructure.persistence.models import CourseCategory, CourseCategoryTranslation
from src.infrastructure.persistence.mappers.category_mapper import CategoryMapper


class CategoryRepository(ICategoryRepository):
    def __init__(self, session: AsyncSession):
        self._session = session
        self._mapper = CategoryMapper()
    
    async def get_all_categories(self, language_id: int = 1, active_only: bool = True) -> list[CategoryEntity]:
        query = (
            select(CourseCategory, CourseCategoryTranslation.name)
            .join(CourseCategoryTranslation, CourseCategory.id == CourseCategoryTranslation.category_id)
            .where(CourseCategoryTranslation.language_id == language_id)
        )
        
        if active_only:
            query = query.where(CourseCategory.is_active == True)
        
        query = query.order_by(CourseCategoryTranslation.name)
        
        result = await self._session.execute(query)
        rows = result.all()
        
        return [self._mapper.to_entity(row[0], row[1]) for row in rows]
    
    async def get_by_id(self, category_id: int, language_id: int = 1) -> CategoryEntity | None:
        query = (
            select(CourseCategory, CourseCategoryTranslation.name)
            .join(CourseCategoryTranslation, CourseCategory.id == CourseCategoryTranslation.category_id)
            .where(
                CourseCategory.id == category_id,
                CourseCategoryTranslation.language_id == language_id
            )
        )
        result = await self._session.execute(query)
        row = result.first()
        
        if not row:
            return None
        
        return self._mapper.to_entity(row[0], row[1])
