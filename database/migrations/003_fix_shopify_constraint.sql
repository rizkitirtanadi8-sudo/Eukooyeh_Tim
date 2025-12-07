-- ============================================
-- FIX: Update oauth_states constraint to allow 'shopify'
-- Run this in Supabase SQL Editor
-- ============================================

-- Drop old constraint
ALTER TABLE public.oauth_states 
DROP CONSTRAINT IF EXISTS oauth_states_platform_check;

-- Add new constraint with 'shopify' included
ALTER TABLE public.oauth_states 
ADD CONSTRAINT oauth_states_platform_check 
CHECK (platform IN ('shopee', 'tiktok_shop', 'shopify'));

-- Verify
SELECT 'Constraint updated successfully! Now supports: shopee, tiktok_shop, shopify' as status;
