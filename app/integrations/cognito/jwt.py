from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any

import httpx
from jose import JWTError, jwt
from jose.exceptions import ExpiredSignatureError, JWTClaimsError

from app.core.config import settings


class CognitoJWTError(Exception):
    pass


@dataclass
class CognitoClaims:
    sub: str
    email: str
    token_use: str
    exp: int
    iss: str
    aud: str
    client_id: str
    username: str


async def _get_cognito_public_keys() -> list[dict[str, Any]]:
    if not settings.cognito_user_pool_id or not settings.aws_region:
        raise CognitoJWTError("Cognito User Pool ID and AWS region must be configured")

    url = (
        f"https://cognito-idp.{settings.aws_region}.amazonaws.com/"
        f"{settings.cognito_user_pool_id}/.well-known/jwks.json"
    )

    async with httpx.AsyncClient() as client:
        if settings.aws_endpoint_url:
            response = await client.get(url, base_url=settings.aws_endpoint_url)
        else:
            response = await client.get(url)
        response.raise_for_status()
        return response.json().get("keys", [])


def _verify_token_claims(claims: dict[str, Any], token_use: str) -> None:
    if claims.get("token_use") != token_use:
        raise CognitoJWTError(f"Invalid token use: expected {token_use}")

    if claims.get("iss") != settings.jwt_issuer:
        raise CognitoJWTError(f"Invalid issuer: {claims.get('iss')}")

    if claims.get("aud") not in (settings.jwt_audience, settings.cognito_client_id):
        raise CognitoJWTError("Invalid audience")

    if time.time() > claims.get("exp", 0):
        raise CognitoJWTError("Token expired")


async def verify_access_token(token: str) -> CognitoClaims:
    try:
        keys = await _get_cognito_public_keys()
    except Exception as exc:
        raise CognitoJWTError(f"Failed to fetch public keys: {exc}") from exc

    unverified_header = jwt.get_unverified_header(token)
    kid = unverified_header.get("kid")
    if not kid:
        raise CognitoJWTError("Token missing kid header")

    key = next((k for k in keys if k.get("kid") == kid), None)
    if key is None:
        raise CognitoJWTError("Public key not found for token")

    public_key = {
        "kty": key["kty"],
        "kid": key["kid"],
        "e": key["e"],
        "n": key["n"],
    }

    try:
        claims = jwt.decode(
            token,
            public_key,
            algorithms=["RS256"],
            issuer=settings.jwt_issuer,
            options={"verify_aud": False},
        )
    except ExpiredSignatureError as exc:
        raise CognitoJWTError("Token expired") from exc
    except JWTClaimsError as exc:
        raise CognitoJWTError(f"Invalid token claims: {exc}") from exc
    except JWTError as exc:
        raise CognitoJWTError(f"Invalid token: {exc}") from exc

    _verify_token_claims(claims, token_use="access")

    return CognitoClaims(
        sub=claims["sub"],
        email=claims.get("email", ""),
        token_use=claims["token_use"],
        exp=claims["exp"],
        iss=claims["iss"],
        aud=claims.get("aud", ""),
        client_id=claims.get("client_id", ""),
        username=claims.get("username", ""),
    )
