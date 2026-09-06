from __future__ import annotations

from typing import Any

from botocore.exceptions import ClientError

from app.core.config import settings
from app.integrations.aws.clients import AWSClientFactory


class CognitoService:
    def __init__(self):
        self.user_pool_id = settings.COGNITO_USER_POOL_ID
        self.client_id = settings.COGNITO_CLIENT_ID
        self.client_secret = settings.COGNITO_CLIENT_SECRET
        self.client = AWSClientFactory.create_client("cognito-idp") if self.client_id else None

    def _ensure_configured(self) -> None:
        if not self.client_id or not self.user_pool_id:
            raise ValueError(
                "Cognito is not configured. Set COGNITO_CLIENT_ID and COGNITO_USER_POOL_ID."
            )

    def sign_up(
        self, email: str, password: str, first_name: str | None, last_name: str | None
    ) -> dict[str, Any]:
        self._ensure_configured()
        user_attrs = []
        if first_name:
            user_attrs.append({"Name": "given_name", "Value": first_name})
        if last_name:
            user_attrs.append({"Name": "family_name", "Value": last_name})

        try:
            params = {
                "ClientId": self.client_id,
                "Username": email,
                "Password": password,
                "UserAttributes": user_attrs,
            }
            if self.client_secret:
                params["SecretHash"] = self._secret_hash(email)
            response = self.client.sign_up(**params)
            return response
        except self.client.exceptions.UsernameExistsException:
            raise ValueError("Email already registered") from None
        except self.client.exceptions.InvalidPasswordException:
            raise ValueError("Invalid password") from None
        except ClientError as exc:
            raise RuntimeError(f"Cognito sign up failed: {exc}") from exc

    def confirm_sign_up(self, email: str, confirmation_code: str) -> None:
        self._ensure_configured()
        try:
            params = {
                "ClientId": self.client_id,
                "Username": email,
                "ConfirmationCode": confirmation_code,
            }
            if self.client_secret:
                params["SecretHash"] = self._secret_hash(email)
            self.client.confirm_sign_up(**params)
        except self.client.exceptions.NotAuthorizedException:
            raise ValueError("User is already confirmed") from None
        except self.client.exceptions.CodeMismatchException:
            raise ValueError("Invalid confirmation code") from None
        except self.client.exceptions.ExpiredCodeException:
            raise ValueError("Confirmation code expired") from None
        except ClientError as exc:
            raise RuntimeError(f"Cognito confirm failed: {exc}") from exc

    def initiate_auth(self, email: str, password: str) -> dict[str, Any]:
        self._ensure_configured()
        try:
            params = {
                "ClientId": self.client_id,
                "AuthFlow": "USER_PASSWORD_AUTH",
                "AuthParameters": {
                    "USERNAME": email,
                    "PASSWORD": password,
                },
            }
            if self.client_secret:
                params["AuthParameters"]["SECRET_HASH"] = self._secret_hash(email)
            response = self.client.initiate_auth(**params)
            return response["AuthenticationResult"]
        except self.client.exceptions.NotAuthorizedException:
            raise ValueError("Invalid credentials") from None
        except self.client.exceptions.UserNotConfirmedException:
            raise ValueError("User not confirmed") from None
        except self.client.exceptions.UserNotFoundException:
            raise ValueError("Invalid credentials") from None
        except ClientError as exc:
            raise RuntimeError(f"Cognito auth failed: {exc}") from exc

    def refresh_token(self, refresh_token: str) -> dict[str, Any]:
        self._ensure_configured()
        try:
            params = {
                "ClientId": self.client_id,
                "AuthFlow": "REFRESH_TOKEN_AUTH",
                "AuthParameters": {
                    "REFRESH_TOKEN": refresh_token,
                },
            }
            if self.client_secret:
                params["AuthParameters"]["SECRET_HASH"] = self._secret_hash_by_token(refresh_token)
            response = self.client.initiate_auth(**params)
            return response["AuthenticationResult"]
        except self.client.exceptions.NotAuthorizedException:
            raise ValueError("Invalid refresh token") from None
        except ClientError as exc:
            raise RuntimeError(f"Cognito refresh failed: {exc}") from exc

    def logout(self, access_token: str) -> None:
        self._ensure_configured()
        try:
            self.client.global_sign_out(AccessToken=access_token)
        except ClientError as exc:
            raise RuntimeError(f"Cognito logout failed: {exc}") from exc

    def get_user(self, access_token: str) -> dict[str, Any]:
        self._ensure_configured()
        try:
            response = self.client.get_user(AccessToken=access_token)
            return response
        except self.client.exceptions.NotAuthorizedException:
            raise ValueError("Invalid access token") from None
        except ClientError as exc:
            raise RuntimeError(f"Cognito get user failed: {exc}") from exc

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

    def _secret_hash_by_token(self, token: str) -> str:
        return self._secret_hash(token)
