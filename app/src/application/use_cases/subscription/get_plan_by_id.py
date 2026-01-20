from src.domain.entities import SubscriptionPlan
from src.domain.interfaces.repositories import ISubscriptionPlanRepository


class GetSubscriptionPlanByIdUseCase:
    def __init__(self, subscription_plan_repository: ISubscriptionPlanRepository):
        self._subscription_plan_repository = subscription_plan_repository

    async def execute(self, plan_id: int) -> SubscriptionPlan | None:
        return await self._subscription_plan_repository.get_by_id(plan_id)
