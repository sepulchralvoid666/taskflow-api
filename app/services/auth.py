from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    is_access_token,
    is_refresh_token,
    verify_password,
)
from app.models.user import User, UserRole
from app.schemas.user import RegisterRequest, TokenResponse


class AuthError(Exception):
    """Raised on authentication/authorization failures."""


class UserExistsError(AuthError):
    """Raised when a user with the same email or username already exists."""


async def register_user(db: AsyncSession, data: RegisterRequest) -> User:
    """Create a new user. Raises UserExistsError if email/username taken."""
    # Check for existing email
    result = await db.execute(select(User).where(User.email == data.email))
    if result.scalar_one_or_none():
        raise UserExistsError("A user with this email already exists")

    # Check for existing username
    result = await db.execute(select(User).where(User.username == data.username))
    if result.scalar_one_or_none():
        raise UserExistsError("A user with this username already exists")

    user = User(
        email=data.email,
        username=data.username,
        hashed_password=hash_password(data.password),
        role=UserRole.USER,
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)
    return user


async def authenticate_user(db: AsyncSession, username: str, password: str) -> User:
    """Verify credentials and return the user. Raises AuthError on failure."""
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()

    if not user or not verify_password(password, user.hashed_password):
        raise AuthError("Invalid username or password")

    if not user.is_active:
        raise AuthError("Account is disabled")

    return user


def create_tokens(user: User) -> TokenResponse:
    """Generate access + refresh token pair for a user."""
    return TokenResponse(
        access_token=create_access_token(user.id, {"role": user.role.value}),
        refresh_token=create_refresh_token(user.id),
    )


async def refresh_access_token(db: AsyncSession, refresh_token: str) -> TokenResponse:
    """Validate a refresh token and issue a new token pair."""
    try:
        payload = decode_token(refresh_token)
    except Exception:
        raise AuthError("Invalid or expired refresh token")

    if not is_refresh_token(payload):
        raise AuthError("Not a refresh token")

    user_id = int(payload["sub"])
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user or not user.is_active:
        raise AuthError("User not found or inactive")

    return create_tokens(user)


async def get_current_user(db: AsyncSession, token: str) -> User:
    """Decode an access token and return the corresponding user."""
    try:
        payload = decode_token(token)
    except Exception:
        raise AuthError("Invalid or expired token")

    if not is_access_token(payload):
        raise AuthError("Not an access token")

    user_id = int(payload["sub"])
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user or not user.is_active:
        raise AuthError("User not found or inactive")

    return user
