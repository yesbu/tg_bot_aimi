from src.infrastructure.persistence.models.payment import (
    Payment as PaymentModel,
    PaymentRefund as PaymentRefundModel,
)
from src.domain.entities import Payment, PaymentRefund


class PaymentMapper:
    @staticmethod
    def to_entity(model: PaymentModel) -> Payment:
        return Payment(
            id=model.id,
            subscription_id=model.subscription_id,
            user_id=model.user_id,
            amount=model.amount,
            currency=model.currency,
            method=model.method,
            status=model.status,
            transaction_id=model.transaction_id,
            invoice_id=model.invoice_id,
            airba_payment_id=model.airba_payment_id,
            redirect_url=model.redirect_url,
            error_message=model.error_message,
            created_at=model.created_at,
            updated_at=model.updated_at,
            processed_at=model.processed_at,
        )
    
    @staticmethod
    def to_model(entity: Payment) -> PaymentModel:
        return PaymentModel(
            id=entity.id,
            user_id=entity.user_id,
            subscription_id=entity.subscription_id,
            amount=entity.amount,
            currency=entity.currency,
            method=entity.method,
            status=entity.status,
            transaction_id=entity.transaction_id,
            invoice_id=entity.invoice_id,
            airba_payment_id=entity.airba_payment_id,
            redirect_url=entity.redirect_url,
            error_message=entity.error_message,
            processed_at=entity.processed_at,
        )
    
    @staticmethod
    def update_model(model: PaymentModel, entity: Payment) -> None:
        model.status = entity.status
        model.transaction_id = entity.transaction_id
        model.error_message = entity.error_message
        model.processed_at = entity.processed_at


class PaymentRefundMapper:
    @staticmethod
    def to_entity(model: PaymentRefundModel) -> PaymentRefund:
        return PaymentRefund(
            id=model.id,
            payment_id=model.payment_id,
            airba_refund_id=model.airba_refund_id,
            ext_id=model.ext_id,
            amount=model.amount,
            reason=model.reason,
            status=model.status,
            processed_at=model.processed_at,
        )
    
    @staticmethod
    def to_model(entity: PaymentRefund) -> PaymentRefundModel:
        return PaymentRefundModel(
            id=entity.id,
            payment_id=entity.payment_id,
            airba_refund_id=entity.airba_refund_id,
            ext_id=entity.ext_id,
            amount=entity.amount,
            reason=entity.reason,
            status=entity.status,
        )
