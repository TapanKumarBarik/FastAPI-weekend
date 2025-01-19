# app/core/exceptions.py
from fastapi import HTTPException, status
from typing import Any, Optional, Dict

class AuthException(HTTPException):
    def __init__(
        self,
        status_code: int,
        detail: Any = None,
        headers: Optional[Dict[str, str]] = None
    ) -> None:
        super().__init__(status_code=status_code, detail=detail, headers=headers)

credentials_exception = AuthException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)

inactive_user_exception = AuthException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Inactive user",
)

email_exists_exception = AuthException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Email already registered",
)

username_exists_exception = AuthException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Username already taken",
)

invalid_credentials_exception = AuthException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Incorrect username or password",
    headers={"WWW-Authenticate": "Bearer"},
)

permission_denied_exception = AuthException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="Not enough permissions",
)

not_found_exception = AuthException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Resource not found",
)