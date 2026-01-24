import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config
from loguru import logger
from alembic import context
import sys

from src.infrastructure.persistence.models.base import Base
from src.infrastructure.persistence.models import *
from src.settings import settings

config = context.config
target_metadata = Base.metadata

logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="INFO",
)


def run_migrations_offline() -> None:
    context.configure(
        url=settings.database.URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
        render_as_batch=True,
    )

    logger.info("Running migrations in offline mode")
    with context.begin_transaction():
        context.run_migrations()
    logger.info("Offline migrations completed successfully")


def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
        render_as_batch=True,
        include_schemas=True,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = settings.database.URL

    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    logger.info(f"Connecting to database: {settings.database.POSTGRES_HOST}:{settings.database.POSTGRES_PORT}/{settings.database.POSTGRES_DB}")

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()
    logger.info("Async migrations completed successfully")


def run_migrations_online() -> None:
    logger.info("Running migrations in online mode")
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()