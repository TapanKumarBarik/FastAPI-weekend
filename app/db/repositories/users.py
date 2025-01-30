# app/db/repositories/users.py
from typing import Optional
from ...models.user import User
from ...schemas.user import UserCreate
from ...core.security import get_password_hash
from ..database import database

class UserRepository:
    async def get_by_email(self, email: str) -> Optional[dict]:
        query = """
        SELECT id, email, username, hashed_password, created_at 
        FROM users WHERE email = :email
        """
        return await database.fetch_one(query=query, values={"email": email})

    async def get_by_username(self, username: str) -> Optional[dict]:
        query = """
        SELECT id, email, username, hashed_password, created_at 
        FROM users WHERE username = :username
        """
        return await database.fetch_one(query=query, values={"username": username})

    async def update_active_status(self, user_id: int, is_active: bool) -> dict:
        query = """
        UPDATE users 
        SET is_active = :is_active
        WHERE id = :user_id
        RETURNING id, email, username, is_active, age, gender, country, created_at
        """
        values = {"user_id": user_id, "is_active": is_active}
        return await database.fetch_one(query=query, values=values)
    
    async def create(self, user: UserCreate) -> dict:
        hashed_password = get_password_hash(user.password)
        query = """
        INSERT INTO users (email, username, hashed_password, is_active)
        VALUES (:email, :username, :hashed_password, :is_active)
        RETURNING id, email, username, is_active, created_at
        """
        values = {
            "email": user.email,
            "username": user.username,
            "hashed_password": hashed_password,
            "is_active": True
        }
        return await database.fetch_one(query=query, values=values)