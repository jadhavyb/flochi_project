from __future__ import annotations

import secrets
from datetime import UTC, datetime
from typing import Any

from app.core.config import settings
from app.integrations.cognito.client import CognitoClient


class OAuthStateStore:
    def __init__(self) -> None:
        self._states: dict[str, dict[str, Any]] = {}

    def create_state(self, provider: str, redirect_uri: str, nonce: str | None = None) -> str:
        state = secrets.token_urlsafe(32)
        self._states[state] = {
            "provider": provider,
            "redirect_uri": redirect_uri,
            "nonce": nonce or secrets.token_urlsafe(16),
            "created_at": datetime.now(UTC),
        }
        return state

    def validate_state(self, state: str, provider: str) -> dict[str, Any] | None:
        stored = self._states.get(state)
        if not stored:
            return None
        if stored["provider"] != provider:
            return None
        created = stored["created_at"]
        if (datetime.now(UTC) - created).total_seconds() > settings.OAUTH_STATE_TTL:
            del self._states[state]
            return None
        return stored

    def consume_state(self, state: str, provider: str) -> dict[str, Any] | None:
        stored = self.validate_state(state, provider)
        if stored:
            del self._states[state]
        return stored


oauth_state_store = OAuthStateStore()


class OAuthService:
    def __init__(self):
        self.cognito = CognitoClient()

    def get_authorization_url(self, provider: str, redirect_uri: str) -> tuple[str, str]:
        if provider == "google" and not settings.GOOGLE_SSO_ENABLED:
            raise ValueError("Google SSO is not enabled")
        if provider == "apple" and not settings.APPLE_SSO_ENABLED:
            raise ValueError("Apple SSO is not enabled")

        state = oauth_state_store.create_state(provider, redirect_uri)
        nonce = secrets.token_urlsafe(16)

        base_url = (
            settings.AWS_ENDPOINT_URL
            or f"https://{settings.COGNITO_USER_POOL_ID}.auth.{settings.AWS_REGION}.amazoncognito.com"
        )
        url = (
            f"{base_url}/oauth2/authorize"
            f"?client_id={settings.COGNITO_CLIENT_ID}"
            f"&response_type=code"
            f"&scope=openid+email+profile"
            f"&redirect_uri={redirect_uri}"
            f"&state={state}"
            f"&nonce={nonce}"
        )

        return url, state

    async def handle_callback(
        self, provider: str, code: str, state: str, redirect_uri: str
    ) -> dict[str, Any]:
        stored = oauth_state_store.consume_state(state, provider)
        if not stored:
            raise ValueError("Invalid or expired state")
        if stored["redirect_uri"] != redirect_uri:
            raise ValueError("Redirect URI mismatch")

        token_result = self.cognito.initiate_auth(
            "USER_PASSWORD_AUTH",
            {"USERNAME": code, "PASSWORD": code},
        )
        return token_result

    def get_providers(self) -> list[dict[str, Any]]:
        providers = []
        if settings.GOOGLE_SSO_ENABLED:
            providers.append({"name": "google", "enabled": True})
        if settings.APPLE_SSO_ENABLED:
            providers.append({"name": "apple", "enabled": True})
        return providers
