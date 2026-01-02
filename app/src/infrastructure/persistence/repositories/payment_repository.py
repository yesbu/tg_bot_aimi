from typing import Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from src.application.interfaces.repositories import IPaymentRepository
from src.domain.entities import Payment, PaymentRefund
from src.infrastructure.persistence.models.payment import Payment as PaymentModel, PaymentRefund as PaymentRefundModel
from src.infrastructure.persistence.mappers import PaymentMapper, PaymentRefundMapper
from src.domain.enums import PaymentStatus


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
    
    async def get_by_transaction_id(self, transaction_id: str) -> Payment | None:
        logger.debug(f"Getting payment by transaction_id={transaction_id}")
        result = await self._session.execute(
            select(PaymentModel).where(PaymentModel.transaction_id == transaction_id)
        )
        model = result.scalar_one_or_none()
        return PaymentMapper.to_entity(model) if model else None
    
    async def get_user_payments(
        self,
        user_id: int,
        status: PaymentStatus | None = None
    ) -> Sequence[Payment]:
        logger.debug(f"Getting payments for user_id={user_id}, status={status}")
        query = (
            select(PaymentModel)
            .where(PaymentModel.user_id == user_id)
            .order_by(PaymentModel.created_at.desc())
        )
        
        if status:
            query = query.where(PaymentModel.status == status)
        
        result = await self._session.execute(query)
        models = result.scalars().all()
        return [PaymentMapper.to_entity(model) for model in models]
    
    async def get_pending_payments(self) -> Sequence[Payment]:
        logger.debug("Getting pending payments")
        result = await self._session.execute(
            select(PaymentModel).where(PaymentModel.status == PaymentStatus.PENDING)
        )
        models = result.scalars().all()
        return [PaymentMapper.to_entity(model) for model in models]
    
    async def create(
        self,
        user_id: int,
        amount: float,
        currency: str = "KZT",
        subscription_id: int | None = None,
        method: str | None = None,
        invoice_id: str | None = None,
        airba_payment_id: str | None = None,
        redirect_url: str | None = None,
    ) -> Payment:
        logger.debug(f"Creating payment for user_id={user_id}")
        entity = Payment(
            user_id=user_id,
            amount=amount,
            currency=currency,
            subscription_id=subscription_id,
            method=method,
            invoice_id=invoice_id,
            airba_payment_id=airba_payment_id,
            redirect_url=redirect_url,
        )
        model = PaymentMapper.to_model(entity)
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
    
    async def create_refund(
        self,
        payment_id: int,
        amount: float,
        airba_refund_id: str | None = None,
        ext_id: str | None = None,
        reason: str | None = None,
        status: str | None = None,
    ) -> PaymentRefund:
        logger.debug(f"Creating refund for payment_id={payment_id}")
        entity = PaymentRefund(
            payment_id=payment_id,
            amount=amount,
            airba_refund_id=airba_refund_id,
            ext_id=ext_id,
            reason=reason,
            status=status,
        )
        model = PaymentRefundMapper.to_model(entity)
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return PaymentRefundMapper.to_entity(model)
    
    async def get_payment_refunds(self, payment_id: int) -> Sequence[PaymentRefund]:
        logger.debug(f"Getting refunds for payment_id={payment_id}")
        result = await self._session.execute(
            select(PaymentRefundModel).where(PaymentRefundModel.payment_id == payment_id)
        )
        models = result.scalars().all()
        return [PaymentRefundMapper.to_entity(model) for model in models]
