"""
Product repository untuk database operations.
Menggunakan repository pattern untuk clean architecture.
"""
from typing import List, Optional
from uuid import UUID
from supabase import Client

from app.models.database import (
    Product,
    ProductCreate,
    ProductUpdate,
    ProductStatus
)


class ProductRepository:
    """Repository untuk Product CRUD operations."""
    
    def __init__(self, db: Client):
        self.db = db
        self.table = "products"
    
    async def create(self, user_id: UUID, product_data: ProductCreate) -> Product:
        """Create new product."""
        data = product_data.model_dump()
        data["user_id"] = str(user_id)
        
        result = self.db.table(self.table).insert(data).execute()
        
        if not result.data:
            raise ValueError("Failed to create product")
        
        return Product(**result.data[0])
    
    async def get_by_id(self, product_id: UUID, user_id: UUID) -> Optional[Product]:
        """Get product by ID (with user ownership check)."""
        result = self.db.table(self.table).select("*").eq(
            "id", str(product_id)
        ).eq(
            "user_id", str(user_id)
        ).execute()
        
        if not result.data:
            return None
        
        return Product(**result.data[0])
    
    async def get_all_by_user(
        self,
        user_id: UUID,
        status: Optional[ProductStatus] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Product]:
        """Get all products for a user with optional filtering."""
        query = self.db.table(self.table).select("*").eq("user_id", str(user_id))
        
        if status:
            query = query.eq("status", status.value)
        
        result = query.order("created_at", desc=True).range(offset, offset + limit - 1).execute()
        
        return [Product(**item) for item in result.data]
    
    async def update(
        self,
        product_id: UUID,
        user_id: UUID,
        product_data: ProductUpdate
    ) -> Optional[Product]:
        """Update product."""
        # Only update fields that are provided
        update_data = product_data.model_dump(exclude_unset=True)
        
        if not update_data:
            # No fields to update
            return await self.get_by_id(product_id, user_id)
        
        result = self.db.table(self.table).update(update_data).eq(
            "id", str(product_id)
        ).eq(
            "user_id", str(user_id)
        ).execute()
        
        if not result.data:
            return None
        
        return Product(**result.data[0])
    
    async def soft_delete(self, product_id: UUID, user_id: UUID) -> bool:
        """Soft delete product (set status to archived)."""
        result = self.db.table(self.table).update({
            "status": ProductStatus.ARCHIVED.value
        }).eq(
            "id", str(product_id)
        ).eq(
            "user_id", str(user_id)
        ).execute()
        
        return bool(result.data)
    
    async def hard_delete(self, product_id: UUID, user_id: UUID) -> bool:
        """Permanently delete product from database."""
        result = self.db.table(self.table).delete().eq(
            "id", str(product_id)
        ).eq(
            "user_id", str(user_id)
        ).execute()
        
        return bool(result.data)
    
    async def mark_as_enriched(
        self,
        product_id: UUID,
        user_id: UUID,
        ai_model: str
    ) -> Optional[Product]:
        """Mark product as AI enriched."""
        from datetime import datetime
        
        result = self.db.table(self.table).update({
            "ai_enriched": True,
            "ai_enriched_at": datetime.utcnow().isoformat(),
            "ai_model_used": ai_model,
            "status": ProductStatus.READY.value
        }).eq(
            "id", str(product_id)
        ).eq(
            "user_id", str(user_id)
        ).execute()
        
        if not result.data:
            return None
        
        return Product(**result.data[0])
    
    async def count_by_user(self, user_id: UUID, status: Optional[ProductStatus] = None) -> int:
        """Count products for a user."""
        query = self.db.table(self.table).select("id", count="exact").eq("user_id", str(user_id))
        
        if status:
            query = query.eq("status", status.value)
        
        result = query.execute()
        
        return result.count or 0
