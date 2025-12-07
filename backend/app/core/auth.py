"""
Authentication utilities - OPEN SOURCE MODE
No user authentication required. Only shop OAuth for marketplace integration.

Demo user ID is used for all operations.
"""
from fastapi import Depends
from supabase import Client
from uuid import UUID

from app.core.database import get_db

# Demo user ID for open source mode
DEMO_USER_ID = UUID("00000000-0000-0000-0000-000000000001")


async def get_current_user_id(db: Client = Depends(get_db)) -> UUID:
    """
    Return demo user ID for open source mode.
    No authentication required.
    
    Returns:
        Demo user UUID
    """
    return DEMO_USER_ID


async def get_optional_user_id(db: Client = Depends(get_db)) -> UUID:
    """
    Return demo user ID for open source mode.
    
    Returns:
        Demo user UUID
    """
    return DEMO_USER_ID
