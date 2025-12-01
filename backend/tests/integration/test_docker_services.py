"""Integration tests for Docker Compose services."""

import pytest
import redis
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError

from src.core.config import get_settings


@pytest.mark.integration
class TestPostgreSQLConnection:
    """Test PostgreSQL database connectivity via Docker Compose."""

    def test_postgresql_service_is_running(self) -> None:
        """PostgreSQL container should be accessible and accepting connections."""
        settings = get_settings()
        database_url = str(settings.database_url)

        # Create engine with minimal pool to test connection only
        engine = create_engine(database_url, pool_pre_ping=True, pool_size=1)

        try:
            # Test connection with simple query
            with engine.connect() as connection:
                result = connection.execute(text("SELECT 1"))
                assert result.scalar() == 1
        except OperationalError as exc:
            pytest.fail(
                f"PostgreSQL service not available. "
                f"Ensure 'docker-compose up -d postgres' is running. Error: {exc}"
            )
        finally:
            engine.dispose()

    def test_postgresql_database_exists(self) -> None:
        """PostgreSQL database specified in config should exist."""
        settings = get_settings()
        database_url = str(settings.database_url)

        engine = create_engine(database_url, pool_pre_ping=True, pool_size=1)

        try:
            with engine.connect() as connection:
                # Query current database name
                result = connection.execute(text("SELECT current_database()"))
                db_name = result.scalar()

                # Should match the database in our connection string
                assert db_name is not None
                assert len(db_name) > 0
        except OperationalError as exc:
            pytest.fail(f"Could not query PostgreSQL database: {exc}")
        finally:
            engine.dispose()

    def test_postgresql_version(self) -> None:
        """PostgreSQL should be version 15 or higher."""
        settings = get_settings()
        database_url = str(settings.database_url)

        engine = create_engine(database_url, pool_pre_ping=True, pool_size=1)

        try:
            with engine.connect() as connection:
                result = connection.execute(text("SHOW server_version"))
                version_string = result.scalar()

                # Extract major version (e.g., "15.3" -> 15)
                major_version = int(version_string.split(".")[0])
                assert (
                    major_version >= 15
                ), f"PostgreSQL version {version_string} is below required 15+"
        except OperationalError as exc:
            pytest.fail(f"Could not check PostgreSQL version: {exc}")
        finally:
            engine.dispose()


@pytest.mark.integration
class TestRedisConnection:
    """Test Redis cache connectivity via Docker Compose."""

    def test_redis_service_is_running(self) -> None:
        """Redis container should be accessible and accepting connections."""
        settings = get_settings()
        redis_url = str(settings.redis_url)

        try:
            # Create Redis client
            client = redis.from_url(redis_url, decode_responses=True)

            # Test connection with ping
            assert client.ping() is True
        except redis.ConnectionError as exc:
            pytest.fail(
                f"Redis service not available. "
                f"Ensure 'docker-compose up -d redis' is running. Error: {exc}"
            )
        finally:
            client.close()

    def test_redis_can_set_and_get_values(self) -> None:
        """Redis should support basic set/get operations."""
        settings = get_settings()
        redis_url = str(settings.redis_url)

        client = redis.from_url(redis_url, decode_responses=True)

        try:
            # Set a test value
            test_key = "integration_test_key"
            test_value = "integration_test_value"

            client.set(test_key, test_value, ex=60)  # Expire in 60 seconds

            # Get the value back
            retrieved = client.get(test_key)
            assert retrieved == test_value

            # Clean up
            client.delete(test_key)
        except redis.RedisError as exc:
            pytest.fail(f"Redis operations failed: {exc}")
        finally:
            client.close()

    def test_redis_version(self) -> None:
        """Redis should be version 7 or higher."""
        settings = get_settings()
        redis_url = str(settings.redis_url)

        client = redis.from_url(redis_url, decode_responses=True)

        try:
            info = client.info("server")
            version_string = info["redis_version"]

            # Extract major version (e.g., "7.2.3" -> 7)
            major_version = int(version_string.split(".")[0])
            assert major_version >= 7, f"Redis version {version_string} is below required 7+"
        except redis.RedisError as exc:
            pytest.fail(f"Could not check Redis version: {exc}")
        finally:
            client.close()


@pytest.mark.integration
class TestEnvironmentConfiguration:
    """Test environment variable loading in realistic scenarios."""

    def test_settings_loads_from_env_file_if_present(self) -> None:
        """Settings should load from .env file in backend directory."""
        # This test verifies the integration between pydantic-settings and .env files
        settings = get_settings()

        # Should successfully load settings without errors
        assert settings is not None
        assert settings.environment in ["development", "staging", "production", "test"]
        assert settings.log_level in ["DEBUG", "INFO", "WARNING", "ERROR"]

    def test_database_url_is_valid_postgres_dsn(self) -> None:
        """Database URL should be a valid PostgreSQL DSN."""
        settings = get_settings()

        db_url = str(settings.database_url)

        # Should start with postgresql://
        assert db_url.startswith("postgresql://"), f"Invalid database URL: {db_url}"

        # Should contain required components
        assert "@" in db_url, "Database URL missing credentials separator"
        assert ":" in db_url, "Database URL missing port separator"
        assert "/" in db_url.split("@")[1], "Database URL missing database name"

    def test_redis_url_is_valid_redis_dsn(self) -> None:
        """Redis URL should be a valid Redis DSN."""
        settings = get_settings()

        redis_url = str(settings.redis_url)

        # Should start with redis://
        assert redis_url.startswith("redis://"), f"Invalid Redis URL: {redis_url}"

        # Should contain required components
        assert ":" in redis_url, "Redis URL missing port separator"
        assert "/" in redis_url, "Redis URL missing database number"

    def test_all_integer_constraints_are_within_bounds(self) -> None:
        """All integer settings should be within their defined constraints."""
        settings = get_settings()

        # Database pool settings
        assert 1 <= settings.db_pool_size <= 100
        assert 0 <= settings.db_max_overflow <= 100
        assert 1 <= settings.db_pool_timeout <= 300

        # Redis settings
        assert 1 <= settings.redis_max_connections <= 100

        # JWT settings
        assert 5 <= settings.jwt_expiration_minutes <= 43200
