from typing import List, Optional

from fastapi import HTTPException
from ...models.expense import Expense, Group
from ...schemas.expense import ExpenseCreate, GroupCreate
from ..database import database

class ExpenseRepository:
    async def create_expense(self, user_id: int, expense: ExpenseCreate) -> dict:
        query = """
        INSERT INTO expenses (amount, description, user_id, group_id)
        VALUES (:amount, :description, :user_id, :group_id)
        RETURNING 
            id, 
            amount, 
            description, 
            user_id, 
            group_id, 
            created_at::timestamp
        """
        values = {
            "amount": expense.amount,
            "description": expense.description,
            "user_id": user_id,
            "group_id": expense.group_id
        }
        result = await database.fetch_one(query=query, values=values)
        if result:
            return dict(result)
        raise HTTPException(status_code=400, detail="Failed to create expense")

    async def create_group(self, user_id: int, group: GroupCreate) -> dict:
        # First check if user already created a group with same name
        check_query = """
        SELECT id FROM groups 
        WHERE name = :name AND created_by = :user_id
        """
        existing_group = await database.fetch_one(
            query=check_query, 
            values={"name": group.name, "user_id": user_id}
        )
        
        if existing_group:
            raise HTTPException(
                status_code=400, 
                detail="You already have a group with this name"
            )

        # Create group
        query = """
        INSERT INTO groups (name, created_by)
        VALUES (:name, :created_by)
        RETURNING id, name, created_by, created_at
        """
        values = {"name": group.name, "created_by": user_id}
        group_record = await database.fetch_one(query=query, values=values)
        
        # Add creator as first member
        await self.add_group_member(group_record['id'], user_id)
        
        # Add other members
        for member_id in group.member_ids:
            if member_id != user_id:  # Don't add creator twice
                await self.add_group_member(group_record['id'], member_id)
        
        return group_record

    async def add_member_to_group(self, group_id: int, new_user_id: int) -> dict:
        # Check if group exists
        group_query = "SELECT created_by FROM groups WHERE id = :group_id"
        group = await database.fetch_one(
            query=group_query, 
            values={"group_id": group_id}
        )
        
        if not group:
            raise HTTPException(status_code=404, detail="Group not found")
        
        # Check if user is already a member
        check_query = """
        SELECT user_id FROM group_members 
        WHERE group_id = :group_id AND user_id = :user_id
        """
        existing_member = await database.fetch_one(
            query=check_query, 
            values={"group_id": group_id, "user_id": new_user_id}
        )
        
        if existing_member:
            raise HTTPException(
                status_code=400, 
                detail="User is already a member of this group"
            )
        
        # Add new member
        await self.add_group_member(group_id, new_user_id)
        
        return {"message": "Member added successfully"}
    async def add_group_member(self, group_id: int, user_id: int) -> dict:
        query = """
        INSERT INTO group_members (group_id, user_id)
        VALUES (:group_id, :user_id)
        RETURNING group_id, user_id
        """
        values = {"group_id": group_id, "user_id": user_id}
        return await database.fetch_one(query=query, values=values)

    async def get_user_expenses(self, user_id: int) -> List[dict]:
        query = """
        SELECT id, amount, description, user_id, group_id, created_at
        FROM expenses
        WHERE user_id = :user_id
        ORDER BY created_at DESC
        """
        return await database.fetch_all(query=query, values={"user_id": user_id})

    async def get_group_expenses(self, group_id: int) -> List[dict]:
        query = """
        SELECT id, amount, description, user_id, group_id, created_at
        FROM expenses
        WHERE group_id = :group_id
        ORDER BY created_at DESC
        """
        return await database.fetch_all(query=query, values={"group_id": group_id})