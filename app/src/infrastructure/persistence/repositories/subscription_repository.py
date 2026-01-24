from datetime import datetime, timedelta
from typing import Sequence
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from src.domain.interfaces.repositories import ISubscriptionRepository
from src.domain.entities import Subscription
from src.domain.enums import SubscriptionStatus
from src.infrastructure.persistence.models.subscription import Subscription as SubscriptionModel
from src.infrastructure.persistence.mappers import SubscriptionMapper


class SubscriptionRepository(ISubscriptionRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
    
    async def get_by_id(self, id: int) -> Subscription | None:
        logger.debug(f"Getting subscription by id={id}")
        result = await self._session.execute(
            select(SubscriptionModel).where(SubscriptionModel.id == id)
        )
        model = result.scalar_one_or_none()
        return SubscriptionMapper.to_entity(model) if model else None
    
    async def get_active_by_user_id(self, user_id: int) -> Subscription | None:
        logger.debug(f"Getting active subscription for user_id={user_id}")
        result = await self._session.execute(
            select(SubscriptionModel).where(
                and_(
                    SubscriptionModel.user_id == user_id,
                    SubscriptionModel.status == SubscriptionStatus.ACTIVE,
                    SubscriptionModel.expires_at > datetime.utcnow()
                )
            ).order_by(SubscriptionModel.expires_at.desc())
        )
        model = result.scalar_one_or_none()
        return SubscriptionMapper.to_entity(model) if model else None
    
    async def get_all_by_user_id(
        self,
        user_id: int,
        limit: int | None = None,
        offset: int | None = None,
    ) -> Sequence[Subscription]:
        logger.debug(f"Getting all subscriptions for user_id={user_id} (limit={limit}, offset={offset})")
        query = (
            select(SubscriptionModel)
            .where(SubscriptionModel.user_id == user_id)
            .order_by(SubscriptionModel.created_at.desc())
        )
        
        if offset:
            query = query.offset(offset)
        if limit:
            query = query.limit(limit)
        
        result = await self._session.execute(query)
        models = result.scalars().all()
        return [SubscriptionMapper.to_entity(model) for model in models]
    
    async def get_expiring_soon(
        self,
        days: int = 7,
        limit: int | None = None,
    ) -> Sequence[Subscription]:
        logger.debug(f"Getting subscriptions expiring in {days} days (limit={limit})")
        expiry_date = datetime.utcnow() + timedelta(days=days)
        query = (
            select(SubscriptionModel)
            .where(
                and_(
                    SubscriptionModel.status == SubscriptionStatus.ACTIVE,
                    SubscriptionModel.expires_at <= expiry_date,
                    SubscriptionModel.expires_at > datetime.utcnow()
                )
            )
            .order_by(SubscriptionModel.expires_at)
        )
        
        if limit:
            query = query.limit(limit)
        
        result = await self._session.execute(query)
        models = result.scalars().all()
        return [SubscriptionMapper.to_entity(model) for model in models]
    
    async def get_by_status(
        self,
        status: SubscriptionStatus,
        limit: int | None = None,
        offset: int | None = None,
    ) -> Sequence[Subscription]:
        logger.debug(f"Getting subscriptions by status={status.value} (limit={limit}, offset={offset})")
        query = (
            select(SubscriptionModel)
            .where(SubscriptionModel.status == status)
            .order_by(SubscriptionModel.created_at.desc())
        )
        
        if offset:
            query = query.offset(offset)
        if limit:
            query = query.limit(limit)
        
        result = await self._session.execute(query)
        models = result.scalars().all()
        return [SubscriptionMapper.to_entity(model) for model in models]
    
    async def create(
        self,
        user_id: int,
        subscription_plan_id: int,
        starts_at: datetime,
        expires_at: datetime,
        payment_id: int | None = None,
    ) -> Subscription:
        logger.debug(f"Creating subscription for user_id={user_id}, plan_id={subscription_plan_id}")
        model = SubscriptionModel(
            user_id=user_id,
            subscription_plan_id=subscription_plan_id,
            status=SubscriptionStatus.ACTIVE,
            starts_at=starts_at,
            expires_at=expires_at,
            payment_id=payment_id,
        )
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return SubscriptionMapper.to_entity(model)
    
    async def update(self, subscription: Subscription) -> Subscription:
        logger.debug(f"Updating subscription id={subscription.id}")
        result = await self._session.execute(
            select(SubscriptionModel).where(SubscriptionModel.id == subscription.id)
        )
        model = result.scalar_one()
        SubscriptionMapper.update_model(model, subscription)
        await self._session.flush()
        await self._session.refresh(model)
        return SubscriptionMapper.to_entity(model)
    
    async def has_active_subscription(self, user_id: int) -> bool:
        logger.debug(f"Checking active subscription for user_id={user_id}")
        result = await self._session.execute(
            select(SubscriptionModel.id).where(
                and_(
                    SubscriptionModel.user_id == user_id,
                    SubscriptionModel.status == SubscriptionStatus.ACTIVE,
                    SubscriptionModel.expires_at > datetime.utcnow()
                )
            )
        )
        return result.scalar_one_or_none() is not None
