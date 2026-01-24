from dataclasses import dataclass
from datetime import datetime, timedelta
from loguru import logger

from src.domain.interfaces.repositories import (
    IPaymentRepository,
    ISubscriptionRepository,
    ISubscriptionPlanRepository,
)
from src.domain.enums import PaymentStatus
from src.infrastructure.payment.airbapay import AirbaPayGateway
from src.infrastructure.payment.status import PaymentErrorCode


@dataclass
class PaymentStatusResult:
    success: bool
    status: PaymentStatus | None = None
    error_code: PaymentErrorCode | None = None
    error_message: str | None = None
    payment_data: dict | None = None
    subscription_created: bool = False


class CheckPaymentStatusUseCase:
    def __init__(
        self,
        payment_gateway: AirbaPayGateway,
        payment_repository: IPaymentRepository,
        subscription_repository: ISubscriptionRepository,
        subscription_plan_repository: ISubscriptionPlanRepository,
    ):
        self._payment_gateway = payment_gateway
        self._payment_repository = payment_repository
        self._subscription_repository = subscription_repository
        self._subscription_plan_repository = subscription_plan_repository

    async def execute(self, payment_id: str) -> PaymentStatusResult:
        try:
            payment = await self._payment_repository.get_by_payment_id(payment_id)
            if not payment:
                logger.error(f"Payment not found in DB: payment_id={payment_id}")
                return PaymentStatusResult(
                    success=False,
                    error_message="Платеж не найден"
                )
            
            status_result = await self._payment_gateway.payment.get_payment_status(payment_id)
            
            if not status_result.get("success"):
                error_msg = status_result.get("error", "Ошибка при проверке платежа")
                logger.error(f"Get payment status failed: {error_msg}")
                return PaymentStatusResult(
                    success=False,
                    error_message=error_msg
                )
            
            payment_data = status_result.get("data", {})
            status_str = payment_data.get("status", "")
            
            try:
                payment_status = PaymentStatus(status_str)
            except ValueError:
                logger.warning(f"Unknown payment status: {status_str}")
                return PaymentStatusResult(
                    success=False,
                    error_message=f"Неизвестный статус платежа: {status_str}"
                )
            
            if payment.status != payment_status:
                payment.status = payment_status
                await self._payment_repository.update(payment)
                logger.info(f"Payment status updated: id={payment.id}, status={payment_status.value}")
            
            error_code = None
            subscription_created = False
            
            if payment_status == PaymentStatus.ERROR:
                error_code_value = payment_data.get("error_code", 0)
                try:
                    error_code = PaymentErrorCode(error_code_value)
                except ValueError:
                    logger.warning(f"Unknown error code: {error_code_value}")
            
            if payment_status == PaymentStatus.SUCCESS:
                existing_subscription = await self._subscription_repository.get_active_by_user_id(payment.user_id)
                
                if not existing_subscription:
                    subscription_plan = await self._get_subscription_plan_from_payment(payment)
                    
                    if subscription_plan:
                        starts_at = datetime.utcnow()
                        expires_at = starts_at + timedelta(days=subscription_plan.duration_months * 30)
                        
                        subscription = await self._subscription_repository.create(
                            user_id=payment.user_id,
                            subscription_plan_id=subscription_plan.id,
                            starts_at=starts_at,
                            expires_at=expires_at,
                            payment_id=payment.id,
                        )
                        
                        subscription_created = True
                        logger.info(f"Subscription created: id={subscription.id}, user_id={payment.user_id}")
            
            return PaymentStatusResult(
                success=True,
                status=payment_status,
                error_code=error_code,
                payment_data=payment_data,
                subscription_created=subscription_created,
            )
            
        except Exception as e:
            logger.error(f"Ошибка при проверке статуса платежа: {e}", exc_info=True)
            return PaymentStatusResult(
                success=False,
                error_message="Ошибка при проверке платежа. Попробуйте позже."
            )
    
    async def _get_subscription_plan_from_payment(self, payment):
        plans = await self._subscription_plan_repository.get_active()
        
        for plan in plans:
            if abs(plan.price - payment.amount) < 0.01:
                return plan
        
        return None
