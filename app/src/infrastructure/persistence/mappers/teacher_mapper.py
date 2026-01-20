from src.infrastructure.persistence.models.teacher import Teacher as TeacherModel
from src.domain.entities import Teacher


class TeacherMapper:
    @staticmethod
    def to_entity(model: TeacherModel) -> Teacher:
        return Teacher(
            id=model.id,
            center_id=model.center_id,
            name=model.name,
            description=model.description,
        )
    
    @staticmethod
    def to_model(entity: Teacher) -> TeacherModel:
        return TeacherModel(
            id=entity.id,
            center_id=entity.center_id,
            name=entity.name,
            description=entity.description,
        )
    
    @staticmethod
    def update_model(model: TeacherModel, entity: Teacher) -> None:
        model.name = entity.name
        model.description = entity.description
