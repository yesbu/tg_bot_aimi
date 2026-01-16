from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, TelegramObject
from dishka import FromDishka

from src.application.interfaces.services import IUserService
from src.domain.enums import Role


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
        user_service: IUserService = data.get("user_service")
        
        if isinstance(event, (Message, CallbackQuery)):
            telegram_id = event.from_user.id
            user = await user_service.get_user_by_telegram_id(telegram_id)
            
            if user and user.role in self.allowed_roles:
                return await handler(event, data)
        
        return None
