from dataclasses import dataclass

from loguru import logger

from src.domain.interfaces.repositories import IPaymentRepository
from src.domain.enums import PaymentStatus


@dataclass
class CancelPaymentResult:
    success: bool
    error_message: str | None = None


class CancelPaymentUseCase:
    def __init__(
        self,
        payment_repository: IPaymentRepository,
    ):
        self._payment_repo = payment_repository

    async def execute(self, payment_id: str) -> CancelPaymentResult:
        logger.info(f"Attempting to cancel payment: {payment_id}")
        
        payment = await self._payment_repo.get_by_payment_id(payment_id)
        
        if not payment:
            logger.warning(f"Payment not found: {payment_id}")
            return CancelPaymentResult(
                success=False,
                error_message="Платеж не найден"
            )
        
        if payment.status == PaymentStatus.SUCCEEDED:
            logger.warning(f"Cannot cancel succeeded payment: {payment_id}")
            return CancelPaymentResult(
                success=False,
                error_message="Нельзя отменить успешный платеж"
            )
        
        if payment.status == PaymentStatus.CANCELLED:
            logger.info(f"Payment already cancelled: {payment_id}")
            return CancelPaymentResult(success=True)
        
        if not payment.is_pending:
            logger.warning(f"Cannot cancel payment with status {payment.status}: {payment_id}")
            return CancelPaymentResult(
                success=False,
                error_message=f"Нельзя отменить платеж со статусом {payment.status.description}"
            )
        
        payment.status = PaymentStatus.CANCELLED
        await self._payment_repo.update(payment)
        
        logger.info(f"Payment cancelled successfully: {payment_id}")
        return CancelPaymentResult(success=True)
