from dataclasses import dataclass
import uuid
from loguru import logger

from src.domain.entities import SubscriptionPlan
from src.domain.interfaces.repositories import (
    ISubscriptionPlanRepository,
    IUserRepository,
    IPaymentRepository,
)
from src.domain.enums import PaymentStatus
from src.infrastructure.payment.airbapay import AirbaPayGateway


@dataclass
class BuySubscriptionResult:
    success: bool
    plan: SubscriptionPlan | None = None
    redirect_url: str | None = None
    payment_id: str | None = None
    error_message: str | None = None


class BuySubscriptionPlanUseCase:
    def __init__(
        self,
        subscription_plan_repository: ISubscriptionPlanRepository,
        user_repository: IUserRepository,
        payment_repository: IPaymentRepository,
        payment_gateway: AirbaPayGateway,
    ):
        self._subscription_plan_repository = subscription_plan_repository
        self._user_repository = user_repository
        self._payment_repository = payment_repository
        self._payment_gateway = payment_gateway

    async def execute(self, telegram_id: int, plan_id: int) -> BuySubscriptionResult:
        user = await self._user_repository.get_by_telegram_id(telegram_id)
        if not user:
            return BuySubscriptionResult(
                success=False,
                error_message="Пользователь не найден"
            )
        
        plan = await self._subscription_plan_repository.get_by_id(plan_id)
        
        if not plan:
            return BuySubscriptionResult(
                success=False,
                error_message="Тариф не найден"
            )
        
        if not plan.is_active:
            return BuySubscriptionResult(
                success=False,
                plan=plan,
                error_message="Этот тариф временно недоступен"
            )
        
        try:
            invoice_id = str(uuid.uuid4())
            account_id = str(telegram_id)
            
            payment_result = await self._payment_gateway.payment.create_payment(
                invoice_id=invoice_id,
                amount=plan.price,
                account_id=account_id,
                render_apple_pay=True,
                render_google_pay=True,
                currency="KZT",
                language="ru",
                description=f"Оплата абонемента: {plan.name}"
            )

            if not payment_result.get("success"):
                error_msg = payment_result.get("error", "Ошибка при создании платежа")
                logger.error(f"Payment gateway error: {error_msg}")
                return BuySubscriptionResult(
                    success=False,
                    plan=plan,
                    error_message=error_msg
                )
            
            redirect_url = payment_result.get("redirect_url")
            external_payment_id = payment_result.get("payment_id")
            
            if not redirect_url:
                return BuySubscriptionResult(
                    success=False,
                    plan=plan,
                    error_message="Ссылка на оплату не получена"
                )
            
            payment = await self._payment_repository.create(
                user_id=user.id,
                amount=plan.price,
                currency="KZT",
                status=PaymentStatus.NEW,
                payment_id=external_payment_id,
                invoice_id=invoice_id,
            )
            
            logger.info(f"Payment created: id={payment.id}, user_id={user.id}, amount={plan.price}")
            
            return BuySubscriptionResult(
                success=True,
                plan=plan,
                redirect_url=redirect_url,
                payment_id=external_payment_id
            )
            
        except Exception as e:
            logger.error(f"Ошибка при покупке абонемента: {e}", exc_info=True)
            return BuySubscriptionResult(
                success=False,
                plan=plan,
                error_message="Ошибка при создании платежа. Попробуйте позже."
            )
        