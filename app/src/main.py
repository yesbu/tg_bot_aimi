import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from dishka.integrations.aiogram import setup_dishka
from loguru import logger

from src.settings import settings
from src.infrastructure.di import create_container
from src.presentation.handlers import command_router


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
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    
    dp = Dispatcher()
    
    container = create_container()
    setup_dishka(container, dp, auto_inject=True)
    
    dp.include_router(command_router)
    
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
