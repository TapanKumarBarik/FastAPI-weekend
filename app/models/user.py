# app/models/user.py
from sqlalchemy import Column, Integer, String, DateTime, Index,Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    age = Column(Integer, nullable=True)
    gender = Column(String(10), nullable=True)
    country = Column(String(100), nullable=True)

    __table_args__ = (
        Index('idx_email_username', email, username),
    )


from typing import List
from pydantic import BaseModel

class UserBasic(BaseModel):
    id: int
    username: str
