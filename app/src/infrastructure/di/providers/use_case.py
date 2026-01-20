from dishka import Provider, Scope, provide

from src.domain.interfaces.repositories import IUserRepository, ISubscriptionPlanRepository
from src.domain.interfaces.cache import ICacheClient
from src.application.use_cases.user import (
    GetOrCreateUserUseCase,
    RegisterUserUseCase,
    GetUserUseCase,
    UpdateUserRoleUseCase,
)
from src.application.use_cases.subscription import (
    GetActiveSubscriptionPlansUseCase,
    GetSubscriptionPlanByIdUseCase,
)
from src.application.use_cases.city import GetAllCitiesUseCase
from src.application.use_cases.category import GetAllCategoriesUseCase
from src.infrastructure.persistence.repositories import CityRepository, CategoryRepository


class UseCaseProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def provide_get_or_create_user(
        self, 
        user_repo: IUserRepository,
        cache: ICacheClient
    ) -> GetOrCreateUserUseCase:
        return GetOrCreateUserUseCase(user_repo, cache)
    
    @provide(scope=Scope.REQUEST)
    def provide_register_user(self, user_repo: IUserRepository) -> RegisterUserUseCase:
        return RegisterUserUseCase(user_repo)
    
    @provide(scope=Scope.REQUEST)
    def provide_get_user(
        self,
        user_repo: IUserRepository,
        cache: ICacheClient
    ) -> GetUserUseCase:
        return GetUserUseCase(user_repo, cache)
    
    @provide(scope=Scope.REQUEST)
    def provide_update_user_role(self, user_repo: IUserRepository) -> UpdateUserRoleUseCase:
        return UpdateUserRoleUseCase(user_repo)
    
    @provide(scope=Scope.REQUEST)
    def provide_get_active_plans(self, subscription_plan_repo: ISubscriptionPlanRepository) -> GetActiveSubscriptionPlansUseCase:
        return GetActiveSubscriptionPlansUseCase(subscription_plan_repo)

    @provide(scope=Scope.REQUEST)
    def provide_get_plan_by_id(self, subscription_plan_repo: ISubscriptionPlanRepository) -> GetSubscriptionPlanByIdUseCase:
        return GetSubscriptionPlanByIdUseCase(subscription_plan_repo)
    
    @provide(scope=Scope.REQUEST)
    def provide_get_all_cities(
        self,
        city_repo: CityRepository,
        cache: ICacheClient
    ) -> GetAllCitiesUseCase:
        return GetAllCitiesUseCase(city_repo, cache)
    
    @provide(scope=Scope.REQUEST)
    def provide_get_all_categories(
        self,
        category_repo: CategoryRepository,
        cache: ICacheClient
    ) -> GetAllCategoriesUseCase:
        return GetAllCategoriesUseCase(category_repo, cache)
