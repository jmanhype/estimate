"""Tests for authentication and authorization utilities."""

from datetime import UTC, datetime, timedelta

import jwt
import pytest
from fastapi.security import HTTPAuthorizationCredentials

from src.core.auth import (
    AuthenticationError,
    AuthorizationError,
    TokenPayload,
    decode_jwt,
    get_current_user,
    require_authenticated,
    require_subscription_tier,
)
from src.core.config import settings


class TestTokenPayload:
    """Tests for TokenPayload model."""

    def test_token_payload_minimal(self):
        """Test TokenPayload with minimal required fields."""
        payload = TokenPayload(
            sub="123e4567-e89b-12d3-a456-426614174000",
            exp=int(datetime.now(tz=UTC).timestamp()) + 3600,
            iat=int(datetime.now(tz=UTC).timestamp()),
        )

        assert payload.sub == "123e4567-e89b-12d3-a456-426614174000"
        assert payload.email is None
        assert payload.role is None
        assert payload.app_metadata == {}
        assert payload.user_metadata == {}

    def test_token_payload_full(self):
        """Test TokenPayload with all fields."""
        now = datetime.now(tz=UTC)
        payload = TokenPayload(
            sub="123e4567-e89b-12d3-a456-426614174000",
            email="user@example.com",
            role="authenticated",
            aud="authenticated",
            exp=int((now + timedelta(hours=1)).timestamp()),
            iat=int(now.timestamp()),
            app_metadata={"subscription_tier": "pro"},
            user_metadata={"name": "John Doe"},
        )

        assert payload.sub == "123e4567-e89b-12d3-a456-426614174000"
        assert payload.email == "user@example.com"
        assert payload.role == "authenticated"
        assert payload.aud == "authenticated"
        assert payload.app_metadata == {"subscription_tier": "pro"}
        assert payload.user_metadata == {"name": "John Doe"}


class TestDecodeJWT:
    """Tests for decode_jwt function."""

    def test_decode_valid_token(self):
        """Test decoding a valid JWT token."""
        now = datetime.now(tz=UTC)
        exp = now + timedelta(hours=1)
        payload_data = {
            "sub": "123e4567-e89b-12d3-a456-426614174000",
            "email": "user@example.com",
            "role": "authenticated",
            "aud": "authenticated",
            "exp": int(exp.timestamp()),
            "iat": int(now.timestamp()),
            "app_metadata": {"subscription_tier": "free"},
            "user_metadata": {},
        }

        token = jwt.encode(payload_data, settings.jwt_secret, algorithm=settings.jwt_algorithm)
        result = decode_jwt(token)

        assert isinstance(result, TokenPayload)
        assert result.sub == "123e4567-e89b-12d3-a456-426614174000"
        assert result.email == "user@example.com"
        assert result.role == "authenticated"

    def test_decode_expired_token(self):
        """Test decoding an expired token raises error."""
        now = datetime.now(tz=UTC)
        exp = now - timedelta(hours=1)  # Expired 1 hour ago
        payload_data = {
            "sub": "123e4567-e89b-12d3-a456-426614174000",
            "email": "user@example.com",
            "aud": "authenticated",
            "exp": int(exp.timestamp()),
            "iat": int((now - timedelta(hours=2)).timestamp()),
        }

        token = jwt.encode(payload_data, settings.jwt_secret, algorithm=settings.jwt_algorithm)

        with pytest.raises(AuthenticationError) as exc_info:
            decode_jwt(token)

        assert exc_info.value.status_code == 401
        assert "expired" in str(exc_info.value.detail).lower()

    def test_decode_invalid_signature(self):
        """Test decoding a token with invalid signature raises error."""
        now = datetime.now(tz=UTC)
        payload_data = {
            "sub": "123e4567-e89b-12d3-a456-426614174000",
            "aud": "authenticated",
            "exp": int((now + timedelta(hours=1)).timestamp()),
            "iat": int(now.timestamp()),
        }

        # Encode with wrong secret
        token = jwt.encode(payload_data, "wrong-secret", algorithm=settings.jwt_algorithm)

        with pytest.raises(AuthenticationError) as exc_info:
            decode_jwt(token)

        assert exc_info.value.status_code == 401
        assert "Invalid token" in exc_info.value.detail

    def test_decode_malformed_token(self):
        """Test decoding a malformed token raises error."""
        with pytest.raises(AuthenticationError) as exc_info:
            decode_jwt("not.a.valid.jwt")

        assert exc_info.value.status_code == 401

    def test_decode_token_missing_expiration(self):
        """Test decoding a token without expiration raises error."""
        payload_data = {
            "sub": "123e4567-e89b-12d3-a456-426614174000",
            "aud": "authenticated",
            # Missing 'exp'
        }

        token = jwt.encode(payload_data, settings.jwt_secret, algorithm=settings.jwt_algorithm)

        with pytest.raises(AuthenticationError) as exc_info:
            decode_jwt(token)

        assert "expiration" in str(exc_info.value.detail).lower()

    def test_decode_token_wrong_audience(self):
        """Test decoding a token with wrong audience raises error."""
        now = datetime.now(tz=UTC)
        payload_data = {
            "sub": "123e4567-e89b-12d3-a456-426614174000",
            "aud": "wrong-audience",  # Wrong audience
            "exp": int((now + timedelta(hours=1)).timestamp()),
            "iat": int(now.timestamp()),
        }

        token = jwt.encode(payload_data, settings.jwt_secret, algorithm=settings.jwt_algorithm)

        with pytest.raises(AuthenticationError) as exc_info:
            decode_jwt(token)

        assert exc_info.value.status_code == 401


class TestGetCurrentUser:
    """Tests for get_current_user dependency."""

    @pytest.mark.asyncio
    async def test_get_current_user_valid_token(self):
        """Test getting current user with valid token."""
        now = datetime.now(tz=UTC)
        payload_data = {
            "sub": "123e4567-e89b-12d3-a456-426614174000",
            "email": "user@example.com",
            "aud": "authenticated",
            "exp": int((now + timedelta(hours=1)).timestamp()),
            "iat": int(now.timestamp()),
        }

        token = jwt.encode(payload_data, settings.jwt_secret, algorithm=settings.jwt_algorithm)
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)

        result = await get_current_user(credentials)

        assert isinstance(result, TokenPayload)
        assert result.sub == "123e4567-e89b-12d3-a456-426614174000"
        assert result.email == "user@example.com"

    @pytest.mark.asyncio
    async def test_get_current_user_invalid_token(self):
        """Test getting current user with invalid token raises error."""
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="invalid-token")

        with pytest.raises(AuthenticationError):
            await get_current_user(credentials)


class TestRequireAuthenticated:
    """Tests for require_authenticated dependency."""

    @pytest.mark.asyncio
    async def test_require_authenticated_success(self):
        """Test require_authenticated passes through valid user."""
        user = TokenPayload(
            sub="123e4567-e89b-12d3-a456-426614174000",
            email="user@example.com",
            exp=int((datetime.now(tz=UTC) + timedelta(hours=1)).timestamp()),
            iat=int(datetime.now(tz=UTC).timestamp()),
        )

        result = await require_authenticated(user)

        assert result == user


class TestRequireSubscriptionTier:
    """Tests for require_subscription_tier dependency factory."""

    @pytest.mark.asyncio
    async def test_require_tier_allowed_free(self):
        """Test tier check passes for allowed tier (free)."""
        user = TokenPayload(
            sub="123e4567-e89b-12d3-a456-426614174000",
            exp=int((datetime.now(tz=UTC) + timedelta(hours=1)).timestamp()),
            iat=int(datetime.now(tz=UTC).timestamp()),
            app_metadata={"subscription_tier": "free"},
        )

        check_tier = require_subscription_tier("free", "pro")
        result = await check_tier(user)

        assert result == user

    @pytest.mark.asyncio
    async def test_require_tier_allowed_pro(self):
        """Test tier check passes for allowed tier (pro)."""
        user = TokenPayload(
            sub="123e4567-e89b-12d3-a456-426614174000",
            exp=int((datetime.now(tz=UTC) + timedelta(hours=1)).timestamp()),
            iat=int(datetime.now(tz=UTC).timestamp()),
            app_metadata={"subscription_tier": "pro"},
        )

        check_tier = require_subscription_tier("pro", "enterprise")
        result = await check_tier(user)

        assert result == user

    @pytest.mark.asyncio
    async def test_require_tier_denied(self):
        """Test tier check raises error for disallowed tier."""
        user = TokenPayload(
            sub="123e4567-e89b-12d3-a456-426614174000",
            exp=int((datetime.now(tz=UTC) + timedelta(hours=1)).timestamp()),
            iat=int(datetime.now(tz=UTC).timestamp()),
            app_metadata={"subscription_tier": "free"},
        )

        check_tier = require_subscription_tier("pro", "enterprise")

        with pytest.raises(AuthorizationError) as exc_info:
            await check_tier(user)

        assert exc_info.value.status_code == 403
        assert "pro, enterprise" in exc_info.value.detail
        assert "free" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_require_tier_default_free_when_missing(self):
        """Test tier check defaults to 'free' when subscription_tier missing."""
        user = TokenPayload(
            sub="123e4567-e89b-12d3-a456-426614174000",
            exp=int((datetime.now(tz=UTC) + timedelta(hours=1)).timestamp()),
            iat=int(datetime.now(tz=UTC).timestamp()),
            app_metadata={},  # No subscription_tier
        )

        check_tier = require_subscription_tier("free")
        result = await check_tier(user)

        assert result == user

    @pytest.mark.asyncio
    async def test_require_tier_multiple_tiers(self):
        """Test tier check with multiple allowed tiers."""
        user = TokenPayload(
            sub="123e4567-e89b-12d3-a456-426614174000",
            exp=int((datetime.now(tz=UTC) + timedelta(hours=1)).timestamp()),
            iat=int(datetime.now(tz=UTC).timestamp()),
            app_metadata={"subscription_tier": "enterprise"},
        )

        check_tier = require_subscription_tier("free", "pro", "enterprise")
        result = await check_tier(user)

        assert result == user


class TestAuthenticationError:
    """Tests for AuthenticationError exception."""

    def test_authentication_error_default(self):
        """Test AuthenticationError with default message."""
        error = AuthenticationError()

        assert error.status_code == 401
        assert error.detail == "Could not validate credentials"
        assert error.headers == {"WWW-Authenticate": "Bearer"}

    def test_authentication_error_custom_message(self):
        """Test AuthenticationError with custom message."""
        error = AuthenticationError("Token expired")

        assert error.status_code == 401
        assert error.detail == "Token expired"


class TestAuthorizationError:
    """Tests for AuthorizationError exception."""

    def test_authorization_error_default(self):
        """Test AuthorizationError with default message."""
        error = AuthorizationError()

        assert error.status_code == 403
        assert error.detail == "Insufficient permissions"

    def test_authorization_error_custom_message(self):
        """Test AuthorizationError with custom message."""
        error = AuthorizationError("Requires pro tier")

        assert error.status_code == 403
        assert error.detail == "Requires pro tier"
