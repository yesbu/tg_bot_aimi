from dataclasses import dataclass
from datetime import datetime


@dataclass
class Course:
    center_id: int
    name: str
    description: str | None = None
    category: str | None = None
    age_min: int | None = None
    age_max: int | None = None
    requirements: str | None = None
    schedule: str | None = None
    rating: float = 0.0
    price_4: int | None = None
    price_8: int | None = None
    price_unlimited: int | None = None
    photo: str | None = None
    id: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    
    def __post_init__(self):
        self.validate()
    
    def validate(self) -> None:
        if not self.name or len(self.name.strip()) == 0:
            raise ValueError("Course name cannot be empty")
        
        if self.age_min is not None and self.age_min < 0:
            raise ValueError("Minimum age cannot be negative")
        
        if self.age_max is not None and self.age_max < 0:
            raise ValueError("Maximum age cannot be negative")
        
        if self.age_min is not None and self.age_max is not None:
            if self.age_min > self.age_max:
                raise ValueError("Minimum age cannot be greater than maximum age")
        
        if self.rating < 0 or self.rating > 5:
            raise ValueError("Rating must be between 0 and 5")
    
    def is_suitable_for_age(self, age: int) -> bool:
        if self.age_min is not None and age < self.age_min:
            return False
        if self.age_max is not None and age > self.age_max:
            return False
        return True
    
    def update_rating(self, new_rating: float) -> None:
        if new_rating < 0 or new_rating > 5:
            raise ValueError("Rating must be between 0 and 5")
        self.rating = round(new_rating, 1)
    
    def update_prices(
        self,
        price_4: int | None = None,
        price_8: int | None = None,
        price_unlimited: int | None = None,
    ) -> None:
        if price_4 is not None:
            if price_4 < 0:
                raise ValueError("Price cannot be negative")
            self.price_4 = price_4
        
        if price_8 is not None:
            if price_8 < 0:
                raise ValueError("Price cannot be negative")
            self.price_8 = price_8
        
        if price_unlimited is not None:
            if price_unlimited < 0:
                raise ValueError("Price cannot be negative")
            self.price_unlimited = price_unlimited
