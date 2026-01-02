from dataclasses import dataclass
from datetime import datetime


@dataclass
class Child:
    parent_id: int
    name: str
    age: int
    id: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    
    def __post_init__(self):
        self.validate()
    
    def validate(self) -> None:
        if self.age < 0 or self.age > 18:
            raise ValueError("Child age must be between 0 and 18")
        
        if not self.name or len(self.name.strip()) == 0:
            raise ValueError("Child name cannot be empty")
    
    def update_age(self, new_age: int) -> None:
        if new_age < 0 or new_age > 18:
            raise ValueError("Child age must be between 0 and 18")
        self.age = new_age
    
    def update_name(self, new_name: str) -> None:
        if not new_name or len(new_name.strip()) == 0:
            raise ValueError("Child name cannot be empty")
        self.name = new_name
