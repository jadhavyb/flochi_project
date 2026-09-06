from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import CognitoJWTError, verify_access_token
from app.models.user import User
from app.repositories.user import UserRepository
from app.repositories.user_identity import UserIdentityRepository
from app.services.cognito import CognitoService


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.cognito = CognitoService()
        self.user_repo = UserRepository(db)
        self.identity_repo = UserIdentityRepository(db)

    async def register(
        self, email: str, password: str, first_name: str | None, last_name: str | None
    ) -> User:
        existing = await self.user_repo.get_by_email(email)
        if existing:
            raise ValueError("Email already registered")

        self.cognito.sign_up(email, password, first_name, last_name)

        user = User(
            email=email,
            cognito_sub=email,
            first_name=first_name,
            last_name=last_name,
            is_active=False,
        )
        return await self.user_repo.create(user)

    async def confirm(self, email: str, confirmation_code: str) -> None:
        self.cognito.confirm_sign_up(email, confirmation_code)
        user = await self.user_repo.get_by_email(email)
        if user:
            user.is_active = True
            await self.db.flush()

    async def login(self, email: str, password: str) -> dict:
        auth_result = self.cognito.initiate_auth(email, password)
        return {
            "access_token": auth_result["AccessToken"],
            "refresh_token": auth_result["RefreshToken"],
            "expires_in": int(auth_result.get("ExpiresIn", 3600)),
            "token_type": "bearer",
        }

    async def refresh(self, refresh_token: str) -> dict:
        auth_result = self.cognito.refresh_token(refresh_token)
        return {
            "access_token": auth_result["AccessToken"],
            "refresh_token": auth_result.get("RefreshToken", refresh_token),
            "expires_in": int(auth_result.get("ExpiresIn", 3600)),
            "token_type": "bearer",
        }

    async def logout(self, access_token: str) -> None:
        self.cognito.logout(access_token)

    async def get_current_user_from_token(self, access_token: str) -> User:
        try:
            claims = await verify_access_token(access_token)
        except CognitoJWTError as exc:
            raise ValueError(str(exc)) from exc

        user = await self.user_repo.get_by_cognito_sub(claims.sub)
        if user is None:
            identity = await self.identity_repo.get_by_provider_and_subject("cognito", claims.sub)
            if identity:
                user = await self.user_repo.get_by_id(identity.user_id)

        if user is None:
            user = User(
                cognito_sub=claims.sub,
                email=claims.email,
                first_name=None,
                last_name=None,
                is_active=True,
            )
            await self.user_repo.create(user)

        return user
