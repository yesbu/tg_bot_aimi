from typing import Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from src.domain.interfaces.repositories import IChildRepository
from src.domain.entities import Child
from src.infrastructure.persistence.models.child import Child as ChildModel
from src.infrastructure.persistence.mappers import ChildMapper


class ChildRepository(IChildRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
    
    async def get_by_id(self, id: int) -> Child | None:
        logger.debug(f"Getting child by id={id}")
        result = await self._session.execute(
            select(ChildModel).where(ChildModel.id == id)
        )
        model = result.scalar_one_or_none()
        return ChildMapper.to_entity(model) if model else None
    
    async def get_by_parent_id(self, parent_id: int) -> Sequence[Child]:
        logger.debug(f"Getting children by parent_id={parent_id}")
        result = await self._session.execute(
            select(ChildModel).where(ChildModel.parent_id == parent_id)
        )
        models = result.scalars().all()
        return [ChildMapper.to_entity(model) for model in models]
    
    async def create(
        self,
        parent_id: int,
        name: str,
        age: int,
    ) -> Child:
        logger.debug(f"Creating child for parent_id={parent_id}")
        entity = Child(parent_id=parent_id, name=name, age=age)
        model = ChildMapper.to_model(entity)
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return ChildMapper.to_entity(model)
    
    async def update(self, child: Child) -> Child:
        logger.debug(f"Updating child id={child.id}")
        result = await self._session.execute(
            select(ChildModel).where(ChildModel.id == child.id)
        )
        model = result.scalar_one()
        ChildMapper.update_model(model, child)
        await self._session.flush()
        await self._session.refresh(model)
        return ChildMapper.to_entity(model)
    
    async def delete(self, id: int) -> bool:
        logger.debug(f"Deleting child id={id}")
        result = await self._session.execute(
            select(ChildModel).where(ChildModel.id == id)
        )
        model = result.scalar_one_or_none()
        
        if model:
            await self._session.delete(model)
            await self._session.flush()
            return True
        return False
