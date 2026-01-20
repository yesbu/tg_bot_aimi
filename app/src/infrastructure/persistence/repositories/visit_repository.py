from typing import Sequence
from datetime import datetime, timedelta
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from src.domain.interfaces.repositories import IVisitRepository
from src.domain.entities import Visit
from src.infrastructure.persistence.models.visit import Visit as VisitModel
from src.infrastructure.persistence.mappers import VisitMapper


class VisitRepository(IVisitRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
    
    async def get_by_id(self, id: int) -> Visit | None:
        logger.debug(f"Getting visit by id={id}")
        result = await self._session.execute(
            select(VisitModel).where(VisitModel.id == id)
        )
        model = result.scalar_one_or_none()
        return VisitMapper.to_entity(model) if model else None
    
    async def get_by_subscription_id(self, subscription_id: int) -> Sequence[Visit]:
        logger.debug(f"Getting visits by subscription_id={subscription_id}")
        result = await self._session.execute(
            select(VisitModel)
            .where(VisitModel.subscription_id == subscription_id)
            .order_by(VisitModel.visited_at.desc())
        )
        models = result.scalars().all()
        return [VisitMapper.to_entity(model) for model in models]
    
    async def check_recent_visit(
        self,
        subscription_id: int,
        center_id: int,
        minutes: int = 5
    ) -> bool:
        logger.debug(f"Checking recent visit for subscription_id={subscription_id}, center_id={center_id}")
        time_threshold = datetime.utcnow() - timedelta(minutes=minutes)
        
        result = await self._session.execute(
            select(func.count())
            .select_from(VisitModel)
            .where(VisitModel.subscription_id == subscription_id)
            .where(VisitModel.center_id == center_id)
            .where(VisitModel.visited_at > time_threshold)
        )
        count = result.scalar_one()
        return count > 0
    
    async def create(
        self,
        subscription_id: int,
        user_id: int,
        center_id: int,
        child_id: int | None = None,
        lesson_id: int | None = None,
    ) -> Visit:
        logger.debug(f"Creating visit for subscription_id={subscription_id}")
        entity = Visit(
            subscription_id=subscription_id,
            user_id=user_id,
            center_id=center_id,
            child_id=child_id,
            lesson_id=lesson_id,
        )
        model = VisitMapper.to_model(entity)
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return VisitMapper.to_entity(model)
    
    async def get_visit_count(
        self,
        user_id: int | None = None,
        child_id: int | None = None,
        center_id: int | None = None
    ) -> int:
        logger.debug(f"Getting visit count: user_id={user_id}, child_id={child_id}, center_id={center_id}")
        
        query = select(func.count()).select_from(VisitModel)
        
        if user_id:
            query = query.where(VisitModel.user_id == user_id)
        if child_id:
            query = query.where(VisitModel.child_id == child_id)
        if center_id:
            query = query.where(VisitModel.center_id == center_id)
        
        result = await self._session.execute(query)
        return result.scalar_one()
