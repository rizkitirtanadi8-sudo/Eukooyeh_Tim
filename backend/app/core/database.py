"""
Supabase database client and connection management.
"""
from supabase import create_client, Client
from functools import lru_cache
from app.core.config import get_settings


@lru_cache()
def get_supabase_client() -> Client:
    """
    Get cached Supabase client instance.
    Uses service role key for backend operations.
    """
    settings = get_settings()
    
    supabase: Client = create_client(
        supabase_url=settings.supabase_url,
        supabase_key=settings.supabase_key
    )
    
    return supabase


def get_db() -> Client:
    """
    Dependency untuk FastAPI routes.
    Usage: db: Client = Depends(get_db)
    """
    return get_supabase_client()
