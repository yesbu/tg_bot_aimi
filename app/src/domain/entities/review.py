from dataclasses import dataclass
from datetime import datetime


@dataclass
class Review:
    course_id: int
    user_id: int
    rating: int
    comment: str | None = None
    id: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    
    def __post_init__(self):
        self.validate()
    
    def validate(self) -> None:
        if self.rating < 1 or self.rating > 5:
            raise ValueError("Rating must be between 1 and 5")
    
    def update_rating(self, new_rating: int) -> None:
        if new_rating < 1 or new_rating > 5:
            raise ValueError("Rating must be between 1 and 5")
        self.rating = new_rating
    
    def update_comment(self, new_comment: str) -> None:
        self.comment = new_comment
