"""Redis cache client for caching and session storage."""

from typing import Any

from redis.asyncio import Redis
from redis.asyncio.connection import ConnectionPool

from src.core.config import settings

# Redis connection pool (created lazily)
_redis_pool: ConnectionPool | None = None
_redis_client: Redis | None = None


def get_redis_pool() -> ConnectionPool:
    """
    Get or create Redis connection pool.

    Returns:
        ConnectionPool: Redis connection pool

    Example:
        pool = get_redis_pool()
        client = Redis(connection_pool=pool)
    """
    global _redis_pool
    if _redis_pool is None:
        _redis_pool = ConnectionPool.from_url(
            str(settings.redis_url),
            max_connections=settings.redis_max_connections,
            decode_responses=True,
        )
    return _redis_pool


async def get_redis() -> Redis:
    """
    Get Redis client instance.

    Returns:
        Redis: Async Redis client

    Example:
        redis = await get_redis()
        await redis.set("key", "value", ex=300)
        value = await redis.get("key")
    """
    global _redis_client
    if _redis_client is None:
        pool = get_redis_pool()
        _redis_client = Redis(connection_pool=pool)
    return _redis_client


async def close_redis() -> None:
    """
    Close Redis connection pool.

    Note: Should be called during application shutdown.

    Example:
        @app.on_event("shutdown")
        async def shutdown():
            await close_redis()
    """
    global _redis_client, _redis_pool
    if _redis_client is not None:
        await _redis_client.aclose()
        _redis_client = None
    if _redis_pool is not None:
        await _redis_pool.aclose()
        _redis_pool = None


class CacheService:
    """
    Service for caching operations with common patterns.

    Provides convenience methods for common caching scenarios like
    get/set with TTL, JSON encoding, and cache invalidation.
    """

    def __init__(self, redis: Redis) -> None:
        """
        Initialize cache service.

        Args:
            redis: Redis client instance
        """
        self.redis = redis

    async def get(self, key: str) -> str | None:
        """
        Get value from cache.

        Args:
            key: Cache key

        Returns:
            str | None: Cached value or None if not found

        Example:
            cache = CacheService(await get_redis())
            value = await cache.get("user:123:profile")
        """
        return await self.redis.get(key)  # type: ignore[return-value,no-any-return]

    async def set(
        self,
        key: str,
        value: str | bytes | int | float,
        ttl: int | None = None,
    ) -> bool:
        """
        Set value in cache with optional TTL.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (optional)

        Returns:
            bool: True if successful

        Example:
            cache = CacheService(await get_redis())
            await cache.set("user:123:profile", json.dumps(profile), ttl=300)
        """
        if ttl is not None:
            return bool(await self.redis.setex(key, ttl, value))
        return bool(await self.redis.set(key, value))

    async def delete(self, key: str) -> int:
        """
        Delete key from cache.

        Args:
            key: Cache key to delete

        Returns:
            int: Number of keys deleted (0 or 1)

        Example:
            cache = CacheService(await get_redis())
            await cache.delete("user:123:profile")
        """
        return await self.redis.delete(key)  # type: ignore[return-value,no-any-return]

    async def delete_pattern(self, pattern: str) -> int:
        """
        Delete all keys matching pattern.

        Args:
            pattern: Key pattern (e.g., "user:*", "price:retailer:*")

        Returns:
            int: Number of keys deleted

        Example:
            cache = CacheService(await get_redis())
            # Clear all user caches
            await cache.delete_pattern("user:*")
        """
        keys = []
        async for key in self.redis.scan_iter(match=pattern):
            keys.append(key)

        if keys:
            return await self.redis.delete(*keys)  # type: ignore[return-value,no-any-return]
        return 0

    async def exists(self, key: str) -> bool:
        """
        Check if key exists in cache.

        Args:
            key: Cache key

        Returns:
            bool: True if key exists

        Example:
            cache = CacheService(await get_redis())
            if await cache.exists("user:123:profile"):
                value = await cache.get("user:123:profile")
        """
        return bool(await self.redis.exists(key))

    async def ttl(self, key: str) -> int:
        """
        Get time-to-live for key in seconds.

        Args:
            key: Cache key

        Returns:
            int: TTL in seconds (-2 if key doesn't exist, -1 if no expiry)

        Example:
            cache = CacheService(await get_redis())
            remaining = await cache.ttl("user:123:profile")
        """
        return await self.redis.ttl(key)  # type: ignore[return-value,no-any-return]

    async def increment(self, key: str, amount: int = 1) -> int:
        """
        Increment integer value atomically.

        Args:
            key: Cache key
            amount: Amount to increment by (default: 1)

        Returns:
            int: New value after increment

        Example:
            cache = CacheService(await get_redis())
            # Rate limiting
            count = await cache.increment("ratelimit:user:123:2025-12-01")
            if count > 100:
                raise TooManyRequestsError()
        """
        return await self.redis.incrby(key, amount)  # type: ignore[return-value,no-any-return]

    async def set_hash(self, key: str, mapping: dict[str, Any], ttl: int | None = None) -> bool:
        """
        Store hash (dictionary) in cache.

        Args:
            key: Cache key
            mapping: Dictionary to store
            ttl: Time-to-live in seconds (optional)

        Returns:
            bool: True if successful

        Example:
            cache = CacheService(await get_redis())
            await cache.set_hash(
                "user:123:profile",
                {"name": "John", "email": "john@example.com"},
                ttl=300
            )
        """
        result = await self.redis.hset(key, mapping=mapping)  # type: ignore[arg-type,misc]
        if ttl is not None:
            await self.redis.expire(key, ttl)
        return bool(result)

    async def get_hash(self, key: str) -> dict[str, str]:
        """
        Get hash (dictionary) from cache.

        Args:
            key: Cache key

        Returns:
            dict[str, str]: Cached dictionary (empty if not found)

        Example:
            cache = CacheService(await get_redis())
            profile = await cache.get_hash("user:123:profile")
        """
        return await self.redis.hgetall(key)  # type: ignore[return-value,no-any-return,misc]

    async def ping(self) -> bool:
        """
        Ping Redis to check connectivity.

        Returns:
            bool: True if Redis is responsive

        Example:
            cache = CacheService(await get_redis())
            if not await cache.ping():
                logger.error("Redis connection lost")
        """
        try:
            return await self.redis.ping()  # type: ignore[return-value,no-any-return,misc]
        except Exception:
            return False
