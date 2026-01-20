from src.domain.entities import Center
from src.domain.interfaces.repositories import ICenterRepository


class RegisterCenterUseCase:
    def __init__(self, center_repository: ICenterRepository):
        self._center_repository = center_repository
    
    async def execute(
        self,
        name: str,
        address: str,
        phone: str,
        owner_id: int,
    ) -> Center:
        center = Center(
            name=name,
            address=address,
            phone=phone,
            owner_id=owner_id,
        )
        
        return await self._center_repository.create(center)
