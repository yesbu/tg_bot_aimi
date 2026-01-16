from .command import router as command_router
from .message import router as message_router
from .query import router as query_router
from src.presentation.bot.middleware import RoleMiddleware
from src.domain.enums import Role

_middleware = RoleMiddleware(allowed_roles=[Role.PARENT], allow_new_users=False)

command_router.message.middleware(_middleware)
message_router.message.middleware(_middleware)
query_router.callback_query.middleware(_middleware)


__all__ = ["command_router", "message_router", "query_router"]
