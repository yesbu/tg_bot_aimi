from loguru import logger

from src.infrastructure.persistence.repositories import CityRepository
from src.domain.interfaces.cache import ICacheClient


class GetAllCitiesUseCase:
    def __init__(self, city_repository: CityRepository, cache: ICacheClient):
        self._city_repository = city_repository
        self._cache = cache
    
    async def execute(self, country_id: int = 1, language_id: int = 1) -> list[tuple[int, str]]:
        cache_key = f"cities:country:{country_id}:lang:{language_id}"
        
        if self._cache:
            cached = await self._cache.get(cache_key)
            if cached:
                logger.debug(f"Cities loaded from cache (key: {cache_key})")
                return [(item[0], item[1]) for item in cached]
        
        logger.debug(f"Cities not in cache, querying database (country_id={country_id}, language_id={language_id})")
        
        cities = await self._city_repository.get_all_cities(country_id, language_id)
        
        if self._cache and cities:
            await self._cache.set(cache_key, cities, ttl=86400)
            logger.debug(f"Cities cached (key: {cache_key}, count: {len(cities)})")
        
        return cities
