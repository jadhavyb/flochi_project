from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, patch

import pytest

from app.models.user import User
from app.models.user_identity import UserIdentity
from app.repositories.user_identity import UserIdentityRepository
from app.services.auth.provisioning import ProvisioningService


def _make_user(db, cognito_sub="cognito-sub-123", email="test@example.com"):
    user = User(
        cognito_sub=cognito_sub,
        email=email,
        first_name="Test",
        last_name="User",
        is_active=True,
    )
    db.add(user)
    import asyncio
    asyncio.get_event_loop().run_until_complete(db.flush())
    asyncio.get_event_loop().run_until_complete(db.refresh(user))
    return user


@pytest.mark.asyncio
async def test_provision_new_google_user(db_session):
    from app.core.security import CognitoClaims
    claims = CognitoClaims(
        sub="google-sub-123",
        email="google@example.com",
        token_use="access",
        exp=9999999999,
        iss="https://cognito-idp.us-east-1.amazonaws.com/us-east-1_test",
        aud="test-client-id",
        client_id="test-client-id",
        username="googleuser",
    )

    provisioning = ProvisioningService(db_session)
    user = await provisioning.provision_user_from_claims(claims, "google")

    assert user.email == "google@example.com"
    assert user.cognito_sub == "google-sub-123"

    identity = await UserIdentityRepository(db_session).get_by_provider_and_subject("google", "google-sub-123")
    assert identity is not None
    assert identity.user_id == user.id


@pytest.mark.asyncio
async def test_provision_existing_google_user(db_session):
    from app.core.security import CognitoClaims
    claims = CognitoClaims(
        sub="google-sub-123",
        email="google@example.com",
        token_use="access",
        exp=9999999999,
        iss="https://cognito-idp.us-east-1.amazonaws.com/us-east-1_test",
        aud="test-client-id",
        client_id="test-client-id",
        username="googleuser",
    )

    provisioning = ProvisioningService(db_session)
    user1 = await provisioning.provision_user_from_claims(claims, "google")
    user2 = await provisioning.provision_user_from_claims(claims, "google")

    assert user1.id == user2.id


@pytest.mark.asyncio
async def test_link_identity_success(db_session):
    user = _make_user(db_session)
    provisioning = ProvisioningService(db_session)
    identity = await provisioning.link_identity(user, "google", "google-sub-456", "linked@example.com")
    assert identity.provider == "google"
    assert identity.provider_subject == "google-sub-456"
    assert identity.user_id == user.id


@pytest.mark.asyncio
async def test_link_duplicate_identity_to_different_user(db_session):
    user1 = _make_user(db_session, email="user1@example.com")
    user2 = _make_user(db_session, email="user2@example.com", cognito_sub="cognito-sub-456")

    provisioning = ProvisioningService(db_session)
    await provisioning.link_identity(user1, "google", "google-sub-789", "dup@example.com")

    with pytest.raises(ValueError, match="already linked to another account"):
        await provisioning.link_identity(user2, "google", "google-sub-789", "dup@example.com")


@pytest.mark.asyncio
async def test_unlink_identity_success(db_session):
    user = _make_user(db_session)
    provisioning = ProvisioningService(db_session)
    await provisioning.link_identity(user, "google", "google-sub-999", "unlink@example.com")
    await provisioning.unlink_identity(user, "google", "google-sub-999")

    identity = await UserIdentityRepository(db_session).get_by_provider_and_subject("google", "google-sub-999")
    assert identity is None
