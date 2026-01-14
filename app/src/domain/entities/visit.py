from dataclasses import dataclass
from datetime import datetime


@dataclass
class Visit:
    subscription_id: int
    user_id: int
    center_id: int
    child_id: int | None = None
    lesson_id: int | None = None
    id: int | None = None
    visited_at: datetime | None = None
    
    def __post_init__(self):
        if self.visited_at is None:
            self.visited_at = datetime.utcnow()
