from abc import ABC, abstractmethod
from typing import Any


class ICacheClient(ABC):
    @abstractmethod
    async def get(self, key: str) -> Any | None:
        pass
    
    @abstractmethod
    async def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> bool:
        pass
    
    @abstractmethod
    async def exists(self, key: str) -> bool:
        pass
