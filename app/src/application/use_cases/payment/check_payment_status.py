from dataclasses import dataclass
from loguru import logger

from src.infrastructure.payment.airbapay import AirbaPayGateway
from src.infrastructure.payment.status import PaymentStatusEnum, PaymentErrorCode


@dataclass
class PaymentStatusResult:
    success: bool
    status: PaymentStatusEnum | None = None
    error_code: PaymentErrorCode | None = None
    error_message: str | None = None
    payment_data: dict | None = None


class CheckPaymentStatusUseCase:
    def __init__(self, payment_gateway: AirbaPayGateway):
        self._payment_gateway = payment_gateway

    async def execute(self, payment_id: str) -> PaymentStatusResult:
        try:
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
                payment_status = PaymentStatusEnum(status_str)
            except ValueError:
                logger.warning(f"Unknown payment status: {status_str}")
                return PaymentStatusResult(
                    success=False,
                    error_message=f"Неизвестный статус платежа: {status_str}"
                )
            
            error_code = None
            if payment_status == PaymentStatusEnum.ERROR:
                error_code_value = payment_data.get("error_code", 0)
                try:
                    error_code = PaymentErrorCode(error_code_value)
                except ValueError:
                    logger.warning(f"Unknown error code: {error_code_value}")
            
            return PaymentStatusResult(
                success=True,
                status=payment_status,
                error_code=error_code,
                payment_data=payment_data
            )
            
        except Exception as e:
            logger.error(f"Ошибка при проверке статуса платежа: {e}", exc_info=True)
            return PaymentStatusResult(
                success=False,
                error_message="Ошибка при проверке платежа. Попробуйте позже."
            )
