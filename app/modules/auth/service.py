from datetime import datetime, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import app.core.redis as redis_module
from app.core.config import settings
from app.core.database import get_db
from app.core.logging import get_logger

logger = get_logger("auth")
from app.models.user import User
from app.modules.auth import utils
from app.modules.auth.schemas import ChangePasswordRequest, LoginRequest, RefreshRequest, RegisterRequest, TokenResponse, UserResponse

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
    logger.info("user_registered", extra={"user_id": user.id, "email": user.email})
    return UserResponse.model_validate(user)


async def login(payload: LoginRequest, db: AsyncSession) -> TokenResponse:
    user = await db.scalar(select(User).where(User.email == payload.email))
    if not user or not utils.verify_password(payload.password, user.hashed_password):
        logger.warning("login_failed", extra={"email": payload.email})
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    access_token = utils.create_access_token({"sub": str(user.id)})
    refresh_token = utils.create_refresh_token()

    await redis_module.redis_client.setex(
        f"refresh:{refresh_token}",
        settings.refresh_token_expire_days * 24 * 60 * 60,
        str(user.id),
    )

    logger.info("user_logged_in", extra={"user_id": user.id, "email": user.email})
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


async def logout(token: str, payload: RefreshRequest) -> dict:
    access_payload = utils.decode_access_token(token)
    exp = access_payload.get("exp")
    if exp:
        ttl = int(exp - datetime.now(timezone.utc).timestamp())
        if ttl > 0:
            await redis_module.redis_client.setex(f"blacklist:{token}", ttl, "1")

    await redis_module.redis_client.delete(f"refresh:{payload.refresh_token}")
    logger.info("user_logged_out")
    return {"message": "Successfully logged out"}


async def refresh(payload: RefreshRequest, db: AsyncSession) -> TokenResponse:
    user_id = await redis_module.redis_client.get(f"refresh:{payload.refresh_token}")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired refresh token")

    user = await db.get(User, int(user_id))
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    await redis_module.redis_client.delete(f"refresh:{payload.refresh_token}")

    new_access_token = utils.create_access_token({"sub": str(user.id)})
    new_refresh_token = utils.create_refresh_token()

    await redis_module.redis_client.setex(
        f"refresh:{new_refresh_token}",
        settings.refresh_token_expire_days * 24 * 60 * 60,
        str(user.id),
    )

    return TokenResponse(access_token=new_access_token, refresh_token=new_refresh_token)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    if await redis_module.redis_client.exists(f"blacklist:{token}"):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has been revoked")

    payload = utils.decode_access_token(token)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    user = await db.get(User, int(user_id))
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    return UserResponse.model_validate(user)


async def change_password(
    payload: ChangePasswordRequest,
    current_user: UserResponse,
    db: AsyncSession,
) -> dict:
    user = await db.get(User, current_user.id)
    if not utils.verify_password(payload.current_password, user.hashed_password):
        logger.warning("change_password_failed", extra={"user_id": current_user.id})
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Current password is incorrect")

    user.hashed_password = utils.hash_password(payload.new_password)
    await db.commit()
    logger.info("password_changed", extra={"user_id": current_user.id})
    return {"message": "Password changed successfully"}
