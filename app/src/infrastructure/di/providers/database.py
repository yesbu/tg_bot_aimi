from typing import AsyncIterable
from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.infrastructure.persistence.database import DatabaseManager


class DatabaseProvider(Provider):
    @provide(scope=Scope.APP)
    def provide_database_manager(self) -> DatabaseManager:
        return DatabaseManager()
    
    @provide(scope=Scope.APP)
    async def provide_session_factory(
        self, db_manager: DatabaseManager
    ) -> async_sessionmaker[AsyncSession]:
        return db_manager.get_session_factory()
    
    @provide(scope=Scope.REQUEST)
    async def provide_session(
        self, session_factory: async_sessionmaker[AsyncSession]
    ) -> AsyncIterable[AsyncSession]:
        async with session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
