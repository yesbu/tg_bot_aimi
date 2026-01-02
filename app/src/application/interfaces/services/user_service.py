from abc import ABC, abstractmethod

from src.domain.entities import User
from src.domain.enums import Role


class IUserService(ABC):
    @abstractmethod
    async def get_or_create_user(
        self,
        telegram_id: int,
        username: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
    ) -> User:
        pass
    
    @abstractmethod
    async def get_user_by_telegram_id(self, telegram_id: int) -> User | None:
        pass
    
    @abstractmethod
    async def update_user_role(self, telegram_id: int, role: Role) -> User:
        pass
    
    @abstractmethod
    async def update_user_city(self, telegram_id: int, city: str) -> User:
        pass
    
    @abstractmethod
    async def user_exists(self, telegram_id: int) -> bool:
        pass
