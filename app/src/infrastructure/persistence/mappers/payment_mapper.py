from src.infrastructure.persistence.models.payment import Payment as PaymentModel
from src.domain.entities import Payment


class PaymentMapper:
    @staticmethod
    def to_entity(model: PaymentModel) -> Payment:
        return Payment(
            id=model.id,
            user_id=model.user_id,
            amount=model.amount,
            currency=model.currency,
            status=model.status,
            payment_id=model.payment_id,
            invoice_id=model.invoice_id,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
    
    @staticmethod
    def to_model(entity: Payment) -> PaymentModel:
        return PaymentModel(
            id=entity.id,
            user_id=entity.user_id,
            amount=entity.amount,
            currency=entity.currency,
            status=entity.status,
            payment_id=entity.payment_id,
            invoice_id=entity.invoice_id,
        )
    
    @staticmethod
    def update_model(model: PaymentModel, entity: Payment) -> None:
        model.amount = entity.amount
        model.currency = entity.currency
        model.status = entity.status
        model.payment_id = entity.payment_id
        model.invoice_id = entity.invoice_id
