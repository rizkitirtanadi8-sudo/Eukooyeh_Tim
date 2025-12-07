"""
Pydantic schemas untuk Product domain.
Digunakan untuk request/response validation.
"""
from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class ProductCategory(str, Enum):
    """Kategori produk yang didukung."""
    ELECTRONICS = "electronics"
    FASHION = "fashion"
    FOOD_BEVERAGE = "food_beverage"
    BEAUTY = "beauty"
    HOME_LIVING = "home_living"
    SPORTS = "sports"
    AUTOMOTIVE = "automotive"
    BOOKS = "books"
    TOYS = "toys"
    OTHER = "other"


class MarketplacePlatform(str, Enum):
    """Platform marketplace yang didukung."""
    SHOPEE = "shopee"
    TOKOPEDIA = "tokopedia"
    TIKTOK_SHOP = "tiktok_shop"


class ProductAnalysisRequest(BaseModel):
    """Request schema untuk analisis produk dari gambar."""
    user_description: Optional[str] = Field(
        None,
        description="Deskripsi/spesifikasi dari user yang akan di-enhance oleh AI"
    )
    user_specifications: Optional[dict] = Field(
        None,
        description="Spesifikasi teknis produk (key-value pairs)",
        example={"brand": "Samsung", "model": "Galaxy S23", "storage": "256GB"}
    )
    target_platforms: list[MarketplacePlatform] = Field(
        default=[MarketplacePlatform.SHOPEE],
        description="Platform marketplace tujuan"
    )


class PriceSuggestion(BaseModel):
    """Saran harga berdasarkan analisis market."""
    min_price: int = Field(..., description="Harga minimum yang disarankan")
    max_price: int = Field(..., description="Harga maksimum yang disarankan")
    recommended_price: int = Field(..., description="Harga yang paling disarankan")
    confidence: float = Field(..., ge=0, le=1, description="Confidence score (0-1)")
    reasoning: str = Field(..., description="Alasan dari saran harga")


class ProductAnalysisResponse(BaseModel):
    """Response schema untuk hasil analisis produk."""
    category: ProductCategory = Field(..., description="Kategori produk yang terdeteksi")
    title: str = Field(..., description="Judul produk yang di-generate")
    description: str = Field(..., description="Deskripsi lengkap dengan copywriting")
    original_user_input: Optional[str] = Field(
        None,
        description="Input asli dari user (preserved)"
    )
    price_suggestion: PriceSuggestion = Field(..., description="Saran harga")
    hashtags: list[str] = Field(..., description="Hashtag yang relevan")
    key_features: list[str] = Field(..., description="Fitur-fitur utama produk")
    confidence_score: float = Field(
        ...,
        ge=0,
        le=1,
        description="Overall confidence dari analisis AI"
    )


class MarketplacePublishRequest(BaseModel):
    """Request untuk publish produk ke marketplace."""
    product_id: str = Field(..., description="ID produk dari database")
    platform: MarketplacePlatform = Field(..., description="Platform tujuan")
    title: str = Field(..., min_length=5, max_length=200)
    description: str = Field(..., min_length=20)
    price: int = Field(..., gt=0, description="Harga dalam rupiah")
    stock: int = Field(default=1, ge=0, description="Jumlah stok")
    images: list[str] = Field(..., min_items=1, description="URLs gambar produk")


class MarketplacePublishResponse(BaseModel):
    """Response dari publish ke marketplace."""
    success: bool
    platform: MarketplacePlatform
    product_url: Optional[str] = Field(None, description="URL produk di marketplace")
    marketplace_product_id: Optional[str] = Field(
        None,
        description="ID produk di marketplace"
    )
    message: str
