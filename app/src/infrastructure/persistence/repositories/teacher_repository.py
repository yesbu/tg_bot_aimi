from typing import Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from src.application.interfaces.repositories.teacher_repository import ITeacherRepository
from src.domain.entities import Teacher
from src.infrastructure.persistence.models.teacher import Teacher as TeacherModel
from src.infrastructure.persistence.mappers import TeacherMapper


class TeacherRepository(ITeacherRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
    
    async def get_by_id(self, id: int) -> Teacher | None:
        logger.debug(f"Getting teacher by id={id}")
        result = await self._session.execute(
            select(TeacherModel).where(TeacherModel.id == id)
        )
        model = result.scalar_one_or_none()
        return TeacherMapper.to_entity(model) if model else None
    
    async def get_by_center_id(self, center_id: int) -> Sequence[Teacher]:
        logger.debug(f"Getting teachers by center_id={center_id}")
        result = await self._session.execute(
            select(TeacherModel).where(TeacherModel.center_id == center_id)
        )
        models = result.scalars().all()
        return [TeacherMapper.to_entity(model) for model in models]
    
    async def create(
        self,
        center_id: int,
        name: str,
        description: str | None = None,
    ) -> Teacher:
        logger.debug(f"Creating teacher for center_id={center_id}")
        model = TeacherModel(
            center_id=center_id,
            name=name,
            description=description,
        )
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return TeacherMapper.to_entity(model)
    
    async def update(self, teacher: Teacher) -> Teacher:
        logger.debug(f"Updating teacher id={teacher.id}")
        result = await self._session.execute(
            select(TeacherModel).where(TeacherModel.id == teacher.id)
        )
        model = result.scalar_one()
        model.name = teacher.name
        model.description = teacher.description
        await self._session.flush()
        await self._session.refresh(model)
        return TeacherMapper.to_entity(model)
    
    async def delete(self, id: int) -> bool:
        logger.debug(f"Deleting teacher id={id}")
        result = await self._session.execute(
            select(TeacherModel).where(TeacherModel.id == id)
        )
        model = result.scalar_one_or_none()
        
        if model:
            await self._session.delete(model)
            await self._session.flush()
            return True
        return False
