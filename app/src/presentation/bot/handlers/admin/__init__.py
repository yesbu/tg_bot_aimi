from .command import router as command_router
from .message import router as message_router
from .query import router as query_router
from src.presentation.bot.filters import RoleFilter
from src.domain.enums import Role

_filter = RoleFilter(Role.ADMIN)

command_router.message.filter(_filter)
message_router.message.filter(_filter)
query_router.callback_query.filter(_filter)


__all__ = ["command_router", "message_router", "query_router"]
