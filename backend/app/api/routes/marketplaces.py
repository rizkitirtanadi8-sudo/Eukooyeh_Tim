"""
Marketplace routes untuk publish dan management produk di berbagai platform.
Terintegrasi dengan database dan AI enrichment.
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List
from supabase import Client
from uuid import UUID

from app.schemas.product import (
    MarketplacePublishRequest,
    MarketplacePublishResponse,
    MarketplacePlatform
)
from app.models.database import ProductStatus
from app.services.marketplace_service import MarketplaceService
from app.repositories.product_repository import ProductRepository
from app.repositories.listing_repository import ListingRepository
from app.core.database import get_db
from app.core.auth import get_current_user_id

router = APIRouter(prefix="/marketplaces", tags=["marketplaces"])
marketplace_service = MarketplaceService()


# ============================================
# REQUEST SCHEMAS
# ============================================

class PublishToMarketplaceRequest(BaseModel):
    """Request untuk publish enriched product."""
    listing_id: UUID
    shop_integration_id: UUID


@router.post("/publish", response_model=MarketplacePublishResponse)
async def publish_product(
    request: PublishToMarketplaceRequest,
    user_id: UUID = Depends(get_current_user_id),
    db: Client = Depends(get_db)
):
    """
    Publish enriched product ke marketplace.
    
    Flow:
    1. Get listing (enriched data) dari database
    2. Get shop integration (access token)
    3. Call marketplace API
    4. Update listing dengan external_product_id
    5. Update product status ke 'published'
    
    Args:
        request: Listing ID dan shop integration ID
        
    Returns:
        Response dengan status dan URL produk di marketplace
    """
    try:
        # 1. Get listing
        listing_repo = ListingRepository(db)
        listing = await listing_repo.get_by_id(request.listing_id)
        
        if not listing:
            raise HTTPException(status_code=404, detail="Listing not found")
        
        # 2. Verify product ownership
        product_repo = ProductRepository(db)
        product = await product_repo.get_by_id(listing.product_id, user_id)
        
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # 3. Get shop integration
        shop_result = db.table("shop_integrations").select("*").eq(
            "id", str(request.shop_integration_id)
        ).eq("user_id", str(user_id)).execute()
        
        if not shop_result.data:
            raise HTTPException(status_code=404, detail="Shop not found")
        
        shop = shop_result.data[0]
        
        # 4. Mark as publishing
        await listing_repo.mark_as_publishing(request.listing_id)
        
        # 5. Build marketplace request from enriched data
        platform_data = listing.platform_data
        
        marketplace_request = MarketplacePublishRequest(
            product_id=str(listing.product_id),
            platform=listing.platform,
            title=platform_data.get("item_name") or platform_data.get("product_name", product.name),
            description=platform_data.get("description") or platform_data.get("description_html", ""),
            price=int(platform_data.get("price", product.price)),
            stock=platform_data.get("stock") or platform_data.get("stock_quantity", product.stock_quantity),
            images=platform_data.get("images", product.images)
        )
        
        # 6. Call marketplace API (mock for now)
        result = await marketplace_service.publish_to_marketplace(marketplace_request)
        
        # 7. Update listing with external IDs
        if result.success:
            await listing_repo.mark_as_published(
                request.listing_id,
                result.marketplace_product_id,
                result.product_url
            )
            
            # 8. Update product status
            await product_repo.update(
                listing.product_id,
                user_id,
                {"status": ProductStatus.PUBLISHED}
            )
        else:
            await listing_repo.mark_as_failed(
                request.listing_id,
                result.message
            )
        
        return result
        
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to publish product: {str(e)}"
        )


@router.get("/published/{product_id}")
async def get_published_listings(
    product_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    db: Client = Depends(get_db)
):
    """
    Get all published listings untuk suatu product.
    Shows where the product is currently live.
    """
    try:
        # Verify ownership
        product_repo = ProductRepository(db)
        product = await product_repo.get_by_id(product_id, user_id)
        
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Get published listings
        listing_repo = ListingRepository(db)
        listings = await listing_repo.get_by_product(product_id)
        
        published = [
            {
                "platform": listing.platform,
                "external_product_id": listing.external_product_id,
                "external_listing_url": listing.external_listing_url,
                "published_at": listing.published_at,
                "status": listing.publish_status
            }
            for listing in listings
            if listing.publish_status == "published"
        ]
        
        return {
            "product_id": product_id,
            "product_name": product.name,
            "total_published": len(published),
            "listings": published
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/platforms")
async def get_supported_platforms():
    """
    Get list platform marketplace yang didukung.
    
    Returns:
        List of supported platforms dengan metadata
    """
    return {
        "platforms": [
            {
                "id": MarketplacePlatform.SHOPEE,
                "name": "Shopee",
                "description": "Platform e-commerce terbesar di Southeast Asia",
                "supported": True
            },
            {
                "id": MarketplacePlatform.TOKOPEDIA,
                "name": "Tokopedia",
                "description": "Platform e-commerce terbesar di Indonesia",
                "supported": True
            },
            {
                "id": MarketplacePlatform.TIKTOK_SHOP,
                "name": "TikTok Shop",
                "description": "Social commerce platform dari TikTok",
                "supported": True
            }
        ]
    }
