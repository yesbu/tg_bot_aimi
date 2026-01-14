from typing import Sequence
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from src.application.interfaces.repositories import ISubscriptionRepository
from src.domain.entities import SubscriptionTemplate, Subscription
from src.infrastructure.persistence.models.subscription import SubscriptionTemplate as SubscriptionTemplateModel, Subscription as SubscriptionModel
from src.infrastructure.persistence.mappers import SubscriptionTemplateMapper, SubscriptionMapper
from src.domain.enums import SubscriptionStatus


class SubscriptionRepository(ISubscriptionRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
    
    async def get_template_by_id(self, id: int) -> SubscriptionTemplate | None:
        logger.debug(f"Getting subscription template by id={id}")
        result = await self._session.execute(
            select(SubscriptionTemplateModel).where(SubscriptionTemplateModel.id == id)
        )
        model = result.scalar_one_or_none()
        return SubscriptionTemplateMapper.to_entity(model) if model else None
    
    async def get_active_templates(self) -> Sequence[SubscriptionTemplate]:
        logger.debug("Getting active subscription templates")
        result = await self._session.execute(
            select(SubscriptionTemplateModel)
            .where(SubscriptionTemplateModel.is_active == True)
            .order_by(SubscriptionTemplateModel.price)
        )
        models = result.scalars().all()
        return [SubscriptionTemplateMapper.to_entity(model) for model in models]
    
    async def create_template(
        self,
        name: str,
        tariff: str,
        price: float,
        description: str | None = None,
        lessons_total: int | None = None,
        created_by: int | None = None,
    ) -> SubscriptionTemplate:
        logger.debug("Creating subscription template")
        entity = SubscriptionTemplate(
            name=name,
            tariff=tariff,
            price=price,
            description=description,
            lessons_total=lessons_total,
            created_by=created_by,
        )
        model = SubscriptionTemplateMapper.to_model(entity)
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return SubscriptionTemplateMapper.to_entity(model)
    
    async def update_template(self, template: SubscriptionTemplate) -> SubscriptionTemplate:
        logger.debug(f"Updating subscription template id={template.id}")
        result = await self._session.execute(
            select(SubscriptionTemplateModel).where(SubscriptionTemplateModel.id == template.id)
        )
        model = result.scalar_one()
        SubscriptionTemplateMapper.update_model(model, template)
        await self._session.flush()
        await self._session.refresh(model)
        return SubscriptionTemplateMapper.to_entity(model)
    
    async def deactivate_template(self, id: int) -> bool:
        logger.debug(f"Deactivating subscription template id={id}")
        result = await self._session.execute(
            update(SubscriptionTemplateModel)
            .where(SubscriptionTemplateModel.id == id)
            .values(is_active=False)
        )
        await self._session.flush()
        return result.rowcount > 0
    
    async def get_subscription_by_id(self, id: int) -> Subscription | None:
        logger.debug(f"Getting subscription by id={id}")
        result = await self._session.execute(
            select(SubscriptionModel).where(SubscriptionModel.id == id)
        )
        model = result.scalar_one_or_none()
        return SubscriptionMapper.to_entity(model) if model else None
    
    async def get_subscription_by_qr_code(self, qr_code: str) -> Subscription | None:
        logger.debug(f"Getting subscription by qr_code")
        result = await self._session.execute(
            select(SubscriptionModel)
            .where(SubscriptionModel.qr_code == qr_code)
            .where(SubscriptionModel.status == SubscriptionStatus.ACTIVE)
        )
        model = result.scalar_one_or_none()
        return SubscriptionMapper.to_entity(model) if model else None
    
    async def get_user_subscriptions(
        self,
        user_id: int,
        child_id: int | None = None
    ) -> Sequence[Subscription]:
        logger.debug(f"Getting subscriptions for user_id={user_id}, child_id={child_id}")
        query = (
            select(SubscriptionModel)
            .where(SubscriptionModel.user_id == user_id)
            .where(SubscriptionModel.status == SubscriptionStatus.ACTIVE)
        )
        
        if child_id:
            query = query.where(SubscriptionModel.child_id == child_id)
        else:
            query = query.where(SubscriptionModel.child_id.is_(None))
        
        result = await self._session.execute(query)
        models = result.scalars().all()
        return [SubscriptionMapper.to_entity(model) for model in models]
    
    async def create_subscription(
        self,
        user_id: int,
        template_id: int,
        qr_code: str,
        child_id: int | None = None,
    ) -> Subscription:
        logger.debug("Creating subscription")
        template_result = await self._session.execute(
            select(SubscriptionTemplateModel).where(SubscriptionTemplateModel.id == template_id)
        )
        template = template_result.scalar_one()
        
        entity = Subscription(
            user_id=user_id,
            child_id=child_id,
            template_id=template_id,
            tariff=template.tariff,
            lessons_total=template.lessons_total,
            lessons_remaining=template.lessons_total,
            qr_code=qr_code,
        )
        
        model = SubscriptionMapper.to_model(entity)
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return SubscriptionMapper.to_entity(model)
    
    async def update_subscription(self, subscription: Subscription) -> Subscription:
        logger.debug(f"Updating subscription id={subscription.id}")
        result = await self._session.execute(
            select(SubscriptionModel).where(SubscriptionModel.id == subscription.id)
        )
        model = result.scalar_one()
        SubscriptionMapper.update_model(model, subscription)
        await self._session.flush()
        await self._session.refresh(model)
        return SubscriptionMapper.to_entity(model)
    
    async def deactivate_subscription(self, id: int) -> bool:
        logger.debug(f"Deactivating subscription id={id}")
        result = await self._session.execute(
            update(SubscriptionModel)
            .where(SubscriptionModel.id == id)
            .values(status=SubscriptionStatus.EXPIRED)
        )
        await self._session.flush()
        return result.rowcount > 0
