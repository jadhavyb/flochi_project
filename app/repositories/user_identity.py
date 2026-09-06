from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user_identity import UserIdentity


class UserIdentityRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_provider_and_subject(self, provider: str, provider_subject: str) -> UserIdentity | None:
        result = await self.db.execute(
            select(UserIdentity).where(
                UserIdentity.provider == provider,
                UserIdentity.provider_subject == provider_subject,
            )
        )
        return result.scalar_one_or_none()

    async def get_by_user_id(self, user_id) -> list[UserIdentity]:
        import uuid
        uid = uuid.UUID(str(user_id))
        result = await self.db.execute(
            select(UserIdentity).where(UserIdentity.user_id == uid)
        )
        return list(result.scalars().all())

    async def delete(self, identity: UserIdentity) -> None:
        await self.db.delete(identity)
        await self.db.flush()
