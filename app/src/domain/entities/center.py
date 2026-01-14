from dataclasses import dataclass
from datetime import datetime

from src.domain.enums import CenterStatus


@dataclass
class Center:
    partner_id: int
    name: str
    city: str
    status: CenterStatus = CenterStatus.PENDING
    address: str | None = None
    phone: str | None = None
    category: str | None = None
    description: str | None = None
    logo: str | None = None
    id: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    
    def __post_init__(self):
        self.validate()
    
    def validate(self) -> None:
        if not self.name or len(self.name.strip()) == 0:
            raise ValueError("Center name cannot be empty")
        
        if not self.city or len(self.city.strip()) == 0:
            raise ValueError("Center city cannot be empty")
    
    @property
    def is_approved(self) -> bool:
        return self.status == CenterStatus.APPROVED
    
    @property
    def is_pending(self) -> bool:
        return self.status == CenterStatus.PENDING
    
    @property
    def is_rejected(self) -> bool:
        return self.status == CenterStatus.REJECTED
    
    def approve(self) -> None:
        if self.status == CenterStatus.APPROVED:
            return
        self.status = CenterStatus.APPROVED
    
    def reject(self) -> None:
        if self.status == CenterStatus.REJECTED:
            return
        self.status = CenterStatus.REJECTED
    
    def update_info(
        self,
        name: str | None = None,
        address: str | None = None,
        phone: str | None = None,
        description: str | None = None,
        logo: str | None = None,
    ) -> None:
        if name:
            if len(name.strip()) == 0:
                raise ValueError("Center name cannot be empty")
            self.name = name
        if address:
            self.address = address
        if phone:
            self.phone = phone
        if description:
            self.description = description
        if logo:
            self.logo = logo
