-- ============================================
-- FIX: Create Demo User for Testing
-- Run this in Supabase SQL Editor
-- ============================================

-- Step 1: Remove foreign key constraint from profiles (temporary)
ALTER TABLE public.profiles DROP CONSTRAINT IF EXISTS profiles_id_fkey;

-- Step 2: Create demo user in profiles table
INSERT INTO public.profiles (id, email, full_name, company_name)
VALUES (
    '00000000-0000-0000-0000-000000000001',
    'demo@aiproduct.com',
    'Demo User',
    'AI Product Demo'
)
ON CONFLICT (id) DO UPDATE SET
    email = EXCLUDED.email,
    full_name = EXCLUDED.full_name,
    company_name = EXCLUDED.company_name;

-- Step 3: Create user settings for demo user
INSERT INTO public.user_settings (
    user_id,
    warehouse_city,
    warehouse_country,
    default_logistics_provider,
    default_stock_quantity,
    default_condition,
    default_weight_kg,
    ai_auto_enrich,
    auto_publish
)
VALUES (
    '00000000-0000-0000-0000-000000000001',
    'Jakarta',
    'ID',
    'JNE',
    100,
    'new',
    0.5,
    true,
    false
)
ON CONFLICT (user_id) DO NOTHING;

-- Step 4: Add foreign key constraint back (but make it optional)
-- We'll keep it removed for demo mode to work without auth

-- ============================================
-- DONE! Demo user created successfully
-- ============================================

SELECT 'Demo user created successfully!' as status;
