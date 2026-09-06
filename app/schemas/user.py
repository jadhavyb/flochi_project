from pydantic import BaseModel


class UserResponse(BaseModel):
    id: str
    cognito_sub: str
    email: str
    first_name: str | None
    last_name: str | None
    is_active: bool
