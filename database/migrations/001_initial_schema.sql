-- ============================================
-- AI PRODUCT LISTING SAAS - DATABASE SCHEMA
-- Run this in Supabase SQL Editor
-- ============================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================
-- 1. PROFILES TABLE
-- ============================================
CREATE TABLE public.profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT UNIQUE NOT NULL,
    phone TEXT,
    full_name TEXT,
    company_name TEXT,
    avatar_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- RLS Policies
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Enable all for service role"
    ON public.profiles FOR ALL
    USING (true)
    WITH CHECK (true);

-- ============================================
-- 2. OAUTH STATES TABLE
-- ============================================
CREATE TABLE public.oauth_states (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    state_token TEXT UNIQUE NOT NULL,
    platform TEXT NOT NULL CHECK (platform IN ('shopee', 'tiktok_shop')),
    redirect_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE DEFAULT (NOW() + INTERVAL '10 minutes')
);

CREATE INDEX idx_oauth_states_token ON public.oauth_states(state_token);
CREATE INDEX idx_oauth_states_user ON public.oauth_states(user_id);

ALTER TABLE public.oauth_states ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Enable all for service role"
    ON public.oauth_states FOR ALL
    USING (true)
    WITH CHECK (true);

-- ============================================
-- 3. SHOP INTEGRATIONS TABLE
-- ============================================
CREATE TABLE public.shop_integrations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    platform TEXT NOT NULL CHECK (platform IN ('shopee', 'tiktok_shop')),
    shop_id TEXT NOT NULL,
    shop_name TEXT,
    access_token TEXT NOT NULL,
    refresh_token TEXT,
    token_expires_at TIMESTAMP WITH TIME ZONE,
    shop_status TEXT DEFAULT 'active' CHECK (shop_status IN ('active', 'expired', 'revoked')),
    connected_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_sync_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, platform, shop_id)
);

CREATE INDEX idx_shop_integrations_user ON public.shop_integrations(user_id);
CREATE INDEX idx_shop_integrations_platform ON public.shop_integrations(platform);

ALTER TABLE public.shop_integrations ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Enable all for service role"
    ON public.shop_integrations FOR ALL
    USING (true)
    WITH CHECK (true);

-- ============================================
-- 4. USER SETTINGS TABLE
-- ============================================
CREATE TABLE public.user_settings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID UNIQUE NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    warehouse_city TEXT DEFAULT 'Jakarta',
    warehouse_country TEXT DEFAULT 'ID',
    default_logistics_provider TEXT DEFAULT 'JNE',
    default_stock_quantity INTEGER DEFAULT 100,
    default_condition TEXT DEFAULT 'new',
    default_weight_kg DECIMAL(10,2) DEFAULT 0.5,
    ai_auto_enrich BOOLEAN DEFAULT true,
    ai_model_preference TEXT DEFAULT 'gpt-4-turbo',
    auto_publish BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_user_settings_user ON public.user_settings(user_id);

ALTER TABLE public.user_settings ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Enable all for service role"
    ON public.user_settings FOR ALL
    USING (true)
    WITH CHECK (true);

-- ============================================
-- 5. PRODUCTS TABLE (Universal Model)
-- ============================================
CREATE TABLE public.products (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    description TEXT,
    price DECIMAL(12,2) NOT NULL CHECK (price >= 0),
    stock_quantity INTEGER DEFAULT 0 CHECK (stock_quantity >= 0),
    images TEXT[] DEFAULT ARRAY[]::TEXT[],
    sku TEXT,
    weight_kg DECIMAL(10,2),
    condition TEXT DEFAULT 'new' CHECK (condition IN ('new', 'used')),
    ai_enriched BOOLEAN DEFAULT false,
    ai_enriched_at TIMESTAMP WITH TIME ZONE,
    ai_model_used TEXT,
    status TEXT DEFAULT 'draft' CHECK (status IN ('draft', 'ready', 'published', 'archived')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_products_user_id ON public.products(user_id);
CREATE INDEX idx_products_status ON public.products(status);

ALTER TABLE public.products ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Enable all for service role"
    ON public.products FOR ALL
    USING (true)
    WITH CHECK (true);

-- ============================================
-- 6. PRODUCT LISTINGS TABLE
-- ============================================
CREATE TABLE public.product_listings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    product_id UUID NOT NULL REFERENCES public.products(id) ON DELETE CASCADE,
    shop_integration_id UUID NOT NULL REFERENCES public.shop_integrations(id) ON DELETE CASCADE,
    platform TEXT NOT NULL CHECK (platform IN ('shopee', 'tiktok_shop')),
    external_product_id TEXT,
    external_listing_url TEXT,
    platform_data JSONB NOT NULL,
    publish_status TEXT DEFAULT 'pending' CHECK (
        publish_status IN ('pending', 'publishing', 'published', 'failed', 'updated')
    ),
    publish_error TEXT,
    published_at TIMESTAMP WITH TIME ZONE,
    last_synced_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(product_id, shop_integration_id)
);

CREATE INDEX idx_product_listings_product_id ON public.product_listings(product_id);
CREATE INDEX idx_product_listings_shop_id ON public.product_listings(shop_integration_id);
CREATE INDEX idx_product_listings_platform ON public.product_listings(platform);
CREATE INDEX idx_product_listings_status ON public.product_listings(publish_status);

ALTER TABLE public.product_listings ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Enable all for service role"
    ON public.product_listings FOR ALL
    USING (true)
    WITH CHECK (true);

-- ============================================
-- 7. AI GENERATION LOGS TABLE
-- ============================================
CREATE TABLE public.ai_generation_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    product_id UUID REFERENCES public.products(id) ON DELETE SET NULL,
    ai_model TEXT NOT NULL,
    target_platform TEXT NOT NULL,
    input_data JSONB NOT NULL,
    output_data JSONB,
    tokens_used INTEGER,
    processing_time_ms INTEGER,
    cost_usd DECIMAL(10,4),
    status TEXT DEFAULT 'processing' CHECK (
        status IN ('processing', 'success', 'failed')
    ),
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_ai_logs_user_id ON public.ai_generation_logs(user_id);
CREATE INDEX idx_ai_logs_product_id ON public.ai_generation_logs(product_id);
CREATE INDEX idx_ai_logs_created_at ON public.ai_generation_logs(created_at);

ALTER TABLE public.ai_generation_logs ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Enable all for service role"
    ON public.ai_generation_logs FOR ALL
    USING (true)
    WITH CHECK (true);

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

CREATE TRIGGER update_profiles_updated_at
    BEFORE UPDATE ON public.profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_shop_integrations_updated_at
    BEFORE UPDATE ON public.shop_integrations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_settings_updated_at
    BEFORE UPDATE ON public.user_settings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_products_updated_at
    BEFORE UPDATE ON public.products
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_product_listings_updated_at
    BEFORE UPDATE ON public.product_listings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- 9. AUTO-CREATE PROFILE ON SIGNUP
-- ============================================
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.profiles (id, email, full_name)
    VALUES (
        NEW.id,
        NEW.email,
        COALESCE(NEW.raw_user_meta_data->>'full_name', '')
    );
    
    INSERT INTO public.user_settings (user_id)
    VALUES (NEW.id);
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- ============================================
-- DONE! All tables created successfully
-- ============================================
