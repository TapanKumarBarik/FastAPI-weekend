from pydantic import BaseModel, Field, validator
from datetime import datetime
from enum import Enum
from typing import Optional
from datetime import datetime, timezone

class TodoStatus(str, Enum):
    NEW = "new"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"

class TodoBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=500)
    due_date: Optional[datetime] = None
    status: TodoStatus = TodoStatus.NEW

    @validator('due_date')
    def ensure_timezone(cls, v):
        if v: 
            if v.tzinfo is None:
                # Convert naive datetime to UTC
                return v.replace(tzinfo=timezone.utc)
            return v
        return v
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class TodoCreate(TodoBase):
    pass

class Todo(TodoBase):
    id: int
    user_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }