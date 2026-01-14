from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Update
from loguru import logger


class ErrorHandlerMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        try:
            return await handler(event, data)
        except Exception as e:
            logger.error(f"Error handling update: {e}", exc_info=True)
            
            if isinstance(event, Update):
                if event.message:
                    try:
                        await event.message.answer(
                            "❌ Произошла ошибка при обработке команды.\n\n"
                            "Попробуйте ещё раз или обратитесь в поддержку."
                        )
                    except Exception:
                        pass
                elif event.callback_query:
                    try:
                        await event.callback_query.answer(
                            "❌ Произошла ошибка",
                            show_alert=True
                        )
                    except Exception:
                        pass
            
            raise
