from src.domain.entities import Child
from src.domain.interfaces.repositories import IChildRepository


class GetChildrenByParentUseCase:
    def __init__(self, child_repository: IChildRepository):
        self._child_repository = child_repository
    
    async def execute(self, parent_id: int) -> list[Child]:
        return await self._child_repository.get_by_parent_id(parent_id)
