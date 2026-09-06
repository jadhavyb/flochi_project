from __future__ import annotations

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.exceptions import UnauthorizedError
from app.core.security import CognitoJWTError, verify_access_token
from app.models.user import User
from app.repositories.user import UserRepository
from app.repositories.user_identity import UserIdentityRepository

oauth2_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    if credentials is None:
        raise UnauthorizedError("Missing authorization token")

    token = credentials.credentials
    try:
        claims = await verify_access_token(token)
    except CognitoJWTError as exc:
        raise UnauthorizedError(str(exc)) from exc

    user_repo = UserRepository(db)
    user = await user_repo.get_by_cognito_sub(claims.sub)
    if user is None:
        identity_repo = UserIdentityRepository(db)
        identity = await identity_repo.get_by_provider_and_subject("cognito", claims.sub)
        if identity:
            user = await user_repo.get_by_id(identity.user_id)

    if user is None:
        user = User(
            cognito_sub=claims.sub,
            email=claims.email,
            first_name=None,
            last_name=None,
            is_active=True,
        )
        db.add(user)
        await db.flush()
        await db.refresh(user)

    return user
