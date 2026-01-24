from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.interfaces.repositories.city_repository import ICityRepository
from src.domain.entities.city import City as CityEntity
from src.infrastructure.persistence.models import City, CityTranslation
from src.infrastructure.persistence.mappers.city_mapper import CityMapper


class CityRepository(ICityRepository):
    def __init__(self, session: AsyncSession):
        self._session = session
        self._mapper = CityMapper()
    
    async def get_all_cities(self, country_id: int = 1, language_id: int = 1) -> list[CityEntity]:
        query = (
            select(City, CityTranslation.name)
            .join(CityTranslation, City.id == CityTranslation.city_id)
            .where(
                City.country_id == country_id,
                CityTranslation.language_id == language_id
            )
            .order_by(CityTranslation.name)
        )
        result = await self._session.execute(query)
        rows = result.all()
        
        return [self._mapper.to_entity(row[0], row[1]) for row in rows]
    
    async def get_by_id(self, city_id: int, language_id: int = 1) -> CityEntity | None:
        query = (
            select(City, CityTranslation.name)
            .join(CityTranslation, City.id == CityTranslation.city_id)
            .where(
                City.id == city_id,
                CityTranslation.language_id == language_id
            )
        )
        result = await self._session.execute(query)
        row = result.first()
        
        if not row:
            return None
        
        return self._mapper.to_entity(row[0], row[1])