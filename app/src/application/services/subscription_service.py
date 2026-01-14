from typing import Sequence
import uuid
from loguru import logger

from src.application.interfaces.services import ISubscriptionService
from src.application.interfaces.repositories import ISubscriptionRepository
from src.domain.entities import SubscriptionTemplate, Subscription


class SubscriptionService(ISubscriptionService):
    def __init__(self, subscription_repository: ISubscriptionRepository) -> None:
        self._sub_repo = subscription_repository
    
    async def get_active_templates(self) -> Sequence[SubscriptionTemplate]:
        logger.info("Getting active subscription templates")
        return await self._sub_repo.get_active_templates()
    
    async def create_template(
        self,
        name: str,
        tariff: str,
        price: float,
        description: str | None = None,
        lessons_total: int | None = None,
        created_by: int | None = None,
    ) -> SubscriptionTemplate:
        logger.info(f"Creating subscription template: {name}")
        return await self._sub_repo.create_template(
            name=name,
            tariff=tariff,
            price=price,
            description=description,
            lessons_total=lessons_total,
            created_by=created_by,
        )
    
    async def get_subscription_by_qr(self, qr_code: str) -> Subscription | None:
        logger.info(f"Getting subscription by QR code")
        return await self._sub_repo.get_subscription_by_qr_code(qr_code)
    
    async def get_user_subscriptions(
        self,
        user_id: int,
        child_id: int | None = None
    ) -> Sequence[Subscription]:
        logger.info(f"Getting subscriptions for user_id={user_id}, child_id={child_id}")
        return await self._sub_repo.get_user_subscriptions(user_id, child_id)
    
    async def create_subscription(
        self,
        user_id: int,
        template_id: int,
        child_id: int | None = None,
    ) -> Subscription:
        logger.info(f"Creating subscription for user_id={user_id}, template_id={template_id}")
        
        qr_code = str(uuid.uuid4())
        
        return await self._sub_repo.create_subscription(
            user_id=user_id,
            template_id=template_id,
            qr_code=qr_code,
            child_id=child_id,
        )
    
    async def use_subscription_lesson(self, subscription_id: int) -> Subscription:
        logger.info(f"Using lesson for subscription_id={subscription_id}")
        subscription = await self._sub_repo.get_subscription_by_id(subscription_id)
        
        if not subscription:
            raise ValueError(f"Subscription {subscription_id} not found")
        
        subscription.use_lesson()
        return await self._sub_repo.update_subscription(subscription)
    
    async def create_subscription_for_course(
        self,
        user_id: int,
        course_id: int,
        tariff: str,
        child_id: int | None = None,
    ) -> Subscription:
        logger.info(f"Creating subscription for user_id={user_id}, course_id={course_id}, tariff={tariff}")
        
        qr_code = str(uuid.uuid4())
        
        lessons_map = {
            "4": 4,
            "8": 8,
            "unlimited": 999
        }
        lessons_total = lessons_map.get(tariff, 8)
        
        return await self._sub_repo.create_subscription_for_course(
            user_id=user_id,
            course_id=course_id,
            qr_code=qr_code,
            lessons_total=lessons_total,
            child_id=child_id,
        )
    
    async def update_qr_code(self, subscription_id: int, qr_code: str) -> Subscription:
        logger.info(f"Updating QR code for subscription_id={subscription_id}")
        subscription = await self._sub_repo.get_subscription_by_id(subscription_id)
        
        if not subscription:
            raise ValueError(f"Subscription {subscription_id} not found")
        
        subscription.qr_code = qr_code
        return await self._sub_repo.update_subscription(subscription)
