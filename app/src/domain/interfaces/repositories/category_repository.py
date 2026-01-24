from abc import ABC, abstractmethod

from src.domain.entities.category import Category


class ICategoryRepository(ABC):
    @abstractmethod
    async def get_all_categories(self, language_id: int = 1, active_only: bool = True) -> list[Category]:
        pass
    
    @abstractmethod
    async def get_by_id(self, category_id: int, language_id: int = 1) -> Category | None:
        pass
