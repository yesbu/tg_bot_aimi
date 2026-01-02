from dataclasses import dataclass
from datetime import datetime

from src.domain.enums import PaymentStatus


@dataclass
class Payment:
    user_id: int
    amount: float
    currency: str = "KZT"
    subscription_id: int | None = None
    method: str | None = None
    status: PaymentStatus = PaymentStatus.PENDING
    transaction_id: str | None = None
    invoice_id: str | None = None
    airba_payment_id: str | None = None
    redirect_url: str | None = None
    error_message: str | None = None
    id: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    processed_at: datetime | None = None
    
    def __post_init__(self):
        self.validate()
    
    def validate(self) -> None:
        if self.amount <= 0:
            raise ValueError("Payment amount must be positive")
        
        if not self.currency or len(self.currency.strip()) == 0:
            raise ValueError("Currency cannot be empty")
    
    @property
    def is_pending(self) -> bool:
        return self.status == PaymentStatus.PENDING
    
    @property
    def is_success(self) -> bool:
        return self.status == PaymentStatus.SUCCESS
    
    @property
    def is_failed(self) -> bool:
        return self.status == PaymentStatus.FAILED
    
    @property
    def is_refunded(self) -> bool:
        return self.status == PaymentStatus.REFUNDED
    
    def confirm(self, transaction_id: str) -> None:
        if self.status != PaymentStatus.PENDING:
            raise ValueError("Can only confirm pending payments")
        
        self.status = PaymentStatus.SUCCESS
        self.transaction_id = transaction_id
        self.processed_at = datetime.utcnow()
    
    def fail(self, error_message: str) -> None:
        if self.status != PaymentStatus.PENDING:
            raise ValueError("Can only fail pending payments")
        
        self.status = PaymentStatus.FAILED
        self.error_message = error_message
        self.processed_at = datetime.utcnow()
    
    def refund(self) -> None:
        if self.status != PaymentStatus.SUCCESS:
            raise ValueError("Can only refund successful payments")
        
        self.status = PaymentStatus.REFUNDED


@dataclass
class PaymentRefund:
    payment_id: int
    amount: float
    airba_refund_id: str | None = None
    ext_id: str | None = None
    reason: str | None = None
    status: str | None = None
    id: int | None = None
    processed_at: datetime | None = None
    
    def __post_init__(self):
        self.validate()
    
    def validate(self) -> None:
        if self.amount <= 0:
            raise ValueError("Refund amount must be positive")
