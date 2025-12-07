-- ============================================
-- SaaS Database Schema for AI Product Listing
-- ============================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================
-- 1. USERS TABLE (Managed by Supabase Auth)
-- ============================================
-- Note: Supabase Auth automatically creates auth.users table
-- We extend it with a profiles table for additional user data

CREATE TABLE public.profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT UNIQUE NOT NULL,
    full_name TEXT,
    company_name TEXT,
    phone TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable Row Level Security
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;

-- RLS Policy: Users can only read/update their own profile
CREATE POLICY "Users can view own profile" 
    ON public.profiles FOR SELECT 
    USING (auth.uid() = id);

CREATE POLICY "Users can update own profile" 
    ON public.profiles FOR UPDATE 
    USING (auth.uid() = id);

-- ============================================
-- 2. OAUTH STATES (Temporary storage for OAuth flow)
-- ============================================
CREATE TABLE public.oauth_states (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    state TEXT NOT NULL UNIQUE,
    platform TEXT NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index for quick lookup
CREATE INDEX idx_oauth_states_state ON public.oauth_states(state);
CREATE INDEX idx_oauth_states_expires ON public.oauth_states(expires_at);

-- Auto-delete expired states (cleanup job)
-- In production, run this periodically
-- DELETE FROM public.oauth_states WHERE expires_at < NOW();

-- ============================================
-- 3. SHOP INTEGRATIONS (OAuth Tokens)
-- ============================================
CREATE TABLE public.shop_integrations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    
    -- Platform Info
    platform TEXT NOT NULL CHECK (platform IN ('shopee', 'tiktok_shop')),
    shop_id TEXT NOT NULL, -- External shop ID from marketplace
    shop_name TEXT,
    
    -- OAuth Credentials (ENCRYPTED in production!)
    access_token TEXT NOT NULL,
    refresh_token TEXT,
    token_expires_at TIMESTAMP WITH TIME ZONE,
    
    -- Shop Metadata
    shop_region TEXT, -- e.g., 'ID', 'SG', 'MY'
    shop_status TEXT DEFAULT 'active' CHECK (shop_status IN ('active', 'expired', 'revoked')),
    
    -- Timestamps
    connected_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_synced_at TIMESTAMP WITH TIME ZONE,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Unique constraint: One shop per platform per user
    UNIQUE(user_id, platform, shop_id)
);

-- Indexes for performance
CREATE INDEX idx_shop_integrations_user_id ON public.shop_integrations(user_id);
CREATE INDEX idx_shop_integrations_platform ON public.shop_integrations(platform);

-- RLS Policies
ALTER TABLE public.shop_integrations ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can manage own shop integrations" 
    ON public.shop_integrations 
    FOR ALL 
    USING (auth.uid() = user_id);

-- ============================================
-- 4. GLOBAL SETTINGS (Warehouse, Logistics)
-- ============================================
CREATE TABLE public.user_settings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    
    -- Warehouse/Shipping Address
    warehouse_name TEXT,
    warehouse_address TEXT,
    warehouse_city TEXT,
    warehouse_province TEXT,
    warehouse_postal_code TEXT,
    warehouse_country TEXT DEFAULT 'ID',
    
    -- Default Logistics (JSON for flexibility)
    default_logistics JSONB DEFAULT '[]'::jsonb,
    -- Example: [{"platform": "shopee", "logistic_id": 123, "logistic_name": "JNE"}]
    
    -- Default Product Settings
    default_stock_quantity INTEGER DEFAULT 100,
    default_condition TEXT DEFAULT 'new' CHECK (default_condition IN ('new', 'used')),
    default_weight_kg DECIMAL(10,2) DEFAULT 0.5,
    
    -- AI Preferences
    ai_model_preference TEXT DEFAULT 'gpt-4', -- or 'claude-3-opus'
    auto_publish BOOLEAN DEFAULT false, -- Auto-publish after AI generation
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- One settings record per user
    UNIQUE(user_id)
);

-- RLS Policies
ALTER TABLE public.user_settings ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can manage own settings" 
    ON public.user_settings 
    FOR ALL 
    USING (auth.uid() = user_id);

-- ============================================
-- 5. PRODUCTS (Universal Product Model)
-- ============================================
CREATE TABLE public.products (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    
    -- Universal Product Data (Simple Input from User)
    name TEXT NOT NULL,
    description TEXT,
    price DECIMAL(12,2) NOT NULL CHECK (price >= 0),
    stock_quantity INTEGER DEFAULT 0 CHECK (stock_quantity >= 0),
    
    -- Images (Array of URLs)
    images TEXT[] DEFAULT ARRAY[]::TEXT[],
    
    -- Product Metadata
    sku TEXT, -- Optional SKU
    weight_kg DECIMAL(10,2),
    condition TEXT DEFAULT 'new' CHECK (condition IN ('new', 'used')),
    
    -- AI Enrichment Status
    ai_enriched BOOLEAN DEFAULT false,
    ai_enriched_at TIMESTAMP WITH TIME ZONE,
    ai_model_used TEXT, -- e.g., 'gpt-4-turbo'
    
    -- Status
    status TEXT DEFAULT 'draft' CHECK (status IN ('draft', 'ready', 'published', 'archived')),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_products_user_id ON public.products(user_id);
CREATE INDEX idx_products_status ON public.products(status);

-- RLS Policies
ALTER TABLE public.products ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can manage own products" 
    ON public.products 
    FOR ALL 
    USING (auth.uid() = user_id);

-- ============================================
-- 6. PRODUCT LISTINGS (Marketplace-Specific Data)
-- ============================================
-- This table stores the AI-generated, platform-specific data
CREATE TABLE public.product_listings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    product_id UUID NOT NULL REFERENCES public.products(id) ON DELETE CASCADE,
    shop_integration_id UUID NOT NULL REFERENCES public.shop_integrations(id) ON DELETE CASCADE,
    
    -- Platform Info
    platform TEXT NOT NULL CHECK (platform IN ('shopee', 'tiktok_shop')),
    
    -- External IDs (after successful publish)
    external_product_id TEXT, -- Shopee item_id or TikTok product_id
    external_listing_url TEXT,
    
    -- AI-Generated Platform-Specific Data (Full JSON Payload)
    platform_data JSONB NOT NULL,
    -- Example for Shopee:
    -- {
    --   "category_id": 100017,
    --   "name": "Sepatu Sneakers Pria...",
    --   "description": "<p>Enhanced description...</p>",
    --   "price": 250000,
    --   "stock": 100,
    --   "images": [...],
    --   "attributes": [{"attribute_id": 123, "value": "No Brand"}],
    --   "logistic_info": [...]
    -- }
    
    -- Publishing Status
    publish_status TEXT DEFAULT 'pending' CHECK (
        publish_status IN ('pending', 'publishing', 'published', 'failed', 'updated')
    ),
    publish_error TEXT, -- Error message if failed
    
    -- Timestamps
    published_at TIMESTAMP WITH TIME ZONE,
    last_synced_at TIMESTAMP WITH TIME ZONE,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Unique: One product can only be listed once per shop
    UNIQUE(product_id, shop_integration_id)
);

-- Indexes
CREATE INDEX idx_product_listings_product_id ON public.product_listings(product_id);
CREATE INDEX idx_product_listings_shop_id ON public.product_listings(shop_integration_id);
CREATE INDEX idx_product_listings_platform ON public.product_listings(platform);
CREATE INDEX idx_product_listings_status ON public.product_listings(publish_status);

-- RLS Policies (Users can only access listings for their own products)
ALTER TABLE public.product_listings ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can manage own product listings" 
    ON public.product_listings 
    FOR ALL 
    USING (
        EXISTS (
            SELECT 1 FROM public.products 
            WHERE products.id = product_listings.product_id 
            AND products.user_id = auth.uid()
        )
    );

-- ============================================
-- 7. AI GENERATION LOGS (Audit Trail)
-- ============================================
CREATE TABLE public.ai_generation_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    product_id UUID REFERENCES public.products(id) ON DELETE SET NULL,
    
    -- AI Request Details
    ai_model TEXT NOT NULL, -- 'gpt-4', 'claude-3-opus'
    target_platform TEXT NOT NULL,
    
    -- Input/Output
    input_data JSONB NOT NULL, -- Simple user input
    output_data JSONB, -- AI-generated platform data
    
    -- Performance Metrics
    tokens_used INTEGER,
    processing_time_ms INTEGER,
    cost_usd DECIMAL(10,4),
    
    -- Status
    status TEXT DEFAULT 'processing' CHECK (
        status IN ('processing', 'success', 'failed')
    ),
    error_message TEXT,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_ai_logs_user_id ON public.ai_generation_logs(user_id);
CREATE INDEX idx_ai_logs_product_id ON public.ai_generation_logs(product_id);
CREATE INDEX idx_ai_logs_created_at ON public.ai_generation_logs(created_at);

-- RLS Policies
ALTER TABLE public.ai_generation_logs ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own AI logs" 
    ON public.ai_generation_logs 
    FOR SELECT 
    USING (auth.uid() = user_id);

-- ============================================
-- 8. TRIGGERS (Auto-update timestamps)
-- ============================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply to all tables with updated_at
CREATE TRIGGER update_profiles_updated_at BEFORE UPDATE ON public.profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_shop_integrations_updated_at BEFORE UPDATE ON public.shop_integrations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_settings_updated_at BEFORE UPDATE ON public.user_settings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_products_updated_at BEFORE UPDATE ON public.products
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_product_listings_updated_at BEFORE UPDATE ON public.product_listings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- 9. INITIAL SEED DATA (Optional)
-- ============================================
-- You can add default logistics data, common categories, etc.

COMMENT ON TABLE public.products IS 'Universal product model - simple user input';
COMMENT ON TABLE public.product_listings IS 'Platform-specific AI-enriched data for each marketplace';
COMMENT ON TABLE public.shop_integrations IS 'OAuth tokens for connected marketplace shops';
COMMENT ON TABLE public.user_settings IS 'Global settings for warehouse, logistics, and AI preferences';
