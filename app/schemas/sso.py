from pydantic import BaseModel


class ProviderResponse(BaseModel):
    name: str
    enabled: bool


class ProvidersResponse(BaseModel):
    providers: list[ProviderResponse]


class AuthorizeResponse(BaseModel):
    authorization_url: str
    state: str


class CallbackResponse(BaseModel):
    access_token: str
    refresh_token: str
    expires_in: int
    token_type: str = "bearer"
    provider: str


class LinkedIdentityResponse(BaseModel):
    id: str
    provider: str
    provider_subject: str
    email: str | None
    created_at: str
