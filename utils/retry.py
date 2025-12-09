"""
Утилиты для повторных попыток выполнения операций
"""
import asyncio
import logging
from typing import Callable, Any, Optional
from functools import wraps

logger = logging.getLogger(__name__)


async def retry_async(
    func: Callable,
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,),
    on_retry: Optional[Callable] = None
) -> Any:
    """
    Повторная попытка выполнения асинхронной функции
    
    Args:
        func: Асинхронная функция для выполнения
        max_attempts: Максимальное количество попыток
        delay: Начальная задержка между попытками (в секундах)
        backoff: Множитель для увеличения задержки
        exceptions: Кортеж исключений, при которых нужно повторять
        on_retry: Функция, вызываемая при каждой повторной попытке
    """
    last_exception = None
    current_delay = delay
    
    for attempt in range(1, max_attempts + 1):
        try:
            return await func()
        except exceptions as e:
            last_exception = e
            if attempt < max_attempts:
                if on_retry:
                    on_retry(attempt, e)
                logger.warning(
                    f"Попытка {attempt}/{max_attempts} не удалась: {e}. "
                    f"Повтор через {current_delay:.1f} сек..."
                )
                await asyncio.sleep(current_delay)
                current_delay *= backoff
            else:
                logger.error(f"Все {max_attempts} попыток не удались. Последняя ошибка: {e}")
    
    raise last_exception


def retry(max_attempts: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """Декоратор для повторных попыток выполнения функций"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            async def attempt():
                return await func(*args, **kwargs)
            
            return await retry_async(
                attempt,
                max_attempts=max_attempts,
                delay=delay,
                backoff=backoff
            )
        
        return wrapper
    return decorator

