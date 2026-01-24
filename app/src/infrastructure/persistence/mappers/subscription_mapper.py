from src.infrastructure.persistence.models.subscription import Subscription as SubscriptionModel
from src.domain.entities import Subscription


class SubscriptionMapper:
    @staticmethod
    def to_entity(model: SubscriptionModel) -> Subscription:
        return Subscription(
            id=model.id,
            user_id=model.user_id,
            subscription_plan_id=model.subscription_plan_id,
            status=model.status,
            starts_at=model.starts_at,
            expires_at=model.expires_at,
            payment_id=model.payment_id,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
    
    @staticmethod
    def to_model(entity: Subscription) -> SubscriptionModel:
        return SubscriptionModel(
            id=entity.id,
            user_id=entity.user_id,
            subscription_plan_id=entity.subscription_plan_id,
            status=entity.status,
            starts_at=entity.starts_at,
            expires_at=entity.expires_at,
            payment_id=entity.payment_id,
        )
    
    @staticmethod
    def update_model(model: SubscriptionModel, entity: Subscription) -> None:
        model.subscription_plan_id = entity.subscription_plan_id
        model.status = entity.status
        model.starts_at = entity.starts_at
        model.expires_at = entity.expires_at
        model.payment_id = entity.payment_id
