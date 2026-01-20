from src.infrastructure.persistence.models.child import Child as ChildModel
from src.domain.entities import Child


class ChildMapper:
    @staticmethod
    def to_entity(model: ChildModel) -> Child:
        return Child(
            id=model.id,
            parent_id=model.parent_id,
            name=model.name,
            age=model.age,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
    
    @staticmethod
    def to_model(entity: Child) -> ChildModel:
        return ChildModel(
            id=entity.id,
            parent_id=entity.parent_id,
            name=entity.name,
            age=entity.age,
        )
    
    @staticmethod
    def update_model(model: ChildModel, entity: Child) -> None:
        model.name = entity.name
        model.age = entity.age
