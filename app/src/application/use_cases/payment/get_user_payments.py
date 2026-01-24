from src.domain.entities import Payment
from src.domain.interfaces.repositories import IPaymentRepository, IUserRepository


class GetUserPaymentsUseCase:
    def __init__(
        self,
        payment_repository: IPaymentRepository,
        user_repository: IUserRepository,
    ):
        self._payment_repository = payment_repository
        self._user_repository = user_repository
    
    async def execute(self, telegram_id: int, limit: int = 10) -> list[Payment]:
        user = await self._user_repository.get_by_telegram_id(telegram_id)
        if not user:
            return []
        
        payments = await self._payment_repository.get_by_user_id(
            user_id=user.id,
            limit=limit
        )
        return list(payments)
