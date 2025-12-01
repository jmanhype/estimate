"""Comprehensive tests for application configuration module."""

import pytest
from pydantic import ValidationError

from src.core.config import Settings, get_settings


class TestSettingsDefaults:
    """Test Settings class with default values."""

    def test_settings_initialization_with_defaults(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Settings should initialize with correct default values."""
        # Clear any environment variables set by CI
        monkeypatch.delenv("ENVIRONMENT", raising=False)
        monkeypatch.delenv("DATABASE_URL", raising=False)
        monkeypatch.delenv("REDIS_URL", raising=False)

        settings = Settings()

        # Environment defaults
        assert settings.environment == "development"
        assert settings.log_level == "INFO"

        # Database defaults
        assert (
            str(settings.database_url)
            == "postgresql://estimate:estimate@localhost:5432/estimate_dev"
        )
        assert settings.db_pool_size == 10
        assert settings.db_max_overflow == 20
        assert settings.db_pool_timeout == 30
        assert settings.db_echo is False

        # Redis defaults
        assert str(settings.redis_url) == "redis://localhost:6379/0"
        assert settings.redis_max_connections == 10

        # API defaults
        assert settings.api_title == "EstiMate API"
        assert settings.api_version == "1.0.0"
        assert settings.api_prefix == "/api/v1"

        # CORS defaults
        assert settings.cors_origins == ["http://localhost:3000", "http://localhost:5173"]
        assert settings.cors_allow_credentials is True

        # Security defaults
        assert settings.jwt_secret == "change-me-in-production"
        assert settings.jwt_algorithm == "HS256"
        assert settings.jwt_expiration_minutes == 60


class TestSettingsEnvironmentVariables:
    """Test Settings class with custom environment variables."""

    def test_settings_loads_custom_environment(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Settings should load custom values from environment variables."""
        monkeypatch.setenv("ENVIRONMENT", "production")
        monkeypatch.setenv("LOG_LEVEL", "ERROR")
        monkeypatch.setenv("DATABASE_URL", "postgresql://prod:secret@db.example.com:5432/proddb")
        monkeypatch.setenv("REDIS_URL", "redis://cache.example.com:6379/1")
        monkeypatch.setenv("JWT_SECRET", "super-secret-key")

        settings = Settings()

        assert settings.environment == "production"
        assert settings.log_level == "ERROR"
        assert "db.example.com" in str(settings.database_url)
        assert "cache.example.com" in str(settings.redis_url)
        assert settings.jwt_secret == "super-secret-key"

    def test_settings_loads_custom_integers(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Settings should load and validate integer fields from environment."""
        monkeypatch.setenv("DB_POOL_SIZE", "25")
        monkeypatch.setenv("DB_MAX_OVERFLOW", "50")
        monkeypatch.setenv("DB_POOL_TIMEOUT", "60")
        monkeypatch.setenv("REDIS_MAX_CONNECTIONS", "20")
        monkeypatch.setenv("JWT_EXPIRATION_MINUTES", "120")

        settings = Settings()

        assert settings.db_pool_size == 25
        assert settings.db_max_overflow == 50
        assert settings.db_pool_timeout == 60
        assert settings.redis_max_connections == 20
        assert settings.jwt_expiration_minutes == 120

    def test_settings_loads_boolean_fields(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Settings should correctly parse boolean environment variables."""
        monkeypatch.setenv("DB_ECHO", "true")
        monkeypatch.setenv("CORS_ALLOW_CREDENTIALS", "false")

        settings = Settings()

        assert settings.db_echo is True
        assert settings.cors_allow_credentials is False

    def test_settings_ignores_extra_fields(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Settings should ignore extra environment variables not in schema."""
        monkeypatch.setenv("UNKNOWN_FIELD", "should-be-ignored")

        settings = Settings()

        # Should not raise an error
        assert not hasattr(settings, "UNKNOWN_FIELD")


class TestSettingsValidation:
    """Test Settings validation rules."""

    def test_invalid_environment_literal(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Settings should reject invalid environment values."""
        monkeypatch.setenv("ENVIRONMENT", "invalid-env")

        with pytest.raises(ValidationError) as exc_info:
            Settings()

        assert "environment" in str(exc_info.value).lower()

    def test_invalid_log_level_literal(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Settings should reject invalid log level values."""
        monkeypatch.setenv("LOG_LEVEL", "TRACE")

        with pytest.raises(ValidationError) as exc_info:
            Settings()

        assert "log_level" in str(exc_info.value).lower()

    def test_invalid_database_url_format(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Settings should reject malformed database URLs."""
        monkeypatch.setenv("DATABASE_URL", "not-a-valid-url")

        with pytest.raises(ValidationError) as exc_info:
            Settings()

        assert "database_url" in str(exc_info.value).lower()

    def test_invalid_redis_url_format(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Settings should reject malformed Redis URLs."""
        monkeypatch.setenv("REDIS_URL", "invalid-redis-url")

        with pytest.raises(ValidationError) as exc_info:
            Settings()

        assert "redis_url" in str(exc_info.value).lower()


class TestSettingsConstraints:
    """Test Settings field constraints (ge, le validators)."""

    def test_db_pool_size_minimum_constraint(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """DB pool size should enforce minimum value of 1."""
        monkeypatch.setenv("DB_POOL_SIZE", "0")

        with pytest.raises(ValidationError) as exc_info:
            Settings()

        error_str = str(exc_info.value).lower()
        assert "db_pool_size" in error_str
        assert "greater than or equal to 1" in error_str

    def test_db_pool_size_maximum_constraint(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """DB pool size should enforce maximum value of 100."""
        monkeypatch.setenv("DB_POOL_SIZE", "101")

        with pytest.raises(ValidationError) as exc_info:
            Settings()

        error_str = str(exc_info.value).lower()
        assert "db_pool_size" in error_str
        assert "less than or equal to 100" in error_str

    def test_db_max_overflow_minimum_constraint(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """DB max overflow should enforce minimum value of 0."""
        monkeypatch.setenv("DB_MAX_OVERFLOW", "-1")

        with pytest.raises(ValidationError) as exc_info:
            Settings()

        error_str = str(exc_info.value).lower()
        assert "db_max_overflow" in error_str
        assert "greater than or equal to 0" in error_str

    def test_db_max_overflow_maximum_constraint(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """DB max overflow should enforce maximum value of 100."""
        monkeypatch.setenv("DB_MAX_OVERFLOW", "101")

        with pytest.raises(ValidationError) as exc_info:
            Settings()

        error_str = str(exc_info.value).lower()
        assert "db_max_overflow" in error_str
        assert "less than or equal to 100" in error_str

    def test_db_pool_timeout_minimum_constraint(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """DB pool timeout should enforce minimum value of 1."""
        monkeypatch.setenv("DB_POOL_TIMEOUT", "0")

        with pytest.raises(ValidationError) as exc_info:
            Settings()

        error_str = str(exc_info.value).lower()
        assert "db_pool_timeout" in error_str
        assert "greater than or equal to 1" in error_str

    def test_db_pool_timeout_maximum_constraint(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """DB pool timeout should enforce maximum value of 300."""
        monkeypatch.setenv("DB_POOL_TIMEOUT", "301")

        with pytest.raises(ValidationError) as exc_info:
            Settings()

        error_str = str(exc_info.value).lower()
        assert "db_pool_timeout" in error_str
        assert "less than or equal to 300" in error_str

    def test_redis_max_connections_minimum_constraint(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Redis max connections should enforce minimum value of 1."""
        monkeypatch.setenv("REDIS_MAX_CONNECTIONS", "0")

        with pytest.raises(ValidationError) as exc_info:
            Settings()

        error_str = str(exc_info.value).lower()
        assert "redis_max_connections" in error_str
        assert "greater than or equal to 1" in error_str

    def test_redis_max_connections_maximum_constraint(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Redis max connections should enforce maximum value of 100."""
        monkeypatch.setenv("REDIS_MAX_CONNECTIONS", "101")

        with pytest.raises(ValidationError) as exc_info:
            Settings()

        error_str = str(exc_info.value).lower()
        assert "redis_max_connections" in error_str
        assert "less than or equal to 100" in error_str

    def test_jwt_expiration_minimum_constraint(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """JWT expiration should enforce minimum value of 5 minutes."""
        monkeypatch.setenv("JWT_EXPIRATION_MINUTES", "4")

        with pytest.raises(ValidationError) as exc_info:
            Settings()

        error_str = str(exc_info.value).lower()
        assert "jwt_expiration_minutes" in error_str
        assert "greater than or equal to 5" in error_str

    def test_jwt_expiration_maximum_constraint(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """JWT expiration should enforce maximum value of 43200 minutes (30 days)."""
        monkeypatch.setenv("JWT_EXPIRATION_MINUTES", "43201")

        with pytest.raises(ValidationError) as exc_info:
            Settings()

        error_str = str(exc_info.value).lower()
        assert "jwt_expiration_minutes" in error_str
        assert "less than or equal to 43200" in error_str


class TestGetSettingsFunction:
    """Test get_settings() function and caching behavior."""

    def test_get_settings_returns_settings_instance(self) -> None:
        """get_settings() should return a Settings instance."""
        settings = get_settings()

        assert isinstance(settings, Settings)

    def test_get_settings_caching_returns_same_instance(self) -> None:
        """get_settings() should return the same cached instance on multiple calls."""
        # Clear the cache first
        get_settings.cache_clear()

        settings1 = get_settings()
        settings2 = get_settings()

        # Should be the exact same object (same id in memory)
        assert settings1 is settings2

    def test_get_settings_cache_can_be_cleared(self) -> None:
        """get_settings() cache should be clearable."""
        # Get initial settings
        settings1 = get_settings()

        # Clear cache
        get_settings.cache_clear()

        # Get new settings
        settings2 = get_settings()

        # Should be different objects after cache clear
        assert settings1 is not settings2

    def test_get_settings_respects_environment_changes_after_cache_clear(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """get_settings() should pick up environment changes after cache is cleared."""
        # Clear cache and get initial settings
        get_settings.cache_clear()
        settings1 = get_settings()
        initial_env = settings1.environment

        # Change environment variable
        new_env = "production" if initial_env != "production" else "staging"
        monkeypatch.setenv("ENVIRONMENT", new_env)

        # Without clearing cache, should still return old settings
        settings2 = get_settings()
        assert settings2.environment == initial_env

        # After clearing cache, should get new settings
        get_settings.cache_clear()
        settings3 = get_settings()
        assert settings3.environment == new_env
