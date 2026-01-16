from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery
from loguru import logger

from src.domain.enums import Role
from src.application.interfaces.services import IUserService


class RoleMiddleware(BaseMiddleware):
    def __init__(self, allowed_roles: list[Role], allow_new_users: bool = False):
        self.allowed_roles = allowed_roles
        self.allow_new_users = allow_new_users

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        telegram_id = self._get_telegram_id(event)

        if telegram_id is None:
            logger.warning("Could not extract telegram_id from event")
            return None

        container = data.get("dishka_container")
        if container is None:
            logger.error("Dishka container not found in middleware data")
            return await handler(event, data)

        user_service: IUserService = await container.get(IUserService)
        user = await user_service.get_user_by_telegram_id(telegram_id)

        if user is None:
            if self.allow_new_users:
                logger.debug(f"New user {telegram_id} allowed (allow_new_users=True)")
                return await handler(event, data)
            else:
                logger.debug(f"New user {telegram_id} blocked (allow_new_users=False)")
                return None

        if user.role in self.allowed_roles:
            logger.debug(f"User {telegram_id} with role {user.role} allowed")
            return await handler(event, data)

        logger.debug(f"User {telegram_id} with role {user.role} blocked (allowed: {self.allowed_roles})")
        return None

    def _get_telegram_id(self, event: TelegramObject) -> int | None:
        if isinstance(event, Message):
            return event.from_user.id if event.from_user else None
        elif isinstance(event, CallbackQuery):
            return event.from_user.id if event.from_user else None
        return None
