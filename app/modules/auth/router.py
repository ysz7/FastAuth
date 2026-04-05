from fastapi import APIRouter

from app.modules.auth import service
from app.modules.auth.schemas import LoginRequest, RegisterRequest, TokenResponse, UserResponse

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=UserResponse, status_code=201)
def register(payload: RegisterRequest):
    return service.register(payload)


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest):
    return service.login(payload)


@router.get("/me", response_model=UserResponse)
def me():
    return service.get_current_user()
