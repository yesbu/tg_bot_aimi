from .command import router as command_router
from .message import router as message_router
from .query import router as query_router


__all__ = ["command_router", "message_router", "query_router"]
