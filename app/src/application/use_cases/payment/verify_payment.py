from src.domain.entities import Payment
from src.domain.interfaces.repositories import IPaymentRepository
from src.domain.interfaces.payment import IPaymentGateway


class VerifyPaymentUseCase:
    def __init__(
        self,
        payment_repository: IPaymentRepository,
        payment_gateway: IPaymentGateway,
    ):
        self._payment_repository = payment_repository
        self._payment_gateway = payment_gateway
    
    async def execute(self, payment_id: int) -> bool:
        payment = await self._payment_repository.get_by_id(payment_id)
        if not payment:
            raise ValueError(f"Payment with id {payment_id} not found")
        
        return await self._payment_gateway.verify_payment(payment)
