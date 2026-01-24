from abc import ABC, abstractmethod
from typing import Sequence

from src.domain.entities import Payment
from src.domain.enums import PaymentStatus


class IPaymentRepository(ABC):
    @abstractmethod
    async def get_by_id(self, id: int) -> Payment | None:
        pass
    
    @abstractmethod
    async def get_by_payment_id(self, payment_id: str) -> Payment | None:
        pass
    
    @abstractmethod
    async def get_by_invoice_id(self, invoice_id: str) -> Payment | None:
        pass
    
    @abstractmethod
    async def get_by_user_id(
        self,
        user_id: int,
        limit: int | None = None,
        offset: int | None = None,
    ) -> Sequence[Payment]:
        pass
    
    @abstractmethod
    async def get_by_status(
        self,
        status: PaymentStatus,
        limit: int | None = None,
        offset: int | None = None,
    ) -> Sequence[Payment]:
        pass
    
    @abstractmethod
    async def create(
        self,
        user_id: int,
        amount: float,
        currency: str,
        status: PaymentStatus = PaymentStatus.NEW,
        payment_id: str | None = None,
        invoice_id: str | None = None,
    ) -> Payment:
        pass
    
    @abstractmethod
    async def update(self, payment: Payment) -> Payment:
        pass
    
    @abstractmethod
    async def exists_by_payment_id(self, payment_id: str) -> bool:
        pass
