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

    async def create(self, user: UserCreate) -> dict:
        hashed_password = get_password_hash(user.password)
        query = """
        INSERT INTO users (email, username, hashed_password)
        VALUES (:email, :username, :hashed_password)
        RETURNING id, email, username, created_at
        """
        values = {
            "email": user.email,
            "username": user.username,
            "hashed_password": hashed_password
        }
        return await database.fetch_one(query=query, values=values)

