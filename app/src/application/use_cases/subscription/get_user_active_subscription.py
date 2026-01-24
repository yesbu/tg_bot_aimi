from src.domain.entities import Subscription
from src.domain.interfaces.repositories import ISubscriptionRepository


class GetUserActiveSubscriptionUseCase:
    def __init__(self, subscription_repository: ISubscriptionRepository):
        self._subscription_repository = subscription_repository
    
    async def execute(self, user_id: int) -> Subscription | None:
        subscription = await self._subscription_repository.get_active_by_user_id(user_id)
        return subscription
