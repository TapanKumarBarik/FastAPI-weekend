from fastapi import APIRouter, Depends, HTTPException
from typing import List
from ...schemas.todo import Todo, TodoCreate
from ...db.repositories.todos import TodoRepository
from ...dependencies import get_current_active_user
from ...schemas.user import User

router = APIRouter()

@router.post("/todos/", response_model=Todo)
async def create_todo(
    todo: TodoCreate,
    current_user: User = Depends(get_current_active_user),
    todo_repo: TodoRepository = Depends()
):
    """Create a new todo item"""
    return await todo_repo.create_todo(current_user.id, todo)

@router.get("/todos/", response_model=List[Todo])
async def get_active_todos(
    current_user: User = Depends(get_current_active_user),
    todo_repo: TodoRepository = Depends()
):
    """Get all active (not completed) todos"""
    return await todo_repo.get_active_todos(current_user.id)

@router.patch("/todos/{todo_id}", response_model=Todo)
async def update_todo(
    todo_id: int,
    updates: TodoCreate,
    current_user: User = Depends(get_current_active_user),
    todo_repo: TodoRepository = Depends()
):
    """Update a todo item"""
    result = await todo_repo.update_todo(todo_id, current_user.id, updates.dict(exclude_unset=True))
    if not result:
        raise HTTPException(status_code=404, detail="Todo not found")
    return result


from pydantic import BaseModel

# Add this response model at the top with other models
class DeleteResponse(BaseModel):
    message: str
    
@router.delete("/todos/{todo_id}", status_code=200, response_model=DeleteResponse)
async def delete_todo(
    todo_id: int,
    current_user: User = Depends(get_current_active_user),
    todo_repo: TodoRepository = Depends()
):
    """Delete a todo item"""
    deleted = await todo_repo.delete_todo(todo_id, current_user.id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Todo not found")
    return DeleteResponse(message="Item deleted successfully")