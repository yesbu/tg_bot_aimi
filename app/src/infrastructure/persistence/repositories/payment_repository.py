from typing import Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from src.domain.interfaces.repositories import IPaymentRepository
from src.domain.entities import Payment
from src.domain.enums import PaymentStatus
from src.infrastructure.persistence.models.payment import Payment as PaymentModel
from src.infrastructure.persistence.mappers import PaymentMapper


class PaymentRepository(IPaymentRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
    
    async def get_by_id(self, id: int) -> Payment | None:
        logger.debug(f"Getting payment by id={id}")
        result = await self._session.execute(
            select(PaymentModel).where(PaymentModel.id == id)
        )
        model = result.scalar_one_or_none()
        return PaymentMapper.to_entity(model) if model else None
    
    async def get_by_payment_id(self, payment_id: str) -> Payment | None:
        logger.debug(f"Getting payment by payment_id={payment_id}")
        result = await self._session.execute(
            select(PaymentModel).where(PaymentModel.payment_id == payment_id)
        )
        model = result.scalar_one_or_none()
        return PaymentMapper.to_entity(model) if model else None
    
    async def get_by_invoice_id(self, invoice_id: str) -> Payment | None:
        logger.debug(f"Getting payment by invoice_id={invoice_id}")
        result = await self._session.execute(
            select(PaymentModel).where(PaymentModel.invoice_id == invoice_id)
        )
        model = result.scalar_one_or_none()
        return PaymentMapper.to_entity(model) if model else None
    
    async def get_by_user_id(
        self,
        user_id: int,
        limit: int | None = None,
        offset: int | None = None,
    ) -> Sequence[Payment]:
        logger.debug(f"Getting payments for user_id={user_id} (limit={limit}, offset={offset})")
        query = select(PaymentModel).where(PaymentModel.user_id == user_id).order_by(PaymentModel.created_at.desc())
        
        if offset:
            query = query.offset(offset)
        if limit:
            query = query.limit(limit)
        
        result = await self._session.execute(query)
        models = result.scalars().all()
        return [PaymentMapper.to_entity(model) for model in models]
    
    async def get_by_status(
        self,
        status: PaymentStatus,
        limit: int | None = None,
        offset: int | None = None,
    ) -> Sequence[Payment]:
        logger.debug(f"Getting payments by status={status.value} (limit={limit}, offset={offset})")
        query = select(PaymentModel).where(PaymentModel.status == status).order_by(PaymentModel.created_at.desc())
        
        if offset:
            query = query.offset(offset)
        if limit:
            query = query.limit(limit)
        
        result = await self._session.execute(query)
        models = result.scalars().all()
        return [PaymentMapper.to_entity(model) for model in models]
    
    async def create(
        self,
        user_id: int,
        amount: float,
        currency: str,
        status: PaymentStatus = PaymentStatus.NEW,
        payment_id: str | None = None,
        invoice_id: str | None = None,
    ) -> Payment:
        logger.debug(f"Creating payment for user_id={user_id}, amount={amount}")
        model = PaymentModel(
            user_id=user_id,
            amount=amount,
            currency=currency,
            status=status,
            payment_id=payment_id,
            invoice_id=invoice_id,
        )
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return PaymentMapper.to_entity(model)
    
    async def update(self, payment: Payment) -> Payment:
        logger.debug(f"Updating payment id={payment.id}")
        result = await self._session.execute(
            select(PaymentModel).where(PaymentModel.id == payment.id)
        )
        model = result.scalar_one()
        PaymentMapper.update_model(model, payment)
        await self._session.flush()
        await self._session.refresh(model)
        return PaymentMapper.to_entity(model)
    
    async def exists_by_payment_id(self, payment_id: str) -> bool:
        logger.debug(f"Checking existence by payment_id={payment_id}")
        result = await self._session.execute(
            select(PaymentModel.id).where(PaymentModel.payment_id == payment_id)
        )
        return result.scalar_one_or_none() is not None
