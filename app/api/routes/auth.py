from __future__ import annotations

from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_db
from app.core.exceptions import BadRequestError, UnauthorizedError
from app.models.user import User
from app.repositories.user_identity import UserIdentityRepository
from app.schemas.auth import (
    ConfirmRequest,
    LoginRequest,
    MeResponse,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
)
from app.schemas.sso import (
    AuthorizeResponse,
    CallbackResponse,
    LinkedIdentityResponse,
    ProviderResponse,
    ProvidersResponse,
)
from app.services.auth import AuthService
from app.services.auth.oauth import OAuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=dict, status_code=status.HTTP_201_CREATED)
async def register(
    body: RegisterRequest,
    db: AsyncSession = Depends(get_db),
) -> dict:
    print("-------------here")
    service = AuthService(db)
    try:
        await service.register(body.email, body.password, body.first_name, body.last_name)
    except ValueError as exc:
        raise BadRequestError(str(exc)) from exc
    return {"message": "Registration successful. Please check your email to confirm."}


@router.post("/confirm", response_model=dict)
async def confirm(
    body: ConfirmRequest,
    db: AsyncSession = Depends(get_db),
) -> dict:
    service = AuthService(db)
    try:
        await service.confirm(body.email, body.confirmation_code)
    except ValueError as exc:
        raise BadRequestError(str(exc)) from exc
    return {"message": "Account confirmed successfully"}


@router.post("/login", response_model=TokenResponse)
async def login(
    body: LoginRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    service = AuthService(db)
    try:
        tokens = await service.login(body.email, body.password)
    except ValueError as exc:
        raise UnauthorizedError(str(exc)) from exc
    return TokenResponse(**tokens)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    body: RefreshRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    service = AuthService(db)
    try:
        tokens = await service.refresh(body.refresh_token)
    except ValueError as exc:
        raise UnauthorizedError(str(exc)) from exc
    return TokenResponse(**tokens)


@router.post("/logout", response_model=dict)
async def logout(
    current_user: User = Depends(get_current_user),
) -> dict:
    return {"message": "Logged out successfully"}


@router.get("/providers", response_model=ProvidersResponse)
async def list_providers() -> ProvidersResponse:
    oauth = OAuthService()
    providers = oauth.get_providers()
    return ProvidersResponse(providers=[ProviderResponse(**p) for p in providers])


@router.get("/{provider}/authorize", response_model=AuthorizeResponse)
async def authorize(
    provider: str,
    request: Request,
    redirect_uri: str = Query(...),
) -> AuthorizeResponse:
    if provider not in ("google", "apple"):
        raise BadRequestError("Unsupported provider")
    oauth = OAuthService()
    try:
        url, state = oauth.get_authorization_url(provider, redirect_uri)
    except ValueError as exc:
        raise BadRequestError(str(exc)) from exc
    return AuthorizeResponse(authorization_url=url, state=state)


@router.get("/{provider}/callback", response_model=CallbackResponse)
async def callback(
    provider: str,
    code: str = Query(...),
    state: str = Query(...),
    redirect_uri: str = Query(...),
) -> CallbackResponse:
    if provider not in ("google", "apple"):
        raise BadRequestError("Unsupported provider")
    oauth = OAuthService()
    try:
        tokens = await oauth.handle_callback(provider, code, state, redirect_uri)
    except ValueError as exc:
        raise UnauthorizedError(str(exc)) from exc
    return CallbackResponse(
        access_token=tokens["AccessToken"],
        refresh_token=tokens["RefreshToken"],
        expires_in=int(tokens.get("ExpiresIn", 3600)),
        provider=provider,
    )


@router.get("/me", response_model=MeResponse)
async def me(
    current_user: User = Depends(get_current_user),
) -> MeResponse:
    return MeResponse(
        id=str(current_user.id),
        cognito_sub=current_user.cognito_sub,
        email=current_user.email,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        is_active=current_user.is_active,
        created_at=str(current_user.created_at),
    )


@router.get("/me/identities", response_model=list[LinkedIdentityResponse])
async def list_linked_identities(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[LinkedIdentityResponse]:
    identity_repo = UserIdentityRepository(db)
    identities = await identity_repo.get_by_user_id(current_user.id)
    return [
        LinkedIdentityResponse(
            id=str(identity.id),
            provider=identity.provider,
            provider_subject=identity.provider_subject,
            email=identity.email,
            created_at=str(identity.created_at),
        )
        for identity in identities
    ]
