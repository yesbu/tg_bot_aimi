"""
Middleware для логирования действий пользователей
"""
import logging
import sys
from typing import Callable, Dict, Any, Awaitable
from datetime import datetime

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery

logger = logging.getLogger(__name__)


def safe_log(log_func, message: str):
    """Безопасное логирование с обработкой ошибок кодировки"""
    try:
        log_func(message)
    except UnicodeEncodeError:
        # Если не удается закодировать (например, эмодзи в Windows cp1251),
        # заменяем проблемные символы на безопасные
        try:
            safe_message = message.encode('ascii', errors='replace').decode('ascii')
            log_func(safe_message)
        except Exception:
            # В крайнем случае логируем без эмодзи
            clean_message = message.encode('utf-8', errors='ignore').decode('utf-8', errors='ignore')
            log_func(clean_message)


class LoggingMiddleware(BaseMiddleware):
    """Middleware для логирования всех действий"""
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        # Логируем входящее обновление
        if isinstance(event, Message):
            user_id = event.from_user.id if event.from_user else 0
            username = event.from_user.username if event.from_user and event.from_user.username else "Нет username"
            text = event.text or event.caption or "[Медиа]"
            
            message = f"📨 Сообщение от {user_id} (@{username}): {text[:100]}"
            safe_log(logger.info, message)
        
        elif isinstance(event, CallbackQuery):
            user_id = event.from_user.id if event.from_user else 0
            username = event.from_user.username if event.from_user and event.from_user.username else "Нет username"
            data_text = event.data or "Нет data"
            
            message = f"🔘 Callback от {user_id} (@{username}): {data_text}"
            safe_log(logger.info, message)
        
        # Выполняем handler
        result = await handler(event, data)
        
        return result
