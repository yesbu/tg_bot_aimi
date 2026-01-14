from .user import command_router as user_command_router
from .user import message_router as user_message_router
from .user import query_router as user_query_router

from .parent import command_router as parent_command_router
from .parent import message_router as parent_message_router
from .parent import query_router as parent_query_router
from .child import command_router as child_command_router
from .child import message_router as child_message_router
from .partner import command_router as partner_command_router
from .partner import message_router as partner_message_router
from .partner import query_router as partner_query_router
from .admin import command_router as admin_command_router
from .admin import message_router as admin_message_router
from .admin import query_router as admin_query_router


__all__ = [
    "user_command_router",
    "user_message_router",
    "user_query_router",
    "parent_command_router",
    "parent_message_router",
    "parent_query_router",
    "child_command_router",
    "child_message_router",
    "partner_command_router",
    "partner_message_router",
    "partner_query_router",
    "admin_command_router",
    "admin_message_router",
    "admin_query_router",
]
