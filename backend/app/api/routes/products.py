"""
Product routes untuk upload, analisis, dan management produk.
Terintegrasi dengan Supabase database dan authentication.
"""
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException, Query
from typing import Optional, List
from supabase import Client
from uuid import UUID, uuid4
import os
import json

from app.schemas.product import (
    ProductAnalysisRequest,
    ProductAnalysisResponse,
    MarketplacePlatform
)
from app.models.database import (
    Product,
    ProductCreate,
    ProductUpdate,
    ProductStatus
)
from app.repositories.product_repository import ProductRepository
from app.services.ai_service import AIProductAnalyzer
from app.core.dependencies import validate_image_file, get_upload_path
from app.core.config import get_settings
from app.core.database import get_db
# from app.core.auth import get_current_user_id  # Disabled for demo

router = APIRouter(prefix="/products", tags=["products"])


@router.post("/analyze", response_model=ProductAnalysisResponse)
async def analyze_product(
    image: UploadFile = File(..., description="Gambar produk"),
    user_description: Optional[str] = Form(None, description="Deskripsi dari user"),
    user_specifications: Optional[str] = Form(
        None,
        description="Spesifikasi dalam format JSON string"
    ),
    upload_path: str = Depends(get_upload_path)
):
    """
    Analisis produk dari gambar menggunakan AI multi-agent system.
    
    Flow:
    1. Upload & validate gambar
    2. AI vision analysis
    3. Category detection
    4. Price suggestion
    5. Copywriting enhancement
    
    Returns:
        ProductAnalysisResponse dengan hasil analisis lengkap
    """
    
    # Validate image file (includes security checks)
    await validate_image_file(image)
    
    # Sanitize filename and save uploaded file
    file_extension = os.path.splitext(image.filename)[1].lower()
    
    # Extra security: only allow known extensions
    if file_extension not in ['.jpg', '.jpeg', '.png', '.webp']:
        raise HTTPException(status_code=400, detail="Invalid file extension")
    
    # Generate secure unique filename
    unique_filename = f"{uuid4().hex}{file_extension}"
    file_path = os.path.join(upload_path, unique_filename)
    
    # Ensure upload path is safe
    real_upload_path = os.path.realpath(upload_path)
    real_file_path = os.path.realpath(file_path)
    if not real_file_path.startswith(real_upload_path):
        raise HTTPException(status_code=400, detail="Invalid file path")
    
    try:
        with open(file_path, "wb") as buffer:
            content = await image.read()
            buffer.write(content)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save file: {str(e)}"
        )
    
    # Parse specifications if provided
    specifications = None
    if user_specifications:
        try:
            specifications = json.loads(user_specifications)
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=400,
                detail="Invalid JSON format for specifications"
            )
    
    # Run AI analysis
    try:
        ai_analyzer = AIProductAnalyzer()
        result = await ai_analyzer.analyze_product(
            image_path=file_path,
            user_description=user_description,
            user_specifications=specifications
        )
        return result
    except ValueError as e:
        # Validation error (gambar tidak sesuai deskripsi)
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        # Cleanup file on error
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(
            status_code=500,
            detail=f"AI analysis failed: {str(e)}"
        )


@router.post("/enhance")
async def enhance_product(
    request: dict
):
    """
    AI enhancement endpoint - Generate optimized description and specifications.
    User can edit the AI-generated content before saving.
    
    Request body:
    {
        "image_url": "https://...",
        "user_description": "optional description",
        "product_name": "product name",
        "price": 100000,
        "category_hint": "optional category"
    }
    
    Returns:
    {
        "enhanced_description": "AI-generated copywriting",
        "specifications": {"key": "value"},
        "category_prediction": "Category Name",
        "seo_keywords": ["keyword1", "keyword2"],
        "suggested_tags": ["tag1", "tag2"],
        "selling_points": ["point1", "point2"]
    }
    """
    try:
        from openai import AsyncOpenAI
        import json
        
        image_url = request.get("image_url")
        user_description = request.get("user_description", "")
        product_name = request.get("product_name", "")
        price = request.get("price", 0)
        category_hint = request.get("category_hint", "")
        
        if not image_url:
            raise HTTPException(status_code=400, detail="image_url is required")
        if not product_name:
            raise HTTPException(status_code=400, detail="product_name is required")
        
        # Initialize OpenAI client
        settings = get_settings()
        
        # Check if mock mode (for testing when API is unavailable)
        if settings.use_mock_ai:
            # Return mock response for testing
            return {
                "enhanced_description": f"""🌟 {product_name} - Pilihan Sempurna untuk Gaya Hidup Aktif Anda!

Dapatkan kenyamanan maksimal dengan {product_name} yang dirancang khusus untuk mendukung aktivitas harian Anda. Produk berkualitas premium ini menggabungkan desain modern dengan teknologi terkini, memberikan pengalaman yang tak tertandingi.

✨ Keunggulan Produk:
• Material berkualitas tinggi yang tahan lama
• Desain ergonomis untuk kenyamanan maksimal  
• Cocok untuk berbagai aktivitas dan gaya
• Mudah dirawat dan dibersihkan

💯 Garansi Kualitas:
Kami menjamin 100% produk original dengan kualitas terbaik. Setiap detail dirancang dengan sempurna untuk memenuhi standar tinggi Anda.

🚀 Pengiriman Cepat:
Tersedia pengiriman ke seluruh Indonesia dengan packaging aman dan rapi. Dapatkan produk impian Anda dengan harga terbaik!

Harga: Rp {price:,.0f}
Stock terbatas - Pesan sekarang juga!""",
                "specifications": {
                    "Brand": "Premium Brand",
                    "Material": "High Quality Material",
                    "Kondisi": "100% Baru",
                    "Garansi": "Resmi",
                    "Berat": "500 gram"
                },
                "category_prediction": "Fashion & Aksesoris",
                "seo_keywords": ["original", "berkualitas", "terpercaya", "harga terbaik", "pengiriman cepat"],
                "suggested_tags": ["#trending", "#bestseller", "#recommended", "#promo"],
                "selling_points": [
                    "Kualitas premium dengan harga terjangkau",
                    "Desain modern dan stylish",
                    "Nyaman digunakan sepanjang hari",
                    "Cocok untuk segala aktivitas",
                    "Garansi resmi dan original 100%"
                ]
            }
        
        client = AsyncOpenAI(
            api_key=settings.openai_api_key,
            base_url=settings.openai_api_base
        )
        
        # Get product info from Google Search for better context
        google_search_context = ""
        try:
            from app.services.google_search_service import get_google_search_service
            search_service = get_google_search_service()
            
            # Search for product information
            product_info = await search_service.search_product_info(
                product_name,
                additional_context=user_description or ""
            )
            
            if product_info.get("descriptions"):
                descriptions = "\n".join(product_info["descriptions"][:3])
                google_search_context = f"""

REAL MARKET DATA FROM GOOGLE SEARCH:
{descriptions}

Use this information to enrich your analysis and ensure accuracy!
"""
            
            # Also get price data for validation
            price_data = await search_service.search_product_prices(product_name)
            if price_data.get("found"):
                google_search_context += f"""

MARKET PRICE DATA:
- Min: Rp {price_data['min_price']:,}
- Max: Rp {price_data['max_price']:,}
- Average: Rp {price_data['avg_price']:,}
- Confidence: {price_data['market_data']['confidence']:.1%}
"""
        except Exception as e:
            pass  # Ignore Google Search errors, continue without it
        
        # Build AI prompt
        prompt = f"""
Analyze this product and create compelling e-commerce content:

PRODUCT INFORMATION:
- Name: {product_name}
- Current Description: {user_description or "Not provided"}
- Price: Rp {price:,.0f}
- Category Hint: {category_hint or "Auto-detect"}
- Image URL: {image_url}

{google_search_context}

TASK:
1. Generate a compelling, SEO-optimized product description (150-300 words)
2. Extract or create DETAILED product specifications from ALL available data sources:
   - Analyze the user description carefully
   - Use Google Search data to fill missing specs
   - Include: Brand, Model, Material, Size, Color, Condition, Weight, Dimensions, etc.
   - Be as specific as possible based on available information
3. Predict the most accurate product category
4. Suggest SEO keywords for marketplace optimization
5. Create catchy tags/hashtags
6. List 3-5 key selling points

GUIDELINES:
- Write in Indonesian language
- Use persuasive copywriting techniques
- Highlight benefits, not just features
- Include emotional triggers (trust, urgency, value)
- Optimize for marketplace search algorithms
- Be specific and detailed
- IMPORTANT: Extract specifications from description and Google Search data

Return ONLY valid JSON in this exact format:
{{
  "enhanced_description": "<compelling description in Indonesian>",
  "specifications": {{
    "Brand": "value",
    "Model": "value",
    "Material": "value",
    "Size": "value",
    "Color": "value",
    "Condition": "value",
    "Weight": "value"
  }},
  "category_prediction": "<category name>",
  "seo_keywords": ["keyword1", "keyword2", "keyword3"],
  "suggested_tags": ["#tag1", "#tag2", "#tag3"],
  "selling_points": ["point1", "point2", "point3"]
}}
"""
        
        # Use text-only prompt (vision not supported by current API)
        response = await client.chat.completions.create(
            model=settings.openai_model_name,
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert e-commerce copywriter and product analyst specializing in Indonesian marketplaces (Shopee, TikTok Shop, Tokopedia). Create compelling, conversion-optimized product content in Indonesian language."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=1500
        )
        
        # Parse AI response
        content = response.choices[0].message.content
        
        # Try to parse as JSON
        try:
            ai_result = json.loads(content)
        except json.JSONDecodeError:
            # If not JSON, extract from markdown code block
            import re
            json_match = re.search(r'```json\s*(\{.*?\})\s*```', content, re.DOTALL)
            if json_match:
                ai_result = json.loads(json_match.group(1))
            else:
                # Fallback: create basic structure
                ai_result = {
                    "enhanced_description": content,
                    "specifications": {},
                    "category_prediction": "General",
                    "seo_keywords": [],
                    "suggested_tags": [],
                    "selling_points": []
                }
        
        return {
            "enhanced_description": ai_result.get("enhanced_description", ""),
            "specifications": ai_result.get("specifications", {}),
            "category_prediction": ai_result.get("category_prediction", "General"),
            "seo_keywords": ai_result.get("seo_keywords", []),
            "suggested_tags": ai_result.get("suggested_tags", []),
            "selling_points": ai_result.get("selling_points", [])
        }
        
    except HTTPException:
        raise
    except Exception as e:
        # Fallback to mock data if AI API fails
        print(f"AI API Error: {str(e)}")
        print("Falling back to mock data...")
        
        return {
            "enhanced_description": f"""🌟 {product_name} - Pilihan Sempurna untuk Gaya Hidup Aktif Anda!

Dapatkan kenyamanan maksimal dengan {product_name} yang dirancang khusus untuk mendukung aktivitas harian Anda. Produk berkualitas premium ini menggabungkan desain modern dengan teknologi terkini, memberikan pengalaman yang tak tertandingi.

✨ Keunggulan Produk:
• Material berkualitas tinggi yang tahan lama
• Desain ergonomis untuk kenyamanan maksimal  
• Cocok untuk berbagai aktivitas dan gaya
• Mudah dirawat dan dibersihkan

💯 Garansi Kualitas:
Kami menjamin 100% produk original dengan kualitas terbaik. Setiap detail dirancang dengan sempurna untuk memenuhi standar tinggi Anda.

🚀 Pengiriman Cepat:
Tersedia pengiriman ke seluruh Indonesia dengan packaging aman dan rapi. Dapatkan produk impian Anda dengan harga terbaik!

Harga: Rp {price:,.0f}
Stock terbatas - Pesan sekarang juga!""",
            "specifications": {
                "Brand": "Premium Brand",
                "Material": "High Quality Material",
                "Kondisi": "100% Baru",
                "Garansi": "Resmi",
                "Berat": "500 gram"
            },
            "category_prediction": "Fashion & Aksesoris",
            "seo_keywords": ["original", "berkualitas", "terpercaya", "harga terbaik", "pengiriman cepat"],
            "suggested_tags": ["#trending", "#bestseller", "#recommended", "#promo"],
            "selling_points": [
                "Kualitas premium dengan harga terjangkau",
                "Desain modern dan stylish",
                "Nyaman digunakan sepanjang hari",
                "Cocok untuk segala aktivitas",
                "Garansi resmi dan original 100%"
            ]
        }


@router.get("/health")
async def health_check():
    """Health check endpoint untuk monitoring."""
    settings = get_settings()
    
    return {
        "status": "healthy",
        "service": "AI Product Analyzer",
        "version": settings.api_version,
        "ai_model": settings.openai_model_name
    }


# ============================================
# PRODUCT CRUD ENDPOINTS
# ============================================

@router.post("", response_model=Product, status_code=201)
async def create_product(
    product_data: ProductCreate,
    db: Client = Depends(get_db)
):
    """
    Create new product (Universal Product Model).
    
    User hanya perlu input data sederhana:
    - Name, description, price, stock
    - Images (URLs)
    - Basic metadata
    
    AI enrichment dilakukan di endpoint terpisah.
    """
    # DEMO MODE: Hardcoded user ID
    demo_user_id = UUID("00000000-0000-0000-0000-000000000001")
    
    try:
        repo = ProductRepository(db)
        product = await repo.create(demo_user_id, product_data)
        return product
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create product: {str(e)}"
        )


@router.get("", response_model=List[Product])
async def list_products(
    status: Optional[ProductStatus] = Query(None, description="Filter by status"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Client = Depends(get_db)
):
    """
    Get all products for current user.
    Supports pagination and status filtering.
    """
    # DEMO MODE: Hardcoded user ID
    demo_user_id = UUID("00000000-0000-0000-0000-000000000001")
    
    try:
        repo = ProductRepository(db)
        products = await repo.get_all_by_user(
            user_id=demo_user_id,
            status=status,
            limit=limit,
            offset=offset
        )
        return products
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list products: {str(e)}"
        )


@router.get("/{product_id}", response_model=Product)
async def get_product(
    product_id: UUID,
    db: Client = Depends(get_db)
):
    """Get single product by ID."""
    repo = ProductRepository(db)
    
    # DEMO MODE: Hardcoded user ID
    demo_user_id = UUID("00000000-0000-0000-0000-000000000001")
    
    try:
        product = await repo.get_by_id(product_id, demo_user_id)
        
        if not product:
            raise HTTPException(
                status_code=404,
                detail="Product not found"
            )
        
        return product
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get product: {str(e)}"
        )


@router.patch("/{product_id}", response_model=Product)
async def update_product(
    product_id: UUID,
    product_data: ProductUpdate,
    db: Client = Depends(get_db)
):
    """Update product data."""
    repo = ProductRepository(db)
    
    # DEMO MODE: Hardcoded user ID
    demo_user_id = UUID("00000000-0000-0000-0000-000000000001")
    
    try:
        product = await repo.update(product_id, demo_user_id, product_data)
        
        if not product:
            raise HTTPException(
                status_code=404,
                detail="Product not found"
            )
        
        return product
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update product: {str(e)}"
        )


@router.delete("/{product_id}")
async def delete_product(
    product_id: UUID,
    db: Client = Depends(get_db)
):
    """
    Delete product permanently (hard delete).
    No archive - direct deletion to save storage.
    """
    repo = ProductRepository(db)
    
    # DEMO MODE: Hardcoded user ID
    demo_user_id = UUID("00000000-0000-0000-0000-000000000001")
    
    try:
        success = await repo.hard_delete(product_id, demo_user_id)
        
        if not success:
            raise HTTPException(
                status_code=404,
                detail="Product not found"
            )
        
        return {"message": "Product permanently deleted"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete product: {str(e)}"
        )


@router.get("/stats/summary")
async def get_product_stats(
    db: Client = Depends(get_db)
):
    """
    Get product statistics for current user.
    """
    repo = ProductRepository(db)
    
    # DEMO MODE: Hardcoded user ID
    demo_user_id = UUID("00000000-0000-0000-0000-000000000001")
    
    try:
        total = await repo.count_by_user(demo_user_id)
        draft = await repo.count_by_user(demo_user_id, ProductStatus.DRAFT)
        ready = await repo.count_by_user(demo_user_id, ProductStatus.READY)
        published = await repo.count_by_user(demo_user_id, ProductStatus.PUBLISHED)
        
        return {
            "total": total,
            "draft": draft,
            "ready": ready,
            "published": published,
            "archived": total - draft - ready - published
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get stats: {str(e)}"
        )
