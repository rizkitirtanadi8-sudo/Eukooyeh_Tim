"""
Trend Analysis API Endpoints
AI-powered market trend prediction using CrewAI.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.services.trend_agent_service import get_trend_analyzer


router = APIRouter(prefix="/analyze", tags=["trend-analysis"])


class TrendAnalysisRequest(BaseModel):
    """Request model for trend analysis."""
    category: str
    region: Optional[str] = "Indonesia"


@router.post("/trends")
async def analyze_market_trends(request: TrendAnalysisRequest):
    """
    Analyze market trends for a specific category.
    
    Uses AI agent to predict viral micro-trends based on:
    - Current season and weather
    - TikTok and social media trends
    - Cultural events and holidays
    - Consumer behavior patterns
    
    Example request:
    ```json
    {
        "category": "Fashion",
        "region": "Indonesia"
    }
    ```
    
    Returns:
    - 3 specific product trend predictions
    - Viral reasons and growth potential
    - Price ranges and target audience
    """
    try:
        analyzer = get_trend_analyzer()
        
        # Analyze trends
        result = await analyzer.analyze_trends(
            category=request.category,
            region=request.region
        )
        
        return {
            "success": True,
            "data": result,
            "message": f"Successfully analyzed trends for {request.category}"
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to analyze trends: {str(e)}"
        )


@router.get("/categories")
async def get_trend_categories():
    """
    Get list of available categories for trend analysis.
    """
    return {
        "categories": [
            {
                "id": "fashion",
                "name": "Fashion & Apparel",
                "description": "Clothing, accessories, footwear"
            },
            {
                "id": "electronics",
                "name": "Electronics",
                "description": "Gadgets, phones, computers"
            },
            {
                "id": "beauty",
                "name": "Beauty & Cosmetics",
                "description": "Skincare, makeup, personal care"
            },
            {
                "id": "food",
                "name": "Food & Beverages",
                "description": "Snacks, drinks, ingredients"
            },
            {
                "id": "home",
                "name": "Home & Living",
                "description": "Furniture, decor, appliances"
            },
            {
                "id": "sports",
                "name": "Sports & Outdoor",
                "description": "Fitness, camping, sports gear"
            },
            {
                "id": "toys",
                "name": "Toys & Hobbies",
                "description": "Kids toys, collectibles, games"
            },
            {
                "id": "health",
                "name": "Health & Wellness",
                "description": "Supplements, fitness, medical"
            }
        ]
    }
