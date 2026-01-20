from src.domain.entities import Review
from src.domain.interfaces.repositories import IReviewRepository


class CreateReviewUseCase:
    def __init__(self, review_repository: IReviewRepository):
        self._review_repository = review_repository
    
    async def execute(
        self,
        user_id: int,
        course_id: int,
        rating: int,
        comment: str | None = None,
    ) -> Review:
        if not 1 <= rating <= 5:
            raise ValueError("Rating must be between 1 and 5")
        
        review = Review(
            user_id=user_id,
            course_id=course_id,
            rating=rating,
            comment=comment,
        )
        
        return await self._review_repository.create(review)
