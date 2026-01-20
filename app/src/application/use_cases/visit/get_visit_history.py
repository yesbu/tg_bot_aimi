from src.domain.entities import Visit
from src.domain.interfaces.repositories import IVisitRepository


class GetVisitHistoryUseCase:    
    def __init__(self, visit_repository: IVisitRepository):
        self._visit_repository = visit_repository
    
    async def execute(self, subscription_id: int) -> list[Visit]:
        return await self._visit_repository.get_by_subscription_id(subscription_id)
