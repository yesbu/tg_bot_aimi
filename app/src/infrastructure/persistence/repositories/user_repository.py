from typing import Sequence
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from src.application.interfaces.repositories import IUserRepository
from src.domain.entities import User
from src.infrastructure.persistence.models.user import User as UserModel
from src.infrastructure.persistence.mappers import UserMapper
from src.domain.enums import Role


class UserRepository(IUserRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
    
    async def get_by_id(self, id: int) -> User | None:
        logger.debug(f"Getting user by id={id}")
        result = await self._session.execute(
            select(UserModel).where(UserModel.id == id)
        )
        model = result.scalar_one_or_none()
        return UserMapper.to_entity(model) if model else None
    
    async def get_by_telegram_id(self, telegram_id: int) -> User | None:
        logger.debug(f"Getting user by telegram_id={telegram_id}")
        result = await self._session.execute(
            select(UserModel).where(UserModel.telegram_id == telegram_id)
        )
        model = result.scalar_one_or_none()
        return UserMapper.to_entity(model) if model else None
    
    async def create(
        self,
        telegram_id: int,
        role: Role = Role.USER,
        username: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
    ) -> User:
        logger.debug(f"Creating user with telegram_id={telegram_id}")
        model = UserModel(
            telegram_id=telegram_id,
            role=role,
            username=username,
            first_name=first_name,
            last_name=last_name,
        )
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return UserMapper.to_entity(model)
    
    async def update(self, user: User) -> User:
        logger.debug(f"Updating user id={user.id}")
        result = await self._session.execute(
            select(UserModel).where(UserModel.id == user.id)
        )
        model = result.scalar_one()
        UserMapper.update_model(model, user)
        await self._session.flush()
        await self._session.refresh(model)
        return UserMapper.to_entity(model)
    
    async def get_all(self, limit: int | None = None, offset: int | None = None) -> Sequence[User]:
        logger.debug(f"Getting all users (limit={limit}, offset={offset})")
        query = select(UserModel)
        
        if offset:
            query = query.offset(offset)
        if limit:
            query = query.limit(limit)
        
        result = await self._session.execute(query)
        models = result.scalars().all()
        return [UserMapper.to_entity(model) for model in models]
    
    async def exists_by_telegram_id(self, telegram_id: int) -> bool:
        logger.debug(f"Checking existence by telegram_id={telegram_id}")
        result = await self._session.execute(
            select(func.count()).select_from(UserModel).where(UserModel.telegram_id == telegram_id)
        )
        count = result.scalar_one()
        return count > 0
