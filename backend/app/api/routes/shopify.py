"""
Shopify Integration routes.
Handle Direct Access Token connection untuk Shopify stores.

Updated to use Direct Admin API Access Token instead of OAuth.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from supabase import Client
from uuid import UUID
from typing import Optional
from datetime import datetime, timedelta
import secrets
import os
import requests

from app.core.database import get_db
from app.core.auth import get_current_user_id
from app.core.config import get_settings


router = APIRouter(prefix="/shops", tags=["shopify-integration"])


# ============================================
# SCHEMAS
# ============================================

class OAuthInitResponse(BaseModel):
    """Response untuk OAuth initialization."""
    authorization_url: str
    state: str


class ShopifyConnectionResponse(BaseModel):
    """Response untuk Shopify connection."""
    id: UUID
    platform: str
    shop_id: str
    shop_name: Optional[str]
    shop_status: str
    connected_at: datetime


# ============================================
# SHOPIFY DIRECT ACCESS ENDPOINTS
# ============================================

@router.get("/shopify/status")
async def check_shopify_status():
    """
    Check if Shopify is connected via Direct Access Token.
    
    This replaces the OAuth flow. Backend uses SHOPIFY_ACCESS_TOKEN from .env.
    
    Returns:
        - connected: true if token is configured and valid
        - shop_name: Store name from Shopify
        - store_url: Store URL
    """
    try:
        # Get credentials from environment
        store_url = os.getenv("SHOPIFY_STORE_URL", "").replace("https://", "").replace("http://", "")
        access_token = os.getenv("SHOPIFY_ACCESS_TOKEN", "")
        
        # Check if credentials exist
        if not store_url or not access_token:
            return {
                "connected": False,
                "message": "Shopify credentials not configured in backend .env"
            }
        
        # Verify token by making a lightweight API call to Shopify
        api_url = f"https://{store_url}/admin/api/2024-01/shop.json"
        headers = {
            "X-Shopify-Access-Token": access_token,
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.get(api_url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                shop_data = response.json().get("shop", {})
                return {
                    "connected": True,
                    "shop_name": shop_data.get("name", store_url.split(".")[0]),
                    "store_url": store_url,
                    "shop_domain": shop_data.get("domain", store_url),
                    "email": shop_data.get("email", ""),
                    "message": "Connected to Shopify via Direct Access Token"
                }
            else:
                return {
                    "connected": False,
                    "message": f"Invalid Shopify token (HTTP {response.status_code})"
                }
                
        except requests.exceptions.Timeout:
            return {
                "connected": False,
                "message": "Shopify API timeout - please check store URL"
            }
        except requests.exceptions.RequestException as e:
            return {
                "connected": False,
                "message": f"Failed to connect to Shopify: {str(e)}"
            }
            
    except Exception as e:
        return {
            "connected": False,
            "message": f"Error checking Shopify status: {str(e)}"
        }


# ============================================
# LEGACY OAUTH ENDPOINTS (Deprecated)
# ============================================

@router.get("/connect/shopify", response_model=OAuthInitResponse)
async def init_shopify_oauth(
    user_id: UUID = Depends(get_current_user_id),
    db: Client = Depends(get_db)
):
    """
    Initialize Shopify OAuth flow.
    
    Returns authorization URL untuk redirect user ke Shopify.
    
    SETUP REQUIRED:
    1. Create Shopify Partner account: https://partners.shopify.com
    2. Create app di Partner Dashboard
    3. Get API Key dan API Secret
    4. Set di .env:
       - SHOPIFY_API_KEY=your_api_key
       - SHOPIFY_API_SECRET=your_api_secret
       - SHOPIFY_REDIRECT_URL=http://localhost:8000/api/v1/shops/callback/shopify
    
    Shopify OAuth Documentation:
    https://shopify.dev/docs/apps/auth/oauth
    """
    settings = get_settings()
    
    # Generate state untuk CSRF protection
    state = secrets.token_urlsafe(32)
    
    # Store state di database untuk verification nanti
    db.table("oauth_states").insert({
        "user_id": str(user_id),
        "state_token": state,
        "platform": "shopify",
        "expires_at": (datetime.utcnow() + timedelta(minutes=10)).isoformat()
    }).execute()
    
    # Get Shopify credentials from environment
    shopify_api_key = os.getenv("SHOPIFY_API_KEY")
    shopify_redirect_url = os.getenv(
        "SHOPIFY_REDIRECT_URL", 
        "http://localhost:8000/api/v1/shops/callback/shopify"
    )
    
    # Check if Shopify credentials are configured
    if not shopify_api_key:
        raise HTTPException(
            status_code=500,
            detail="Shopify API credentials not configured. Please add SHOPIFY_API_KEY to .env file."
        )
    
    # Shopify store domain (user akan input ini di frontend)
    # Untuk sekarang, kita gunakan placeholder
    shop_domain = "your-store.myshopify.com"
    
    # Build Shopify OAuth URL
    # Format: https://{shop}.myshopify.com/admin/oauth/authorize
    scopes = "read_products,write_products,read_orders,write_orders"
    
    shopify_auth_url = (
        f"https://{shop_domain}/admin/oauth/authorize"
        f"?client_id={shopify_api_key}"
        f"&scope={scopes}"
        f"&redirect_uri={shopify_redirect_url}"
        f"&state={state}"
    )
    
    return OAuthInitResponse(
        authorization_url=shopify_auth_url,
        state=state
    )


@router.get("/callback/shopify")
async def shopify_oauth_callback(
    code: str = Query(..., description="Authorization code from Shopify"),
    shop: str = Query(..., description="Shop domain from Shopify"),
    state: str = Query(..., description="State for CSRF protection"),
    hmac: str = Query(..., description="HMAC signature for verification"),
    db: Client = Depends(get_db)
):
    """
    Handle Shopify OAuth callback.
    
    Flow:
    1. Verify HMAC signature
    2. Verify state
    3. Exchange code for access_token
    4. Get shop info
    5. Save to shop_integrations table
    
    IMPLEMENTATION STEPS:
    1. Verify HMAC menggunakan SHOPIFY_API_SECRET
    2. Call POST https://{shop}/admin/oauth/access_token
    3. Save access_token ke database
    4. Redirect ke frontend success page
    
    Shopify Access Token Documentation:
    https://shopify.dev/docs/apps/auth/oauth/access-tokens
    """
    try:
        # 1. Verify state
        state_result = db.table("oauth_states").select("*").eq(
            "state_token", state
        ).eq("platform", "shopify").execute()
        
        if not state_result.data:
            raise HTTPException(
                status_code=400,
                detail="Invalid state parameter"
            )
        
        oauth_state = state_result.data[0]
        user_id = oauth_state["user_id"]
        
        # Check if state expired
        expires_at = datetime.fromisoformat(oauth_state["expires_at"])
        if datetime.utcnow() > expires_at:
            raise HTTPException(
                status_code=400,
                detail="State expired. Please try again."
            )
        
        # 2. TODO: Verify HMAC signature
        # import hmac
        # import hashlib
        # shopify_secret = os.getenv("SHOPIFY_API_SECRET")
        # Verify HMAC here...
        
        # 3. Exchange code for access_token
        # TODO: Call Shopify API
        # POST https://{shop}/admin/oauth/access_token
        # Body: {
        #   "client_id": SHOPIFY_API_KEY,
        #   "client_secret": SHOPIFY_API_SECRET,
        #   "code": code
        # }
        
        # MOCK: Generate fake token for now
        access_token = f"shpat_{secrets.token_urlsafe(32)}"
        
        # 4. Get shop info
        # TODO: Call GET https://{shop}/admin/api/2024-01/shop.json
        shop_name = shop.replace(".myshopify.com", "").title()
        
        # 5. Save to database
        shop_data = {
            "user_id": user_id,
            "platform": "shopify",
            "shop_id": shop,
            "shop_name": shop_name,
            "access_token": access_token,
            "shop_status": "active"
        }
        
        # Check if shop already connected
        existing = db.table("shop_integrations").select("*").eq(
            "user_id", user_id
        ).eq("platform", "shopify").eq("shop_id", shop).execute()
        
        if existing.data:
            # Update existing
            db.table("shop_integrations").update(shop_data).eq(
                "id", existing.data[0]["id"]
            ).execute()
        else:
            # Create new
            db.table("shop_integrations").insert(shop_data).execute()
        
        # Delete used state
        db.table("oauth_states").delete().eq("state_token", state).execute()
        
        # Redirect to frontend success page
        return RedirectResponse(
            url=f"http://localhost:3000/dashboard/shops?connected=true&shop={shop}"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Shopify OAuth callback failed: {str(e)}"
        )


@router.delete("/{shop_id}")
async def disconnect_shopify_shop(
    shop_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    db: Client = Depends(get_db)
):
    """
    Disconnect Shopify shop.
    
    TODO: Optionally revoke access token on Shopify side.
    """
    try:
        result = db.table("shop_integrations").delete().eq(
            "id", str(shop_id)
        ).eq("user_id", str(user_id)).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=404,
                detail="Shop not found"
            )
        
        return {"message": "Shop disconnected successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to disconnect shop: {str(e)}"
        )


# ============================================
# HELPER: Get Connected Shops
# ============================================

@router.get("", response_model=list[ShopifyConnectionResponse])
async def get_connected_shops(
    user_id: UUID = Depends(get_current_user_id),
    db: Client = Depends(get_db)
):
    """
    Get all connected Shopify shops for current user.
    """
    try:
        result = db.table("shop_integrations").select("*").eq(
            "user_id", str(user_id)
        ).eq("platform", "shopify").execute()
        
        return result.data
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch shops: {str(e)}"
        )
