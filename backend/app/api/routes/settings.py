"""
User settings routes.
Manages warehouse, logistics, dan AI preferences.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from supabase import Client
from uuid import UUID

from app.core.database import get_db
from app.core.auth import get_current_user_id
from app.models.database import UserSettings, UserSettingsUpdate


router = APIRouter(prefix="/settings", tags=["settings"])


@router.get("", response_model=UserSettings)
async def get_user_settings(
    user_id: UUID = Depends(get_current_user_id),
    db: Client = Depends(get_db)
):
    """
    Get user settings.
    Jika belum ada, create default settings.
    """
    try:
        # Try to get existing settings
        result = db.table("user_settings").select("*").eq("user_id", str(user_id)).execute()
        
        if result.data:
            return UserSettings(**result.data[0])
        
        # Create default settings if not exists
        default_settings = {
            "user_id": str(user_id),
            "warehouse_country": "ID",
            "default_stock_quantity": 100,
            "default_condition": "new",
            "default_weight_kg": 0.5,
            "ai_model_preference": "gpt-4",
            "auto_publish": False,
            "default_logistics": []
        }
        
        create_result = db.table("user_settings").insert(default_settings).execute()
        
        if not create_result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create default settings"
            )
        
        return UserSettings(**create_result.data[0])
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get settings: {str(e)}"
        )


@router.patch("", response_model=UserSettings)
async def update_user_settings(
    settings_update: UserSettingsUpdate,
    user_id: UUID = Depends(get_current_user_id),
    db: Client = Depends(get_db)
):
    """
    Update user settings.
    """
    try:
        update_data = settings_update.model_dump(exclude_unset=True)
        
        if not update_data:
            # No fields to update, return current settings
            return await get_user_settings(user_id, db)
        
        # Ensure settings exist first
        existing = db.table("user_settings").select("id").eq("user_id", str(user_id)).execute()
        
        if not existing.data:
            # Create if not exists
            update_data["user_id"] = str(user_id)
            result = db.table("user_settings").insert(update_data).execute()
        else:
            # Update existing
            result = db.table("user_settings").update(update_data).eq(
                "user_id", str(user_id)
            ).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Settings not found"
            )
        
        return UserSettings(**result.data[0])
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update settings: {str(e)}"
        )
