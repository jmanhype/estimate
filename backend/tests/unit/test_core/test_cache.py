"""Tests for Redis cache client."""

import json
from unittest.mock import AsyncMock

import pytest
from redis.asyncio import Redis
from redis.asyncio.connection import ConnectionPool

from src.core.cache import CacheService, close_redis, get_redis, get_redis_pool


class TestRedisPool:
    """Tests for Redis connection pool management."""

    def test_get_redis_pool(self) -> None:
        """Test getting Redis connection pool."""
        pool = get_redis_pool()
        assert isinstance(pool, ConnectionPool)

        # Should return same instance
        pool2 = get_redis_pool()
        assert pool is pool2

    @pytest.mark.asyncio
    async def test_get_redis(self) -> None:
        """Test getting Redis client."""
        redis = await get_redis()
        assert isinstance(redis, Redis)

        # Should return same instance
        redis2 = await get_redis()
        assert redis is redis2

    @pytest.mark.asyncio
    async def test_close_redis(self) -> None:
        """Test closing Redis connections."""
        # Get client to initialize
        await get_redis()

        # Close should not raise error
        await close_redis()


class TestCacheService:
    """Tests for CacheService operations."""

    @pytest.fixture
    def mock_redis(self) -> AsyncMock:
        """Create mock Redis client."""
        mock = AsyncMock(spec=Redis)
        # Pre-configure all async methods as AsyncMock
        mock.get = AsyncMock()
        mock.set = AsyncMock()
        mock.setex = AsyncMock()
        mock.delete = AsyncMock()
        mock.exists = AsyncMock()
        mock.ttl = AsyncMock()
        mock.incrby = AsyncMock()
        mock.hset = AsyncMock()
        mock.expire = AsyncMock()
        mock.hgetall = AsyncMock()
        mock.ping = AsyncMock()
        return mock

    @pytest.fixture
    def cache_service(self, mock_redis: AsyncMock) -> CacheService:
        """Create CacheService instance with mock Redis."""
        return CacheService(mock_redis)

    @pytest.mark.asyncio
    async def test_get(self, cache_service: CacheService, mock_redis: AsyncMock) -> None:
        """Test getting value from cache."""
        mock_redis.get.return_value = "cached_value"

        result = await cache_service.get("test_key")

        assert result == "cached_value"
        mock_redis.get.assert_called_once_with("test_key")

    @pytest.mark.asyncio
    async def test_get_not_found(
        self, cache_service: CacheService, mock_redis: AsyncMock
    ) -> None:
        """Test getting non-existent key."""
        mock_redis.get.return_value = None

        result = await cache_service.get("missing_key")

        assert result is None

    @pytest.mark.asyncio
    async def test_set_without_ttl(
        self, cache_service: CacheService, mock_redis: AsyncMock
    ) -> None:
        """Test setting value without TTL."""
        mock_redis.set.return_value = True

        result = await cache_service.set("test_key", "test_value")

        assert result is True
        mock_redis.set.assert_called_once_with("test_key", "test_value")

    @pytest.mark.asyncio
    async def test_set_with_ttl(
        self, cache_service: CacheService, mock_redis: AsyncMock
    ) -> None:
        """Test setting value with TTL."""
        mock_redis.setex.return_value = True

        result = await cache_service.set("test_key", "test_value", ttl=300)

        assert result is True
        mock_redis.setex.assert_called_once_with("test_key", 300, "test_value")

    @pytest.mark.asyncio
    async def test_set_with_different_types(
        self, cache_service: CacheService, mock_redis: AsyncMock
    ) -> None:
        """Test setting different value types."""
        mock_redis.set.return_value = True

        # String
        await cache_service.set("str_key", "string_value")
        # Bytes
        await cache_service.set("bytes_key", b"bytes_value")
        # Int
        await cache_service.set("int_key", 42)
        # Float
        await cache_service.set("float_key", 3.14)

        assert mock_redis.set.call_count == 4

    @pytest.mark.asyncio
    async def test_delete(self, cache_service: CacheService, mock_redis: AsyncMock) -> None:
        """Test deleting key."""
        mock_redis.delete.return_value = 1

        result = await cache_service.delete("test_key")

        assert result == 1
        mock_redis.delete.assert_called_once_with("test_key")

    @pytest.mark.asyncio
    async def test_delete_pattern(
        self, cache_service: CacheService, mock_redis: AsyncMock
    ) -> None:
        """Test deleting keys by pattern."""
        # Mock scan_iter to return keys
        async def mock_scan_iter(match: str):  # type: ignore[no-untyped-def]
            for key in ["user:1", "user:2", "user:3"]:
                yield key

        mock_redis.scan_iter = mock_scan_iter
        mock_redis.delete.return_value = 3

        result = await cache_service.delete_pattern("user:*")

        assert result == 3
        mock_redis.delete.assert_called_once_with("user:1", "user:2", "user:3")

    @pytest.mark.asyncio
    async def test_delete_pattern_no_matches(
        self, cache_service: CacheService, mock_redis: AsyncMock
    ) -> None:
        """Test deleting with pattern that matches no keys."""

        async def mock_scan_iter(match: str):  # type: ignore[no-untyped-def]
            return
            yield  # Make it async generator

        mock_redis.scan_iter = mock_scan_iter

        result = await cache_service.delete_pattern("nonexistent:*")

        assert result == 0
        mock_redis.delete.assert_not_called()

    @pytest.mark.asyncio
    async def test_exists(self, cache_service: CacheService, mock_redis: AsyncMock) -> None:
        """Test checking if key exists."""
        mock_redis.exists.return_value = 1

        result = await cache_service.exists("test_key")

        assert result is True
        mock_redis.exists.assert_called_once_with("test_key")

    @pytest.mark.asyncio
    async def test_exists_not_found(
        self, cache_service: CacheService, mock_redis: AsyncMock
    ) -> None:
        """Test checking non-existent key."""
        mock_redis.exists.return_value = 0

        result = await cache_service.exists("missing_key")

        assert result is False

    @pytest.mark.asyncio
    async def test_ttl(self, cache_service: CacheService, mock_redis: AsyncMock) -> None:
        """Test getting TTL."""
        mock_redis.ttl.return_value = 300

        result = await cache_service.ttl("test_key")

        assert result == 300
        mock_redis.ttl.assert_called_once_with("test_key")

    @pytest.mark.asyncio
    async def test_ttl_no_expiry(
        self, cache_service: CacheService, mock_redis: AsyncMock
    ) -> None:
        """Test TTL for key with no expiry."""
        mock_redis.ttl.return_value = -1

        result = await cache_service.ttl("persistent_key")

        assert result == -1

    @pytest.mark.asyncio
    async def test_ttl_key_not_found(
        self, cache_service: CacheService, mock_redis: AsyncMock
    ) -> None:
        """Test TTL for non-existent key."""
        mock_redis.ttl.return_value = -2

        result = await cache_service.ttl("missing_key")

        assert result == -2

    @pytest.mark.asyncio
    async def test_increment(
        self, cache_service: CacheService, mock_redis: AsyncMock
    ) -> None:
        """Test incrementing value."""
        mock_redis.incrby.return_value = 6

        result = await cache_service.increment("counter_key", amount=5)

        assert result == 6
        mock_redis.incrby.assert_called_once_with("counter_key", 5)

    @pytest.mark.asyncio
    async def test_increment_default_amount(
        self, cache_service: CacheService, mock_redis: AsyncMock
    ) -> None:
        """Test incrementing with default amount."""
        mock_redis.incrby.return_value = 2

        result = await cache_service.increment("counter_key")

        assert result == 2
        mock_redis.incrby.assert_called_once_with("counter_key", 1)

    @pytest.mark.asyncio
    async def test_set_hash(
        self, cache_service: CacheService, mock_redis: AsyncMock
    ) -> None:
        """Test storing hash."""
        mock_redis.hset.return_value = 1

        mapping = {"name": "John", "email": "john@example.com"}
        result = await cache_service.set_hash("user:123", mapping)

        assert result is True
        mock_redis.hset.assert_called_once_with("user:123", mapping=mapping)

    @pytest.mark.asyncio
    async def test_set_hash_with_ttl(
        self, cache_service: CacheService, mock_redis: AsyncMock
    ) -> None:
        """Test storing hash with TTL."""
        mock_redis.hset.return_value = 1

        mapping = {"name": "John"}
        result = await cache_service.set_hash("user:123", mapping, ttl=300)

        assert result is True
        mock_redis.hset.assert_called_once_with("user:123", mapping=mapping)
        mock_redis.expire.assert_called_once_with("user:123", 300)

    @pytest.mark.asyncio
    async def test_get_hash(
        self, cache_service: CacheService, mock_redis: AsyncMock
    ) -> None:
        """Test getting hash."""
        expected = {"name": "John", "email": "john@example.com"}
        mock_redis.hgetall.return_value = expected

        result = await cache_service.get_hash("user:123")

        assert result == expected
        mock_redis.hgetall.assert_called_once_with("user:123")

    @pytest.mark.asyncio
    async def test_get_hash_not_found(
        self, cache_service: CacheService, mock_redis: AsyncMock
    ) -> None:
        """Test getting non-existent hash."""
        mock_redis.hgetall.return_value = {}

        result = await cache_service.get_hash("missing:key")

        assert result == {}

    @pytest.mark.asyncio
    async def test_ping_success(
        self, cache_service: CacheService, mock_redis: AsyncMock
    ) -> None:
        """Test pinging Redis successfully."""
        mock_redis.ping.return_value = True

        result = await cache_service.ping()

        assert result is True
        mock_redis.ping.assert_called_once()

    @pytest.mark.asyncio
    async def test_ping_failure(
        self, cache_service: CacheService, mock_redis: AsyncMock
    ) -> None:
        """Test ping when Redis is down."""
        mock_redis.ping.side_effect = Exception("Connection refused")

        result = await cache_service.ping()

        assert result is False


class TestCacheServiceIntegration:
    """Integration tests for common cache patterns."""

    @pytest.fixture
    def mock_redis(self) -> AsyncMock:
        """Create mock Redis client."""
        mock = AsyncMock(spec=Redis)
        mock.get = AsyncMock()
        mock.set = AsyncMock()
        mock.setex = AsyncMock()
        mock.incrby = AsyncMock()
        return mock

    @pytest.fixture
    def cache_service(self, mock_redis: AsyncMock) -> CacheService:
        """Create CacheService instance with mock Redis."""
        return CacheService(mock_redis)

    @pytest.mark.asyncio
    async def test_cache_aside_pattern(
        self, cache_service: CacheService, mock_redis: AsyncMock
    ) -> None:
        """Test cache-aside (lazy loading) pattern."""
        mock_redis.get.return_value = None  # Cache miss
        mock_redis.setex.return_value = True

        # Simulate cache-aside pattern
        cached = await cache_service.get("user:123:profile")
        if cached is None:
            # Fetch from database (mocked)
            profile = {"id": 123, "name": "John"}
            await cache_service.set(
                "user:123:profile", json.dumps(profile), ttl=300
            )

        mock_redis.get.assert_called_once()
        mock_redis.setex.assert_called_once()

    @pytest.mark.asyncio
    async def test_rate_limiting_pattern(
        self, cache_service: CacheService, mock_redis: AsyncMock
    ) -> None:
        """Test rate limiting pattern."""
        mock_redis.incrby.return_value = 1
        mock_redis.setex.return_value = True

        # Simulate rate limiting
        key = "ratelimit:user:123:2025-12-01-09:00"
        count = await cache_service.increment(key)
        if count == 1:
            # First request in this window, set TTL
            await cache_service.set(key, count, ttl=3600)

        assert count == 1
        mock_redis.incrby.assert_called_once()
