from loguru import logger
from sqlalchemy.exc import IntegrityError

from src.domain.entities import User
from src.domain.enums import Role
from src.domain.interfaces.repositories import IUserRepository
from src.domain.interfaces.cache import ICacheClient


class GetOrCreateUserUseCase:
    def __init__(self, user_repository: IUserRepository, cache: ICacheClient):
        self._user_repository = user_repository
        self._cache = cache
    
    async def execute(
        self,
        telegram_id: int,
        username: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
    ) -> User:
        logger.info(f"Getting or creating user telegram_id={telegram_id}")
        
        cache_key = f"user:telegram_id:{telegram_id}"
        
        cached_data = await self._cache.get(cache_key)
        if cached_data:
            return self._deserialize_user(cached_data)
        
        user = await self._user_repository.get_by_telegram_id(telegram_id)
        if user:
            await self._cache.set(cache_key, self._serialize_user(user), ttl=3600)
            return user
        
        try:
            created_user = await self._user_repository.create(
                telegram_id=telegram_id,
                username=username,
                first_name=first_name,
                last_name=last_name,
                role=Role.USER,
            )
            await self._cache.set(cache_key, self._serialize_user(created_user), ttl=3600)
            return created_user
        except IntegrityError:
            logger.warning(f"Race condition detected for telegram_id={telegram_id}, fetching existing user")
            user = await self._user_repository.get_by_telegram_id(telegram_id)
            if user:
                await self._cache.set(cache_key, self._serialize_user(user), ttl=3600)
                return user
            raise
    
    @staticmethod
    def _serialize_user(user: User) -> dict:
        return {
            "id": user.id,
            "telegram_id": user.telegram_id,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "phone": user.phone,
            "city": user.city,
            "role": user.role.value,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "updated_at": user.updated_at.isoformat() if user.updated_at else None,
            "is_deleted": user.is_deleted,
        }
    
    @staticmethod
    def _deserialize_user(data: dict) -> User:
        return User(
            id=data.get("id"),
            telegram_id=data["telegram_id"],
            username=data.get("username"),
            first_name=data.get("first_name"),
            last_name=data.get("last_name"),
            phone=data.get("phone"),
            city=data.get("city"),
            role=Role(data["role"]),
            is_deleted=data.get("is_deleted", False),
        )
