from src.domain.entities import User
from src.domain.enums import Role
from src.domain.interfaces.repositories import IUserRepository


class UpdateUserRoleUseCase:
    def __init__(self, user_repository: IUserRepository):
        self._user_repository = user_repository
    
    async def execute(self, user_id: int, new_role: Role) -> User:
        user = await self._user_repository.get_by_id(user_id)
        if not user:
            raise ValueError(f"User with id {user_id} not found")
        
        user.role = new_role
        return await self._user_repository.update(user)
