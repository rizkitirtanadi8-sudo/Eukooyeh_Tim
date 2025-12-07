"""
Marketplace Endpoints - Direct Publishing to Shopify
Public endpoints for publishing products to marketplaces (no authentication required for demo).
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
from datetime import datetime

from app.services.shopify_service import ShopifyService

router = APIRouter(prefix="/publish", tags=["marketplaces"])


# ============================================
# REQUEST/RESPONSE SCHEMAS
# ============================================

class ShopifyPublishRequest(BaseModel):
    """Request schema for publishing to Shopify."""
    name: str
    description: str
    price: float
    stock: Optional[int] = 100
    images: Optional[List[str]] = []
    sku: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Premium Wireless Headphones",
                "description": "<p>High-quality wireless headphones with noise cancellation</p>",
                "price": 299.99,
                "stock": 50,
                "images": [
                    "https://example.com/image1.jpg",
                    "https://example.com/image2.jpg"
                ],
                "sku": "WH-001"
            }
        }


class ShopifyPublishResponse(BaseModel):
    """Response schema for Shopify publishing."""
    success: bool
    product_id: Optional[str] = None
    variant_id: Optional[str] = None
    product_url: Optional[str] = None
    message: str
    published_at: Optional[str] = None
    platform: str = "shopify"


# ============================================
# ENDPOINTS
# ============================================

@router.post("/shopify", response_model=ShopifyPublishResponse)
async def publish_to_shopify(request: ShopifyPublishRequest):
    """
    Publish a product directly to Shopify using Admin API.
    
    This endpoint is PUBLIC (no authentication required) for demo purposes.
    
    Flow:
    1. Receive product data
    2. Initialize Shopify service with credentials from .env
    3. Call Shopify Admin API to create product
    4. Return success result with Shopify Product ID
    
    Args:
        request: Product data (name, description, price, etc.)
        
    Returns:
        Response with success status, product ID, and admin URL
        
    Raises:
        HTTPException: If publishing fails
    """
    try:
        # Initialize Shopify service
        shopify_service = ShopifyService()
        
        # Prepare product data
        product_data = {
            "name": request.name,
            "description": request.description,
            "price": request.price,
            "stock": request.stock,
            "images": request.images,
            "sku": request.sku
        }
        
        # Publish to Shopify
        result = shopify_service.publish_product_to_shopify(product_data)
        
        # Return response
        if result["success"]:
            return ShopifyPublishResponse(
                success=True,
                product_id=result.get("product_id"),
                variant_id=result.get("variant_id"),
                product_url=result.get("product_url"),
                message=result.get("message"),
                published_at=result.get("published_at")
            )
        else:
            # Return error but don't raise exception
            return ShopifyPublishResponse(
                success=False,
                message=result.get("message", "Failed to publish to Shopify")
            )
            
    except ValueError as e:
        # Configuration error (missing credentials)
        raise HTTPException(
            status_code=500,
            detail=f"Configuration error: {str(e)}"
        )
    except Exception as e:
        # Unexpected error
        raise HTTPException(
            status_code=500,
            detail=f"Failed to publish to Shopify: {str(e)}"
        )


@router.get("/shopify/product/{product_id}")
async def get_shopify_product(product_id: str):
    """
    Get a product from Shopify by ID.
    
    Args:
        product_id: Shopify product ID
        
    Returns:
        Product data from Shopify
    """
    try:
        shopify_service = ShopifyService()
        product = shopify_service.get_product(product_id)
        
        if product:
            return {
                "success": True,
                "product": product
            }
        else:
            raise HTTPException(
                status_code=404,
                detail="Product not found in Shopify"
            )
            
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get product: {str(e)}"
        )


@router.get("/shopify/status")
async def check_shopify_connection():
    """
    Check if Shopify credentials are configured correctly.
    
    Returns:
        Connection status
    """
    try:
        shopify_service = ShopifyService()
        
        return {
            "success": True,
            "message": "Shopify credentials are configured",
            "store_url": shopify_service.store_url,
            "api_version": shopify_service.api_version
        }
        
    except ValueError as e:
        return {
            "success": False,
            "message": str(e)
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Error: {str(e)}"
        }
