# app/api/v1/users.py
from fastapi import APIRouter, Depends, HTTPException, status
from ...db.repositories.users import UserRepository
from ...schemas.user import UserCreate, User

from ...dependencies import get_current_user
router = APIRouter()

@router.post("/register", response_model=User)
async def register(
    user: UserCreate,
    user_repo: UserRepository = Depends()
):
    if await user_repo.get_by_email(user.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    if await user_repo.get_by_username(user.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    return await user_repo.create(user)

@router.get("/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

