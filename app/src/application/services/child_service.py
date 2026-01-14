from loguru import logger

from src.application.interfaces.repositories import IChildRepository
from src.domain.entities import Child


class ChildService:
    def __init__(self, child_repo: IChildRepository):
        self._child_repo = child_repo
    
    async def create_child(self, parent_id: int, name: str, age: int) -> Child:
        logger.info(f"Creating child for parent_id={parent_id}, name={name}, age={age}")
        return await self._child_repo.create(
            parent_id=parent_id,
            name=name,
            age=age
        )
    
    async def get_parent_children(self, parent_id: int) -> list[Child]:
        logger.info(f"Getting children for parent_id={parent_id}")
        return await self._child_repo.get_by_parent_id(parent_id)
    
    async def get_child_by_id(self, child_id: int) -> Child | None:
        logger.info(f"Getting child by id={child_id}")
        return await self._child_repo.get_by_id(child_id)
