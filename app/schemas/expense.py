from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import List, Optional

class ExpenseBase(BaseModel):
    amount: float = Field(..., gt=0)
    description: str = Field(..., min_length=1, max_length=200)
    group_id: Optional[int] = None
    
    @validator('amount')
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError('Amount must be greater than zero')
        return round(v, 2)  # Round to 2 decimal places

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
    name: str = Field(..., min_length=1, max_length=100)
    member_ids: List[int] = Field(..., min_items=1)
    
    @validator('member_ids')
    def validate_members(cls, v):
        if len(set(v)) != len(v):
            raise ValueError('Duplicate member IDs are not allowed')
        return v

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