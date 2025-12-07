"""
Google Search API Service untuk market research dan price validation.
Digunakan untuk mendapatkan data real-time dari internet.
"""
import aiohttp
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import json
from app.core.config import get_settings


class GoogleSearchService:
    """
    Service untuk menggunakan Google Custom Search API.
    Digunakan untuk:
    1. Market trend analysis
    2. Price validation dan comparison
    3. Product information enrichment
    4. Competitor analysis
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.api_key = self.settings.google_search_api_key
        self.engine_id = self.settings.google_search_engine_id
        self.enabled = self.settings.google_search_enabled and self.api_key and self.engine_id
        self.base_url = "https://www.googleapis.com/customsearch/v1"
    
    async def search(
        self,
        query: str,
        num_results: int = 10,
        search_type: str = "web"
    ) -> List[Dict[str, Any]]:
        """
        Perform Google search and return results.
        
        Args:
            query: Search query
            num_results: Number of results to return (max 10 per request)
            search_type: Type of search (web, image, etc.)
            
        Returns:
            List of search results with title, link, snippet
        """
        if not self.enabled:
            return []
        
        try:
            params = {
                "key": self.api_key,
                "cx": self.engine_id,
                "q": query,
                "num": min(num_results, 10)
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(self.base_url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        items = data.get("items", [])
                        
                        results = []
                        for item in items:
                            results.append({
                                "title": item.get("title", ""),
                                "link": item.get("link", ""),
                                "snippet": item.get("snippet", ""),
                                "displayLink": item.get("displayLink", "")
                            })
                        
                        return results
                    else:
                        print(f"Google Search API error: {response.status}")
                        return []
        
        except Exception as e:
            print(f"Error performing Google search: {e}")
            return []
    
    async def search_product_prices(
        self,
        product_name: str,
        category: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Search for product prices across marketplaces.
        
        Args:
            product_name: Name of the product
            category: Optional category for better results
            
        Returns:
            Dict with price information and market data
        """
        # Build search query for Indonesian marketplaces
        query = f"{product_name} harga"
        if category:
            query += f" {category}"
        query += " site:tokopedia.com OR site:shopee.co.id OR site:bukalapak.com OR site:lazada.co.id"
        
        results = await self.search(query, num_results=10)
        
        # Extract price information from snippets
        prices = []
        sources = []
        
        for result in results:
            snippet = result.get("snippet", "")
            title = result.get("title", "")
            
            # Try to extract price from snippet or title
            import re
            price_patterns = [
                r'Rp\s*([\d.,]+)',
                r'IDR\s*([\d.,]+)',
                r'(\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})?)'
            ]
            
            for pattern in price_patterns:
                matches = re.findall(pattern, snippet + " " + title)
                for match in matches:
                    try:
                        # Clean and convert price
                        price_str = match.replace('.', '').replace(',', '')
                        price = int(price_str)
                        
                        # Sanity check: price should be reasonable (1000 - 1 billion)
                        if 1000 <= price <= 1_000_000_000:
                            prices.append(price)
                            sources.append({
                                "price": price,
                                "source": result.get("displayLink", ""),
                                "title": title,
                                "link": result.get("link", "")
                            })
                    except:
                        continue
        
        # Calculate statistics
        if prices:
            prices.sort()
            return {
                "found": True,
                "min_price": min(prices),
                "max_price": max(prices),
                "avg_price": sum(prices) // len(prices),
                "median_price": prices[len(prices) // 2],
                "price_count": len(prices),
                "sources": sources[:5],  # Top 5 sources
                "market_data": {
                    "competitive": len(prices) >= 5,
                    "price_range": max(prices) - min(prices),
                    "confidence": min(len(prices) / 10, 1.0)
                }
            }
        else:
            return {
                "found": False,
                "message": "No price data found",
                "sources": []
            }
    
    async def search_product_info(
        self,
        product_name: str,
        additional_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Search for detailed product information.
        
        Args:
            product_name: Name of the product
            additional_context: Additional context for better search
            
        Returns:
            Dict with product information
        """
        query = f"{product_name}"
        if additional_context:
            query += f" {additional_context}"
        query += " spesifikasi review"
        
        results = await self.search(query, num_results=5)
        
        # Compile information from search results
        info = {
            "product_name": product_name,
            "descriptions": [],
            "specifications": [],
            "reviews": [],
            "sources": []
        }
        
        for result in results:
            info["descriptions"].append(result.get("snippet", ""))
            info["sources"].append({
                "title": result.get("title", ""),
                "link": result.get("link", ""),
                "source": result.get("displayLink", "")
            })
        
        return info
    
    async def get_market_trends(
        self,
        categories: List[str],
        region: str = "Indonesia"
    ) -> Dict[str, Any]:
        """
        Get market trends for specific categories.
        
        Args:
            categories: List of product categories
            region: Region for market trends
            
        Returns:
            Dict with trend data per category
        """
        trends = {}
        
        for category in categories:
            query = f"trending {category} {region} 2024"
            results = await self.search(query, num_results=5)
            
            # Extract trending products/keywords
            trending_items = []
            for result in results:
                snippet = result.get("snippet", "")
                title = result.get("title", "")
                
                # Simple keyword extraction
                keywords = self._extract_keywords(snippet + " " + title, category)
                trending_items.extend(keywords)
            
            # Count frequency
            from collections import Counter
            keyword_counts = Counter(trending_items)
            
            trends[category] = {
                "category": category,
                "trending_products": [
                    {"name": k, "mentions": v} 
                    for k, v in keyword_counts.most_common(10)
                ],
                "last_updated": datetime.now().isoformat(),
                "sources": [r.get("link", "") for r in results]
            }
        
        return trends
    
    def _extract_keywords(self, text: str, category: str) -> List[str]:
        """Extract relevant keywords from text."""
        import re
        
        # Remove common words
        stop_words = {
            'dan', 'atau', 'yang', 'untuk', 'dari', 'di', 'ke', 'dengan',
            'adalah', 'ini', 'itu', 'pada', 'dalam', 'akan', 'dapat',
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for'
        }
        
        # Split into words
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        
        # Filter keywords
        keywords = [
            w for w in words 
            if w not in stop_words and len(w) > 3
        ]
        
        return keywords[:20]  # Limit to 20 keywords
    
    async def analyze_competition(
        self,
        product_name: str,
        category: str
    ) -> Dict[str, Any]:
        """
        Analyze competition for a product.
        
        Args:
            product_name: Product name
            category: Product category
            
        Returns:
            Competition analysis data
        """
        query = f"{product_name} {category} terlaris best seller"
        results = await self.search(query, num_results=10)
        
        competitors = []
        for result in results:
            competitors.append({
                "title": result.get("title", ""),
                "source": result.get("displayLink", ""),
                "snippet": result.get("snippet", ""),
                "link": result.get("link", "")
            })
        
        return {
            "product": product_name,
            "category": category,
            "competitor_count": len(competitors),
            "competitors": competitors,
            "market_saturation": "high" if len(competitors) >= 8 else "medium" if len(competitors) >= 4 else "low",
            "analysis_date": datetime.now().isoformat()
        }


# Singleton instance
_google_search_service: Optional[GoogleSearchService] = None


def get_google_search_service() -> GoogleSearchService:
    """Get or create GoogleSearchService singleton."""
    global _google_search_service
    if _google_search_service is None:
        _google_search_service = GoogleSearchService()
    return _google_search_service
