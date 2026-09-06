from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.user import UserResponse
from app.services.item import ItemService

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)) -> UserResponse:
    return UserResponse(
        id=str(current_user.id),
        cognito_sub=current_user.cognito_sub,
        email=current_user.email,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        is_active=current_user.is_active,
    )


@router.get("/me/items")
async def get_my_items(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ItemService(db)
    items = await service.list_for_owner(current_user.id)
    return [
        {
            "id": str(item.id),
            "name": item.name,
            "description": item.description,
            "owner_id": str(item.owner_id),
            "created_at": str(item.created_at),
            "updated_at": str(item.updated_at),
        }
        for item in items
    ]
