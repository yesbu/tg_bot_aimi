from abc import ABC, abstractmethod

from src.domain.entities.city import City


class ICityRepository(ABC):
    @abstractmethod
    async def get_all_cities(self, country_id: int = 1, language_id: int = 1) -> list[City]:
        pass
    
    @abstractmethod
    async def get_by_id(self, city_id: int, language_id: int = 1) -> City | None:
        pass
