import uuid
from datetime import datetime, timezone

from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from core.exceptions import (
    InactiveUserError,
    InvalidCredentialsError,
    InvalidTokenError,
    UserAlreadyExistsError,
    UserNotFoundError,
)
from db.models import User
from repositories.user_repository import RefreshTokenRepository, UserRepository
from schemas.user import TokenResponse, UserResponse
from utils.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)


class AuthService:
    """
    Business logic for auth operations.
    Orchestrates repositories and security utilities.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.user_repo = UserRepository(session)
        self.token_repo = RefreshTokenRepository(session)

    async def register(
        self, email: str, password: str, full_name: str
    ) -> UserResponse:
        # Check for duplicate email
        existing = await self.user_repo.get_by_email(email)
        if existing:
            raise UserAlreadyExistsError()

        hashed = hash_password(password)
        user = await self.user_repo.create(
            email=email,
            hashed_password=hashed,
            full_name=full_name,
        )
        return UserResponse.model_validate(user)

    async def login(self, email: str, password: str) -> TokenResponse:
        user = await self.user_repo.get_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            raise InvalidCredentialsError()

        if not user.is_active:
            raise InactiveUserError()

        return await self._issue_tokens(user)

    async def refresh(self, raw_refresh_token: str) -> TokenResponse:
        # Validate JWT signature and expiry
        try:
            payload = decode_token(raw_refresh_token)
        except JWTError:
            raise InvalidTokenError()

        if payload.get("type") != "refresh":
            raise InvalidTokenError("Token is not a refresh token.")

        # Check the token exists in DB and hasn't been revoked
        stored = await self.token_repo.get_by_token(raw_refresh_token)
        if not stored or stored.revoked:
            raise InvalidTokenError("Refresh token has been revoked or is invalid.")

        # Check expiry at the DB level too (belt and braces)
        if stored.expires_at.replace(tzinfo=timezone.utc) < datetime.now(tz=timezone.utc):
            raise InvalidTokenError("Refresh token has expired.")

        user = await self.user_repo.get_by_id(stored.user_id)
        if not user:
            raise UserNotFoundError()
        if not user.is_active:
            raise InactiveUserError()

        # Rotate: revoke old token, issue a fresh pair
        await self.token_repo.revoke(raw_refresh_token)
        return await self._issue_tokens(user)

    async def get_current_user(self, raw_access_token: str) -> UserResponse:
        try:
            payload = decode_token(raw_access_token)
        except JWTError:
            raise InvalidTokenError()

        if payload.get("type") != "access":
            raise InvalidTokenError("Token is not an access token.")

        user_id = uuid.UUID(payload["sub"])
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundError()
        if not user.is_active:
            raise InactiveUserError()

        return UserResponse.model_validate(user)

    # ──────────────────────────────────────────
    # Private helpers
    # ──────────────────────────────────────────

    async def _issue_tokens(self, user: User) -> TokenResponse:
        """Create an access + refresh token pair and persist the refresh token."""
        access_token = create_access_token(
            subject=str(user.id),
            extra_claims={"email": user.email, "role": user.role},
        )
        raw_refresh, expires_at = create_refresh_token(subject=str(user.id))
        await self.token_repo.create(
            user_id=user.id,
            token=raw_refresh,
            expires_at=expires_at,
        )
        return TokenResponse(access_token=access_token, refresh_token=raw_refresh)
