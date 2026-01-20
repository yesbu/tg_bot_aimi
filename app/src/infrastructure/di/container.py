from dishka import make_async_container, AsyncContainer

from src.infrastructure.di.providers.database import DatabaseProvider
from src.infrastructure.di.providers.repository import RepositoryProvider
from src.infrastructure.di.providers.cache import CacheProvider
from src.infrastructure.di.providers.use_case import UseCaseProvider


def create_container() -> AsyncContainer:
    return make_async_container(
        DatabaseProvider(),
        CacheProvider(),
        RepositoryProvider(),
        UseCaseProvider(),
    )
