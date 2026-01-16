from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, TelegramObject

from src.domain.enums import Role
from dishka.integrations.aiogram import CONTAINER_NAME
from src.application.interfaces.services import IUserService


class RoleFilterMiddleware(BaseMiddleware):
    def __init__(self, allowed_roles: list[Role]):
        self.allowed_roles = allowed_roles
        super().__init__()
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:

        container = data.get(CONTAINER_NAME)
        if not container:
            return await handler(event, data)
        
        if isinstance(event, (Message, CallbackQuery)):
            telegram_id = event.from_user.id
            
            async with container() as request_container:
                user_service = await request_container.get(IUserService)
                user = await user_service.get_user_by_telegram_id(telegram_id)
                
                if user and user.role in self.allowed_roles:
                    return await handler(event, data)
        
        return None
