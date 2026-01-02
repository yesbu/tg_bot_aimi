from typing import Sequence
from loguru import logger

from src.application.interfaces.services import ICenterService
from src.application.interfaces.repositories import ICenterRepository
from src.domain.entities import Center
from src.domain.enums import CenterStatus


class CenterService(ICenterService):
    def __init__(self, center_repository: ICenterRepository) -> None:
        self._center_repo = center_repository
    
    async def get_center_by_id(self, id: int) -> Center | None:
        logger.info(f"Getting center by id={id}")
        return await self._center_repo.get_by_id(id)
    
    async def get_partner_center(self, partner_id: int) -> Center | None:
        logger.info(f"Getting center for partner_id={partner_id}")
        return await self._center_repo.get_by_partner_id(partner_id)
    
    async def search_centers(
        self,
        city: str | None = None,
        category: str | None = None,
        limit: int | None = None,
        offset: int | None = None
    ) -> Sequence[Center]:
        logger.info(f"Searching centers: city={city}, category={category}")
        return await self._center_repo.get_by_filters(
            city=city,
            category=category,
            status=CenterStatus.APPROVED,
            limit=limit,
            offset=offset,
        )
    
    async def create_center(
        self,
        partner_id: int,
        name: str,
        city: str,
        address: str | None = None,
        phone: str | None = None,
        category: str | None = None,
        description: str | None = None,
        logo: str | None = None,
    ) -> Center:
        logger.info(f"Creating center for partner_id={partner_id}")
        
        existing = await self._center_repo.get_by_partner_id(partner_id)
        if existing:
            raise ValueError(f"Partner {partner_id} already has a center")
        
        return await self._center_repo.create(
            partner_id=partner_id,
            name=name,
            city=city,
            address=address,
            phone=phone,
            category=category,
            description=description,
            logo=logo,
        )
    
    async def update_center(self, center: Center) -> Center:
        logger.info(f"Updating center id={center.id}")
        return await self._center_repo.update(center)
    
    async def approve_center(self, center_id: int) -> Center:
        logger.info(f"Approving center id={center_id}")
        center = await self._center_repo.get_by_id(center_id)
        if not center:
            raise ValueError(f"Center {center_id} not found")
        
        center.approve()
        return await self._center_repo.update(center)
    
    async def reject_center(self, center_id: int) -> Center:
        logger.info(f"Rejecting center id={center_id}")
        center = await self._center_repo.get_by_id(center_id)
        if not center:
            raise ValueError(f"Center {center_id} not found")
        
        center.reject()
        return await self._center_repo.update(center)
    
    async def get_pending_centers(self) -> Sequence[Center]:
        logger.info("Getting pending centers for approval")
        return await self._center_repo.get_pending_centers()
