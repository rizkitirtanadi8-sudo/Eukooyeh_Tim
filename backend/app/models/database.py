"""
Database models yang match dengan Supabase schema.
Menggunakan Pydantic untuk type safety dan validation.
"""
from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from enum import Enum
from uuid import UUID


# ============================================
# ENUMS
# ============================================

class MarketplacePlatform(str, Enum):
    """Platform marketplace yang didukung."""
    SHOPEE = "shopee"
    TIKTOK_SHOP = "tiktok_shop"


class ShopStatus(str, Enum):
    """Status koneksi shop."""
    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"


class ProductStatus(str, Enum):
    """Status produk."""
    DRAFT = "draft"
    READY = "ready"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class PublishStatus(str, Enum):
    """Status publishing ke marketplace."""
    PENDING = "pending"
    PUBLISHING = "publishing"
    PUBLISHED = "published"
    FAILED = "failed"
    UPDATED = "updated"


class ProductCondition(str, Enum):
    """Kondisi produk."""
    NEW = "new"
    USED = "used"


# ============================================
# DATABASE MODELS
# ============================================

class Profile(BaseModel):
    """User profile model."""
    id: UUID
    email: str
    full_name: Optional[str] = None
    company_name: Optional[str] = None
    phone: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ShopIntegration(BaseModel):
    """Shop integration model untuk OAuth tokens."""
    id: UUID
    user_id: UUID
    platform: MarketplacePlatform
    shop_id: str
    shop_name: Optional[str] = None
    access_token: str
    refresh_token: Optional[str] = None
    token_expires_at: Optional[datetime] = None
    shop_region: Optional[str] = None
    shop_status: ShopStatus = ShopStatus.ACTIVE
    connected_at: datetime
    last_synced_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class UserSettings(BaseModel):
    """User settings model."""
    id: UUID
    user_id: UUID
    
    # Warehouse info
    warehouse_name: Optional[str] = None
    warehouse_address: Optional[str] = None
    warehouse_city: Optional[str] = None
    warehouse_province: Optional[str] = None
    warehouse_postal_code: Optional[str] = None
    warehouse_country: str = "ID"
    
    # Default logistics (JSON)
    default_logistics: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Default product settings
    default_stock_quantity: int = 100
    default_condition: ProductCondition = ProductCondition.NEW
    default_weight_kg: float = 0.5
    
    # AI preferences
    ai_model_preference: str = "gpt-4"
    auto_publish: bool = False
    
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class Product(BaseModel):
    """Universal product model - simple user input."""
    id: UUID
    user_id: UUID
    
    # Core product data
    name: str
    description: Optional[str] = None
    price: float = Field(ge=0)
    stock_quantity: int = Field(default=0, ge=0)
    
    # Images
    images: List[str] = Field(default_factory=list)
    
    # Metadata
    sku: Optional[str] = None
    weight_kg: Optional[float] = None
    condition: ProductCondition = ProductCondition.NEW
    
    # AI enrichment status
    ai_enriched: bool = False
    ai_enriched_at: Optional[datetime] = None
    ai_model_used: Optional[str] = None
    
    # Status
    status: ProductStatus = ProductStatus.DRAFT
    
    created_at: datetime
    updated_at: datetime
    
    @field_validator('user_id', mode='before')
    @classmethod
    def validate_user_id(cls, v):
        """Accept both UUID and string, convert to UUID."""
        if isinstance(v, str):
            return UUID(v)
        return v
    
    class Config:
        from_attributes = True


class ProductListing(BaseModel):
    """Platform-specific AI-enriched product listing."""
    id: UUID
    product_id: UUID
    shop_integration_id: UUID
    platform: MarketplacePlatform
    
    # External IDs (after publish)
    external_product_id: Optional[str] = None
    external_listing_url: Optional[str] = None
    
    # AI-generated platform-specific data (JSONB)
    platform_data: Dict[str, Any]
    
    # Publishing status
    publish_status: PublishStatus = PublishStatus.PENDING
    publish_error: Optional[str] = None
    
    # Timestamps
    published_at: Optional[datetime] = None
    last_synced_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class AIGenerationLog(BaseModel):
    """AI generation audit log."""
    id: UUID
    user_id: UUID
    product_id: Optional[UUID] = None
    
    # AI details
    ai_model: str
    target_platform: str
    
    # Input/Output
    input_data: Dict[str, Any]
    output_data: Optional[Dict[str, Any]] = None
    
    # Metrics
    tokens_used: Optional[int] = None
    processing_time_ms: Optional[int] = None
    cost_usd: Optional[float] = None
    
    # Status
    status: str  # 'processing', 'success', 'failed'
    error_message: Optional[str] = None
    
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============================================
# CREATE/UPDATE SCHEMAS (for API requests)
# ============================================

class ProfileCreate(BaseModel):
    """Schema for creating user profile."""
    email: str
    full_name: Optional[str] = None
    company_name: Optional[str] = None
    phone: Optional[str] = None


class ProfileUpdate(BaseModel):
    """Schema for updating user profile."""
    full_name: Optional[str] = None
    company_name: Optional[str] = None
    phone: Optional[str] = None


class ShopIntegrationCreate(BaseModel):
    """Schema for creating shop integration."""
    platform: MarketplacePlatform
    shop_id: str
    shop_name: Optional[str] = None
    access_token: str
    refresh_token: Optional[str] = None
    token_expires_at: Optional[datetime] = None
    shop_region: Optional[str] = None


class ProductCreate(BaseModel):
    """Schema for creating product (simple user input)."""
    name: str = Field(..., min_length=3, max_length=200)
    description: Optional[str] = None
    price: float = Field(..., gt=0)
    stock_quantity: int = Field(default=100, ge=0)
    images: List[str] = Field(default_factory=list)
    sku: Optional[str] = None
    weight_kg: Optional[float] = Field(default=0.5, gt=0)
    condition: ProductCondition = ProductCondition.NEW


class ProductUpdate(BaseModel):
    """Schema for updating product."""
    name: Optional[str] = Field(None, min_length=3, max_length=200)
    description: Optional[str] = None
    price: Optional[float] = Field(None, gt=0)
    stock_quantity: Optional[int] = Field(None, ge=0)
    images: Optional[List[str]] = None
    sku: Optional[str] = None
    weight_kg: Optional[float] = Field(None, gt=0)
    condition: Optional[ProductCondition] = None
    status: Optional[ProductStatus] = None


class UserSettingsUpdate(BaseModel):
    """Schema for updating user settings."""
    warehouse_name: Optional[str] = None
    warehouse_address: Optional[str] = None
    warehouse_city: Optional[str] = None
    warehouse_province: Optional[str] = None
    warehouse_postal_code: Optional[str] = None
    warehouse_country: Optional[str] = None
    default_logistics: Optional[List[Dict[str, Any]]] = None
    default_stock_quantity: Optional[int] = None
    default_condition: Optional[ProductCondition] = None
    default_weight_kg: Optional[float] = None
    ai_model_preference: Optional[str] = None
    auto_publish: Optional[bool] = None
