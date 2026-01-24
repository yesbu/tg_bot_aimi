from loguru import logger

from src.domain.interfaces.repositories import ICategoryRepository
from src.domain.interfaces.cache import ICacheClient
from src.domain.entities import Category


class GetAllCategoriesUseCase:
    def __init__(self, category_repository: ICategoryRepository, cache: ICacheClient):
        self._category_repository = category_repository
        self._cache = cache
    
    async def execute(self, language_id: int = 1, active_only: bool = True) -> list[Category]:
        cache_key = f"categories:lang:{language_id}:active:{active_only}"
        
        if self._cache:
            cached = await self._cache.get(cache_key)
            if cached:
                logger.debug(f"Categories loaded from cache (key: {cache_key})")
                return [Category(id=item["id"], name=item["name"], is_active=item["is_active"]) for item in cached]
        
        logger.debug(f"Categories not in cache, querying database (language_id={language_id})")
        
        categories = await self._category_repository.get_all_categories(language_id, active_only)
        
        if self._cache and categories:
            categories_dict = [{"id": cat.id, "name": cat.name, "is_active": cat.is_active} for cat in categories]
            await self._cache.set(cache_key, categories_dict, ttl=86400)
            logger.debug(f"Categories cached (key: {cache_key}, count: {len(categories)})")
        
        return categories
