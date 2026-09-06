from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.item import Item


class ItemRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, item_id, owner_id=None) -> Item | None:
        import uuid

        iid = uuid.UUID(str(item_id))
        stmt = select(Item).where(Item.id == iid)
        if owner_id:
            oid = uuid.UUID(str(owner_id))
            stmt = stmt.where(Item.owner_id == oid)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_owner(self, owner_id, skip: int = 0, limit: int = 100) -> list[Item]:
        import uuid

        oid = uuid.UUID(str(owner_id))
        result = await self.db.execute(
            select(Item)
            .where(Item.owner_id == oid)
            .order_by(Item.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def count_by_owner(self, owner_id) -> int:
        import uuid

        oid = uuid.UUID(str(owner_id))
        result = await self.db.execute(select(func.count(Item.id)).where(Item.owner_id == oid))
        return result.scalar_one()

    async def create(self, item: Item) -> Item:
        self.db.add(item)
        await self.db.flush()
        await self.db.refresh(item)
        return item

    async def update(self, item: Item) -> Item:
        await self.db.flush()
        await self.db.refresh(item)
        return item

    async def delete(self, item: Item) -> None:
        await self.db.delete(item)
        await self.db.flush()
