from typing import Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from src.domain.interfaces.repositories import ISubscriptionPlanRepository
from src.domain.entities import SubscriptionPlan
from src.infrastructure.persistence.models.subscription_plan import SubscriptionPlan as SubscriptionPlanModel
from src.infrastructure.persistence.mappers import SubscriptionPlanMapper


class SubscriptionPlanRepository(ISubscriptionPlanRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
    
    async def get_by_id(self, id: int) -> SubscriptionPlan | None:
        logger.debug(f"Getting subscription plan by id={id}")
        result = await self._session.execute(
            select(SubscriptionPlanModel).where(SubscriptionPlanModel.id == id)
        )
        model = result.scalar_one_or_none()
        return SubscriptionPlanMapper.to_entity(model) if model else None
    
    async def get_by_name(self, name: str) -> SubscriptionPlan | None:
        logger.debug(f"Getting subscription plan by name={name}")
        result = await self._session.execute(
            select(SubscriptionPlanModel).where(SubscriptionPlanModel.name == name)
        )
        model = result.scalar_one_or_none()
        return SubscriptionPlanMapper.to_entity(model) if model else None
    
    async def get_all(self) -> Sequence[SubscriptionPlan]:
        logger.debug("Getting all subscription plans")
        result = await self._session.execute(
            select(SubscriptionPlanModel).order_by(SubscriptionPlanModel.display_order)
        )
        models = result.scalars().all()
        return [SubscriptionPlanMapper.to_entity(model) for model in models]
    
    async def get_active(self) -> Sequence[SubscriptionPlan]:
        logger.debug("Getting active subscription plans")
        result = await self._session.execute(
            select(SubscriptionPlanModel)
            .where(SubscriptionPlanModel.is_active == True)
            .order_by(SubscriptionPlanModel.display_order)
        )
        models = result.scalars().all()
        return [SubscriptionPlanMapper.to_entity(model) for model in models]
    
    async def create(
        self,
        name: str,
        duration_months: int,
        price: float,
        visits_limit: int,
        description: str | None = None,
        display_order: int = 0,
    ) -> SubscriptionPlan:
        logger.debug(f"Creating subscription plan name={name}")
        model = SubscriptionPlanModel(
            name=name,
            duration_months=duration_months,
            price=price,
            visits_limit=visits_limit,
            description=description,
            display_order=display_order,
            is_active=True,
        )
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return SubscriptionPlanMapper.to_entity(model)
    
    async def update(self, plan: SubscriptionPlan) -> SubscriptionPlan:
        logger.debug(f"Updating subscription plan id={plan.id}")
        result = await self._session.execute(
            select(SubscriptionPlanModel).where(SubscriptionPlanModel.id == plan.id)
        )
        model = result.scalar_one()
        SubscriptionPlanMapper.update_model(model, plan)
        await self._session.flush()
        await self._session.refresh(model)
        return SubscriptionPlanMapper.to_entity(model)
    
    async def deactivate(self, id: int) -> bool:
        logger.debug(f"Deactivating subscription plan id={id}")
        result = await self._session.execute(
            select(SubscriptionPlanModel).where(SubscriptionPlanModel.id == id)
        )
        model = result.scalar_one_or_none()
        if not model:
            return False
        model.is_active = False
        await self._session.flush()
        return True
    
    async def activate(self, id: int) -> bool:
        logger.debug(f"Activating subscription plan id={id}")
        result = await self._session.execute(
            select(SubscriptionPlanModel).where(SubscriptionPlanModel.id == id)
        )
        model = result.scalar_one_or_none()
        if not model:
            return False
        model.is_active = True
        await self._session.flush()
        return True
