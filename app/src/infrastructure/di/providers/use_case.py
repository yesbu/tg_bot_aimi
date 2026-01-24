from dishka import Provider, Scope, provide

from src.domain.interfaces.repositories import (
    IUserRepository,
    ISubscriptionPlanRepository,
    ICityRepository,
    ICategoryRepository,
)
from src.domain.interfaces.cache import ICacheClient
from src.application.use_cases.user import (
    GetOrCreateUserUseCase,
    GetUserUseCase,
)
from src.application.use_cases.subscription import (
    GetActiveSubscriptionPlansUseCase,
    BuySubscriptionPlanUseCase
    
)
from src.application.use_cases.payment import CheckPaymentStatusUseCase
from src.application.use_cases.city import GetAllCitiesUseCase
from src.application.use_cases.category import GetAllCategoriesUseCase
from src.infrastructure.payment.airbapay import AirbaPayGateway


class UseCaseProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def provide_get_or_create_user(
        self, 
        user_repo: IUserRepository,
        cache: ICacheClient
    ) -> GetOrCreateUserUseCase:
        return GetOrCreateUserUseCase(user_repo, cache)
        
    @provide(scope=Scope.REQUEST)
    def provide_get_user(
        self,
        user_repo: IUserRepository,
        cache: ICacheClient
    ) -> GetUserUseCase:
        return GetUserUseCase(user_repo, cache)
    
    @provide(scope=Scope.REQUEST)
    def provide_get_active_plans(self, subscription_plan_repo: ISubscriptionPlanRepository) -> GetActiveSubscriptionPlansUseCase:
        return GetActiveSubscriptionPlansUseCase(subscription_plan_repo)

    @provide(scope=Scope.REQUEST)
    def provide_get_all_cities(
        self,
        city_repo: ICityRepository,
        cache: ICacheClient
    ) -> GetAllCitiesUseCase:
        return GetAllCitiesUseCase(city_repo, cache)
    
    @provide(scope=Scope.REQUEST)
    def provide_get_all_categories(
        self,
        category_repo: ICategoryRepository,
        cache: ICacheClient
    ) -> GetAllCategoriesUseCase:
        return GetAllCategoriesUseCase(category_repo, cache)
    
    @provide(scope=Scope.REQUEST)
    def provide_buy_subscription_plan(
        self,
        subscription_plan_repo: ISubscriptionPlanRepository,
        payment_gateway: AirbaPayGateway,
    ) -> BuySubscriptionPlanUseCase:
        return BuySubscriptionPlanUseCase(
            subscription_plan_repo,
            payment_gateway,
        )
    
    @provide(scope=Scope.REQUEST)
    def provide_check_payment_status(
        self,
        payment_gateway: AirbaPayGateway,
    ) -> CheckPaymentStatusUseCase:
        return CheckPaymentStatusUseCase(payment_gateway)