from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    """Request model for user login."""

    username: str = Field(..., min_length=1, max_length=100)
    password: str = Field(..., min_length=1, max_length=100)


class LoginResponse(BaseModel):
    """Response model for successful login."""

    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """JWT token payload structure."""

    sub: str  # subject (username)
    exp: int  # expiration timestamp
