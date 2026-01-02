from dishka import Provider, Scope, provide

from src.application.interfaces.repositories import (
    IUserRepository,
    ICenterRepository,
    ICourseRepository,
    ISubscriptionRepository,
    IVisitRepository,
    IPaymentRepository,
    IReviewRepository,
)
from src.application.services import (
    UserService,
    CenterService,
    CourseService,
    SubscriptionService,
    VisitService,
    PaymentService,
    ReviewService,
)


class ServiceProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def provide_user_service(self, user_repo: IUserRepository) -> UserService:
        return UserService(user_repo)
    
    @provide(scope=Scope.REQUEST)
    def provide_center_service(self, center_repo: ICenterRepository) -> CenterService:
        return CenterService(center_repo)
    
    @provide(scope=Scope.REQUEST)
    def provide_course_service(
        self,
        course_repo: ICourseRepository,
        review_repo: IReviewRepository,
    ) -> CourseService:
        return CourseService(course_repo, review_repo)
    
    @provide(scope=Scope.REQUEST)
    def provide_subscription_service(
        self, subscription_repo: ISubscriptionRepository
    ) -> SubscriptionService:
        return SubscriptionService(subscription_repo)
    
    @provide(scope=Scope.REQUEST)
    def provide_visit_service(
        self,
        visit_repo: IVisitRepository,
        subscription_repo: ISubscriptionRepository,
    ) -> VisitService:
        return VisitService(visit_repo, subscription_repo)
    
    @provide(scope=Scope.REQUEST)
    def provide_payment_service(self, payment_repo: IPaymentRepository) -> PaymentService:
        return PaymentService(payment_repo)
    
    @provide(scope=Scope.REQUEST)
    def provide_review_service(
        self,
        review_repo: IReviewRepository,
        course_repo: ICourseRepository,
    ) -> ReviewService:
        return ReviewService(review_repo, course_repo)
