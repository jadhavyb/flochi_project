from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.item import Item
from app.repositories.item import ItemRepository
from app.schemas.item import ItemCreate, ItemUpdate


class ItemService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = ItemRepository(db)

    async def create(self, owner_id: UUID, data: ItemCreate) -> Item:
        item = Item(
            name=data.name,
            description=data.description,
            owner_id=owner_id,
        )
        return await self.repo.create(item)

    async def get(self, item_id: UUID, owner_id: UUID) -> Item | None:
        return await self.repo.get_by_id(item_id, owner_id)

    async def list_for_owner(self, owner_id: UUID, skip: int = 0, limit: int = 100) -> list[Item]:
        return await self.repo.get_by_owner(owner_id, skip=skip, limit=limit)

    async def update(self, item: Item, data: ItemUpdate) -> Item:
        if data.name is not None:
            item.name = data.name
        if data.description is not None:
            item.description = data.description
        return await self.repo.update(item)

    async def delete(self, item: Item) -> None:
        await self.repo.delete(item)
