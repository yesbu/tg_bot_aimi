from .command import router as command_router
from .message import router as message_router
from src.presentation.bot.filters import RoleFilter
from src.domain.enums import Role

_filter = RoleFilter(Role.CHILD)

command_router.message.filter(_filter)
message_router.message.filter(_filter)


__all__ = ["command_router", "message_router"]
