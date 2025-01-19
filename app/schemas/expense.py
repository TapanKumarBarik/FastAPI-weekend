from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class ExpenseBase(BaseModel):
    amount: float
    description: str
    group_id: Optional[int] = None

class ExpenseCreate(ExpenseBase):
    pass

class Expense(ExpenseBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class GroupBase(BaseModel):
    name: str

class GroupCreate(GroupBase):
    member_ids: List[int]

class Group(GroupBase):
    id: int
    created_by: int
    created_at: datetime
    member_count: int
    member_ids: List[int]
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }