-- Supabase Migration: Add onboarding_completed column to users table
-- Run this in Supabase SQL Editor or via supabase migration

-- Step 1: Add the onboarding_completed column to users table
ALTER TABLE users 
ADD COLUMN onboarding_completed BOOLEAN DEFAULT FALSE NOT NULL;

-- Step 2: Create index for faster queries
CREATE INDEX IF NOT EXISTS idx_users_onboarding_completed 
ON users(onboarding_completed);

-- Step 3: Update existing users based on personality profiles
-- Users who have personality profiles have completed onboarding
UPDATE users 
SET onboarding_completed = TRUE 
WHERE id IN (
    SELECT DISTINCT user_id 
    FROM personality_profiles 
    WHERE user_id IS NOT NULL
);

-- Step 4: Add comment for documentation
COMMENT ON COLUMN users.onboarding_completed IS 'Indicates whether user has completed the onboarding process';

-- Verification query (optional - run after migration)
-- SELECT 
--     COUNT(*) as total_users,
--     COUNT(CASE WHEN onboarding_completed = TRUE THEN 1 END) as completed_onboarding,
--     COUNT(CASE WHEN onboarding_completed = FALSE THEN 1 END) as needs_onboarding
-- FROM users;