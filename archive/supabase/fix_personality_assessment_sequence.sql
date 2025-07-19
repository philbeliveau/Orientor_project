-- Fix personality_assessments table sequence
-- This ensures the id column auto-increments properly

-- Check current sequence value
SELECT nextval('personality_assessments_id_seq') AS current_next_id;

-- Reset sequence to the correct value (max id + 1)
SELECT setval('personality_assessments_id_seq', 
    COALESCE((SELECT MAX(id) FROM personality_assessments), 0) + 1, 
    false);

-- Verify the sequence is working
SELECT nextval('personality_assessments_id_seq') AS next_id_after_fix;

-- Check the column default
SELECT column_name, column_default 
FROM information_schema.columns 
WHERE table_name = 'personality_assessments' AND column_name = 'id';

-- If the sequence doesn't exist, create it
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_class WHERE relkind = 'S' AND relname = 'personality_assessments_id_seq') THEN
        CREATE SEQUENCE personality_assessments_id_seq;
        ALTER TABLE personality_assessments ALTER COLUMN id SET DEFAULT nextval('personality_assessments_id_seq');
        ALTER SEQUENCE personality_assessments_id_seq OWNED BY personality_assessments.id;
        SELECT setval('personality_assessments_id_seq', 
            COALESCE((SELECT MAX(id) FROM personality_assessments), 0) + 1, 
            false);
    END IF;
END $$;