from datetime import datetime

from app.modules.auth.schemas import LoginRequest, RegisterRequest, TokenResponse, UserResponse

MOCK_USER = UserResponse(
    id=1,
    email="user@example.com",
    username="john_doe",
    is_active=True,
    created_at=datetime(2026, 1, 1, 12, 0, 0),
)


def register(payload: RegisterRequest) -> UserResponse:
    return MOCK_USER


def login(payload: LoginRequest) -> TokenResponse:
    return TokenResponse(access_token="mock.jwt.token")


def get_current_user() -> UserResponse:
    return MOCK_USER
