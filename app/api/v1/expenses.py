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

@router.get("/groups/{group_id}/members", response_model=List[str])
async def get_group_members(
    group_id: int,
    current_user: User = Depends(get_current_active_user),
    expense_repo: ExpenseRepository = Depends()
):
    """Get all user names of a specific group"""
    return await expense_repo.get_group_member_names(group_id)

@router.delete("/expenses/{expense_id}", status_code=204)
async def delete_expense(
    expense_id: int,
    current_user: User = Depends(get_current_active_user),
    expense_repo: ExpenseRepository = Depends()
):
    """Delete an expense. Only the owner can delete their expenses."""
    deleted = await expense_repo.delete_expense(expense_id, current_user.id)
    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Expense not found or you don't have permission to delete it"
        )
    return 

@router.delete("/groups/{group_id}")  # Remove status_code=204
async def delete_group(
    group_id: int,
    current_user: User = Depends(get_current_active_user),
    expense_repo: ExpenseRepository = Depends()
):
    """Delete a group and all its members. Only the group creator can delete it."""
    deleted = await expense_repo.delete_group(group_id, current_user.id)
    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Group not found or you don't have permission to delete it"
        )
    return {"message": "Group deleted successfully", "group_id": group_id}