from __future__ import annotations

import time
from unittest.mock import AsyncMock, patch

import pytest

from app.core.security import CognitoJWTError, verify_access_token


def _make_claims(**overrides):
    defaults = {
        "sub": "cognito-sub-123",
        "email": "test@example.com",
        "token_use": "access",
        "exp": int(time.time()) + 3600,
        "iss": "https://cognito-idp.us-east-1.amazonaws.com/us-east-1_test",
        "aud": "test-client-id",
        "client_id": "test-client-id",
        "username": "testuser",
    }
    defaults.update(overrides)
    return defaults


@pytest.mark.asyncio
async def test_verify_access_token_valid():
    with patch("app.core.security._get_cognito_public_keys", return_value=[
        {"kty": "RSA", "kid": "test-kid", "e": "AQAB", "n": "test-n"}
    ]):
        with patch("jose.jwt.decode", return_value=_make_claims()):
            claims = await verify_access_token("valid-token")
            assert claims.sub == "cognito-sub-123"
            assert claims.email == "test@example.com"


@pytest.mark.asyncio
async def test_verify_access_token_missing_kid():
    with patch("jose.jwt.get_unverified_header", return_value={"alg": "RS256"}):
        with pytest.raises(CognitoJWTError, match="Token missing kid header"):
            await verify_access_token("invalid-token")


@pytest.mark.asyncio
async def test_verify_access_token_key_not_found():
    with patch("jose.jwt.get_unverified_header", return_value={"kid": "unknown-kid"}):
        with pytest.raises(CognitoJWTError, match="Public key not found"):
            await verify_access_token("invalid-token")


@pytest.mark.asyncio
async def test_verify_access_token_expired():
    from jose.exceptions import ExpiredSignatureError
    with patch("app.core.security._get_cognito_public_keys", return_value=[
        {"kty": "RSA", "kid": "test-kid", "e": "AQAB", "n": "test-n"}
    ]):
        with patch("jose.jwt.decode", side_effect=ExpiredSignatureError("expired")):
            with pytest.raises(CognitoJWTError, match="Token expired"):
                await verify_access_token("expired-token")


@pytest.mark.asyncio
async def test_verify_access_token_invalid_issuer():
    with patch("app.core.security._get_cognito_public_keys", return_value=[
        {"kty": "RSA", "kid": "test-kid", "e": "AQAB", "n": "test-n"}
    ]):
        with patch("jose.jwt.decode", return_value=_make_claims(iss="wrong-issuer")):
            with pytest.raises(CognitoJWTError, match="Invalid issuer"):
                await verify_access_token("invalid-token")


@pytest.mark.asyncio
async def test_verify_access_token_invalid_audience():
    with patch("app.core.security._get_cognito_public_keys", return_value=[
        {"kty": "RSA", "kid": "test-kid", "e": "AQAB", "n": "test-n"}
    ]):
        with patch("jose.jwt.decode", return_value=_make_claims(aud="wrong-audience")):
            with pytest.raises(CognitoJWTError, match="Invalid audience"):
                await verify_access_token("invalid-token")


@pytest.mark.asyncio
async def test_verify_access_token_wrong_token_use():
    with patch("app.core.security._get_cognito_public_keys", return_value=[
        {"kty": "RSA", "kid": "test-kid", "e": "AQAB", "n": "test-n"}
    ]):
        with patch("jose.jwt.decode", return_value=_make_claims(token_use="id")):
            with pytest.raises(CognitoJWTError, match="Invalid token use"):
                await verify_access_token("invalid-token")
