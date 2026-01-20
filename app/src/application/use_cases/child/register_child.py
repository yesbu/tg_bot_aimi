from src.domain.entities import Child
from src.domain.interfaces.repositories import IChildRepository


class RegisterChildUseCase:
    def __init__(self, child_repository: IChildRepository):
        self._child_repository = child_repository
    
    async def execute(
        self,
        first_name: str,
        last_name: str,
        parent_id: int,
        birth_date: str | None = None,
    ) -> Child:
        child = Child(
            first_name=first_name,
            last_name=last_name,
            parent_id=parent_id,
            birth_date=birth_date,
        )
        
        return await self._child_repository.create(child)
