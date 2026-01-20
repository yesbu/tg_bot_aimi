from src.domain.entities import Payment
from src.domain.enums import PaymentStatus
from src.domain.interfaces.repositories import IPaymentRepository


class CreatePaymentUseCase:
    def __init__(self, payment_repository: IPaymentRepository):
        self._payment_repository = payment_repository
    
    async def execute(
        self,
        user_id: int,
        amount: float,
        subscription_id: int | None = None,
    ) -> Payment:
        payment = Payment(
            user_id=user_id,
            amount=amount,
            subscription_id=subscription_id,
            status=PaymentStatus.PENDING,
        )
        
        return await self._payment_repository.create(payment)
