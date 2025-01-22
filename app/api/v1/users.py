# app/api/v1/users.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status

from app.db.repositories.expenses import ExpenseRepository
from app.models.user import UserBasic
from ...db.repositories.users import UserRepository
from ...schemas.user import UserCreate, User

from ...dependencies import get_current_active_user, get_current_user
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

@router.patch("/deactivate", response_model=User)
async def deactivate_user(
    current_user: User = Depends(get_current_user),
    user_repo: UserRepository = Depends()
):
    return await user_repo.update_active_status(current_user.id, False)


@router.get("/users/search", response_model=List[UserBasic])  # Remove {query} from path
async def search_users(
    query: str = None,
    current_user: User = Depends(get_current_active_user),
    expense_repo: ExpenseRepository = Depends()
):
    """Search for users by username or get top 100 users if no query provided"""
    return await expense_repo.search_users(query=query, current_user_id=current_user.id)