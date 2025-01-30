# app/schemas/user.py
from pydantic import BaseModel, EmailStr, constr
from typing import Optional
from datetime import datetime

# Shared properties
class UserBase(BaseModel):
    email: EmailStr
    username: constr(min_length=3, max_length=50)
    is_active: bool = True
    age: Optional[int] = None
    gender: Optional[str] = None
    country: Optional[str] = None

# Properties to receive via API on creation
class UserCreate(UserBase):
    password: constr(min_length=8, max_length=100)

# Properties to receive via API on update
class UserUpdate(UserBase):
    password: Optional[constr(min_length=8, max_length=100)] = None

# Properties shared by models stored in DB
class UserInDBBase(UserBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True

class User(UserInDBBase):
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

# Properties stored in DB
class UserInDB(UserInDBBase):
    hashed_password: str

# Token schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# Login schema
class UserLogin(BaseModel):
    username: str
    password: str

