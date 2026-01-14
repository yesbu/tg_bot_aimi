from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from src.infrastructure.persistence.models import City, CityTranslation
from src.application.interfaces.cache.cache_client import ICacheClient


class CityRepository:
    def __init__(self, session: AsyncSession, cache: ICacheClient | None = None):
        self._session = session
        self._cache = cache
    
    async def get_all_cities(self, country_id: int = 1, language_id: int = 1):
        cache_key = f"cities:country:{country_id}:lang:{language_id}"
        
        if self._cache:
            cached = await self._cache.get(cache_key)
            if cached:
                logger.debug(f"Cities loaded from cache (key: {cache_key})")
                return [(item[0], item[1]) for item in cached]
        
        logger.debug(f"Cities not in cache, querying database (country_id={country_id}, language_id={language_id})")
        
        query = (
            select(City.id, CityTranslation.name)
            .join(CityTranslation, City.id == CityTranslation.city_id)
            .where(
                City.country_id == country_id,
                CityTranslation.language_id == language_id
            )
            .order_by(CityTranslation.name)
        )
        result = await self._session.execute(query)
        cities = result.all()
        
        cities_list = [(row[0], row[1]) for row in cities]
        
        if self._cache and cities_list:
            await self._cache.set(cache_key, cities_list, ttl=86400)
            logger.debug(f"Cities cached (key: {cache_key}, count: {len(cities_list)})")
        
        return cities_list
