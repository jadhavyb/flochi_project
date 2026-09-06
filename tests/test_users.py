from __future__ import annotations

import pytest

from app.schemas.user import UserResponse


@pytest.mark.asyncio
async def test_get_me_authenticated(client):
    await client.post(
        "/api/v1/auth/register",
        json={"email": "user@example.com", "password": "SecurePass123!"},
    )
    response = await client.get("/api/v1/auth/me")
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "user@example.com"
    assert "id" in data


@pytest.mark.asyncio
async def test_get_my_items_empty(client):
    await client.post(
        "/api/v1/auth/register",
        json={"email": "items@example.com", "password": "SecurePass123!"},
    )
    response = await client.get("/api/v1/users/me/items")
    assert response.status_code == 200
    assert response.json() == []