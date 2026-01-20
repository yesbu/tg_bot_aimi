from loguru import logger

from src.infrastructure.persistence.repositories import CategoryRepository
from src.domain.interfaces.cache import ICacheClient


class GetAllCategoriesUseCase:
    def __init__(self, category_repository: CategoryRepository, cache: ICacheClient):
        self._category_repository = category_repository
        self._cache = cache
    
    async def execute(self, language_id: int = 1) -> list[tuple[int, str]]:
        cache_key = f"categories:lang:{language_id}"
        
        if self._cache:
            cached = await self._cache.get(cache_key)
            if cached:
                logger.debug(f"Categories loaded from cache (key: {cache_key})")
                return [(item[0], item[1]) for item in cached]
        
        logger.debug(f"Categories not in cache, querying database (language_id={language_id})")
        
        categories = await self._category_repository.get_all_categories(language_id)
        
        if self._cache and categories:
            await self._cache.set(cache_key, categories, ttl=86400)
            logger.debug(f"Categories cached (key: {cache_key}, count: {len(categories)})")
        
        return categories
