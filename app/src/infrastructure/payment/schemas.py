from datetime import datetime
from typing import Optional
from narwhals import Decimal
from pydantic import BaseModel, Field
from src.infrastructure.payment.status import PaymentStatusEnum


class RefundData(BaseModel):
    created: datetime
    amount: Decimal
    reason: Optional[str] = None

class PaymentStatusResponseSchema(BaseModel):
    id: str
    created: datetime
    terminal_id: str
    invoice_id: str
    amount: Decimal
    currency: str
    description: str
    email: str
    phone: str
    language: str
    status: PaymentStatusEnum
    error_message: str
    card_id: str
    success_back_url: str
    failure_back_url: str
    success_callback: str
    failure_callback: str
    refunds: Optional[RefundData] = None