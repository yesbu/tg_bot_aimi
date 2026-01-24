from dishka import Provider, Scope, provide
from typing import AsyncIterable
from redis.asyncio import Redis
from loguru import logger

from src.domain.interfaces.cache import ICacheClient
from src.infrastructure.cache import RedisClient
from src.settings import settings


class CacheProvider(Provider):
    @provide(scope=Scope.APP)
    async def provide_redis(self) -> AsyncIterable[Redis]:
        logger.info(f"Connecting to Redis at {settings.redis.host}:{settings.redis.port}")
        
        redis = Redis(
            host=settings.redis.host,
            port=settings.redis.port,
            db=settings.redis.db,
            password=settings.redis.password,
            decode_responses=False,
            socket_connect_timeout=5,
            socket_timeout=5,
            retry_on_timeout=True,
            health_check_interval=30,
        )
        
        try:
            await redis.ping()
            logger.info("Successfully connected to Redis")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            await redis.close()
            raise
        
        yield redis
        
        await redis.close()
        logger.info("Redis connection closed")
    
    @provide(scope=Scope.REQUEST)
    def provide_cache_client(self, redis: Redis) -> ICacheClient:
        return RedisClient(redis)
