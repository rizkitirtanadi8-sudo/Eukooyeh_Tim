"""
Mock Marketplace API Endpoints
Simulates real marketplace APIs (Shopee, TikTok) without actual connections.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
import time
import random
from datetime import datetime

router = APIRouter(prefix="/mock-marketplaces", tags=["mock-marketplaces"])


class ProductData(BaseModel):
    """Product data for marketplace publishing."""
    name: str
    description: str
    price: float
    category: str
    images: list[str] = []
    specifications: Optional[Dict[str, Any]] = None
    stock: int = 100


class PublishResponse(BaseModel):
    """Standard response for marketplace publishing."""
    status: str
    platform: str
    platform_status: str
    product_id: str
    published_at: str
    message: str


@router.post("/publish/shopee", response_model=PublishResponse)
async def publish_to_shopee(product_data: ProductData):
    """
    Simulate publishing product to Shopee.
    
    Simulates:
    - Network latency (1.5-2.0 seconds)
    - Product ID generation
    - Platform review process
    """
    try:
        # Simulate network latency
        latency = random.uniform(1.5, 2.0)
        time.sleep(latency)
        
        # Generate fake product ID
        product_id = f"SHOPEE-{random.randint(100000, 999999)}"
        
        # Simulate response
        return PublishResponse(
            status="success",
            platform="shopee",
            platform_status="under_review",
            product_id=product_id,
            published_at=datetime.now().isoformat(),
            message=f"Product '{product_data.name}' successfully submitted to Shopee. Currently under review."
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to publish to Shopee: {str(e)}"
        )


@router.post("/publish/tiktok", response_model=PublishResponse)
async def publish_to_tiktok(product_data: ProductData):
    """
    Simulate publishing product to TikTok Shop.
    
    Simulates:
    - Network latency (1.5-2.0 seconds)
    - Product ID generation
    - Platform review process
    """
    try:
        # Simulate network latency
        latency = random.uniform(1.5, 2.0)
        time.sleep(latency)
        
        # Generate fake product ID
        product_id = f"TTS-{random.randint(100000, 999999)}"
        
        # Simulate response
        return PublishResponse(
            status="success",
            platform="tiktok",
            platform_status="under_review",
            product_id=product_id,
            published_at=datetime.now().isoformat(),
            message=f"Product '{product_data.name}' successfully submitted to TikTok Shop. Currently under review."
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to publish to TikTok Shop: {str(e)}"
        )


@router.post("/publish/tokopedia", response_model=PublishResponse)
async def publish_to_tokopedia(product_data: ProductData):
    """
    Simulate publishing product to Tokopedia.
    
    Simulates:
    - Network latency (1.5-2.0 seconds)
    - Product ID generation
    - Platform review process
    """
    try:
        # Simulate network latency
        latency = random.uniform(1.5, 2.0)
        time.sleep(latency)
        
        # Generate fake product ID
        product_id = f"TOPED-{random.randint(100000, 999999)}"
        
        # Simulate response
        return PublishResponse(
            status="success",
            platform="tokopedia",
            platform_status="under_review",
            product_id=product_id,
            published_at=datetime.now().isoformat(),
            message=f"Product '{product_data.name}' successfully submitted to Tokopedia. Currently under review."
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to publish to Tokopedia: {str(e)}"
        )


@router.get("/platforms")
async def get_available_platforms():
    """
    Get list of available marketplace platforms.
    """
    return {
        "platforms": [
            {
                "id": "shopee",
                "name": "Shopee",
                "status": "available",
                "description": "Leading e-commerce platform in Southeast Asia",
                "features": ["Auto-pricing", "Bulk upload", "Analytics"]
            },
            {
                "id": "tiktok",
                "name": "TikTok Shop",
                "status": "available",
                "description": "Social commerce platform integrated with TikTok",
                "features": ["Live selling", "Short video", "Influencer marketing"]
            },
            {
                "id": "tokopedia",
                "name": "Tokopedia",
                "status": "available",
                "description": "Indonesia's largest marketplace",
                "features": ["Free shipping", "Cashback", "Official store"]
            }
        ]
    }
