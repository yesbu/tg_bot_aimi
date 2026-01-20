from src.domain.entities import Center
from src.domain.interfaces.repositories import ICenterRepository


class GetAllCentersUseCase:
    def __init__(self, center_repository: ICenterRepository):
        self._center_repository = center_repository
    
    async def execute(self) -> list[Center]:
        return await self._center_repository.get_all()
