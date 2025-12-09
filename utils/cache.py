"""
Простое кэширование для оптимизации запросов
"""
import asyncio
from typing import Any, Optional, Dict
from datetime import datetime, timedelta
from functools import wraps

logger = None
try:
    import logging
    logger = logging.getLogger(__name__)
except:
    pass


class SimpleCache:
    """Простой кэш с TTL"""
    
    def __init__(self, default_ttl: int = 300):
        self.cache: Dict[str, tuple[Any, datetime]] = {}
        self.default_ttl = default_ttl
        self._lock = asyncio.Lock()
    
    async def get(self, key: str) -> Optional[Any]:
        """Получить значение из кэша"""
        async with self._lock:
            if key not in self.cache:
                return None
            
            value, expiry = self.cache[key]
            
            if datetime.now() > expiry:
                del self.cache[key]
                return None
            
            return value
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Установить значение в кэш"""
        async with self._lock:
            ttl = ttl or self.default_ttl
            expiry = datetime.now() + timedelta(seconds=ttl)
            self.cache[key] = (value, expiry)
    
    async def delete(self, key: str):
        """Удалить значение из кэша"""
        async with self._lock:
            if key in self.cache:
                del self.cache[key]
    
    async def clear(self):
        """Очистить весь кэш"""
        async with self._lock:
            self.cache.clear()
    
    async def cleanup(self):
        """Очистить истекшие записи"""
        async with self._lock:
            now = datetime.now()
            expired_keys = [
                key for key, (_, expiry) in self.cache.items()
                if now > expiry
            ]
            for key in expired_keys:
                del self.cache[key]


# Глобальный экземпляр кэша
cache = SimpleCache(default_ttl=300)


def cached(ttl: int = 300):
    """Декоратор для кэширования результатов функций"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Создаем ключ кэша из аргументов
            cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            
            # Пытаемся получить из кэша
            cached_value = await cache.get(cache_key)
            if cached_value is not None:
                return cached_value
            
            # Выполняем функцию
            result = await func(*args, **kwargs)
            
            # Сохраняем в кэш
            await cache.set(cache_key, result, ttl)
            
            return result
        
        return wrapper
    return decorator

