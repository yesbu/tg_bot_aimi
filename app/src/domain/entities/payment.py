from dataclasses import dataclass
from datetime import datetime

from src.domain.enums import PaymentStatus


@dataclass
class Payment:
    user_id: int
    amount: float
    currency: str
    status: PaymentStatus
    payment_id: str | None = None
    invoice_id: str | None = None
    id: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    
    @property
    def is_successful(self) -> bool:
        return self.status == PaymentStatus.SUCCEEDED
    
    @property
    def is_pending(self) -> bool:
        return self.status in (PaymentStatus.NEW, PaymentStatus.PENDING, PaymentStatus.PROCESSING)
    
    @property
    def is_failed(self) -> bool:
        return self.status in (PaymentStatus.FAILED, PaymentStatus.CANCELLED)
    
    @property
    def can_be_refunded(self) -> bool:
        return self.status == PaymentStatus.SUCCEEDED
    
    def mark_as_succeeded(self) -> None:
        if self.is_successful:
            return
        self.status = PaymentStatus.SUCCEEDED
    
    def mark_as_failed(self) -> None:
        if self.is_failed:
            return
        self.status = PaymentStatus.FAILED
    
    def mark_as_refunded(self) -> None:
        if not self.can_be_refunded:
            raise ValueError("Only succeeded payments can be refunded")
        self.status = PaymentStatus.REFUNDED
    
    def update_external_ids(
        self,
        payment_id: str | None = None,
        invoice_id: str | None = None,
    ) -> None:
        if payment_id:
            self.payment_id = payment_id
        if invoice_id:
            self.invoice_id = invoice_id
