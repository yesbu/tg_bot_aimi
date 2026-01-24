from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.interfaces.repositories import (
    IUserRepository,
    ISubscriptionPlanRepository,
    ICityRepository,
    ICategoryRepository,
    IPaymentRepository,
    ISubscriptionRepository,
)
from src.infrastructure.persistence.repositories.user_repository import UserRepository
from src.infrastructure.persistence.repositories.subscription_plan_repository import SubscriptionPlanRepository
from src.infrastructure.persistence.repositories.city_repository import CityRepository
from src.infrastructure.persistence.repositories.category_repository import CategoryRepository
from src.infrastructure.persistence.repositories.payment_repository import PaymentRepository
from src.infrastructure.persistence.repositories.subscription_repository import SubscriptionRepository


class RepositoryProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def provide_user_repository(self, session: AsyncSession) -> IUserRepository:
        return UserRepository(session)
       
    @provide(scope=Scope.REQUEST)
    def provide_subscription_plan_repository(self, session: AsyncSession) -> ISubscriptionPlanRepository:
        return SubscriptionPlanRepository(session)
   
    @provide(scope=Scope.REQUEST)
    def provide_city_repository(self, session: AsyncSession) -> ICityRepository:
        return CityRepository(session)
    
    @provide(scope=Scope.REQUEST)
    def provide_category_repository(self, session: AsyncSession) -> ICategoryRepository:
        return CategoryRepository(session)
    
    @provide(scope=Scope.REQUEST)
    def provide_payment_repository(self, session: AsyncSession) -> IPaymentRepository:
        return PaymentRepository(session)
    
    @provide(scope=Scope.REQUEST)
    def provide_subscription_repository(self, session: AsyncSession) -> ISubscriptionRepository:
        return SubscriptionRepository(session)
