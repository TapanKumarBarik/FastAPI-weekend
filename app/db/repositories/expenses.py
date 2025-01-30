from typing import List, Optional

from fastapi import HTTPException
from ...models.expense import Expense, Group
from ...schemas.expense import ExpenseCreate, GroupCreate
from ..database import database

class ExpenseRepository:
    
    async def create_expense(self, user_id: int, expense: ExpenseCreate) -> dict:
        
        # Validate group exists if group_id is provided
        if expense.group_id:
            group = await self.get_group_details(expense.group_id)
            if not group:
                raise HTTPException(status_code=404, detail="Group not found")
            
            # Check if user is member of group
            if user_id not in group['member_ids']:
                raise HTTPException(
                status_code=403, 
                detail="You must be a member of the group to create expenses"
                )

        try:
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
        
        except Exception as e:
            raise HTTPException(
            status_code=500,
            detail=f"Database error while creating expense: {str(e)}"
            )
            
            
    async def create_group(self, user_id: int, group: GroupCreate) -> dict:
        
        # Validate member_ids
        if not group.member_ids:
            raise HTTPException(
                status_code=400,
                detail="At least one member is required"
            )
        
        # Check if all members exist
        for member_id in group.member_ids:
            member_exists = await self.check_user_exists(member_id)
            if not member_exists:
                raise HTTPException(
                    status_code=400,
                    detail=f"User with id {member_id} does not exist"
                )

        try:
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
            
            # Return complete group details including member count and member ids
            result_query = """
            SELECT 
                g.id, 
                g.name, 
                g.created_by, 
                g.created_at,
                COUNT(gm.user_id) as member_count,
                ARRAY_AGG(gm.user_id) as member_ids
            FROM groups g
            LEFT JOIN group_members gm ON g.id = gm.group_id
            WHERE g.id = :group_id
            GROUP BY g.id, g.name, g.created_by, g.created_at
            """
            return await database.fetch_one(query=result_query, values={"group_id": group_record['id']})
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Database error while creating group: {str(e)}"
            )
     
     
    async def check_user_exists(self, user_id: int) -> bool:
        """Check if a user exists in the database"""
        query = """
        SELECT id FROM users WHERE id = :user_id
        """
        result = await database.fetch_one(query=query, values={"user_id": user_id})
        return result is not None   
            
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
            SELECT 
                e.id,
                e.amount,
                e.description,
                e.user_id,
                e.group_id,
                e.created_at,
                g.id as group_id,
                g.name as group_name
            FROM expenses e
            LEFT JOIN groups g ON e.group_id = g.id
            WHERE e.user_id = :user_id
            ORDER BY e.created_at DESC
            """
        rows = await database.fetch_all(query=query, values={"user_id": user_id})
            
            # Format the results to include nested group object
        expenses = []
        for row in rows:
            expense = dict(row)
            if expense['group_id']:
                expense['group'] = {
                        'id': expense['group_id'],
                        'name': expense['group_name']
                }
            else:
                expense['group'] = None
                    
            # Clean up extra fields
            del expense['group_id']
            del expense['group_name']
            expenses.append(expense)
                
        return expenses
    
    async def get_group_expenses(self, group_id: int) -> List[dict]:
        query = """
        SELECT id, amount, description, user_id, group_id, created_at
        FROM expenses
        WHERE group_id = :group_id
        ORDER BY created_at DESC
        """
        return await database.fetch_all(query=query, values={"group_id": group_id})
    
    async def get_user_expenses_by_period(self, user_id: int, period: str, value: int) -> List[dict]:
        query = """
        SELECT id, amount, description, user_id, group_id, created_at
        FROM expenses
        WHERE user_id = :user_id 
        AND date_trunc(:period, created_at) = date_trunc(:period, TIMESTAMP :value)
        ORDER BY created_at DESC
        """
        values = {"user_id": user_id, "period": period, "value": value}
        return await database.fetch_all(query=query, values=values)

    async def get_user_groups(self, user_id: int) -> List[dict]:
        query = """
        WITH group_members_count AS (
            SELECT group_id, COUNT(*) as member_count
            FROM group_members
            GROUP BY group_id
        )
        SELECT 
            g.id, 
            g.name, 
            g.created_by, 
            g.created_at,
            gmc.member_count,
            ARRAY_AGG(gm2.user_id) as member_ids
        FROM groups g
        INNER JOIN group_members gm ON g.id = gm.group_id
        INNER JOIN group_members_count gmc ON g.id = gmc.group_id
        LEFT JOIN group_members gm2 ON g.id = gm2.group_id
        WHERE gm.user_id = :user_id
        GROUP BY g.id, g.name, g.created_by, g.created_at, gmc.member_count
        ORDER BY g.created_at DESC
        """
        return await database.fetch_all(query=query, values={"user_id": user_id})
    
    async def get_group_details(self, group_id: int) -> dict:
        query = """
        SELECT 
            g.id, 
            g.name, 
            g.created_by, 
            g.created_at,
            ARRAY_AGG(gm.user_id) as member_ids,
            COUNT(gm.user_id) as member_count
        FROM groups g
        LEFT JOIN group_members gm ON g.id = gm.group_id
        WHERE g.id = :group_id
        GROUP BY g.id, g.name, g.created_by, g.created_at
        """
        return await database.fetch_one(query=query, values={"group_id": group_id})
    
    async def get_group_member_names(self, group_id: int) -> List[str]:
        query = """
            SELECT u.username
            FROM users u
            INNER JOIN group_members gm ON u.id = gm.user_id
            WHERE gm.group_id = :group_id
            """
        rows = await database.fetch_all(query=query, values={"group_id": group_id})
        return [row["username"] for row in rows]
    
    # Add to ExpenseRepository class in app/db/repositories/expenses.py
    async def delete_expense(self, expense_id: int, user_id: int) -> bool:
        # First check if expense exists and belongs to user
        check_query = """
        SELECT id FROM expenses 
        WHERE id = :expense_id AND user_id = :user_id
        """
        expense = await database.fetch_one(
            query=check_query,
            values={"expense_id": expense_id, "user_id": user_id}
        )
        
        if not expense:
            return False
    
        # Delete the expense
        delete_query = """
        DELETE FROM expenses 
        WHERE id = :expense_id AND user_id = :user_id
        """
        await database.execute(
            query=delete_query,
            values={"expense_id": expense_id, "user_id": user_id}
        )
        return True
    async def search_users(self, query: str = None, current_user_id: int = None) -> List[dict]:
        """Search users by username or get top 100 users if no query"""
        if query:
            search_query = """
            SELECT id, username
            FROM users 
            WHERE username ILIKE :query
            AND id != :current_user_id
            LIMIT 10
            """
            values = {
                "query": f"%{query}%",
                "current_user_id": current_user_id
            }
        else:
            search_query = """
            SELECT id, username
            FROM users
            WHERE id != :current_user_id
            ORDER BY username
            LIMIT 100
            """
            values = {"current_user_id": current_user_id}
        
        users = await database.fetch_all(query=search_query, values=values)
        return [{"id": user["id"], "username": user["username"]} for user in users]
    async def delete_group(self, group_id: int, user_id: int) -> dict:
        """Delete a group and its members. Only the creator can delete the group."""
        try:
            async with database.transaction():
                # First check if group exists and user is the creator
                check_query = """
                SELECT id, name FROM groups 
                WHERE id = :group_id AND created_by = :user_id
                """
                group = await database.fetch_one(
                    query=check_query,
                    values={"group_id": group_id, "user_id": user_id}
                )
                
                if not group:
                    return False
                    
                # Delete group members first
                delete_members_query = """
                DELETE FROM group_members 
                WHERE group_id = :group_id
                """
                await database.execute(
                    query=delete_members_query,
                    values={"group_id": group_id}
                )
                
                # Delete associated expenses
                delete_expenses_query = """
                DELETE FROM expenses 
                WHERE group_id = :group_id
                """
                await database.execute(
                    query=delete_expenses_query,
                    values={"group_id": group_id}
                )
                
                # Finally delete the group
                delete_group_query = """
                DELETE FROM groups 
                WHERE id = :group_id AND created_by = :user_id
                """
                await database.execute(
                    query=delete_group_query,
                    values={"group_id": group_id, "user_id": user_id}
                )
                
                return True
        except Exception as e:
            return False 