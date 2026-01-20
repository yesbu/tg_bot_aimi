from src.infrastructure.persistence.models.course import Course as CourseModel
from src.domain.entities import Course


class CourseMapper:
    @staticmethod
    def to_entity(model: CourseModel) -> Course:
        return Course(
            id=model.id,
            center_id=model.center_id,
            name=model.name,
            description=model.description,
            category=model.category,
            age_min=model.age_min,
            age_max=model.age_max,
            requirements=model.requirements,
            schedule=model.schedule,
            rating=model.rating,
            price_4=model.price_4,
            price_8=model.price_8,
            price_unlimited=model.price_unlimited,
            photo=model.photo,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
    
    @staticmethod
    def to_model(entity: Course) -> CourseModel:
        return CourseModel(
            id=entity.id,
            center_id=entity.center_id,
            name=entity.name,
            description=entity.description,
            category=entity.category,
            age_min=entity.age_min,
            age_max=entity.age_max,
            requirements=entity.requirements,
            schedule=entity.schedule,
            rating=entity.rating,
            price_4=entity.price_4,
            price_8=entity.price_8,
            price_unlimited=entity.price_unlimited,
            photo=entity.photo,
        )
    
    @staticmethod
    def update_model(model: CourseModel, entity: Course) -> None:
        model.name = entity.name
        model.description = entity.description
        model.category = entity.category
        model.age_min = entity.age_min
        model.age_max = entity.age_max
        model.requirements = entity.requirements
        model.schedule = entity.schedule
        model.rating = entity.rating
        model.price_4 = entity.price_4
        model.price_8 = entity.price_8
        model.price_unlimited = entity.price_unlimited
        model.photo = entity.photo
