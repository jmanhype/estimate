"""Authentication and authorization utilities for Supabase JWT validation."""

from datetime import UTC, datetime
from typing import Annotated, Any

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field

from src.core.config import settings

# Security scheme for FastAPI docs
security = HTTPBearer()


class TokenPayload(BaseModel):
    """
    JWT token payload structure from Supabase.

    Supabase JWTs contain standard claims plus custom app_metadata and user_metadata.
    """

    sub: str  # User ID (UUID from auth.users)
    email: str | None = None
    role: str | None = None  # Supabase role (authenticated, anon, etc.)
    aud: str | None = None  # Audience (should be 'authenticated')
    exp: int  # Expiration timestamp
    iat: int  # Issued at timestamp
    app_metadata: dict = Field(default_factory=dict)
    user_metadata: dict = Field(default_factory=dict)


class AuthenticationError(HTTPException):
    """Authentication failed exception."""

    def __init__(self, detail: str = "Could not validate credentials"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


class AuthorizationError(HTTPException):
    """Authorization failed exception."""

    def __init__(self, detail: str = "Insufficient permissions"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
        )


def decode_jwt(token: str) -> TokenPayload:
    """
    Decode and validate a Supabase JWT token.

    Args:
        token: JWT token string from Authorization header

    Returns:
        TokenPayload: Decoded token payload with user information

    Raises:
        AuthenticationError: If token is invalid, expired, or malformed
    """
    try:
        # Decode token using Supabase JWT secret
        payload = jwt.decode(
            token,
            settings.supabase_jwt_secret or settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
            audience="authenticated",  # Supabase default audience
        )

        # Validate expiration
        exp = payload.get("exp")
        if exp is None:
            raise AuthenticationError("Token missing expiration")

        if datetime.fromtimestamp(exp, tz=UTC) < datetime.now(tz=UTC):
            raise AuthenticationError("Token has expired")

        return TokenPayload(**payload)

    except jwt.ExpiredSignatureError as e:
        raise AuthenticationError("Token has expired") from e
    except jwt.InvalidTokenError as e:
        raise AuthenticationError(f"Invalid token: {e!s}") from e
    except ValueError as e:
        raise AuthenticationError(f"Invalid token payload: {e!s}") from e


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
) -> TokenPayload:
    """
    FastAPI dependency to get current authenticated user from JWT.

    Extracts and validates JWT from Authorization header.

    Args:
        credentials: HTTP Bearer credentials from request header

    Returns:
        TokenPayload: Decoded token with user information

    Raises:
        AuthenticationError: If authentication fails

    Usage:
        ```python
        @router.get("/me")
        async def get_me(user: TokenPayload = Depends(get_current_user)):
            return {"user_id": user.sub, "email": user.email}
        ```
    """
    token = credentials.credentials
    return decode_jwt(token)


async def require_authenticated(
    user: Annotated[TokenPayload, Depends(get_current_user)],
) -> TokenPayload:
    """
    Dependency to ensure user is authenticated.

    This is an alias for get_current_user with clearer naming.

    Args:
        user: Current user from get_current_user dependency

    Returns:
        TokenPayload: Current user information

    Raises:
        AuthenticationError: If not authenticated
    """
    return user


def require_subscription_tier(*allowed_tiers: str) -> Any:
    """
    Create a dependency to check user subscription tier.

    Args:
        *allowed_tiers: Allowed subscription tiers (e.g., "free", "pro", "enterprise")

    Returns:
        Dependency function that validates subscription tier

    Raises:
        AuthorizationError: If user's tier is not in allowed_tiers

    Usage:
        ```python
        @router.post("/premium-feature", dependencies=[Depends(require_subscription_tier("pro", "enterprise"))])
        async def premium_feature(user: TokenPayload = Depends(get_current_user)):
            return {"message": "Access granted"}
        ```
    """

    async def check_tier(
        user: Annotated[TokenPayload, Depends(get_current_user)],
    ) -> TokenPayload:
        # Check app_metadata for subscription tier
        tier = user.app_metadata.get("subscription_tier", "free")

        if tier not in allowed_tiers:
            raise AuthorizationError(
                f"This feature requires one of: {', '.join(allowed_tiers)}. Your tier: {tier}"
            )

        return user

    return check_tier
