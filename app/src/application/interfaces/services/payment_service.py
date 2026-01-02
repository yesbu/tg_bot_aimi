from abc import ABC, abstractmethod
from typing import Sequence

from src.domain.entities import Payment
from src.domain.enums import PaymentStatus


class IPaymentService(ABC):
    @abstractmethod
    async def get_user_payments(
        self,
        user_id: int,
        status: PaymentStatus | None = None
    ) -> Sequence[Payment]:
        pass
    
    @abstractmethod
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
        pass
    
    @abstractmethod
    async def confirm_payment(
        self,
        payment_id: int,
        transaction_id: str,
    ) -> Payment:
        pass
    
    @abstractmethod
    async def fail_payment(
        self,
        payment_id: int,
        error_message: str,
    ) -> Payment:
        pass
