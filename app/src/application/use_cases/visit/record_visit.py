from datetime import datetime

from src.domain.entities import Visit
from src.domain.interfaces.repositories import IVisitRepository


class RecordVisitUseCase:
    def __init__(self, visit_repository: IVisitRepository):
        self._visit_repository = visit_repository
    
    async def execute(
        self,
        subscription_id: int,
        visit_date: datetime | None = None,
    ) -> Visit:
        visit = Visit(
            subscription_id=subscription_id,
            visit_date=visit_date or datetime.now(),
        )
        
        return await self._visit_repository.create(visit)
