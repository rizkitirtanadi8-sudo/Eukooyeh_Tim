-- Create market_trends_cache table for storing daily trend data
CREATE TABLE IF NOT EXISTS market_trends_cache (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    trends_data JSONB NOT NULL,
    categories TEXT[] NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create index on updated_at for efficient queries
CREATE INDEX IF NOT EXISTS idx_market_trends_cache_updated_at 
ON market_trends_cache(updated_at DESC);

-- Add comment
COMMENT ON TABLE market_trends_cache IS 'Cache for market trends data, updated daily';
COMMENT ON COLUMN market_trends_cache.trends_data IS 'JSON data containing trending products per category';
COMMENT ON COLUMN market_trends_cache.categories IS 'List of categories included in this cache entry';
COMMENT ON COLUMN market_trends_cache.updated_at IS 'Last update timestamp for cache invalidation';
