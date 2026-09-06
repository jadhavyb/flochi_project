from __future__ import annotations

from unittest.mock import patch

import pytest

from app.schemas.sso import ProvidersResponse


@pytest.mark.asyncio
async def test_list_providers_google_enabled():
    with patch("app.services.auth.oauth.settings.google_sso_enabled", True):
        with patch("app.services.auth.oauth.settings.apple_sso_enabled", False):
            from app.services.auth.oauth import OAuthService
            oauth = OAuthService()
            response = oauth.get_providers()
            assert len(response) == 1
            assert response[0]["name"] == "google"
            assert response[0]["enabled"] is True


@pytest.mark.asyncio
async def test_list_providers_apple_enabled():
    with patch("app.services.auth.oauth.settings.google_sso_enabled", False):
        with patch("app.services.auth.oauth.settings.apple_sso_enabled", True):
            from app.services.auth.oauth import OAuthService
            oauth = OAuthService()
            response = oauth.get_providers()
            assert len(response) == 1
            assert response[0]["name"] == "apple"
            assert response[0]["enabled"] is True


@pytest.mark.asyncio
async def test_list_providers_none_enabled():
    with patch("app.services.auth.oauth.settings.google_sso_enabled", False):
        with patch("app.services.auth.oauth.settings.apple_sso_enabled", False):
            from app.services.auth.oauth import OAuthService
            oauth = OAuthService()
            response = oauth.get_providers()
            assert len(response) == 0
