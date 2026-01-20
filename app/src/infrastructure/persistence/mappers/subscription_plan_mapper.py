from src.domain.entities.subscription_plan import SubscriptionPlan
from src.infrastructure.persistence.models.subscription_plan import SubscriptionPlan as SubscriptionPlanModel


class SubscriptionPlanMapper:
    @staticmethod
    def to_entity(model: SubscriptionPlanModel) -> SubscriptionPlan:
        return SubscriptionPlan(
            id=model.id,
            name=model.name,
            duration_months=model.duration_months,
            price=model.price,
            visits_limit=model.visits_limit,
            description=model.description,
            is_active=model.is_active,
            display_order=model.display_order,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
    
    @staticmethod
    def to_model(entity: SubscriptionPlan) -> SubscriptionPlanModel:
        return SubscriptionPlanModel(
            id=entity.id,
            name=entity.name,
            duration_months=entity.duration_months,
            price=entity.price,
            visits_limit=entity.visits_limit,
            description=entity.description,
            is_active=entity.is_active,
            display_order=entity.display_order,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )
    
    @staticmethod
    def update_model(model: SubscriptionPlanModel, entity: SubscriptionPlan) -> None:
        model.name = entity.name
        model.duration_months = entity.duration_months
        model.price = entity.price
        model.visits_limit = entity.visits_limit
        model.description = entity.description
        model.is_active = entity.is_active
        model.display_order = entity.display_order
