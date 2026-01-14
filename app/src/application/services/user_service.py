from loguru import logger

from src.application.interfaces.services import IUserService
from src.application.interfaces.repositories import IUserRepository
from src.domain.entities import User
from src.domain.enums import Role


class UserService(IUserService):
    def __init__(self, user_repository: IUserRepository) -> None:
        self._user_repo = user_repository
    
    async def get_or_create_user(
        self,
        telegram_id: int,
        username: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
    ) -> User:
        logger.info(f"Getting or creating user telegram_id={telegram_id}")
        
        user = await self._user_repo.get_by_telegram_id(telegram_id)
        if user:
            return user
        
        return await self._user_repo.create(
            telegram_id=telegram_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
        )
    
    async def get_user_by_telegram_id(self, telegram_id: int) -> User | None:
        logger.info(f"Getting user by telegram_id={telegram_id}")
        return await self._user_repo.get_by_telegram_id(telegram_id)
    
    async def update_user_role(self, telegram_id: int, role: Role) -> User:
        logger.info(f"Updating user role: telegram_id={telegram_id}, role={role}")
        user = await self._user_repo.get_by_telegram_id(telegram_id)
        if not user:
            raise ValueError(f"User with telegram_id={telegram_id} not found")
        
        user.change_role(role)
        return await self._user_repo.update(user)
    
    async def update_user_city(self, telegram_id: int, city: str) -> User:
        logger.info(f"Updating user city: telegram_id={telegram_id}, city={city}")
        user = await self._user_repo.get_by_telegram_id(telegram_id)
        if not user:
            raise ValueError(f"User with telegram_id={telegram_id} not found")
        
        user.update_city(city)
        return await self._user_repo.update(user)
    
    async def user_exists(self, telegram_id: int) -> bool:
        return await self._user_repo.exists_by_telegram_id(telegram_id)
