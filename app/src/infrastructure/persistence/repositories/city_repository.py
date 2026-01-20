from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.persistence.models import City, CityTranslation


class CityRepository:
    def __init__(self, session: AsyncSession):
        self._session = session
    
    async def get_all_cities(self, country_id: int = 1, language_id: int = 1) -> list[tuple[int, str]]:
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
        
        return [(row[0], row[1]) for row in cities]
