from loguru import logger

from src.domain.interfaces.repositories import ICityRepository
from src.domain.interfaces.cache import ICacheClient
from src.domain.entities import City


class GetAllCitiesUseCase:
    def __init__(self, city_repository: ICityRepository, cache: ICacheClient):
        self._city_repository = city_repository
        self._cache = cache
    
    async def execute(self, country_id: int = 1, language_id: int = 1) -> list[City]:
        cache_key = f"cities:country:{country_id}:lang:{language_id}"
        
        if self._cache:
            cached = await self._cache.get(cache_key)
            if cached:
                logger.debug(f"Cities loaded from cache (key: {cache_key})")
                return [City(id=item["id"], name=item["name"], country_id=item["country_id"]) for item in cached]
        
        logger.debug(f"Cities not in cache, querying database (country_id={country_id}, language_id={language_id})")
        
        cities = await self._city_repository.get_all_cities(country_id, language_id)
        
        if self._cache and cities:
            cities_dict = [{"id": city.id, "name": city.name, "country_id": city.country_id} for city in cities]
            await self._cache.set(cache_key, cities_dict, ttl=86400)
            logger.debug(f"Cities cached (key: {cache_key}, count: {len(cities)})")
        
        return cities
