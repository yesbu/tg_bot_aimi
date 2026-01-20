from src.infrastructure.persistence.models.visit import Visit as VisitModel
from src.domain.entities import Visit


class VisitMapper:
    @staticmethod
    def to_entity(model: VisitModel) -> Visit:
        return Visit(
            id=model.id,
            subscription_id=model.subscription_id,
            user_id=model.user_id,
            child_id=model.child_id,
            center_id=model.center_id,
            lesson_id=model.lesson_id,
            visited_at=model.visited_at,
        )
    
    @staticmethod
    def to_model(entity: Visit) -> VisitModel:
        return VisitModel(
            id=entity.id,
            subscription_id=entity.subscription_id,
            user_id=entity.user_id,
            child_id=entity.child_id,
            center_id=entity.center_id,
            lesson_id=entity.lesson_id,
        )
