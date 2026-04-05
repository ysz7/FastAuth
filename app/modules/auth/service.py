from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.user import User
from app.modules.auth import utils
from app.modules.auth.schemas import LoginRequest, RegisterRequest, TokenResponse, UserResponse

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def register(payload: RegisterRequest, db: AsyncSession) -> UserResponse:
    existing = await db.scalar(select(User).where(
        (User.email == payload.email) | (User.username == payload.username)
    ))
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email or username already taken")

    user = User(
        email=payload.email,
        username=payload.username,
        hashed_password=utils.hash_password(payload.password),
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return UserResponse.model_validate(user)


async def login(payload: LoginRequest, db: AsyncSession) -> TokenResponse:
    user = await db.scalar(select(User).where(User.email == payload.email))
    if not user or not utils.verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    token = utils.create_access_token({"sub": str(user.id)})
    return TokenResponse(access_token=token)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    payload = utils.decode_access_token(token)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    user = await db.get(User, int(user_id))
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    return UserResponse.model_validate(user)
