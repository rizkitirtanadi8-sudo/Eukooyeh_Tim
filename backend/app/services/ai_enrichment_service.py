"""
AI Enrichment Service - Transform simple product input into marketplace-specific data.

This is the CORE VALUE PROPOSITION of the SaaS:
- User inputs simple data (name, price, description)
- AI predicts category_id, fills attributes, enhances description
- Output is ready-to-publish JSON for Shopee/TikTok Shop
"""
from typing import Dict, Any, Optional, List
from openai import AsyncOpenAI
import json

from app.core.config import get_settings
from app.models.database import Product, MarketplacePlatform, UserSettings


class AIEnrichmentService:
    """
    AI service untuk enrichment product data.
    Menggunakan OpenAI/Kolosal API untuk intelligent transformation.
    """
    
    def __init__(self):
        settings = get_settings()
        self.client = AsyncOpenAI(
            api_key=settings.openai_api_key,
            base_url=settings.openai_api_base
        )
        self.model = settings.openai_model_name
    
    async def enrich_for_shopee(
        self,
        product: Product,
        user_settings: UserSettings
    ) -> Dict[str, Any]:
        """
        Enrich product untuk Shopee.
        
        Args:
            product: Universal product model
            user_settings: User's global settings
            
        Returns:
            Shopee-specific JSON payload
        """
        # Build AI prompt
        prompt = self._build_shopee_prompt(product, user_settings)
        
        # Call AI
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": """You are an expert e-commerce product listing specialist for Shopee Indonesia.
Your task is to transform simple product information into a complete, optimized Shopee listing.

CRITICAL RULES:
1. Predict the most accurate category_id based on product name/description
2. Fill ALL mandatory attributes with smart defaults if not provided
3. Enhance product title for SEO (max 120 chars)
4. Write compelling HTML description with proper formatting
5. Suggest relevant hashtags
6. Return ONLY valid JSON, no markdown or explanations

Common Shopee Categories (Indonesia):
- 100017: Sepatu Pria
- 100018: Sepatu Wanita
- 100630: Fashion Pria
- 100631: Fashion Wanita
- 100011: Elektronik
- 100012: Handphone & Aksesoris
- 100644: Makanan & Minuman
- 100645: Kecantikan
- 100646: Kesehatan

Common Attributes:
- Brand (attribute_id: 100001): "No Brand" if unknown
- Condition (attribute_id: 100002): "New" or "Used"
- Size (attribute_id: 100003): Based on product type
- Color (attribute_id: 100004): Based on images/description
"""
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3,  # Lower for more consistent output
            response_format={"type": "json_object"}
        )
        
        # Parse AI response
        ai_output = json.loads(response.choices[0].message.content)
        
        # Build Shopee payload
        shopee_data = self._build_shopee_payload(
            product=product,
            ai_output=ai_output,
            user_settings=user_settings
        )
        
        return shopee_data
    
    async def enrich_for_tiktok(
        self,
        product: Product,
        user_settings: UserSettings
    ) -> Dict[str, Any]:
        """
        Enrich product untuk TikTok Shop.
        
        Args:
            product: Universal product model
            user_settings: User's global settings
            
        Returns:
            TikTok Shop-specific JSON payload
        """
        prompt = self._build_tiktok_prompt(product, user_settings)
        
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": """You are an expert e-commerce product listing specialist for TikTok Shop Indonesia.
Your task is to transform simple product information into a viral-worthy TikTok Shop listing.

CRITICAL RULES:
1. Predict the most accurate category_id for TikTok Shop
2. Write catchy, social-media friendly product title (max 100 chars)
3. Create engaging description with emojis and hashtags
4. Fill product attributes (brand, size, color, etc.)
5. Suggest trending hashtags for TikTok
6. Return ONLY valid JSON, no markdown

TikTok Shop Categories (Indonesia):
- 201001: Fashion Pria
- 201002: Fashion Wanita
- 201003: Elektronik
- 201004: Kecantikan & Perawatan
- 201005: Makanan & Minuman
- 201006: Olahraga & Outdoor
- 201007: Rumah Tangga

Style Guide:
- Use emojis strategically ✨🔥💯
- Write in conversational tone
- Highlight benefits, not just features
- Create urgency and FOMO
"""
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.5,  # Slightly higher for more creative output
            response_format={"type": "json_object"}
        )
        
        ai_output = json.loads(response.choices[0].message.content)
        
        tiktok_data = self._build_tiktok_payload(
            product=product,
            ai_output=ai_output,
            user_settings=user_settings
        )
        
        return tiktok_data
    
    def _build_shopee_prompt(self, product: Product, user_settings: UserSettings) -> str:
        """Build prompt untuk Shopee enrichment."""
        return f"""
Transform this product into a complete Shopee listing:

PRODUCT INFORMATION:
- Name: {product.name}
- Description: {product.description or "No description provided"}
- Price: Rp {product.price:,.0f}
- Stock: {product.stock_quantity}
- Weight: {product.weight_kg} kg
- Condition: {product.condition}
- Images: {len(product.images)} images available

USER SETTINGS:
- Warehouse City: {user_settings.warehouse_city or "Jakarta"}
- Default Logistics: {json.dumps(user_settings.default_logistics)}

REQUIRED OUTPUT (JSON):
{{
  "category_id": <predicted_category_id>,
  "category_name": "<category_name>",
  "title": "<SEO-optimized title max 120 chars>",
  "description_html": "<HTML formatted description with <p>, <ul>, <li> tags>",
  "attributes": [
    {{"attribute_id": 100001, "attribute_name": "Brand", "value": "No Brand"}},
    {{"attribute_id": 100002, "attribute_name": "Condition", "value": "New"}}
  ],
  "hashtags": ["#tag1", "#tag2"],
  "seo_keywords": ["keyword1", "keyword2"],
  "reasoning": "<brief explanation of category choice>"
}}

Analyze the product carefully and return the complete JSON.
"""
    
    def _build_tiktok_prompt(self, product: Product, user_settings: UserSettings) -> str:
        """Build prompt untuk TikTok Shop enrichment."""
        return f"""
Transform this product into a viral TikTok Shop listing:

PRODUCT INFORMATION:
- Name: {product.name}
- Description: {product.description or "No description provided"}
- Price: Rp {product.price:,.0f}
- Stock: {product.stock_quantity}
- Weight: {product.weight_kg} kg
- Condition: {product.condition}

REQUIRED OUTPUT (JSON):
{{
  "category_id": <predicted_category_id>,
  "category_name": "<category_name>",
  "title": "<catchy title with emojis max 100 chars>",
  "description": "<engaging description with emojis and line breaks>",
  "product_attributes": [
    {{"name": "Brand", "value": "No Brand"}},
    {{"name": "Condition", "value": "New"}}
  ],
  "hashtags": ["#viral", "#fyp", "#trending"],
  "selling_points": ["point1", "point2", "point3"],
  "reasoning": "<brief explanation>"
}}

Make it engaging and viral-worthy!
"""
    
    def _build_shopee_payload(
        self,
        product: Product,
        ai_output: Dict[str, Any],
        user_settings: UserSettings
    ) -> Dict[str, Any]:
        """
        Build final Shopee API payload.
        Combines AI output with user settings and product data.
        """
        # Get logistics from user settings or use defaults
        logistics = user_settings.default_logistics or []
        shopee_logistics = [
            log for log in logistics 
            if log.get("platform") == "shopee"
        ]
        
        # Build complete Shopee payload
        payload = {
            # Basic Info
            "item_name": ai_output.get("title", product.name)[:120],
            "description": ai_output.get("description_html", product.description or ""),
            "category_id": ai_output.get("category_id"),
            
            # Pricing & Stock
            "price": float(product.price),
            "stock": product.stock_quantity,
            
            # Physical Attributes
            "weight": float(product.weight_kg or user_settings.default_weight_kg),
            "condition": "NEW" if product.condition == "new" else "USED",
            
            # Images (Shopee requires image IDs, not URLs)
            # In production, you'd upload images first and get image_ids
            "images": product.images,
            
            # Attributes
            "attributes": ai_output.get("attributes", []),
            
            # Logistics
            "logistics": shopee_logistics,
            
            # Warehouse
            "warehouse_id": None,  # Set if user has warehouse_id
            
            # SEO
            "item_sku": product.sku,
            
            # AI Metadata (for our tracking)
            "_ai_metadata": {
                "category_name": ai_output.get("category_name"),
                "hashtags": ai_output.get("hashtags", []),
                "seo_keywords": ai_output.get("seo_keywords", []),
                "reasoning": ai_output.get("reasoning")
            }
        }
        
        return payload
    
    def _build_tiktok_payload(
        self,
        product: Product,
        ai_output: Dict[str, Any],
        user_settings: UserSettings
    ) -> Dict[str, Any]:
        """
        Build final TikTok Shop API payload.
        """
        payload = {
            # Basic Info
            "product_name": ai_output.get("title", product.name)[:100],
            "description": ai_output.get("description", product.description or ""),
            "category_id": ai_output.get("category_id"),
            
            # Pricing
            "price": {
                "currency": "IDR",
                "amount": int(product.price)
            },
            
            # Stock
            "stock_quantity": product.stock_quantity,
            
            # Attributes
            "product_attributes": ai_output.get("product_attributes", []),
            
            # Images
            "images": product.images,
            
            # Weight (in grams for TikTok)
            "weight": int((product.weight_kg or user_settings.default_weight_kg) * 1000),
            
            # SKU
            "seller_sku": product.sku,
            
            # AI Metadata
            "_ai_metadata": {
                "category_name": ai_output.get("category_name"),
                "hashtags": ai_output.get("hashtags", []),
                "selling_points": ai_output.get("selling_points", []),
                "reasoning": ai_output.get("reasoning")
            }
        }
        
        return payload
    
    async def predict_category(
        self,
        product_name: str,
        description: Optional[str],
        platform: MarketplacePlatform
    ) -> Dict[str, Any]:
        """
        Quick category prediction without full enrichment.
        Useful for preview/suggestions.
        """
        prompt = f"""
Predict the most accurate category for this product on {platform.value}:

Product Name: {product_name}
Description: {description or "N/A"}

Return JSON:
{{
  "category_id": <id>,
  "category_name": "<name>",
  "confidence": <0.0-1.0>,
  "alternatives": [
    {{"category_id": <id>, "category_name": "<name>", "confidence": <score>}}
  ]
}}
"""
        
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a product categorization expert."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            response_format={"type": "json_object"}
        )
        
        return json.loads(response.choices[0].message.content)
