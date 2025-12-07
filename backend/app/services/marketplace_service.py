"""
Marketplace service dengan mock implementation.
Menggunakan abstract base class untuk mudah diganti dengan real API.
"""
import asyncio
from abc import ABC, abstractmethod
from typing import Optional
from uuid import uuid4
from app.schemas.product import (
    MarketplacePlatform,
    MarketplacePublishRequest,
    MarketplacePublishResponse
)
from app.core.config import get_settings


class MarketplaceAPI(ABC):
    """Abstract base class untuk marketplace API integration."""
    
    @abstractmethod
    async def publish_product(
        self,
        request: MarketplacePublishRequest
    ) -> MarketplacePublishResponse:
        """Publish produk ke marketplace."""
        pass
    
    @abstractmethod
    async def update_product(
        self,
        marketplace_product_id: str,
        request: MarketplacePublishRequest
    ) -> MarketplacePublishResponse:
        """Update produk yang sudah ada."""
        pass
    
    @abstractmethod
    async def delete_product(self, marketplace_product_id: str) -> bool:
        """Delete produk dari marketplace."""
        pass


class ShopeeAPI(MarketplaceAPI):
    """Mock implementation untuk Shopee API."""
    
    async def publish_product(
        self,
        request: MarketplacePublishRequest
    ) -> MarketplacePublishResponse:
        """Mock publish ke Shopee."""
        settings = get_settings()
        
        # Simulate API call delay
        await asyncio.sleep(settings.marketplace_mock_delay)
        
        # Mock success response
        mock_product_id = f"SHOPEE_{uuid4().hex[:8]}"
        
        return MarketplacePublishResponse(
            success=True,
            platform=MarketplacePlatform.SHOPEE,
            product_url=f"https://shopee.co.id/product/{mock_product_id}",
            marketplace_product_id=mock_product_id,
            message="Produk berhasil dipublish ke Shopee!"
        )
    
    async def update_product(
        self,
        marketplace_product_id: str,
        request: MarketplacePublishRequest
    ) -> MarketplacePublishResponse:
        """Mock update product di Shopee."""
        settings = get_settings()
        await asyncio.sleep(settings.marketplace_mock_delay)
        
        return MarketplacePublishResponse(
            success=True,
            platform=MarketplacePlatform.SHOPEE,
            product_url=f"https://shopee.co.id/product/{marketplace_product_id}",
            marketplace_product_id=marketplace_product_id,
            message="Produk berhasil diupdate di Shopee!"
        )
    
    async def delete_product(self, marketplace_product_id: str) -> bool:
        """Mock delete product dari Shopee."""
        settings = get_settings()
        await asyncio.sleep(settings.marketplace_mock_delay)
        return True


class TokopediaAPI(MarketplaceAPI):
    """Mock implementation untuk Tokopedia API."""
    
    async def publish_product(
        self,
        request: MarketplacePublishRequest
    ) -> MarketplacePublishResponse:
        """Mock publish ke Tokopedia."""
        settings = get_settings()
        await asyncio.sleep(settings.marketplace_mock_delay)
        
        mock_product_id = f"TOKPED_{uuid4().hex[:8]}"
        
        return MarketplacePublishResponse(
            success=True,
            platform=MarketplacePlatform.TOKOPEDIA,
            product_url=f"https://tokopedia.com/product/{mock_product_id}",
            marketplace_product_id=mock_product_id,
            message="Produk berhasil dipublish ke Tokopedia!"
        )
    
    async def update_product(
        self,
        marketplace_product_id: str,
        request: MarketplacePublishRequest
    ) -> MarketplacePublishResponse:
        """Mock update product di Tokopedia."""
        settings = get_settings()
        await asyncio.sleep(settings.marketplace_mock_delay)
        
        return MarketplacePublishResponse(
            success=True,
            platform=MarketplacePlatform.TOKOPEDIA,
            product_url=f"https://tokopedia.com/product/{marketplace_product_id}",
            marketplace_product_id=marketplace_product_id,
            message="Produk berhasil diupdate di Tokopedia!"
        )
    
    async def delete_product(self, marketplace_product_id: str) -> bool:
        """Mock delete product dari Tokopedia."""
        settings = get_settings()
        await asyncio.sleep(settings.marketplace_mock_delay)
        return True


class TikTokShopAPI(MarketplaceAPI):
    """Mock implementation untuk TikTok Shop API."""
    
    async def publish_product(
        self,
        request: MarketplacePublishRequest
    ) -> MarketplacePublishResponse:
        """Mock publish ke TikTok Shop."""
        settings = get_settings()
        await asyncio.sleep(settings.marketplace_mock_delay)
        
        mock_product_id = f"TIKTOK_{uuid4().hex[:8]}"
        
        return MarketplacePublishResponse(
            success=True,
            platform=MarketplacePlatform.TIKTOK_SHOP,
            product_url=f"https://shop.tiktok.com/product/{mock_product_id}",
            marketplace_product_id=mock_product_id,
            message="Produk berhasil dipublish ke TikTok Shop!"
        )
    
    async def update_product(
        self,
        marketplace_product_id: str,
        request: MarketplacePublishRequest
    ) -> MarketplacePublishResponse:
        """Mock update product di TikTok Shop."""
        settings = get_settings()
        await asyncio.sleep(settings.marketplace_mock_delay)
        
        return MarketplacePublishResponse(
            success=True,
            platform=MarketplacePlatform.TIKTOK_SHOP,
            product_url=f"https://shop.tiktok.com/product/{marketplace_product_id}",
            marketplace_product_id=marketplace_product_id,
            message="Produk berhasil diupdate di TikTok Shop!"
        )
    
    async def delete_product(self, marketplace_product_id: str) -> bool:
        """Mock delete product dari TikTok Shop."""
        settings = get_settings()
        await asyncio.sleep(settings.marketplace_mock_delay)
        return True


class MarketplaceService:
    """
    Service layer untuk marketplace operations.
    Menggunakan factory pattern untuk instantiate API yang sesuai.
    """
    
    def __init__(self):
        self._apis: dict[MarketplacePlatform, MarketplaceAPI] = {
            MarketplacePlatform.SHOPEE: ShopeeAPI(),
            MarketplacePlatform.TOKOPEDIA: TokopediaAPI(),
            MarketplacePlatform.TIKTOK_SHOP: TikTokShopAPI()
        }
    
    def _get_api(self, platform: MarketplacePlatform) -> MarketplaceAPI:
        """Get API instance untuk platform tertentu."""
        api = self._apis.get(platform)
        if not api:
            raise ValueError(f"Platform {platform} not supported")
        return api
    
    async def publish_to_marketplace(
        self,
        request: MarketplacePublishRequest
    ) -> MarketplacePublishResponse:
        """
        Publish produk ke marketplace yang dipilih.
        
        Args:
            request: Request dengan detail produk dan platform
            
        Returns:
            Response dengan status dan URL produk
        """
        api = self._get_api(request.platform)
        return await api.publish_product(request)
    
    async def publish_to_multiple_marketplaces(
        self,
        requests: list[MarketplacePublishRequest]
    ) -> list[MarketplacePublishResponse]:
        """
        Publish produk ke multiple marketplaces secara parallel.
        
        Args:
            requests: List of publish requests
            
        Returns:
            List of responses dari setiap marketplace
        """
        tasks = [
            self.publish_to_marketplace(request)
            for request in requests
        ]
        
        # Execute all publishes in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Convert exceptions to error responses
        responses = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                responses.append(
                    MarketplacePublishResponse(
                        success=False,
                        platform=requests[i].platform,
                        message=f"Error: {str(result)}"
                    )
                )
            else:
                responses.append(result)
        
        return responses
    
    async def update_product(
        self,
        platform: MarketplacePlatform,
        marketplace_product_id: str,
        request: MarketplacePublishRequest
    ) -> MarketplacePublishResponse:
        """Update produk yang sudah ada di marketplace."""
        api = self._get_api(platform)
        return await api.update_product(marketplace_product_id, request)
    
    async def delete_product(
        self,
        platform: MarketplacePlatform,
        marketplace_product_id: str
    ) -> bool:
        """Delete produk dari marketplace."""
        api = self._get_api(platform)
        return await api.delete_product(marketplace_product_id)
