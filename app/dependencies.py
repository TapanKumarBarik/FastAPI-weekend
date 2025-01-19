# app/dependencies.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from typing import AsyncGenerator, Optional, Generator

from .config import get_settings
from .db.repositories.users import UserRepository
from .schemas.user import TokenData, User
from .core.exceptions import credentials_exception
from .db.database import database

settings = get_settings()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/token")

def get_user_repository() -> UserRepository:
    return UserRepository()

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    user_repo: UserRepository = Depends(get_user_repository)
) -> User:
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception

    user = await user_repo.get_by_username(username=token_data.username)
    if user is None:
        raise credentials_exception

    return User(**user)

async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user

# Database dependency
async def get_db() -> AsyncGenerator:
    try:
        await database.connect()
        yield database
    finally:
        await database.disconnect()

