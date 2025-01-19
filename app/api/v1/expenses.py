from fastapi import APIRouter, Depends, HTTPException
from typing import List
from ...db.repositories.expenses import ExpenseRepository
from ...schemas.expense import Expense, ExpenseCreate, Group, GroupCreate
from ...dependencies import get_current_active_user
from ...schemas.user import User
from datetime import datetime
from enum import Enum

router = APIRouter()


class Period(str, Enum):
    day = "day"
    month = "month"
    year = "year"
    
@router.post("/expenses/", response_model=Expense)
async def create_expense(
    expense: ExpenseCreate,
    current_user: User = Depends(get_current_active_user),
    expense_repo: ExpenseRepository = Depends()
):
    return await expense_repo.create_expense(current_user.id, expense)

@router.get("/expenses/", response_model=List[Expense])
async def get_user_expenses(
    current_user: User = Depends(get_current_active_user),
    expense_repo: ExpenseRepository = Depends()
):
    return await expense_repo.get_user_expenses(current_user.id)

@router.post("/groups/", response_model=Group)
async def create_group(
    group: GroupCreate,
    current_user: User = Depends(get_current_active_user),
    expense_repo: ExpenseRepository = Depends()
):
    return await expense_repo.create_group(current_user.id, group)

@router.get("/groups/{group_id}/expenses", response_model=List[Expense])
async def get_group_expenses(
    group_id: int,
    current_user: User = Depends(get_current_active_user),
    expense_repo: ExpenseRepository = Depends()
):
    return await expense_repo.get_group_expenses(group_id)

@router.post("/groups/{group_id}/members/{user_id}")
async def add_member(
    group_id: int,
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    expense_repo: ExpenseRepository = Depends()
):
    return await expense_repo.add_member_to_group(group_id, user_id)



@router.get("/expenses/{period}/{value}", response_model=List[Expense])
async def get_expenses_by_period(
    period: Period,
    value: datetime,
    current_user: User = Depends(get_current_active_user),
    expense_repo: ExpenseRepository = Depends()
):
    """
    Get expenses for a specific day, month or year.
    Value should be in ISO format: YYYY-MM-DD
    """
    return await expense_repo.get_user_expenses_by_period(current_user.id, period, value)

@router.get("/groups/", response_model=List[Group])
async def get_my_groups(
    current_user: User = Depends(get_current_active_user),
    expense_repo: ExpenseRepository = Depends()
):
    """Get all groups where the current user is a member"""
    return await expense_repo.get_user_groups(current_user.id)


@router.get("/groups/{group_id}", response_model=Group)
async def get_group_details(
    group_id: int,
    current_user: User = Depends(get_current_active_user),
    expense_repo: ExpenseRepository = Depends()
):
    """Get detailed information about a specific group including members"""
    return await expense_repo.get_group_details(group_id)