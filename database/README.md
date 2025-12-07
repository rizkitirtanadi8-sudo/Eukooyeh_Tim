# Database

This directory contains database schemas and migrations.

## Files

- `schema.sql` - Complete database schema
- `migrations/` - Migration scripts in order

## Setup

1. Create Supabase project
2. Run migrations in order:
   ```sql
   -- Run in Supabase SQL Editor
   \i 001_initial_schema.sql
   \i 002_fix_demo_user.sql
   \i 003_fix_shopify_constraint.sql
   ```

## Schema

See `schema.sql` for the complete database structure.
