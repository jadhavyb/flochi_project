from __future__ import annotations

from typing import Any

from botocore.exceptions import ClientError

from app.core.config import settings
from app.integrations.aws.clients import AWSClientFactory


class CognitoService:
    def __init__(self):
        self.client = AWSClientFactory.create_client("cognito-idp")
        self.user_pool_id = settings.cognito_user_pool_id
        self.client_id = settings.cognito_client_id
        self.client_secret = settings.cognito_client_secret

    def sign_up(
        self, email: str, password: str, first_name: str | None, last_name: str | None
    ) -> dict[str, Any]:
        user_attrs = []
        if first_name:
            user_attrs.append({"Name": "given_name", "Value": first_name})
        if last_name:
            user_attrs.append({"Name": "family_name", "Value": last_name})

        try:
            response = self.client.sign_up(
                ClientId=self.client_id,
                SecretHash=self._secret_hash(email),
                Username=email,
                Password=password,
                UserAttributes=user_attrs,
            )
            return response
        except self.client.exceptions.UsernameExistsException:
            raise ValueError("Email already registered") from None
        except self.client.exceptions.InvalidPasswordException:
            raise ValueError("Invalid password") from None
        except ClientError as exc:
            raise RuntimeError(f"Cognito sign up failed: {exc}") from exc

    def confirm_sign_up(self, email: str, confirmation_code: str) -> None:
        try:
            self.client.confirm_sign_up(
                ClientId=self.client_id,
                SecretHash=self._secret_hash(email),
                Username=email,
                ConfirmationCode=confirmation_code,
            )
        except self.client.exceptions.NotAuthorizedException:
            raise ValueError("User is already confirmed") from None
        except self.client.exceptions.CodeMismatchException:
            raise ValueError("Invalid confirmation code") from None
        except self.client.exceptions.ExpiredCodeException:
            raise ValueError("Confirmation code expired") from None
        except ClientError as exc:
            raise RuntimeError(f"Cognito confirm failed: {exc}") from exc

    def initiate_auth(self, email: str, password: str) -> dict[str, Any]:
        try:
            response = self.client.initiate_auth(
                ClientId=self.client_id,
                AuthFlow="USER_PASSWORD_AUTH",
                AuthParameters={
                    "USERNAME": email,
                    "PASSWORD": password,
                    "SECRET_HASH": self._secret_hash(email),
                },
            )
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
        try:
            response = self.client.initiate_auth(
                ClientId=self.client_id,
                AuthFlow="REFRESH_TOKEN_AUTH",
                AuthParameters={
                    "REFRESH_TOKEN": refresh_token,
                    "SECRET_HASH": self._secret_hash_by_token(refresh_token),
                },
            )
            return response["AuthenticationResult"]
        except self.client.exceptions.NotAuthorizedException:
            raise ValueError("Invalid refresh token") from None
        except ClientError as exc:
            raise RuntimeError(f"Cognito refresh failed: {exc}") from exc

    def logout(self, access_token: str) -> None:
        try:
            self.client.global_sign_out(AccessToken=access_token)
        except ClientError as exc:
            raise RuntimeError(f"Cognito logout failed: {exc}") from exc

    def get_user(self, access_token: str) -> dict[str, Any]:
        try:
            response = self.client.get_user(AccessToken=access_token)
            return response
        except self.client.exceptions.NotAuthorizedException:
            raise ValueError("Invalid access token") from None
        except ClientError as exc:
            raise RuntimeError(f"Cognito get user failed: {exc}") from exc

    def _secret_hash(self, username: str) -> str:
        import base64
        import hashlib
        import hmac

        message = bytes(username + self.client_id, "utf-8")
        secret = bytes(self.client_secret, "utf-8")
        digest = hmac.new(secret, message, hashlib.sha256).digest()
        return base64.b64encode(digest).decode()

    def _secret_hash_by_token(self, token: str) -> str:
        return self._secret_hash(token)
