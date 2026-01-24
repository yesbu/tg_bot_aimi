from src.domain.entities.category import Category as CategoryEntity
from src.infrastructure.persistence.models.course_category import CourseCategory as CategoryModel


class CategoryMapper:
    @staticmethod
    def to_entity(model: CategoryModel, name: str) -> CategoryEntity:
        return CategoryEntity(
            id=model.id,
            name=name,
            is_active=model.is_active
        )
    
    @staticmethod
    def to_model(entity: CategoryEntity) -> CategoryModel:
        return CategoryModel(
            id=entity.id,
            is_active=entity.is_active
        )
