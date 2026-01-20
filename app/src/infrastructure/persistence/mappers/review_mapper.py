from src.infrastructure.persistence.models.review import Review as ReviewModel
from src.domain.entities import Review


class ReviewMapper:
    @staticmethod
    def to_entity(model: ReviewModel) -> Review:
        return Review(
            id=model.id,
            course_id=model.course_id,
            user_id=model.user_id,
            rating=model.rating,
            comment=model.comment,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
    
    @staticmethod
    def to_model(entity: Review) -> ReviewModel:
        return ReviewModel(
            id=entity.id,
            course_id=entity.course_id,
            user_id=entity.user_id,
            rating=entity.rating,
            comment=entity.comment,
        )
    
    @staticmethod
    def update_model(model: ReviewModel, entity: Review) -> None:
        model.rating = entity.rating
        model.comment = entity.comment
