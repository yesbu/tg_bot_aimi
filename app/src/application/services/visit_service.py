from typing import Sequence
from loguru import logger

from src.application.interfaces.services import IVisitService
from src.application.interfaces.repositories import IVisitRepository, ISubscriptionRepository
from src.domain.entities import Visit


class VisitService(IVisitService):
    def __init__(
        self,
        visit_repository: IVisitRepository,
        subscription_repository: ISubscriptionRepository,
    ) -> None:
        self._visit_repo = visit_repository
        self._sub_repo = subscription_repository
    
    async def get_subscription_visits(self, subscription_id: int) -> Sequence[Visit]:
        logger.info(f"Getting visits for subscription_id={subscription_id}")
        return await self._visit_repo.get_by_subscription_id(subscription_id)
    
    async def register_visit(
        self,
        qr_code: str,
        center_id: int,
        lesson_id: int | None = None,
    ) -> Visit:
        logger.info(f"Registering visit for QR code at center_id={center_id}")
        
        subscription = await self._sub_repo.get_subscription_by_qr_code(qr_code)
        if not subscription:
            raise ValueError("Invalid QR code or subscription not found")
        
        if not subscription.is_active:
            raise ValueError("Subscription is not active")
        
        is_recent = await self._visit_repo.check_recent_visit(
            subscription.id,
            center_id,
            minutes=5
        )
        
        if is_recent:
            raise ValueError("Duplicate visit detected within 5 minutes")
        
        visit = await self._visit_repo.create(
            subscription_id=subscription.id,
            user_id=subscription.user_id,
            child_id=subscription.child_id,
            center_id=center_id,
            lesson_id=lesson_id,
        )
        
        logger.info(f"Visit registered: id={visit.id}")
        return visit
    
    async def get_visit_count(
        self,
        user_id: int | None = None,
        child_id: int | None = None,
        center_id: int | None = None
    ) -> int:
        logger.info(f"Getting visit count: user_id={user_id}, child_id={child_id}, center_id={center_id}")
        return await self._visit_repo.get_visit_count(user_id, child_id, center_id)
