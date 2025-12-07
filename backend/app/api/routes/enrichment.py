"""
AI Enrichment routes.
Transform simple product → marketplace-ready data.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from supabase import Client
from uuid import UUID
from typing import Dict, Any, Optional

from app.core.database import get_db
from app.core.auth import get_current_user_id
from app.models.database import MarketplacePlatform, ProductListing
from app.repositories.product_repository import ProductRepository
from app.repositories.listing_repository import ListingRepository
from app.services.ai_enrichment_service import AIEnrichmentService


router = APIRouter(prefix="/enrichment", tags=["ai-enrichment"])


# ============================================
# REQUEST/RESPONSE SCHEMAS
# ============================================

class EnrichRequest(BaseModel):
    """Request untuk enrich product."""
    product_id: UUID
    platform: MarketplacePlatform
    shop_integration_id: Optional[UUID] = Field(
        None,
        description="Optional: Shop integration ID jika sudah tahu mau publish ke shop mana"
    )


class EnrichResponse(BaseModel):
    """Response dari enrichment."""
    listing_id: UUID
    product_id: UUID
    platform: MarketplacePlatform
    platform_data: Dict[str, Any]
    status: str
    message: str


class CategoryPredictionRequest(BaseModel):
    """Request untuk predict category saja."""
    product_name: str
    description: Optional[str] = None
    platform: MarketplacePlatform


class CategoryPredictionResponse(BaseModel):
    """Response category prediction."""
    category_id: int
    category_name: str
    confidence: float
    alternatives: list


# ============================================
# ENDPOINTS
# ============================================

@router.post("/enrich", response_model=EnrichResponse)
async def enrich_product(
    request: EnrichRequest,
    user_id: UUID = Depends(get_current_user_id),
    db: Client = Depends(get_db)
):
    """
    Enrich product dengan AI untuk platform tertentu.
    
    Flow:
    1. Get product dari database
    2. Get user settings
    3. Call AI enrichment service
    4. Save enriched data ke product_listings table
    5. Update product status ke 'ready'
    
    Returns:
        Enriched product listing dengan platform-specific data
    """
    try:
        # 1. Get product
        product_repo = ProductRepository(db)
        product = await product_repo.get_by_id(request.product_id, user_id)
        
        if not product:
            raise HTTPException(
                status_code=404,
                detail="Product not found"
            )
        
        # 2. Get user settings
        settings_result = db.table("user_settings").select("*").eq(
            "user_id", str(user_id)
        ).execute()
        
        if not settings_result.data:
            raise HTTPException(
                status_code=404,
                detail="User settings not found. Please configure settings first."
            )
        
        from app.models.database import UserSettings
        user_settings = UserSettings(**settings_result.data[0])
        
        # 3. Call AI enrichment
        ai_service = AIEnrichmentService()
        
        if request.platform == MarketplacePlatform.SHOPEE:
            platform_data = await ai_service.enrich_for_shopee(product, user_settings)
        elif request.platform == MarketplacePlatform.TIKTOK_SHOP:
            platform_data = await ai_service.enrich_for_tiktok(product, user_settings)
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Platform {request.platform} not supported yet"
            )
        
        # 4. Save to product_listings
        listing_repo = ListingRepository(db)
        
        # Check if listing already exists
        if request.shop_integration_id:
            existing = await listing_repo.get_by_product_and_shop(
                request.product_id,
                request.shop_integration_id
            )
            
            if existing:
                # Update existing listing
                listing = await listing_repo.update_platform_data(
                    existing.id,
                    platform_data
                )
            else:
                # Create new listing
                listing = await listing_repo.create(
                    product_id=request.product_id,
                    shop_integration_id=request.shop_integration_id,
                    platform=request.platform,
                    platform_data=platform_data
                )
        else:
            # Create listing without shop (for preview/draft)
            # Use a dummy shop_integration_id or handle differently
            raise HTTPException(
                status_code=400,
                detail="shop_integration_id is required. Please connect a shop first."
            )
        
        # 5. Mark product as AI enriched
        await product_repo.mark_as_enriched(
            request.product_id,
            user_id,
            user_settings.ai_model_preference
        )
        
        # 6. Log AI generation
        log_data = {
            "user_id": str(user_id),
            "product_id": str(request.product_id),
            "ai_model": user_settings.ai_model_preference,
            "target_platform": request.platform.value,
            "input_data": {
                "name": product.name,
                "price": product.price,
                "description": product.description
            },
            "output_data": platform_data,
            "status": "success"
        }
        
        db.table("ai_generation_logs").insert(log_data).execute()
        
        return EnrichResponse(
            listing_id=listing.id,
            product_id=product.id,
            platform=request.platform,
            platform_data=platform_data,
            status="success",
            message=f"Product successfully enriched for {request.platform.value}"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        # Log failed generation
        try:
            log_data = {
                "user_id": str(user_id),
                "product_id": str(request.product_id),
                "ai_model": "unknown",
                "target_platform": request.platform.value,
                "input_data": {},
                "status": "failed",
                "error_message": str(e)
            }
            db.table("ai_generation_logs").insert(log_data).execute()
        except:
            pass
        
        raise HTTPException(
            status_code=500,
            detail=f"Enrichment failed: {str(e)}"
        )


@router.post("/predict-category", response_model=CategoryPredictionResponse)
async def predict_category(
    request: CategoryPredictionRequest,
    user_id: UUID = Depends(get_current_user_id)
):
    """
    Predict category untuk product tanpa full enrichment.
    Useful untuk preview/suggestions saat user input product.
    """
    try:
        ai_service = AIEnrichmentService()
        
        result = await ai_service.predict_category(
            product_name=request.product_name,
            description=request.description,
            platform=request.platform
        )
        
        return CategoryPredictionResponse(**result)
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Category prediction failed: {str(e)}"
        )


@router.get("/listings/{product_id}")
async def get_product_listings(
    product_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    db: Client = Depends(get_db)
):
    """
    Get all enriched listings untuk suatu product.
    Shows platform-specific data for each marketplace.
    """
    try:
        # Verify product ownership
        product_repo = ProductRepository(db)
        product = await product_repo.get_by_id(product_id, user_id)
        
        if not product:
            raise HTTPException(
                status_code=404,
                detail="Product not found"
            )
        
        # Get all listings
        listing_repo = ListingRepository(db)
        listings = await listing_repo.get_by_product(product_id)
        
        return {
            "product_id": product_id,
            "product_name": product.name,
            "total_listings": len(listings),
            "listings": [
                {
                    "id": listing.id,
                    "platform": listing.platform,
                    "status": listing.publish_status,
                    "platform_data": listing.platform_data,
                    "external_product_id": listing.external_product_id,
                    "external_listing_url": listing.external_listing_url,
                    "created_at": listing.created_at
                }
                for listing in listings
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get listings: {str(e)}"
        )
