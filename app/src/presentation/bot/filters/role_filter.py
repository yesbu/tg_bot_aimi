from aiogram.filters import Filter
from aiogram.types import Message
from dishka import FromDishka

from src.application.interfaces.services import IUserService


class RoleFilter(Filter):
    def __init__(self, role: str):
        self.role = role
    
    async def __call__(
        self, 
        message: Message,
        user_service: FromDishka[IUserService]
    ) -> bool:
        user = await user_service.get_user_by_telegram_id(message.from_user.id)
        if not user:
            return False
        return user.role == self.role
