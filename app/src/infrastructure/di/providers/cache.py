from dishka import Provider, Scope, provide
from redis.asyncio import Redis
from typing import AsyncIterable

from src.infrastructure.cache import ICacheClient, RedisClient, get_redis


class CacheProvider(Provider):
    @provide(scope=Scope.APP)
    async def provide_redis(self) -> AsyncIterable[Redis]:
        redis = await get_redis()
        yield redis
        await redis.close()
    
    @provide(scope=Scope.REQUEST, provides=ICacheClient)
    def provide_cache_client(self, redis: Redis) -> RedisClient:
        return RedisClient(redis)
