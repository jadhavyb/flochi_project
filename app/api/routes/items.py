from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_db
from app.core.exceptions import NotFoundError
from app.models.user import User
from app.schemas.item import ItemCreate, ItemResponse, ItemUpdate
from app.services.item import ItemService

router = APIRouter(prefix="/items", tags=["Items"])


@router.post("", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
async def create_item(
    body: ItemCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ItemResponse:
    service = ItemService(db)
    item = await service.create(current_user.id, body)
    return ItemResponse(
        id=item.id,
        name=item.name,
        description=item.description,
        owner_id=item.owner_id,
        created_at=str(item.created_at),
        updated_at=str(item.updated_at),
    )


@router.get("", response_model=list[ItemResponse])
async def list_items(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[ItemResponse]:
    service = ItemService(db)
    items = await service.list_for_owner(current_user.id)
    return [
        ItemResponse(
            id=item.id,
            name=item.name,
            description=item.description,
            owner_id=item.owner_id,
            created_at=str(item.created_at),
            updated_at=str(item.updated_at),
        )
        for item in items
    ]


@router.get("/{item_id}", response_model=ItemResponse)
async def get_item(
    item_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ItemResponse:
    service = ItemService(db)
    item = await service.get(item_id, current_user.id)
    if item is None:
        raise NotFoundError("Item not found")
    return ItemResponse(
        id=item.id,
        name=item.name,
        description=item.description,
        owner_id=item.owner_id,
        created_at=str(item.created_at),
        updated_at=str(item.updated_at),
    )


@router.patch("/{item_id}", response_model=ItemResponse)
async def update_item(
    item_id: UUID,
    body: ItemUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ItemResponse:
    service = ItemService(db)
    item = await service.get(item_id, current_user.id)
    if item is None:
        raise NotFoundError("Item not found")
    updated = await service.update(item, body)
    return ItemResponse(
        id=updated.id,
        name=updated.name,
        description=updated.description,
        owner_id=updated.owner_id,
        created_at=str(updated.created_at),
        updated_at=str(updated.updated_at),
    )


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT, response_model=None)
async def delete_item(
    item_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    service = ItemService(db)
    item = await service.get(item_id, current_user.id)
    if item is None:
        raise NotFoundError("Item not found")
    await service.delete(item)
    return None
