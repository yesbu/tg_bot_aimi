from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager

from src.infrastructure.persistence.database import db_manager


@asynccontextmanager
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async for session in db_manager.get_session():
        yield session


async def provide_session() -> AsyncGenerator[AsyncSession, None]:
    async for session in db_manager.get_session():
        yield session
