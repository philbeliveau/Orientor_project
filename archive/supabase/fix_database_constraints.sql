-- Fix multiple database issues for onboarding and recommendations

-- 1. Fix personality_responses constraint to allow onboarding_question
ALTER TABLE personality_responses 
DROP CONSTRAINT IF EXISTS personality_responses_item_type_check;

ALTER TABLE personality_responses 
ADD CONSTRAINT personality_responses_item_type_check 
CHECK (item_type IN ('likert', 'scenario', 'ranking', 'open_ended', 'onboarding_question'));

-- 2. Add onboarding_completed column to users table (original fix)
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS onboarding_completed BOOLEAN DEFAULT FALSE NOT NULL;

-- 3. Create index for onboarding_completed
CREATE INDEX IF NOT EXISTS idx_users_onboarding_completed 
ON users(onboarding_completed);

-- 4. Update existing users based on personality profiles
UPDATE users 
SET onboarding_completed = TRUE 
WHERE id IN (
    SELECT DISTINCT user_id 
    FROM personality_profiles 
    WHERE user_id IS NOT NULL
);

-- 5. Add comment for documentation
COMMENT ON COLUMN users.onboarding_completed IS 'Indicates whether user has completed the onboarding process';

-- Verification queries
SELECT 
    'Users with onboarding status' as description,
    COUNT(*) as total_users,
    COUNT(CASE WHEN onboarding_completed = TRUE THEN 1 END) as completed_onboarding,
    COUNT(CASE WHEN onboarding_completed = FALSE THEN 1 END) as needs_onboarding
FROM users;

-- Test the constraint fix
SELECT 
    'Constraint fixed' as description,
    constraint_name,
    check_clause
FROM information_schema.check_constraints 
WHERE constraint_name = 'personality_responses_item_type_check';