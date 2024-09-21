import redis.asyncio as aioredis
from datetime import timedelta
from typing import Any, Dict
from pydantic import RedisDsn
from app.core.config import settings


class RedisClient:
    def __init__(self, url: str, db: int = 0):
        self.redis = aioredis.from_url(url, db=db, decode_responses=True)

    async def set(self, key: str, value: str) -> Any:
        await self.redis.set(key, value)

    async def get(self, key: str) -> Any:
        return await self.redis.get(key)

    async def setex(self, key: str, expiration: timedelta, value: str) -> Any:
        await self.redis.setex(key, int(expiration.total_seconds()), value)

    async def delete(self, key: str) -> Any:
        return await self.redis.delete(key)

    async def expire(self, key: str, expiration: timedelta) -> Any:
        return await self.redis.expire(key, int(expiration.total_seconds()))


class RedisManager:
    def __init__(self, url: str):
        self.redis_url = url
        self.clients: Dict[int, RedisClient] = {}

    def get_client(self, db: int = 0) -> RedisClient:
        if db not in self.clients:
            self.clients[db] = RedisClient(url=self.redis_url, db=db)
        return self.clients[db]


redis_url = RedisDsn.build(
    scheme="redis",
    host=settings.REDIS_SERVER,
    port=settings.REDIS_PORT,
    password=settings.REDIS_PASSWORD or None,
)
redis_manager = RedisManager(url=str(redis_url))
