"""
Common dependencies used across the application.
"""
from fastapi import Depends
from sqlalchemy.orm import Session

from backend.auth import get_current_active_user
from backend.db import UserDB, get_db


def get_current_user_dep():
    """Dependency to get current active user."""
    return Depends(get_current_active_user)


def get_db_dep():
    """Dependency to get database session."""
    return Depends(get_db)
