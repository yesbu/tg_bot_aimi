from src.domain.entities import User
from src.domain.enums import Role
from src.domain.interfaces.repositories import IUserRepository


class RegisterUserUseCase:
    def __init__(self, user_repository: IUserRepository):
        self._user_repository = user_repository
    
    async def execute(
        self,
        telegram_id: int,
        username: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
        role: Role = Role.USER,
    ) -> User:
        user = User(
            telegram_id=telegram_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
            role=role,
        )
        
        return await self._user_repository.create(user)
