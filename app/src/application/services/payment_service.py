from typing import Sequence
from loguru import logger

from src.application.interfaces.services import IPaymentService
from src.application.interfaces.repositories import IPaymentRepository
from src.domain.entities import Payment
from src.domain.enums import PaymentStatus


class PaymentService(IPaymentService):
    def __init__(self, payment_repository: IPaymentRepository) -> None:
        self._payment_repo = payment_repository
    
    async def get_user_payments(
        self,
        user_id: int,
        status: PaymentStatus | None = None
    ) -> Sequence[Payment]:
        logger.info(f"Getting payments for user_id={user_id}, status={status}")
        return await self._payment_repo.get_user_payments(user_id, status)
    
    async def create_payment(
        self,
        user_id: int,
        amount: float,
        subscription_id: int | None = None,
        currency: str = "KZT",
        method: str | None = None,
        invoice_id: str | None = None,
        airba_payment_id: str | None = None,
        redirect_url: str | None = None,
    ) -> Payment:
        logger.info(f"Creating payment for user_id={user_id}, amount={amount}")
        return await self._payment_repo.create(
            user_id=user_id,
            amount=amount,
            currency=currency,
            subscription_id=subscription_id,
            method=method,
            invoice_id=invoice_id,
            airba_payment_id=airba_payment_id,
            redirect_url=redirect_url,
        )
    
    async def confirm_payment(
        self,
        payment_id: int,
        transaction_id: str,
    ) -> Payment:
        logger.info(f"Confirming payment id={payment_id}")
        payment = await self._payment_repo.get_by_id(payment_id)
        
        if not payment:
            raise ValueError(f"Payment {payment_id} not found")
        
        payment.confirm(transaction_id)
        return await self._payment_repo.update(payment)
    
    async def fail_payment(
        self,
        payment_id: int,
        error_message: str,
    ) -> Payment:
        logger.info(f"Failing payment id={payment_id}")
        payment = await self._payment_repo.get_by_id(payment_id)
        
        if not payment:
            raise ValueError(f"Payment {payment_id} not found")
        
        payment.fail(error_message)
        return await self._payment_repo.update(payment)
