from redis.asyncio import Redis
from loguru import logger

from src.settings import settings


async def get_redis() -> Redis:
    logger.info(f"Connecting to Redis at {settings.redis.host}:{settings.redis.port}")
    
    redis = Redis(
        host=settings.redis.host,
        port=settings.redis.port,
        db=settings.redis.db,
        password=settings.redis.password if settings.redis.password else None,
        decode_responses=False,
        socket_connect_timeout=5,
        socket_timeout=5,
    )
    
    try:
        await redis.ping()
        logger.info("Successfully connected to Redis")
    except Exception as e:
        logger.error(f"Failed to connect to Redis: {e}")
        raise
    
    return redis


async def close_redis(redis: Redis):
    await redis.close()
    logger.info("Redis connection closed")
