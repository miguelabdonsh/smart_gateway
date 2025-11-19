from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, HTTPException, status
from jwt import encode

from gateway.config.settings import settings
from gateway.models.auth import LoginRequest, LoginResponse

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/login", response_model=LoginResponse)
async def login(credentials: LoginRequest) -> LoginResponse:
    """
    Simple login endpoint for JWT token generation.
    For v1.0: hardcoded test user validation.
    """
    # Simple validation (hardcoded for v1.0)
    if credentials.username != "test" or credentials.password != "test":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Generate JWT token
    expiry = datetime.now(timezone.utc) + timedelta(hours=24)
    payload = {
        "sub": credentials.username,
        "exp": int(expiry.timestamp()),
    }

    token = encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

    return LoginResponse(access_token=token)
