from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Update
from loguru import logger


class LoggingMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        if isinstance(event, Update):
            if event.message:
                user_id = event.message.from_user.id if event.message.from_user else None
                text = event.message.text or event.message.caption or "<non-text>"
                logger.info(f"Message from user {user_id}: {text[:50]}")
            elif event.callback_query:
                user_id = event.callback_query.from_user.id if event.callback_query.from_user else None
                callback_data = event.callback_query.data
                logger.info(f"Callback from user {user_id}: {callback_data}")
        
        return await handler(event, data)
