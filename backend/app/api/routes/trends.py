"""
Market Trends API routes.
Provides trending products and market insights updated daily.
"""
from fastapi import APIRouter, Depends, HTTPException
from supabase import Client
from typing import List, Dict, Any
from datetime import datetime, timedelta
from uuid import UUID

from app.core.database import get_db
from app.core.auth import get_current_user_id
from app.services.google_search_service import get_google_search_service


router = APIRouter(prefix="/trends", tags=["market-trends"])


# Default categories untuk market trends
DEFAULT_CATEGORIES = [
    "Fashion Pria",
    "Fashion Wanita", 
    "Elektronik",
    "Handphone",
    "Kecantikan",
    "Makanan & Minuman",
    "Olahraga",
    "Rumah Tangga"
]


@router.get("/market")
async def get_market_trends(
    db: Client = Depends(get_db)
):
    """
    Get market trends updated daily.
    Returns trending products per category.
    Public endpoint - no auth required.
    
    Cache strategy:
    - Check if trends exist in DB and are less than 24 hours old
    - If yes, return cached data
    - If no, fetch new data from Google Search API and cache it
    """
    try:
        # Check if Google Search is enabled
        search_service = get_google_search_service()
        if not search_service.enabled:
            # Return empty trends if Google Search not configured
            return {
                "success": True,
                "trends": {},
                "message": "Google Search API not configured. Add GOOGLE_SEARCH_API_KEY to enable market trends.",
                "last_updated": datetime.now().isoformat(),
                "cache_hit": False
            }
        
        # Check cache in database
        try:
            cache_result = db.table("market_trends_cache").select("*").order(
                "updated_at", desc=True
            ).limit(1).execute()
        except Exception as db_error:
            # Table doesn't exist yet - return empty
            return {
                "success": True,
                "trends": {},
                "message": "Market trends table not created. Run migrations first.",
                "last_updated": datetime.now().isoformat(),
                "cache_hit": False
            }
        
        # Check if cache is valid (less than 24 hours old)
        cache_valid = False
        if cache_result.data:
            cache_entry = cache_result.data[0]
            updated_at = datetime.fromisoformat(cache_entry["updated_at"].replace('Z', '+00:00'))
            cache_age = datetime.now(updated_at.tzinfo) - updated_at
            
            if cache_age < timedelta(hours=24):
                cache_valid = True
                trends_data = cache_entry["trends_data"]
        
        # If cache invalid, fetch new data
        if not cache_valid:
            search_service = get_google_search_service()
            
            # Get trends for each category
            trends_data = await search_service.get_market_trends(
                categories=DEFAULT_CATEGORIES,
                region="Indonesia"
            )
            
            # Save to cache
            cache_entry = {
                "trends_data": trends_data,
                "updated_at": datetime.now().isoformat(),
                "categories": DEFAULT_CATEGORIES
            }
            
            # Upsert to database
            db.table("market_trends_cache").upsert(cache_entry).execute()
        
        return {
            "success": True,
            "trends": trends_data,
            "last_updated": cache_entry.get("updated_at") if cache_valid else datetime.now().isoformat(),
            "cache_hit": cache_valid
        }
    
    except Exception as e:
        # Return empty trends on error
        return {
            "success": False,
            "trends": {},
            "error": str(e),
            "message": "Failed to fetch market trends"
        }


@router.get("/recommendations")
async def get_product_recommendations(
    category: str,
    user_id: UUID = Depends(get_current_user_id),
    db: Client = Depends(get_db)
):
    """
    Get product recommendations based on market trends.
    
    Args:
        category: Product category to get recommendations for
    
    Returns:
        List of recommended products to sell
    """
    try:
        # Get market trends
        trends_response = await get_market_trends(user_id=user_id, db=db)
        
        if not trends_response.get("success"):
            raise HTTPException(status_code=500, detail="Failed to fetch trends")
        
        trends = trends_response.get("trends", {})
        
        # Get recommendations for specific category
        category_trends = trends.get(category, {})
        
        if not category_trends:
            return {
                "category": category,
                "recommendations": [],
                "message": f"No trends found for category: {category}"
            }
        
        trending_products = category_trends.get("trending_products", [])
        
        # Format recommendations
        recommendations = []
        for idx, product in enumerate(trending_products[:10]):
            recommendations.append({
                "rank": idx + 1,
                "product_name": product.get("name", ""),
                "trend_score": product.get("mentions", 0),
                "category": category,
                "recommendation_reason": f"Trending dengan {product.get('mentions', 0)} mentions"
            })
        
        return {
            "category": category,
            "recommendations": recommendations,
            "total": len(recommendations),
            "last_updated": category_trends.get("last_updated")
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get recommendations: {str(e)}"
        )


@router.post("/refresh")
async def refresh_market_trends(
    db: Client = Depends(get_db)
):
    """
    Force refresh market trends data.
    Public endpoint - no auth required.
    """
    try:
        search_service = get_google_search_service()
        
        # Fetch fresh data
        trends_data = await search_service.get_market_trends(
            categories=DEFAULT_CATEGORIES,
            region="Indonesia"
        )
        
        # Save to cache
        cache_entry = {
            "trends_data": trends_data,
            "updated_at": datetime.now().isoformat(),
            "categories": DEFAULT_CATEGORIES
        }
        
        db.table("market_trends_cache").upsert(cache_entry).execute()
        
        return {
            "success": True,
            "message": "Market trends refreshed successfully",
            "trends": trends_data,
            "updated_at": cache_entry["updated_at"]
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to refresh trends: {str(e)}"
        )
