from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import CognitoClaims, verify_access_token
from app.models.user import User
from app.models.user_identity import UserIdentity
from app.repositories.user import UserRepository
from app.repositories.user_identity import UserIdentityRepository
from app.services.cognito import CognitoService


class ProvisioningService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.cognito = CognitoService()
        self.user_repo = UserRepository(db)
        self.identity_repo = UserIdentityRepository(db)

    async def provision_user_from_claims(self, claims: CognitoClaims, provider: str) -> User:
        identity = await self.identity_repo.get_by_provider_and_subject(provider, claims.sub)
        if identity:
            return await self.user_repo.get_by_id(identity.user_id)

        user = await self.user_repo.get_by_cognito_sub(claims.sub)
        if user is None:
            user = User(
                cognito_sub=claims.sub,
                email=claims.email,
                first_name=None,
                last_name=None,
                is_active=True,
            )
            await self.user_repo.create(user)

        new_identity = UserIdentity(
            user_id=user.id,
            provider=provider,
            provider_subject=claims.sub,
            email=claims.email,
        )
        self.db.add(new_identity)
        await self.db.flush()

        return user

    async def get_user_by_identity(self, provider: str, provider_subject: str) -> User | None:
        identity = await self.identity_repo.get_by_provider_and_subject(provider, provider_subject)
        if identity:
            return await self.user_repo.get_by_id(identity.user_id)
        return None

    async def link_identity(self, user: User, provider: str, provider_subject: str, email: str | None) -> UserIdentity:
        existing = await self.identity_repo.get_by_provider_and_subject(provider, provider_subject)
        if existing:
            if existing.user_id != user.id:
                raise ValueError("This identity is already linked to another account")
            return existing

        identity = UserIdentity(
            user_id=user.id,
            provider=provider,
            provider_subject=provider_subject,
            email=email,
        )
        self.db.add(identity)
        await self.db.flush()
        return identity

    async def unlink_identity(self, user: User, provider: str, provider_subject: str) -> None:
        identity = await self.identity_repo.get_by_provider_and_subject(provider, provider_subject)
        if not identity:
            raise ValueError("Identity not found")
        if identity.user_id != user.id:
            raise ValueError("Forbidden")

        await self.identity_repo.delete(identity)
