from typing import Any
from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery, TelegramObject
from loguru import logger

from src.domain.enums import Role
from src.application.interfaces.services import IUserService


class RoleFilter(BaseFilter):
    def __init__(self, *allowed_roles: Role, allow_new_users: bool = False):
        self.allowed_roles = allowed_roles
        self.allow_new_users = allow_new_users

    async def __call__(
        self,
        event: TelegramObject,
        **kwargs: Any,
    ) -> bool:
        telegram_id = self._get_telegram_id(event)

        container = kwargs.get("dishka_container")
        if container is None:
            logger.error("Dishka container not found in filter kwargs")
            return False

        user_service: IUserService = await container.get(IUserService)

        if telegram_id is None:
            logger.warning("Could not extract telegram_id from event")
            return False

        user = await user_service.get_user_by_telegram_id(telegram_id)

        if user is None:
            if self.allow_new_users:
                logger.debug(f"New user {telegram_id} allowed (allow_new_users=True)")
                return True
            else:
                logger.debug(f"New user {telegram_id} rejected (allow_new_users=False)")
                return False

        if user.role in self.allowed_roles:
            logger.debug(f"User {telegram_id} with role {user.role} allowed")
            return True

        logger.debug(
            f"User {telegram_id} with role {user.role} rejected "
            f"(allowed: {self.allowed_roles})"
        )
        return False

    def _get_telegram_id(self, event: TelegramObject) -> int | None:
        if isinstance(event, Message):
            return event.from_user.id if event.from_user else None
        elif isinstance(event, CallbackQuery):
            return event.from_user.id if event.from_user else None
        return None
