from dishka import make_async_container, AsyncContainer

from src.infrastructure.di.providers import (
    DatabaseProvider,
    RepositoryProvider,
    ServiceProvider,
)


def create_container() -> AsyncContainer:
    container = make_async_container(
        DatabaseProvider(),
        RepositoryProvider(),
        ServiceProvider(),
    )
    return container
