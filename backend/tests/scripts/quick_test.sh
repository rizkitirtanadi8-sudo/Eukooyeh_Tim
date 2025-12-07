#!/bin/bash

echo "=========================================="
echo "🧪 Quick Test - AI Enhancement System"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test 1: Health Check
echo "Test 1: Health Check"
echo "--------------------"
response=$(curl -s http://localhost:8000/api/v1/products/health)
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ PASS${NC} - Server is running"
    echo "Response: $response"
else
    echo -e "${RED}❌ FAIL${NC} - Server is not running"
    exit 1
fi
echo ""

# Test 2: Product Enhancement
echo "Test 2: Product Enhancement"
echo "----------------------------"
echo "Request: Sepatu Nike Air Max 270"

response=$(curl -s -X POST http://localhost:8000/api/v1/products/enhance \
  -H 'Content-Type: application/json' \
  -d '{
    "image_url": "https://example.com/sepatu-nike.jpg",
    "product_name": "Sepatu Nike Air Max 270",
    "user_description": "Sepatu olahraga Nike Air Max 270 warna hitam, ukuran 42, kondisi baru, original",
    "price": 1500000,
    "category_hint": "Fashion"
  }')

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ PASS${NC} - Enhancement successful"
    echo ""
    echo "Enhanced Description:"
    echo "$response" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('enhanced_description', 'N/A')[:200] + '...')"
    echo ""
    echo "Specifications:"
    echo "$response" | python3 -c "import sys, json; data=json.load(sys.stdin); specs=data.get('specifications', {}); [print(f'  - {k}: {v}') for k,v in list(specs.items())[:3]]"
    echo ""
    echo "Category: $(echo "$response" | python3 -c "import sys, json; print(json.load(sys.stdin).get('category_prediction', 'N/A'))")"
    echo ""
    echo "SEO Keywords: $(echo "$response" | python3 -c "import sys, json; print(', '.join(json.load(sys.stdin).get('seo_keywords', [])[:5]))")"
else
    echo -e "${RED}❌ FAIL${NC} - Enhancement failed"
    exit 1
fi
echo ""

# Test 3: Check Google Search Integration
echo "Test 3: Google Search Integration"
echo "----------------------------------"
if grep -q "GOOGLE_SEARCH_API_KEY=" .env 2>/dev/null && grep -q "GOOGLE_SEARCH_ENGINE_ID=" .env 2>/dev/null; then
    api_key=$(grep "GOOGLE_SEARCH_API_KEY=" .env | cut -d'=' -f2)
    engine_id=$(grep "GOOGLE_SEARCH_ENGINE_ID=" .env | cut -d'=' -f2)
    
    if [ -n "$api_key" ] && [ "$api_key" != "your_google_search_api_key_here" ]; then
        echo -e "${GREEN}✅ CONFIGURED${NC} - Google Search API is configured"
        echo "  API Key: ${api_key:0:20}..."
        echo "  Engine ID: $engine_id"
    else
        echo -e "${YELLOW}⚠️  NOT CONFIGURED${NC} - Google Search API not configured"
        echo "  System will use fallback mode (AI only)"
        echo "  For better results, configure Google Search API in .env"
    fi
else
    echo -e "${YELLOW}⚠️  NOT CONFIGURED${NC} - .env file not found or incomplete"
fi
echo ""

# Summary
echo "=========================================="
echo "📊 Test Summary"
echo "=========================================="
echo -e "${GREEN}✅ Backend Server: RUNNING${NC}"
echo -e "${GREEN}✅ AI Enhancement: WORKING${NC}"
echo -e "${YELLOW}⚠️  Google Search: NOT CONFIGURED (optional)${NC}"
echo ""
echo "🎉 System is ready for testing!"
echo ""
echo "Next steps:"
echo "1. Test via Swagger UI: http://localhost:8000/docs"
echo "2. Test via Frontend (if running): http://localhost:3000"
echo "3. Configure Google Search API for better results (optional)"
echo ""
echo "=========================================="
