from __future__ import annotations

import pytest

from app.core.exceptions import BadRequestError, UnauthorizedError
from app.schemas.auth import ConfirmRequest, LoginRequest, RegisterRequest, TokenResponse


@pytest.mark.asyncio
async def test_register(client):
    response = await client.post(
        "/api/v1/auth/register",
        json={"email": "test@example.com", "password": "SecurePass123!", "first_name": "John", "last_name": "Doe"},
    )
    assert response.status_code == 201
    assert "message" in response.json()


@pytest.mark.asyncio
async def test_register_duplicate_email(client):
    await client.post(
        "/api/v1/auth/register",
        json={"email": "dup@example.com", "password": "SecurePass123!"},
    )
    response = await client.post(
        "/api/v1/auth/register",
        json={"email": "dup@example.com", "password": "SecurePass123!"},
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_login_missing_fields(client):
    response = await client.post("/api/v1/auth/login", json={})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_me_unauthenticated(client):
    response = await client.get("/api/v1/auth/me")
    assert response.status_code == 401