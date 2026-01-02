from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.interfaces.repositories import (
    IUserRepository,
    IChildRepository,
    ICenterRepository,
    ICourseRepository,
    ISubscriptionRepository,
    IVisitRepository,
    IPaymentRepository,
    IReviewRepository,
)
from src.infrastructure.persistence.repositories.user_repository import UserRepository
from src.infrastructure.persistence.repositories.child_repository import ChildRepository
from src.infrastructure.persistence.repositories.center_repository import CenterRepository
from src.infrastructure.persistence.repositories.course_repository import CourseRepository
from src.infrastructure.persistence.repositories.subscription_repository import SubscriptionRepository
from src.infrastructure.persistence.repositories.visit_repository import VisitRepository
from src.infrastructure.persistence.repositories.payment_repository import PaymentRepository
from src.infrastructure.persistence.repositories.review_repository import ReviewRepository


class RepositoryProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def provide_user_repository(self, session: AsyncSession) -> IUserRepository:
        return UserRepository(session)
    
    @provide(scope=Scope.REQUEST)
    def provide_child_repository(self, session: AsyncSession) -> IChildRepository:
        return ChildRepository(session)
    
    @provide(scope=Scope.REQUEST)
    def provide_center_repository(self, session: AsyncSession) -> ICenterRepository:
        return CenterRepository(session)
    
    @provide(scope=Scope.REQUEST)
    def provide_course_repository(self, session: AsyncSession) -> ICourseRepository:
        return CourseRepository(session)
    
    @provide(scope=Scope.REQUEST)
    def provide_subscription_repository(self, session: AsyncSession) -> ISubscriptionRepository:
        return SubscriptionRepository(session)
    
    @provide(scope=Scope.REQUEST)
    def provide_visit_repository(self, session: AsyncSession) -> IVisitRepository:
        return VisitRepository(session)
    
    @provide(scope=Scope.REQUEST)
    def provide_payment_repository(self, session: AsyncSession) -> IPaymentRepository:
        return PaymentRepository(session)
    
    @provide(scope=Scope.REQUEST)
    def provide_review_repository(self, session: AsyncSession) -> IReviewRepository:
        return ReviewRepository(session)
