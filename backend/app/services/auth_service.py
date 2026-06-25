# backend/app/services/auth_service.py

from __future__ import annotations
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.exceptions import (
    BadRequestException,
    ConflictException,
    CredentialsException,
)
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models.user import User
from app.repositories.user_repo import UserRepository
from app.schemas.auth import TokenResponse, UserRegisterRequest


class AuthService:
    def __init__(self, db: AsyncSession):
        self.repo = UserRepository(db)

    async def register(self, data: UserRegisterRequest) -> User:
        existing = await self.repo.get_by_email(data.email)
        if existing:
            raise ConflictException("An account with this email already exists.")
        user = await self.repo.create(
            email=data.email,
            hashed_password=hash_password(data.password),
            full_name=data.full_name,
        )
        return user

    async def login(self, email: str, password: str) -> TokenResponse:
        user = await self.repo.get_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            raise CredentialsException("Invalid email or password.")
        if not user.is_active:
            raise BadRequestException("Account is deactivated.")
        return TokenResponse(
            access_token=create_access_token(str(user.id)),
            refresh_token=create_refresh_token(str(user.id)),
        )

    async def refresh(self, refresh_token: str) -> TokenResponse:
        try:
            payload = decode_token(refresh_token)
            if payload.get("type") != "refresh":
                raise CredentialsException("Invalid token type.")
            user_id = payload.get("sub")
            if not user_id:
                raise CredentialsException()
        except Exception:
            raise CredentialsException("Refresh token is invalid or expired.")
        return TokenResponse(
            access_token=create_access_token(user_id),
            refresh_token=create_refresh_token(user_id),
        )

    async def get_current_user(self, token: str) -> User:
        try:
            payload = decode_token(token)
            user_id = payload.get("sub")
            if not user_id:
                raise CredentialsException()
        except Exception:
            raise CredentialsException()
        user = await self.repo.get_by_id(uuid.UUID(user_id))
        if not user or not user.is_active:
            raise CredentialsException("User not found or inactive.")
        return user