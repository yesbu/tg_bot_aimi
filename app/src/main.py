import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from dishka.integrations.aiogram import setup_dishka
from loguru import logger

from src.settings import settings
from src.infrastructure.di import create_container
from src.presentation.bot.handlers import (
    user_command_router,
    user_message_router,
    user_query_router,
    parent_command_router,
    parent_message_router,
    parent_query_router,
    child_command_router,
    child_message_router,
    partner_command_router,
    partner_message_router,
    partner_query_router,
    admin_command_router,
    admin_message_router,
    admin_query_router
)
from src.presentation.bot.middleware import ErrorHandlerMiddleware, LoggingMiddleware, RoleFilterMiddleware
from src.domain.enums import Role


async def on_startup():
    logger.info("Starting bot...")


async def on_shutdown():
    logger.info("Shutting down bot...")


async def main():
    logger.add(
        "logs/bot.log",
        rotation="10 MB",
        retention="7 days",
        compression="zip",
        level="INFO",
    )
    
    logger.info("Initializing bot...")
    
    bot = Bot(
        token=settings.telegram.TELEGRAM_BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    
    dp = Dispatcher()
    
    dp.message.middleware(LoggingMiddleware())
    dp.callback_query.middleware(LoggingMiddleware())
    
    dp.message.middleware(ErrorHandlerMiddleware())
    dp.callback_query.middleware(ErrorHandlerMiddleware())
    
    container = create_container()
    setup_dishka(container, dp, auto_inject=True)
    
    user_command_router.message.middleware(RoleFilterMiddleware([Role.USER]))
    user_message_router.message.middleware(RoleFilterMiddleware([Role.USER]))
    user_query_router.callback_query.middleware(RoleFilterMiddleware([Role.USER]))
    
    parent_command_router.message.middleware(RoleFilterMiddleware([Role.PARENT]))
    parent_message_router.message.middleware(RoleFilterMiddleware([Role.PARENT]))
    parent_query_router.callback_query.middleware(RoleFilterMiddleware([Role.PARENT]))
    
    child_command_router.message.middleware(RoleFilterMiddleware([Role.CHILD]))
    child_message_router.message.middleware(RoleFilterMiddleware([Role.CHILD]))
    
    partner_command_router.message.middleware(RoleFilterMiddleware([Role.PARTNER]))
    partner_message_router.message.middleware(RoleFilterMiddleware([Role.PARTNER]))
    partner_query_router.callback_query.middleware(RoleFilterMiddleware([Role.PARTNER]))
    
    admin_command_router.message.middleware(RoleFilterMiddleware([Role.ADMIN]))
    admin_message_router.message.middleware(RoleFilterMiddleware([Role.ADMIN]))
    admin_query_router.callback_query.middleware(RoleFilterMiddleware([Role.ADMIN]))
    
    dp.include_router(user_command_router)
    dp.include_router(user_message_router)
    dp.include_router(user_query_router)
    dp.include_router(parent_command_router)
    dp.include_router(parent_message_router)
    dp.include_router(parent_query_router)
    dp.include_router(child_command_router)
    dp.include_router(child_message_router)
    dp.include_router(partner_command_router)
    dp.include_router(partner_message_router)
    dp.include_router(partner_query_router)
    dp.include_router(admin_command_router)
    dp.include_router(admin_message_router)
    dp.include_router(admin_query_router)
    
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    
    logger.info("Starting polling...")
    
    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await container.close()
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")

