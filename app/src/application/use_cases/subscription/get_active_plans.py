from src.domain.entities import SubscriptionPlan
from src.domain.interfaces.repositories import ISubscriptionPlanRepository


class GetActiveSubscriptionPlansUseCase:
    def __init__(self, subscription_plan_repository: ISubscriptionPlanRepository):
        self._subscription_plan_repository = subscription_plan_repository
    
    async def execute(self) -> list[SubscriptionPlan]:
        plans = await self._subscription_plan_repository.get_active()
        return list(plans)
