from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, TelegramObject
from dishka.integrations.aiogram import CONTAINER_NAME

from src.application.interfaces.services import IUserService
from src.domain.enums import Role


class RoleFilterMiddleware(BaseMiddleware):
    def __init__(self, allowed_role: Role):
        self.allowed_role = allowed_role
        super().__init__()
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        container = data.get(CONTAINER_NAME)
        if not container:
            return None
        
        if isinstance(event, (Message, CallbackQuery)):
            telegram_id = event.from_user.id
            
            async with container() as request_container:
                user_service = await request_container.get(IUserService)
                user = await user_service.get_user_by_telegram_id(telegram_id)
                
                if user and user.role == self.allowed_role:
                    return await handler(event, data)
        
        return None
