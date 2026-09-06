from __future__ import annotations

import uuid

import pytest

from app.schemas.item import ItemCreate, ItemResponse


@pytest.mark.asyncio
async def test_create_item(client):
    await client.post(
        "/api/v1/auth/register",
        json={"email": "owner@example.com", "password": "SecurePass123!"},
    )
    response = await client.post(
        "/api/v1/items",
        json={"name": "Test Item", "description": "A test item"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Item"
    assert data["description"] == "A test item"
    assert "id" in data
    assert "owner_id" in data


@pytest.mark.asyncio
async def test_list_items_empty(client):
    response = await client.get("/api/v1/items")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_get_item_not_found(client):
    fake_id = str(uuid.uuid4())
    response = await client.get(f"/api/v1/items/{fake_id}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_create_item_unauthorized(client):
    response = await client.post("/api/v1/items", json={"name": "No Auth"})
    assert response.status_code == 401