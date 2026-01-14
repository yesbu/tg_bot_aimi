from abc import ABC, abstractmethod
from typing import Sequence

from src.domain.entities import User
from src.domain.enums import Role


class IUserRepository(ABC):
    @abstractmethod
    async def get_by_id(self, id: int) -> User | None:
        pass
    
    @abstractmethod
    async def get_by_telegram_id(self, telegram_id: int) -> User | None:
        pass
    
    @abstractmethod
    async def create(
        self,
        telegram_id: int,
        role: Role = Role.USER,
        username: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
    ) -> User:
        pass
    
    @abstractmethod
    async def update(self, user: User) -> User:
        pass
    
    @abstractmethod
    async def get_all(self, limit: int | None = None, offset: int | None = None) -> Sequence[User]:
        pass
    
    @abstractmethod
    async def exists_by_telegram_id(self, telegram_id: int) -> bool:
        pass
