# 🛠️ Panduan Implementasi Lengkap Shopify API

## 📊 Status Saat Ini

### ✅ Yang Sudah Ada
1. **Environment Variables** - Sudah dikonfigurasi di `.env`
2. **OAuth Endpoints** - Structure sudah dibuat
3. **Database Schema** - Tables sudah ready
4. **CSRF Protection** - State token sudah diimplementasi

### ⚠️ Yang Masih TODO (Untuk Production)
1. **HMAC Verification** - Belum diimplementasi
2. **Real Shopify API Calls** - Masih pakai mock data
3. **Token Refresh** - Belum ada mechanism
4. **Error Handling** - Perlu diperkuat

---

## 🚀 Quick Start (Testing Mode)

### 1. Start Backend
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload
```

### 2. Verify Configuration
```bash
# Run test script
python test_shopify_connection.py
```

Expected output:
```
✅ SHOPIFY_API_KEY: ********** (set)
✅ SHOPIFY_API_SECRET: ********** (set)
✅ SHOPIFY_REDIRECT_URL: ********** (set)
✅ OAuth URL generated successfully
```

### 3. Test API Endpoints
```bash
# Health check
curl http://localhost:8000/

# Test OAuth init (akan error karena butuh auth, tapi endpoint ada)
curl http://localhost:8000/api/v1/shops/connect/shopify
```

---

## 🔧 Implementasi Real Shopify API (Optional)

Jika kamu mau implement real Shopify API calls (bukan mock), ikuti langkah ini:

### Step 1: Install Dependencies
```bash
# Sudah ada di requirements.txt
pip install httpx  # Untuk async HTTP calls
```

### Step 2: Update shopify.py - Add HMAC Verification

Tambahkan function ini di `backend/app/api/routes/shopify.py`:

```python
import hmac
import hashlib
from urllib.parse import urlencode

def verify_shopify_hmac(params: dict, hmac_to_verify: str, secret: str) -> bool:
    """
    Verify Shopify HMAC signature.
    
    Args:
        params: Query parameters dari callback (tanpa hmac)
        hmac_to_verify: HMAC signature dari Shopify
        secret: SHOPIFY_API_SECRET
    
    Returns:
        True jika valid, False jika tidak
    """
    # Remove hmac from params
    params_copy = {k: v for k, v in params.items() if k != 'hmac'}
    
    # Sort and encode
    encoded_params = urlencode(sorted(params_copy.items()))
    
    # Compute HMAC
    computed_hmac = hmac.new(
        secret.encode('utf-8'),
        encoded_params.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    # Compare
    return hmac.compare_digest(computed_hmac, hmac_to_verify)
```

### Step 3: Update Callback Handler - Exchange Code for Token

Replace mock token dengan real API call:

```python
import httpx

# Di dalam shopify_oauth_callback function, replace line 177-187:

# 3. Exchange code for access_token
shopify_api_key = os.getenv("SHOPIFY_API_KEY")
shopify_api_secret = os.getenv("SHOPIFY_API_SECRET")

# Verify HMAC first
params = {
    "code": code,
    "shop": shop,
    "state": state,
    "timestamp": request.query_params.get("timestamp", "")
}
if not verify_shopify_hmac(params, hmac, shopify_api_secret):
    raise HTTPException(status_code=400, detail="Invalid HMAC signature")

# Exchange code for access token
async with httpx.AsyncClient() as client:
    token_response = await client.post(
        f"https://{shop}/admin/oauth/access_token",
        json={
            "client_id": shopify_api_key,
            "client_secret": shopify_api_secret,
            "code": code
        }
    )
    
    if token_response.status_code != 200:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to get access token: {token_response.text}"
        )
    
    token_data = token_response.json()
    access_token = token_data["access_token"]

# 4. Get shop info
async with httpx.AsyncClient() as client:
    shop_response = await client.get(
        f"https://{shop}/admin/api/2024-01/shop.json",
        headers={"X-Shopify-Access-Token": access_token}
    )
    
    if shop_response.status_code == 200:
        shop_info = shop_response.json()["shop"]
        shop_name = shop_info.get("name", shop.replace(".myshopify.com", "").title())
    else:
        shop_name = shop.replace(".myshopify.com", "").title()
```

---

## 🧪 Testing Flow

### Mode 1: Mock Testing (Current)
Saat ini code pakai mock data, jadi bisa test tanpa real Shopify store.

**Pros:**
- ✅ Tidak perlu Shopify store
- ✅ Cepat untuk development
- ✅ Tidak ada rate limiting

**Cons:**
- ❌ Tidak test real API
- ❌ Tidak dapat real shop data

### Mode 2: Real Shopify Testing

**Requirements:**
1. Shopify Partner account
2. Development store (gratis dari Partner Dashboard)
3. App credentials (API Key & Secret)

**Steps:**
1. Create development store di Partner Dashboard
2. Install app ke development store
3. Test OAuth flow dengan real store
4. Verify data tersimpan dengan benar

---

## 📝 Frontend Integration

### Update Shop Connection Page

File: `frontend/src/app/dashboard/shops/page.tsx`

Add shop domain input:

```typescript
const [shopDomain, setShopDomain] = useState('');

const handleConnectShopify = async () => {
  try {
    // Get OAuth URL from backend
    const response = await fetch(
      `${API_URL}/shops/connect/shopify?shop=${shopDomain}`
    );
    const data = await response.json();
    
    // Redirect to Shopify
    window.location.href = data.authorization_url;
  } catch (error) {
    console.error('Failed to connect:', error);
  }
};

// In JSX:
<input
  type="text"
  placeholder="your-store.myshopify.com"
  value={shopDomain}
  onChange={(e) => setShopDomain(e.target.value)}
/>
<button onClick={handleConnectShopify}>
  Connect Shopify
</button>
```

---

## 🔐 Security Checklist

### Development
- [x] State token untuk CSRF protection
- [x] Access token encrypted di database
- [x] OAuth state expires (10 minutes)
- [ ] HMAC verification (TODO untuk production)

### Production
- [ ] HTTPS enabled (required by Shopify)
- [ ] HMAC verification implemented
- [ ] Rate limiting
- [ ] Token refresh mechanism
- [ ] Webhook signature verification
- [ ] IP whitelist (optional)

---

## 🐛 Common Issues & Solutions

### Issue 1: "Invalid state parameter"
**Cause:** State token expired atau tidak ditemukan  
**Solution:** Ulangi OAuth flow dari awal

### Issue 2: "Shopify API credentials not configured"
**Cause:** `.env` tidak ter-load atau credentials kosong  
**Solution:**
```bash
# Check .env file
cat backend/.env | grep SHOPIFY

# Restart backend
uvicorn app.main:app --reload
```

### Issue 3: "Backend is NOT running"
**Cause:** Backend server belum di-start  
**Solution:**
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload
```

### Issue 4: Database Connection Error
**Cause:** Supabase credentials salah atau internet issue  
**Solution:**
```bash
# Test Supabase connection
python -c "from app.core.database import get_db; print('OK')"
```

### Issue 5: CORS Error di Frontend
**Cause:** Frontend URL tidak ada di CORS_ORIGINS  
**Solution:**
```env
# Update .env
CORS_ORIGINS=http://localhost:3000,http://localhost:3001
```

---

## 📊 Database Schema Reference

### shop_integrations Table
```sql
CREATE TABLE shop_integrations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id),
    platform TEXT NOT NULL,  -- 'shopify', 'tokopedia', etc
    shop_id TEXT NOT NULL,   -- Shop domain or ID
    shop_name TEXT,
    access_token TEXT NOT NULL,  -- Encrypted
    refresh_token TEXT,
    token_expires_at TIMESTAMP WITH TIME ZONE,
    shop_region TEXT,
    shop_status TEXT DEFAULT 'active',
    connected_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_synced_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, platform, shop_id)
);
```

### oauth_states Table
```sql
CREATE TABLE oauth_states (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    state_token TEXT NOT NULL UNIQUE,
    platform TEXT NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

---

## 🎯 Next Actions

### Untuk Testing (Sekarang)
1. ✅ Run test script: `python test_shopify_connection.py`
2. ⏳ Start backend: `uvicorn app.main:app --reload`
3. ⏳ Start frontend: `npm run dev`
4. ⏳ Test OAuth flow di browser

### Untuk Production (Nanti)
1. ⏳ Implement HMAC verification
2. ⏳ Implement real Shopify API calls
3. ⏳ Add token refresh mechanism
4. ⏳ Setup HTTPS
5. ⏳ Update redirect URL di Shopify Partner Dashboard
6. ⏳ Add webhook handlers

---

## 📞 Resources

### Shopify Documentation
- **OAuth Guide:** https://shopify.dev/docs/apps/auth/oauth
- **Access Tokens:** https://shopify.dev/docs/apps/auth/oauth/access-tokens
- **API Reference:** https://shopify.dev/docs/api/admin-rest
- **Webhooks:** https://shopify.dev/docs/apps/webhooks

### Partner Dashboard
- **URL:** https://partners.shopify.com
- **Create App:** Partners > Apps > Create app
- **Development Stores:** Partners > Stores > Add store

### Testing Tools
- **Postman Collection:** Available di Shopify docs
- **Shopify CLI:** `npm install -g @shopify/cli`

---

## ✅ Summary

**Current Status:** READY FOR TESTING ✅

**What Works:**
- ✅ Environment variables configured
- ✅ OAuth flow structure ready
- ✅ Database schema ready
- ✅ Mock implementation working

**What's Needed for Production:**
- ⏳ HMAC verification
- ⏳ Real API calls
- ⏳ HTTPS setup
- ⏳ Token refresh

**Estimated Time:**
- Testing: 10-15 minutes
- Production implementation: 2-3 hours

---

**Last Updated:** 7 Desember 2024, 19:55 WIB
