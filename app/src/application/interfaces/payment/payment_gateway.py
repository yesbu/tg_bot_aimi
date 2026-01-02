from abc import ABC, abstractmethod
from typing import Any


class IPaymentGateway(ABC):
    @abstractmethod
    async def create_payment(
        self,
        invoice_id: str,
        amount: float,
        currency: str,
        account_id: str,
        phone: str | None = None,
        email: str | None = None,
        description: str | None = None,
        success_callback: str | None = None,
        failure_callback: str | None = None,
        auto_charge: bool = True,
        card_save: bool = False,
    ) -> dict[str, Any]:
        pass
    
    @abstractmethod
    async def get_payment_status(self, payment_id: str) -> dict[str, Any]:
        pass
    
    @abstractmethod
    async def refund_payment(
        self,
        payment_id: str,
        amount: float | None = None,
        reason: str | None = None,
    ) -> dict[str, Any]:
        pass
    
    @abstractmethod
    async def close(self) -> None:
        pass
