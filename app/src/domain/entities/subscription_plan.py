from dataclasses import dataclass
from datetime import datetime


@dataclass
class SubscriptionPlan:
    name: str
    duration_months: int
    price: float
    visits_limit: int
    description: str | None = None
    is_active: bool = True
    display_order: int = 0
    id: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

