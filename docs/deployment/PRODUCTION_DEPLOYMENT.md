# 🚀 Production Deployment Guide

## 📋 Pre-Deployment Checklist

### ✅ Yang Sudah Siap
- [x] Backend API (FastAPI)
- [x] Frontend (Next.js 14)
- [x] Database (Supabase)
- [x] AI Integration (Kolosal AI)
- [x] No User Auth (Open Source Mode)
- [x] Dark Mode Support

### ⚠️ Yang Perlu Diisi

---

## 🔑 Environment Variables yang WAJIB Diisi

### 1. **Backend (.env)** - 39 lines

#### ✅ Sudah Terisi (Jangan Ubah):
```env
# AI Configuration
OPENAI_API_KEY="kol_eyJhbGc..." # ✅ Kolosal AI
OPENAI_API_BASE="https://api.kolosal.ai/v1" # ✅
OPENAI_MODEL_NAME="openai/Claude Sonnet 4.5" # ✅

# Database
SUPABASE_URL=https://wglyahwtobonxjcgvltk.supabase.co # ✅
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9... # ✅
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9... # ✅

# Google Search (Optional - untuk market trends)
SERPER_API_KEY="19e82cc163b38c63efc2adb8514bfee67aef5530" # ✅

# App Settings
USE_MOCK_AI=false # ✅ FIXED - was causing slow loading!
CORS_ORIGINS=http://localhost:3000,http://localhost:3001 # ✅
```

#### ⚠️ PERLU DIISI (Shopify OAuth):

**Option A: Skip Shopify (Untuk Demo)**
```env
SHOPIFY_API_KEY=""  # Leave empty
SHOPIFY_API_SECRET=""  # Leave empty
```
**Catatan:** Shopify integration akan disabled, tapi sistem tetap jalan normal.

**Option B: Enable Shopify (Untuk Production)**
```env
SHOPIFY_API_KEY="your_shopify_api_key_here"
SHOPIFY_API_SECRET="your_shopify_api_secret_here"
SHOPIFY_REDIRECT_URL="https://your-backend-domain.com/api/v1/shops/callback/shopify"
```

**Cara dapat Shopify API Keys:**
1. Go to: https://partners.shopify.com
2. Sign up for Partner account (FREE)
3. Click "Apps" → "Create app"
4. Choose "Custom app"
5. Copy **API Key** dan **API Secret Key**
6. Paste ke `.env`

#### ⚠️ PERLU DIISI (Google Search - Optional):
```env
GOOGLE_SEARCH_API_KEY=""  # Optional - untuk market trends
GOOGLE_SEARCH_ENGINE_ID=""  # Optional
GOOGLE_SEARCH_ENABLED=false  # Set true jika mau enable
```

**Cara dapat Google Search API:**
1. Go to: https://console.cloud.google.com
2. Create project
3. Enable "Custom Search API"
4. Create credentials (API Key)
5. Create Custom Search Engine: https://programmablesearchengine.google.com

---

### 2. **Frontend (.env.local)** - 1 line

#### Untuk Development:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

#### Untuk Production:
```env
NEXT_PUBLIC_API_URL=https://your-backend-domain.com/api/v1
```

**Ganti `your-backend-domain.com` dengan domain backend kamu!**

---

## 🗄️ Database Setup (Supabase)

### ✅ Sudah Terisi:
- Database URL
- Service Role Key
- Anon Key

### ⚠️ WAJIB RUN SQL Scripts:

#### 1. **SUPABASE_MIGRATION.sql** (Create Tables)
```sql
-- Run di Supabase SQL Editor
-- File: SUPABASE_MIGRATION.sql
-- Creates: profiles, oauth_states, shop_integrations, products, etc.
```

#### 2. **FIX_DEMO_USER.sql** (Create Demo User)
```sql
-- Run di Supabase SQL Editor
-- File: FIX_DEMO_USER.sql
-- Creates demo user: 00000000-0000-0000-0000-000000000001
```

#### 3. **FIX_SHOPIFY_CONSTRAINT.sql** (Fix OAuth)
```sql
-- Run di Supabase SQL Editor
-- File: FIX_SHOPIFY_CONSTRAINT.sql
-- Allows 'shopify' platform in oauth_states
```

**Urutan Eksekusi:**
1. SUPABASE_MIGRATION.sql (pertama)
2. FIX_DEMO_USER.sql (kedua)
3. FIX_SHOPIFY_CONSTRAINT.sql (ketiga)

---

## 🌐 Deployment Options

### Option 1: Vercel (Frontend) + Railway (Backend)

#### Frontend (Vercel):
```bash
# 1. Install Vercel CLI
npm i -g vercel

# 2. Deploy
cd frontend
vercel

# 3. Set environment variable di Vercel Dashboard:
NEXT_PUBLIC_API_URL=https://your-backend-url.railway.app/api/v1
```

#### Backend (Railway):
```bash
# 1. Go to: https://railway.app
# 2. Create new project
# 3. Connect GitHub repo
# 4. Select /backend folder
# 5. Add environment variables (copy dari .env)
# 6. Deploy!
```

**Railway Environment Variables:**
- Copy semua dari `backend/.env`
- Update `CORS_ORIGINS` dengan Vercel URL
- Update `SHOPIFY_REDIRECT_URL` dengan Railway URL

---

### Option 2: Vercel (Frontend) + Render (Backend)

#### Frontend (Vercel):
Same as above

#### Backend (Render):
```bash
# 1. Go to: https://render.com
# 2. New → Web Service
# 3. Connect GitHub repo
# 4. Root Directory: /backend
# 5. Build Command: pip install -r requirements.txt
# 6. Start Command: uvicorn app.main:app --host 0.0.0.0 --port $PORT
# 7. Add environment variables
# 8. Deploy!
```

---

### Option 3: Docker (Self-Hosted)

#### Backend Dockerfile:
```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Frontend Dockerfile:
```dockerfile
FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

CMD ["npm", "start"]
```

#### Docker Compose:
```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    env_file:
      - ./backend/.env
    
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://backend:8000/api/v1
    depends_on:
      - backend
```

---

## 🔒 Security Checklist

### ✅ Before Deployment:

- [ ] **Never commit `.env` files** (check .gitignore)
- [ ] **Use HTTPS** for production URLs
- [ ] **Update CORS_ORIGINS** dengan production domain
- [ ] **Keep Supabase Service Role Key secret**
- [ ] **Use environment variables** untuk semua credentials
- [ ] **Enable RLS** di Supabase (sudah enabled)
- [ ] **Test all endpoints** sebelum deploy

---

## 🧪 Testing Before Production

### 1. Local Testing:
```bash
# Backend
cd backend
source venv/bin/activate
uvicorn app.main:app --reload

# Frontend
cd frontend
npm run dev

# Test:
curl http://localhost:8000/api/v1/products/health
```

### 2. Production Testing:
```bash
# Test backend
curl https://your-backend-url.com/api/v1/products/health

# Test frontend
# Open browser: https://your-frontend-url.com
```

---

## 📊 Performance Optimization

### ✅ Sudah Dioptimasi:

1. **USE_MOCK_AI=false** - No artificial delays
2. **Next.js 14** - Automatic optimization
3. **Database indexes** - Fast queries
4. **Caching** - Market trends cached 24h
5. **Lazy loading** - Components load on demand

### 🚀 Additional Tips:

- Use CDN untuk static assets
- Enable gzip compression
- Monitor dengan Sentry/LogRocket
- Use Redis untuk caching (optional)

---

## 🐛 Common Issues & Solutions

### Issue 1: "Shopify API credentials not configured"
**Solution:** Add `SHOPIFY_API_KEY` to backend `.env` atau leave empty untuk skip

### Issue 2: "oauth_states constraint violation"
**Solution:** Run `FIX_SHOPIFY_CONSTRAINT.sql` di Supabase

### Issue 3: "CORS error"
**Solution:** Update `CORS_ORIGINS` di backend `.env` dengan frontend URL

### Issue 4: "Slow loading"
**Solution:** Set `USE_MOCK_AI=false` di backend `.env`

### Issue 5: "Database connection error"
**Solution:** Check Supabase credentials di `.env`

---

## 📝 Deployment Summary

### Minimum Required (Demo Mode):
```env
# Backend
✅ OPENAI_API_KEY (Kolosal AI)
✅ SUPABASE_URL
✅ SUPABASE_KEY
✅ USE_MOCK_AI=false
⚠️ SHOPIFY_API_KEY="" (empty = disabled)

# Frontend
✅ NEXT_PUBLIC_API_URL

# Database
✅ Run 3 SQL scripts
```

### Full Production:
```env
# Backend
✅ All above
✅ SHOPIFY_API_KEY (from Shopify Partners)
✅ SHOPIFY_API_SECRET
✅ GOOGLE_SEARCH_API_KEY (optional)
✅ Update CORS_ORIGINS
✅ Update SHOPIFY_REDIRECT_URL

# Frontend
✅ NEXT_PUBLIC_API_URL (production URL)

# Database
✅ Run 3 SQL scripts
✅ Verify RLS policies
```

---

## 🎯 Quick Deploy Commands

### Vercel (Frontend):
```bash
cd frontend
vercel --prod
```

### Railway (Backend):
```bash
# Via Railway Dashboard
# 1. Connect GitHub
# 2. Select repo
# 3. Add env vars
# 4. Deploy
```

---

## ✅ Post-Deployment Checklist

- [ ] Frontend accessible via HTTPS
- [ ] Backend API responding
- [ ] Database connected
- [ ] AI analysis working
- [ ] Shopify OAuth working (if enabled)
- [ ] Dark mode working
- [ ] Mobile responsive
- [ ] No console errors
- [ ] Performance acceptable (<2s load)

---

## 📞 Support

**Issues?**
- Check logs di deployment platform
- Verify environment variables
- Test API endpoints
- Check Supabase logs

**Ready to deploy!** 🚀

---

**Built with ❤️ by Eukooyeh Tim**
