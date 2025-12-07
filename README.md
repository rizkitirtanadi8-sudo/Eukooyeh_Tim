# 🤖 AI E-commerce Product Manager

**AI-powered platform untuk automasi product listing ke marketplace menggunakan multi-agent system.**

> ✅ **Production-Ready** | 🌐 **Open Source** | 🔐 **Shopify Direct API** | 🤖 **AI Multi-Agent**

[![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-14.2.33-000000?logo=next.js)](https://nextjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0-3178C6?logo=typescript)](https://www.typescriptlang.org/)
[![Python](https://img.shields.io/badge/Python-3.12+-3776AB?logo=python)](https://www.python.org/)

---

## 🎯 Fitur Utama

### 🤖 AI-Powered Features
- ✅ **AI Vision Analysis** - Analisis produk dari gambar dengan GPT-4 Vision
- ✅ **Auto Category Detection** - Deteksi kategori produk otomatis (10+ categories)
- ✅ **Smart Price Suggestion** - Saran harga berdasarkan data pasar real
- ✅ **AI Copywriting** - Generate deskripsi menarik & SEO-friendly
- ✅ **Auto Specifications** - Ekstrak spesifikasi produk otomatis

### 📊 Market Intelligence
- ✅ **Market Trends Dashboard** - Trending products per kategori
- ✅ **Competitor Analysis** - Analisis harga kompetitor
- ✅ **Real-time Data** - Google Search API integration
- ✅ **Trend Predictions** - AI-powered trend forecasting

### 🛒 Marketplace Integration
- ✅ **Shopify Direct API** - Publish langsung ke Shopify store
- ✅ **One-Click Publishing** - Publish produk dengan satu klik
- ✅ **Inventory Sync** - Sinkronisasi stok otomatis
- ✅ **Multi-Store Support** - Kelola multiple stores

### 🎨 Modern UI/UX
- ✅ **Dark Mode** - Complete dark/light theme support
- ✅ **Responsive Design** - Mobile-first, tablet & desktop optimized
- ✅ **Intuitive Interface** - Clean & user-friendly
- ✅ **Real-time Updates** - Instant feedback & notifications

---

## 🏗️ Tech Stack

### Backend
```
FastAPI (Python 3.12+)
├── AI Engine: CrewAI (Multi-agent orchestration)
├── LLM: OpenAI GPT-4 Vision / Kolosal AI
├── Database: Supabase (PostgreSQL)
├── External APIs: Google Search API
└── Validation: Pydantic v2
```

### Frontend
```
Next.js 14 (App Router)
├── Language: TypeScript
├── Styling: TailwindCSS + Shadcn/ui
├── Icons: Lucide React
├── HTTP Client: Axios
└── State Management: React Hooks
```

### Infrastructure
- **Database:** Supabase (PostgreSQL with Row Level Security)
- **File Storage:** Supabase Storage
- **Deployment:** Vercel (Frontend) + Railway/Render (Backend)
- **Monitoring:** Built-in health checks

---

## 🤖 AI Multi-Agent System

### 4 Specialized Agents:

```
┌─────────────────────────────────────────────────────────┐
│  1. Vision Agent 👁️                                     │
│     - Analisis gambar produk                            │
│     - Identifikasi brand & model                        │
│     - Deteksi kondisi produk                            │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│  2. Category Agent 🏷️                                   │
│     - Klasifikasi kategori otomatis                     │
│     - Confidence scoring                                │
│     - Sub-category detection                            │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│  3. Pricing Agent 💰                                     │
│     - Market research via Google Search                 │
│     - Competitor price analysis                         │
│     - Saran harga kompetitif                            │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│  4. Copywriter Agent ✍️                                  │
│     - Generate judul menarik                            │
│     - Deskripsi SEO-friendly                            │
│     - Hashtags & keywords                               │
└─────────────────────────────────────────────────────────┘
```

**Workflow:**
```
Upload Image → Vision Analysis → Category Detection → 
Market Research → Price Suggestion → Copywriting → 
Complete Product Data → Publish to Shopify
```

---

## 🚀 Quick Start

### Prerequisites
- **Python 3.12+**
- **Node.js 18+**
- **Supabase account** (free tier)
- **OpenAI/Kolosal AI API key**
- **Shopify store** (for publishing)

### 1. Clone Repository

```bash
git clone https://github.com/your-username/ai-ecommerce-manager.git
cd ai-ecommerce-manager
```

### 2. Database Setup

```bash
# 1. Create Supabase project at https://supabase.com
# 2. Run SQL migrations in Supabase SQL Editor:
#    - SUPABASE_MIGRATION.sql (create tables)
#    - FIX_DEMO_USER.sql (create demo user)
```

### 3. Backend Setup

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env with your credentials:
# - OPENAI_API_KEY
# - OPENAI_API_BASE
# - SUPABASE_URL
# - SUPABASE_KEY
# - SHOPIFY_STORE_URL
# - SHOPIFY_ACCESS_TOKEN

# Start backend server
uvicorn app.main:app --reload
```

✅ **Backend:** http://localhost:8000  
📚 **API Docs:** http://localhost:8000/docs

### 4. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure environment variables
cp .env.example .env.local
# Edit .env.local:
# NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1

# Start development server
npm run dev
```

✅ **Frontend:** http://localhost:3000

---

## 🔧 Configuration

### Backend Environment Variables

```env
# AI Configuration (Required)
OPENAI_API_KEY=your_api_key_here
OPENAI_API_BASE=https://api.kolosal.ai/v1
OPENAI_MODEL_NAME=gpt-4-vision-preview

# Database (Required)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_service_role_key

# Shopify Direct API (Required for publishing)
SHOPIFY_STORE_URL=your-store.myshopify.com
SHOPIFY_ACCESS_TOKEN=shpat_your_admin_api_token

# Google Search API (Optional - for market trends)
GOOGLE_SEARCH_API_KEY=your_google_api_key
GOOGLE_SEARCH_ENGINE_ID=your_search_engine_id
GOOGLE_SEARCH_ENABLED=true

# Server Configuration
CORS_ORIGINS=http://localhost:3000,http://localhost:3001
```

### Frontend Environment Variables

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

### Shopify Setup

1. **Create Shopify Store** (if you don't have one)
   - Go to https://www.shopify.com
   - Sign up for free trial

2. **Generate Admin API Access Token**
   - Shopify Admin → Settings → Apps and sales channels
   - Develop apps → Create an app
   - Configure Admin API scopes:
     - `read_products`
     - `write_products`
   - Install app → Reveal token
   - Copy Admin API access token

3. **Add to Backend .env**
   ```env
   SHOPIFY_STORE_URL=your-store.myshopify.com
   SHOPIFY_ACCESS_TOKEN=shpat_xxxxxxxxxxxxx
   ```

---

## 📁 Project Structure

```
ai-ecommerce-manager/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── routes/           # API route handlers
│   │   │   └── endpoints/        # Additional endpoints
│   │   ├── core/                 # Config, auth, database
│   │   ├── models/               # Database models
│   │   ├── repositories/         # Data access layer
│   │   ├── schemas/              # Pydantic schemas
│   │   └── services/             # Business logic
│   │       ├── ai_service.py     # AI multi-agent
│   │       ├── shopify_service.py # Shopify integration
│   │       └── google_search.py  # Market research
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── dashboard/        # Dashboard pages
│   │   │   │   ├── page.tsx      # Main dashboard
│   │   │   │   ├── products/     # Product management
│   │   │   │   ├── shops/        # Shop connections
│   │   │   │   └── trends/       # Market trends
│   │   │   ├── globals.css
│   │   │   └── layout.tsx
│   │   ├── components/           # React components
│   │   ├── services/             # API clients
│   │   └── types/                # TypeScript types
│   ├── package.json
│   └── .env.example
│
├── database/
│   ├── SUPABASE_MIGRATION.sql    # Database schema
│   └── FIX_DEMO_USER.sql         # Demo user setup
│
├── .gitignore
├── README.md
└── LICENSE
```

---

## 🔌 API Endpoints

### Products
```
POST   /api/v1/products/analyze      # AI analysis from image
POST   /api/v1/products              # Create product
GET    /api/v1/products              # List products
GET    /api/v1/products/{id}         # Get product detail
PATCH  /api/v1/products/{id}         # Update product
DELETE /api/v1/products/{id}         # Delete product
GET    /api/v1/products/health       # Health check
```

### Market Trends
```
POST   /api/v1/analyze/trends        # Analyze market trends
GET    /api/v1/trends/market         # Get trending products
POST   /api/v1/trends/refresh        # Force refresh trends
GET    /api/v1/trends/recommendations # Get recommendations
```

### Shopify Integration
```
GET    /api/v1/shops/shopify/status  # Check connection status
POST   /api/v1/publish/shopify       # Publish to Shopify
GET    /api/v1/publish/shopify/status # Check publish config
GET    /api/v1/publish/shopify/product/{id} # Get Shopify product
```

### AI Enrichment
```
POST   /api/v1/products/enhance      # AI enhancement
POST   /api/v1/enrichment/enrich     # Platform-specific enrichment
```

---

## 🎯 User Flow

### 1. Create Product (30 seconds)
```
Dashboard → New Product → Fill Form
↓
Name: "Sepatu Nike Air Max"
Description: "Sepatu olahraga berkualitas"
Price: Rp 500,000
Upload Image
↓
Click "Create Product"
↓
Auto-redirect to Product Detail Page
```

### 2. AI Enhancement (Optional - 20 seconds)
```
Product Detail Page → Click "Enhance with AI"
↓
AI analyzes image & description
↓
Results:
- ✅ Category detected
- ✅ Price suggested
- ✅ Specifications extracted
- ✅ Description enhanced
```

### 3. Publish to Shopify (10 seconds)
```
Product Detail Page
↓
Platform: Shopify (pre-selected) ✅
Shop: My Shopify Store (pre-selected) ✅
↓
Click "Publish to Shopify"
↓
Success! Product live on Shopify
```

### 4. View in Shopify Admin
```
Success Page → Click "View in Shopify Admin"
↓
Opens Shopify product page
↓
Product is live and ready to sell!
```

---

## 🧪 Testing

### Quick Test Script

```bash
# Run automated test
./QUICK_TEST.sh

# Expected output:
# ✅ Backend Health: OK
# ✅ Shopify Connection: Connected
# ✅ Test Product Published: Success
```

### Manual Testing

```bash
# 1. Health Check
curl http://localhost:8000/api/v1/products/health

# 2. Create Product
curl -X POST http://localhost:8000/api/v1/products \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Product",
    "price": 100000,
    "description": "Test description"
  }'

# 3. Publish to Shopify
curl -X POST http://localhost:8000/api/v1/publish/shopify \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Product",
    "description": "<p>Test description</p>",
    "price": 99000,
    "stock": 50
  }'
```

### Frontend Testing
1. Open http://localhost:3000
2. Create a new product
3. Verify Shopify is pre-selected
4. Publish to Shopify
5. Check product in Shopify Admin

---

## 📊 Features Showcase

### ✨ AI Vision Analysis
- Upload product image
- AI detects brand, model, condition
- Automatic category classification
- Confidence scoring

### 💰 Smart Pricing
- Real-time market research
- Competitor price analysis
- Price range suggestions
- Profit margin calculator

### 📈 Market Trends
- Trending products by category
- Viral product detection
- Growth potential scoring
- Target audience insights

### 🛒 Shopify Publishing
- One-click publish
- Automatic inventory sync
- Product variant support
- Image upload to Shopify

---

## 🎨 UI/UX Features

### Dark Mode
- Complete dark/light theme
- Smooth transitions
- Proper contrast ratios
- Eye-friendly colors

### Responsive Design
- Mobile-first approach
- Tablet optimization
- Desktop full features
- Touch-friendly controls

### User Experience
- Intuitive navigation
- Clear call-to-actions
- Real-time feedback
- Error handling with helpful messages

---

## 🔒 Security

### Environment Variables
- ✅ Never commit `.env` files
- ✅ Use `.env.example` as template
- ✅ Separate dev/prod configs
- ✅ API key rotation support

### API Security
- ✅ CORS configuration
- ✅ Input validation (Pydantic)
- ✅ Rate limiting ready
- ✅ Error sanitization

### Database Security
- ✅ Supabase Row Level Security
- ✅ Prepared statements
- ✅ Input sanitization
- ✅ Secure connections

---

## 📈 Performance

### Metrics
- **API Response Time:** < 2s (AI analysis)
- **Page Load Time:** < 1s (Next.js SSR)
- **Database Queries:** Optimized with indexes
- **Caching:** Market trends cached 24h
- **Error Rate:** < 1%

### Optimizations
- ✅ Database indexing
- ✅ Query optimization
- ✅ Image lazy loading
- ✅ Code splitting
- ✅ API response caching

---

## 🚀 Deployment

### Backend (Railway/Render)

```bash
# 1. Push to GitHub
git push origin main

# 2. Connect to Railway/Render
# 3. Set environment variables
# 4. Deploy!
```

### Frontend (Vercel)

```bash
# 1. Push to GitHub
git push origin main

# 2. Import to Vercel
# 3. Set NEXT_PUBLIC_API_URL
# 4. Deploy!
```

### Environment Variables (Production)

**Backend:**
- `OPENAI_API_KEY`
- `SUPABASE_URL`
- `SUPABASE_KEY`
- `SHOPIFY_STORE_URL`
- `SHOPIFY_ACCESS_TOKEN`

**Frontend:**
- `NEXT_PUBLIC_API_URL` (your backend URL)

---

## 🛠️ Development

### Code Quality
- ✅ Type hints (Python) & TypeScript
- ✅ Docstrings & comments
- ✅ Modular architecture
- ✅ Clear naming conventions
- ✅ Comprehensive error handling

### Best Practices
- ✅ Separation of concerns
- ✅ Repository pattern
- ✅ Dependency injection
- ✅ Clean code principles
- ✅ DRY (Don't Repeat Yourself)

### Git Workflow
```bash
# 1. Create feature branch
git checkout -b feature/new-feature

# 2. Make changes
git add .
git commit -m "feat: add new feature"

# 3. Push to GitHub
git push origin feature/new-feature

# 4. Create Pull Request
```

---

## 🐛 Troubleshooting

### Backend Issues

**Issue:** `ModuleNotFoundError`
```bash
# Solution: Activate virtual environment
source venv/bin/activate
pip install -r requirements.txt
```

**Issue:** Database connection failed
```bash
# Solution: Check Supabase credentials in .env
# Verify SUPABASE_URL and SUPABASE_KEY
```

### Frontend Issues

**Issue:** `Module not found`
```bash
# Solution: Reinstall dependencies
rm -rf node_modules package-lock.json
npm install
```

**Issue:** API calls failing
```bash
# Solution: Check NEXT_PUBLIC_API_URL in .env.local
# Ensure backend is running on correct port
```

### Shopify Issues

**Issue:** "Invalid Shopify token"
```bash
# Solution: Generate new Admin API Access Token
# Update SHOPIFY_ACCESS_TOKEN in backend .env
```

---

## 🌟 Unique Selling Points

1. **AI Multi-Agent System** - 4 specialized agents working together
2. **Real-time Market Intelligence** - Google Search API integration
3. **Shopify Direct API** - No OAuth complexity, instant publishing
4. **Production-Ready Code** - Clean architecture, type-safe
5. **Modern UI/UX** - Dark mode, responsive, intuitive
6. **Open Source** - No user authentication, instant access

---

## 📚 Documentation

- **API Documentation:** http://localhost:8000/docs (Swagger UI)
- **Database Schema:** `database/SUPABASE_MIGRATION.sql`
- **Environment Setup:** `.env.example` files
- **Deployment Guide:** See Deployment section above

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👥 Team

**Eukooyeh Tim** - Hackathon Project 2025

---

## 🙏 Acknowledgments

- [CrewAI](https://www.crewai.com/) - Multi-agent framework
- [Kolosal AI](https://kolosal.ai/) / [OpenAI](https://openai.com/) - LLM API
- [Shadcn/ui](https://ui.shadcn.com/) - Beautiful components
- [Next.js](https://nextjs.org/) - React framework
- [FastAPI](https://fastapi.tiangolo.com/) - Python web framework
- [Supabase](https://supabase.com/) - Database platform
- [TailwindCSS](https://tailwindcss.com/) - CSS framework

---

## 📞 Support

For issues and questions:
- **GitHub Issues:** [Create an issue](https://github.com/your-username/ai-ecommerce-manager/issues)
- **Email:** your-email@example.com

---

## 🎯 Roadmap

### Phase 1 (Current) ✅
- [x] AI Vision Analysis
- [x] Category Detection
- [x] Price Suggestions
- [x] Shopify Integration
- [x] Market Trends
- [x] Dark Mode

### Phase 2 (Planned)
- [ ] Additional marketplaces (Tokopedia, Bukalapak)
- [ ] Bulk operations
- [ ] Product analytics
- [ ] Price history tracking
- [ ] Competitor monitoring

### Phase 3 (Future)
- [ ] Mobile app
- [ ] Multi-language support
- [ ] Real-time updates (WebSocket)
- [ ] Advanced AI features
- [ ] Team collaboration

---

**Built with ❤️ for Hackathon 2025**

**⭐ Star this repo if you find it useful!**

---

## 📸 Screenshots

### Dashboard
![Dashboard](docs/screenshots/dashboard.png)

### Create Product
![Create Product](docs/screenshots/create-product.png)

### AI Analysis
![AI Analysis](docs/screenshots/ai-analysis.png)

### Shopify Publishing
![Shopify Publishing](docs/screenshots/shopify-publish.png)

### Market Trends
![Market Trends](docs/screenshots/market-trends.png)

---

**Ready to revolutionize your e-commerce product management? Let's get started!** 🚀
