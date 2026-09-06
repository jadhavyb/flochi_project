from __future__ import annotations

from typing import Any

from app.core.config import settings
from app.integrations.aws.clients import AWSClientFactory


class CognitoClient:
    def __init__(self):
        self.user_pool_id = settings.COGNITO_USER_POOL_ID
        self.client_id = settings.COGNITO_CLIENT_ID
        self.client_secret = settings.COGNITO_CLIENT_SECRET
        self.client = AWSClientFactory.create_client("cognito-idp") if self.client_id else None

    def _ensure_configured(self) -> None:
        if not self.client_id or not self.user_pool_id:
            raise ValueError("Cognito is not configured. Set COGNITO_CLIENT_ID and COGNITO_USER_POOL_ID.")

    def initiate_auth(self, auth_flow: str, auth_parameters: dict[str, Any]) -> dict[str, Any]:
        self._ensure_configured()
        try:
            response = self.client.initiate_auth(
                ClientId=self.client_id,
                AuthFlow=auth_flow,
                AuthParameters=auth_parameters,
            )
            return response.get("AuthenticationResult", {})
        except self.client.exceptions.NotAuthorizedException:
            raise ValueError("Invalid credentials") from None
        except self.client.exceptions.UserNotFoundException:
            raise ValueError("User not found") from None
        except self.client.exceptions.UserNotConfirmedException:
            raise ValueError("User not confirmed") from None
        except Exception as exc:
            raise RuntimeError(f"Cognito auth failed: {exc}") from exc

    def refresh_token(self, refresh_token: str) -> dict[str, Any]:
        self._ensure_configured()
        auth_parameters = {"REFRESH_TOKEN": refresh_token}
        if self.client_secret:
            auth_parameters["SECRET_HASH"] = self._secret_hash(refresh_token)
        return self.initiate_auth("REFRESH_TOKEN_AUTH", auth_parameters)

    def get_user(self, access_token: str) -> dict[str, Any]:
        self._ensure_configured()
        try:
            return self.client.get_user(AccessToken=access_token)
        except self.client.exceptions.NotAuthorizedException:
            raise ValueError("Invalid access token") from None
        except Exception as exc:
            raise RuntimeError(f"Cognito get user failed: {exc}") from exc

    def global_sign_out(self, access_token: str) -> None:
        self._ensure_configured()
        try:
            self.client.global_sign_out(AccessToken=access_token)
        except Exception as exc:
            raise RuntimeError(f"Cognito logout failed: {exc}") from exc

    def _secret_hash(self, username: str) -> str:
        if not self.client_secret:
            return ""
        import base64
        import hashlib
        import hmac

        message = bytes(username + self.client_id, "utf-8")
        secret = bytes(self.client_secret, "utf-8")
        digest = hmac.new(secret, message, hashlib.sha256).digest()
        return base64.b64encode(digest).decode()
