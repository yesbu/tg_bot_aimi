from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from src.infrastructure.persistence.models import CourseCategory, CourseCategoryTranslation
from src.application.interfaces.cache.cache_client import ICacheClient


class CategoryRepository:
    def __init__(self, session: AsyncSession, cache: ICacheClient | None = None):
        self._session = session
        self._cache = cache
    
    async def get_all_categories(self, language_id: int = 1):
        cache_key = f"categories:lang:{language_id}"
        
        if self._cache:
            cached = await self._cache.get(cache_key)
            if cached:
                logger.debug(f"Categories loaded from cache (key: {cache_key})")
                return [(item[0], item[1]) for item in cached]
        
        logger.debug(f"Categories not in cache, querying database (language_id={language_id})")
        
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
        
        categories_list = [(row[0], row[1]) for row in categories]
        
        if self._cache and categories_list:
            await self._cache.set(cache_key, categories_list, ttl=86400)
            logger.debug(f"Categories cached (key: {cache_key}, count: {len(categories_list)})")
        
        return categories_list
