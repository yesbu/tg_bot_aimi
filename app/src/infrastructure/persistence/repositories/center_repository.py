from typing import Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from src.domain.interfaces.repositories import ICenterRepository
from src.domain.entities import Center
from src.infrastructure.persistence.models.center import Center as CenterModel
from src.infrastructure.persistence.mappers import CenterMapper
from src.domain.enums import CenterStatus


class CenterRepository(ICenterRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
    
    async def get_by_id(self, id: int) -> Center | None:
        logger.debug(f"Getting center by id={id}")
        result = await self._session.execute(
            select(CenterModel).where(CenterModel.id == id)
        )
        model = result.scalar_one_or_none()
        return CenterMapper.to_entity(model) if model else None
    
    async def get_by_partner_id(self, partner_id: int) -> Center | None:
        logger.debug(f"Getting center by partner_id={partner_id}")
        result = await self._session.execute(
            select(CenterModel).where(CenterModel.partner_id == partner_id)
        )
        model = result.scalar_one_or_none()
        return CenterMapper.to_entity(model) if model else None
    
    async def get_by_filters(
        self,
        city: str | None = None,
        category: str | None = None,
        status: CenterStatus | None = None,
        limit: int | None = None,
        offset: int | None = None
    ) -> Sequence[Center]:
        logger.debug(f"Getting centers with filters")
        query = select(CenterModel)
        
        if city:
            query = query.where(CenterModel.city == city)
        if category:
            query = query.where(CenterModel.category == category)
        if status:
            query = query.where(CenterModel.status == status)
        
        if offset:
            query = query.offset(offset)
        if limit:
            query = query.limit(limit)
        
        result = await self._session.execute(query)
        models = result.scalars().all()
        return [CenterMapper.to_entity(model) for model in models]
    
    async def get_pending_centers(self) -> Sequence[Center]:
        logger.debug("Getting pending centers")
        result = await self._session.execute(
            select(CenterModel).where(CenterModel.status == CenterStatus.PENDING)
        )
        models = result.scalars().all()
        return [CenterMapper.to_entity(model) for model in models]
    
    async def create(
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
        logger.debug(f"Creating center for partner_id={partner_id}")
        entity = Center(
            partner_id=partner_id,
            name=name,
            city=city,
            address=address,
            phone=phone,
            category=category,
            description=description,
            logo=logo,
        )
        model = CenterMapper.to_model(entity)
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return CenterMapper.to_entity(model)
    
    async def update(self, center: Center) -> Center:
        logger.debug(f"Updating center id={center.id}")
        result = await self._session.execute(
            select(CenterModel).where(CenterModel.id == center.id)
        )
        model = result.scalar_one()
        CenterMapper.update_model(model, center)
        await self._session.flush()
        await self._session.refresh(model)
        return CenterMapper.to_entity(model)
    
    async def delete(self, id: int) -> bool:
        logger.debug(f"Deleting center id={id}")
        result = await self._session.execute(
            select(CenterModel).where(CenterModel.id == id)
        )
        model = result.scalar_one_or_none()
        
        if model:
            await self._session.delete(model)
            await self._session.flush()
            return True
        return False
