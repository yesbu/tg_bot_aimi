from dataclasses import dataclass
from datetime import datetime


@dataclass
class AirbaAuthResponse:
    token: str
    expires_at: datetime | None = None


@dataclass
class AirbaPaymentResponse:
    id: str
    invoice_id: str
    redirect_url: str


@dataclass
class AirbaRefund:
    created: datetime
    amount: float
    reason: str | None = None


@dataclass
class AirbaPaymentStatusResponse:
    id: str
    created: datetime
    terminal_id: str
    invoice_id: str
    amount: float
    currency: str
    status: str
    description: str | None = None
    email: str | None = None
    phone: str | None = None
    language: str | None = None
    error_message: str | None = None
    card_id: str | None = None
    success_back_url: str | None = None
    failure_back_url: str | None = None
    success_callback: str | None = None
    failure_callback: str | None = None
    refunds: list[AirbaRefund] | None = None


@dataclass
class AirbaRefundResponse:
    id: str
    ext_id: str | None
    status: str


@dataclass
class AirbaErrorResponse:
    status: str
    code: int
    message: str
