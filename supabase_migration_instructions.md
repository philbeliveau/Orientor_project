# Supabase Migration Instructions: Fix Onboarding Issue

## Problem
Users keep having to redo onboarding because the `users` table is missing the `onboarding_completed` column that the backend code expects.

## Solution
Add the `onboarding_completed` column to the Supabase database.

## Migration Steps

### Method 1: Using Supabase Dashboard (Recommended)

1. **Login to Supabase Dashboard**
   - Go to [supabase.com](https://supabase.com)
   - Login to your project

2. **Open SQL Editor**
   - Go to "SQL Editor" in the left sidebar
   - Click "New Query"

3. **Run the Migration**
   - Copy the contents of `supabase_onboarding_migration.sql`
   - Paste into the SQL Editor
   - Click "Run" to execute

4. **Verify the Migration**
   - Go to "Database" → "Tables" → "users"
   - Check that `onboarding_completed` column exists
   - It should be a `boolean` type with default `false`

### Method 2: Using Supabase CLI

```bash
# If you have supabase CLI installed
supabase db push

# Or create a new migration file
supabase migration new add_onboarding_completed_column
# Then add the SQL content to the generated file
```

### Method 3: Manual SQL Execution

If you have direct database access:

```sql
-- Run this SQL command
ALTER TABLE users ADD COLUMN onboarding_completed BOOLEAN DEFAULT FALSE NOT NULL;

-- Update existing users
UPDATE users 
SET onboarding_completed = TRUE 
WHERE id IN (
    SELECT DISTINCT user_id 
    FROM personality_profiles 
    WHERE user_id IS NOT NULL
);
```

## Post-Migration Verification

After running the migration, verify it worked:

1. **Check Column Exists:**
   ```sql
   SELECT column_name, data_type, is_nullable, column_default 
   FROM information_schema.columns 
   WHERE table_name = 'users' AND column_name = 'onboarding_completed';
   ```

2. **Check Data:**
   ```sql
   SELECT 
       COUNT(*) as total_users,
       COUNT(CASE WHEN onboarding_completed = TRUE THEN 1 END) as completed_onboarding,
       COUNT(CASE WHEN onboarding_completed = FALSE THEN 1 END) as needs_onboarding
   FROM users;
   ```

3. **Test the API:**
   - Try logging in with an existing user
   - Check that `/auth/onboarding-status` returns the correct status
   - Verify that users with personality profiles have `onboarding_completed = true`

## Expected Results

After migration:
- ✅ New users: `onboarding_completed = false` (need to complete onboarding)
- ✅ Existing users with personality profiles: `onboarding_completed = true` (skip onboarding)
- ✅ Existing users without profiles: `onboarding_completed = false` (need onboarding)
- ✅ No more infinite onboarding loops!

## Rollback (if needed)

If something goes wrong, you can rollback:

```sql
-- Remove the column (WARNING: This will lose data!)
ALTER TABLE users DROP COLUMN onboarding_completed;
```

## Environment Variables

Make sure your backend is configured to use Supabase:

```env
DATABASE_URL=postgresql://[username]:[password]@[host]:[port]/[database]
# or
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
```

## Testing

After migration, run:
```bash
python test_onboarding_fix_comprehensive.py
```

This will verify that:
1. New users start with `onboarding_completed = false`
2. After completing onboarding, users have `onboarding_completed = true`
3. Returning users don't get stuck in onboarding loop
4. The API endpoints work correctly