from datetime import timezone
from typing import Any, Dict, List
from fastapi import HTTPException
from ...schemas.todo import TodoCreate, TodoStatus
from ..database import database

class TodoRepository:
    async def create_todo(self, user_id: int, todo: TodoCreate) -> dict:
        query = """
        INSERT INTO todos (title, description, due_date, status, user_id)
        VALUES (:title, :description, :due_date AT TIME ZONE 'UTC', :status, :user_id)
        RETURNING id, title, description, due_date, status, user_id, created_at
        """
        values = {
            **todo.dict(),
            "user_id": user_id
        }
        return await database.fetch_one(query=query, values=values)
    async def get_completed_todos(self, user_id: int) -> List[dict]:
        """Get all completed todos for a user"""
        query = """
        SELECT id, title, description, due_date, status, user_id, created_at
        FROM todos
        WHERE user_id = :user_id AND status = 'completed'
        ORDER BY created_at DESC
        """
        return await database.fetch_all(query=query, values={"user_id": user_id})  
    
    async def get_active_todos(self, user_id: int) -> List[dict]:
        query = """
        SELECT id, title, description, due_date, status, user_id, created_at
        FROM todos
        WHERE user_id = :user_id AND status != 'completed'
        ORDER BY due_date ASC
        """
        return await database.fetch_all(query=query, values={"user_id": user_id})
    
    def _ensure_timezone(self, values: Dict[str, Any]) -> Dict[str, Any]:
        """Helper to ensure datetime values have UTC timezone"""
        if 'due_date' in values and values['due_date']:
            if values['due_date'].tzinfo is None:
                values['due_date'] = values['due_date'].replace(tzinfo=timezone.utc)
        return values
    async def update_todo(self, todo_id: int, user_id: int, updates: Dict[str, Any]) -> dict:
        # First check if todo exists and belongs to user
        check_query = """
        SELECT id FROM todos 
        WHERE id = :todo_id AND user_id = :user_id
        """
        todo = await database.fetch_one(
            query=check_query,
            values={"todo_id": todo_id, "user_id": user_id}
        )
        
        if not todo:
            return None

        # Build UPDATE query dynamically based on provided fields
        set_parts = []
        values = {"todo_id": todo_id, "user_id": user_id}
        
        if 'title' in updates:
            set_parts.append("title = :title")
            values['title'] = updates['title']
        
        if 'description' in updates:
            set_parts.append("description = :description")
            values['description'] = updates['description']
        
        if 'due_date' in updates:
            set_parts.append("due_date = :due_date AT TIME ZONE 'UTC'")
            values['due_date'] = updates['due_date']
        
        if 'status' in updates:
            set_parts.append("status = :status")
            values['status'] = updates['status']

        if not set_parts:
            return await self.get_todo(todo_id, user_id)

        query = f"""
        UPDATE todos 
        SET {', '.join(set_parts)}
        WHERE id = :todo_id AND user_id = :user_id
        RETURNING id, title, description, due_date, status, user_id, created_at
        """
        
        result = await database.fetch_one(query=query, values=values)
        return dict(result) if result else None
    
    async def delete_todo(self, todo_id: int, user_id: int) -> bool:
        # First check if todo exists and belongs to user
        check_query = """
        SELECT id FROM todos 
        WHERE id = :todo_id AND user_id = :user_id
        """
        todo = await database.fetch_one(
            query=check_query,
            values={"todo_id": todo_id, "user_id": user_id}
        )
        
        if not todo:
            return False
    
        # Delete the todo
        query = """
        DELETE FROM todos
        WHERE id = :todo_id AND user_id = :user_id
        RETURNING id
        """
        result = await database.fetch_one(
            query=query,
            values={"todo_id": todo_id, "user_id": user_id}
        )
        return result is not None