from dataclasses import dataclass, field
from datetime import datetime

from src.domain.enums import Role


@dataclass
class User:
    telegram_id: int
    role: Role = Role.USER
    username: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    phone: str | None = None
    city: str | None = None
    id: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    is_deleted: bool = False
    
    @property
    def full_name(self) -> str:
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.first_name or self.username or f"User {self.telegram_id}"
    
    @property
    def is_parent(self) -> bool:
        return self.role == Role.PARENT
    
    @property
    def is_partner(self) -> bool:
        return self.role == Role.PARTNER
    
    @property
    def is_admin(self) -> bool:
        return self.role == Role.ADMIN
    
    def change_role(self, new_role: Role) -> None:
        if self.role == new_role:
            return
        self.role = new_role
    
    def update_city(self, city: str) -> None:
        self.city = city
    
    def update_contact_info(
        self,
        phone: str | None = None,
        username: str | None = None,
    ) -> None:
        if phone:
            self.phone = phone
        if username:
            self.username = username
