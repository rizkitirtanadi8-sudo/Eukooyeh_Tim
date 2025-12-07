"""
Product Listing repository untuk manage marketplace-specific listings.
"""
from typing import List, Optional
from uuid import UUID
from supabase import Client
from datetime import datetime

from app.models.database import (
    ProductListing,
    MarketplacePlatform,
    PublishStatus
)


class ListingRepository:
    """Repository untuk ProductListing operations."""
    
    def __init__(self, db: Client):
        self.db = db
        self.table = "product_listings"
    
    async def create(
        self,
        product_id: UUID,
        shop_integration_id: UUID,
        platform: MarketplacePlatform,
        platform_data: dict
    ) -> ProductListing:
        """Create new product listing."""
        data = {
            "product_id": str(product_id),
            "shop_integration_id": str(shop_integration_id),
            "platform": platform.value,
            "platform_data": platform_data,
            "publish_status": PublishStatus.PENDING.value
        }
        
        result = self.db.table(self.table).insert(data).execute()
        
        if not result.data:
            raise ValueError("Failed to create listing")
        
        return ProductListing(**result.data[0])
    
    async def get_by_id(self, listing_id: UUID) -> Optional[ProductListing]:
        """Get listing by ID."""
        result = self.db.table(self.table).select("*").eq(
            "id", str(listing_id)
        ).execute()
        
        if not result.data:
            return None
        
        return ProductListing(**result.data[0])
    
    async def get_by_product_and_shop(
        self,
        product_id: UUID,
        shop_integration_id: UUID
    ) -> Optional[ProductListing]:
        """Get listing by product and shop (unique constraint)."""
        result = self.db.table(self.table).select("*").eq(
            "product_id", str(product_id)
        ).eq(
            "shop_integration_id", str(shop_integration_id)
        ).execute()
        
        if not result.data:
            return None
        
        return ProductListing(**result.data[0])
    
    async def get_by_product(self, product_id: UUID) -> List[ProductListing]:
        """Get all listings for a product."""
        result = self.db.table(self.table).select("*").eq(
            "product_id", str(product_id)
        ).execute()
        
        return [ProductListing(**item) for item in result.data]
    
    async def update_platform_data(
        self,
        listing_id: UUID,
        platform_data: dict
    ) -> Optional[ProductListing]:
        """Update platform-specific data."""
        result = self.db.table(self.table).update({
            "platform_data": platform_data
        }).eq("id", str(listing_id)).execute()
        
        if not result.data:
            return None
        
        return ProductListing(**result.data[0])
    
    async def mark_as_publishing(self, listing_id: UUID) -> Optional[ProductListing]:
        """Mark listing as currently publishing."""
        result = self.db.table(self.table).update({
            "publish_status": PublishStatus.PUBLISHING.value
        }).eq("id", str(listing_id)).execute()
        
        if not result.data:
            return None
        
        return ProductListing(**result.data[0])
    
    async def mark_as_published(
        self,
        listing_id: UUID,
        external_product_id: str,
        external_listing_url: str
    ) -> Optional[ProductListing]:
        """Mark listing as successfully published."""
        result = self.db.table(self.table).update({
            "publish_status": PublishStatus.PUBLISHED.value,
            "external_product_id": external_product_id,
            "external_listing_url": external_listing_url,
            "published_at": datetime.utcnow().isoformat(),
            "last_synced_at": datetime.utcnow().isoformat()
        }).eq("id", str(listing_id)).execute()
        
        if not result.data:
            return None
        
        return ProductListing(**result.data[0])
    
    async def mark_as_failed(
        self,
        listing_id: UUID,
        error_message: str
    ) -> Optional[ProductListing]:
        """Mark listing as failed to publish."""
        result = self.db.table(self.table).update({
            "publish_status": PublishStatus.FAILED.value,
            "publish_error": error_message
        }).eq("id", str(listing_id)).execute()
        
        if not result.data:
            return None
        
        return ProductListing(**result.data[0])
    
    async def delete(self, listing_id: UUID) -> bool:
        """Delete listing."""
        result = self.db.table(self.table).delete().eq(
            "id", str(listing_id)
        ).execute()
        
        return bool(result.data)
