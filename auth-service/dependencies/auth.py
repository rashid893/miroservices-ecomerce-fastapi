from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_db
from schemas.user import UserResponse
from services.auth_service import AuthService

# HTTPBearer extracts the token from the "Authorization: Bearer <token>" header
bearer_scheme = HTTPBearer()


async def get_auth_service(session: AsyncSession = Depends(get_db)) -> AuthService:
    """Dependency that creates an AuthService with a DB session."""
    return AuthService(session)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    auth_service: AuthService = Depends(get_auth_service),
) -> UserResponse:
    """
    FastAPI dependency — extracts and validates the access token,
    returning the current user. Use this on any protected endpoint.
    """
    return await auth_service.get_current_user(credentials.credentials)
