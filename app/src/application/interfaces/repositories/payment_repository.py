from abc import ABC, abstractmethod
from typing import Sequence

from src.domain.entities import Payment, PaymentRefund
from src.domain.enums import PaymentStatus


class IPaymentRepository(ABC):
    @abstractmethod
    async def get_by_id(self, id: int) -> Payment | None:
        pass
    
    @abstractmethod
    async def get_by_transaction_id(self, transaction_id: str) -> Payment | None:
        pass
    
    @abstractmethod
    async def get_user_payments(
        self,
        user_id: int,
        status: PaymentStatus | None = None
    ) -> Sequence[Payment]:
        pass
    
    @abstractmethod
    async def get_pending_payments(self) -> Sequence[Payment]:
        pass
    
    @abstractmethod
    async def create(
        self,
        user_id: int,
        amount: float,
        currency: str = "KZT",
        subscription_id: int | None = None,
        method: str | None = None,
        invoice_id: str | None = None,
        airba_payment_id: str | None = None,
        redirect_url: str | None = None,
    ) -> Payment:
        pass
    
    @abstractmethod
    async def update(self, payment: Payment) -> Payment:
        pass
    
    @abstractmethod
    async def create_refund(
        self,
        payment_id: int,
        amount: float,
        airba_refund_id: str | None = None,
        ext_id: str | None = None,
        reason: str | None = None,
        status: str | None = None,
    ) -> PaymentRefund:
        pass
    
    @abstractmethod
    async def get_payment_refunds(self, payment_id: int) -> Sequence[PaymentRefund]:
        pass
