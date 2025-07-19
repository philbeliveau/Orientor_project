-- School Programs Database Schema
-- Designed for the Orientor platform school programs integration
-- Supports CEGEP, university, and college program data

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Institutions table
CREATE TABLE IF NOT EXISTS institutions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    name_fr VARCHAR(255),
    institution_type VARCHAR(50) NOT NULL CHECK (institution_type IN ('cegep', 'university', 'college')),
    country VARCHAR(2) NOT NULL DEFAULT 'CA', -- ISO 3166-1 alpha-2
    province_state VARCHAR(50),
    city VARCHAR(100),
    postal_code VARCHAR(20),
    website_url TEXT,
    accreditation_status VARCHAR(100),
    student_count INTEGER,
    established_year INTEGER,
    languages_offered VARCHAR(10)[] DEFAULT ARRAY['en'],
    contact_info JSONB DEFAULT '{}',
    geographic_coordinates POINT,
    
    -- Source tracking
    source_system VARCHAR(50) NOT NULL,
    source_id VARCHAR(100) NOT NULL,
    source_url TEXT,
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_synced TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    active BOOLEAN DEFAULT true,
    
    -- Constraints
    UNIQUE(source_system, source_id)
);

-- Programs table
CREATE TABLE IF NOT EXISTS programs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(255) NOT NULL,
    title_fr VARCHAR(255),
    description TEXT,
    description_fr TEXT,
    
    -- Institution reference
    institution_id UUID REFERENCES institutions(id) ON DELETE CASCADE,
    
    -- Program classification
    program_type VARCHAR(50) NOT NULL, -- 'technical', 'academic', 'pre-university', etc.
    level VARCHAR(50) NOT NULL CHECK (level IN ('certificate', 'diploma', 'associate', 'bachelor', 'master', 'phd', 'professional')),
    field_of_study VARCHAR(100),
    field_of_study_fr VARCHAR(100),
    
    -- Program details
    duration_months INTEGER,
    credits DECIMAL(5,2),
    semester_count INTEGER,
    language VARCHAR(10)[] DEFAULT ARRAY['en'],
    delivery_mode VARCHAR(50) DEFAULT 'in-person', -- 'in-person', 'online', 'hybrid'
    
    -- Classification codes
    cip_code VARCHAR(10), -- Classification of Instructional Programs
    isced_code VARCHAR(10), -- International Standard Classification of Education
    noc_code VARCHAR(10), -- National Occupational Classification (Canada)
    program_code VARCHAR(20), -- Institution-specific code
    
    -- Academic requirements
    admission_requirements JSONB DEFAULT '[]',
    prerequisite_courses JSONB DEFAULT '[]',
    min_gpa DECIMAL(3,2),
    language_requirements JSONB DEFAULT '{}',
    
    -- Program structure
    curriculum_outline JSONB DEFAULT '{}',
    internship_required BOOLEAN DEFAULT false,
    coop_available BOOLEAN DEFAULT false,
    thesis_required BOOLEAN DEFAULT false,
    
    -- Career outcomes
    career_outcomes JSONB DEFAULT '[]',
    employment_rate DECIMAL(3,2),
    average_salary_range JSONB DEFAULT '{}', -- {min: x, max: y, currency: 'CAD'}
    top_employers JSONB DEFAULT '[]',
    
    -- Financial information
    tuition_domestic DECIMAL(10,2),
    tuition_international DECIMAL(10,2),
    fees_additional JSONB DEFAULT '{}',
    financial_aid_available BOOLEAN DEFAULT false,
    scholarships_available JSONB DEFAULT '[]',
    
    -- Application information
    application_deadline DATE,
    application_method VARCHAR(100),
    application_fee DECIMAL(8,2),
    application_requirements JSONB DEFAULT '[]',
    
    -- Source tracking
    source_system VARCHAR(50) NOT NULL,
    source_id VARCHAR(100) NOT NULL,
    source_url TEXT,
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_synced TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    active BOOLEAN DEFAULT true,
    
    -- Search optimization
    search_vector tsvector GENERATED ALWAYS AS (
        setweight(to_tsvector('english', COALESCE(title, '')), 'A') ||
        setweight(to_tsvector('english', COALESCE(description, '')), 'B') ||
        setweight(to_tsvector('english', COALESCE(field_of_study, '')), 'C')
    ) STORED,
    
    -- Constraints
    UNIQUE(source_system, source_id),
    CHECK (duration_months > 0),
    CHECK (employment_rate >= 0 AND employment_rate <= 1)
);

-- Program classifications for hierarchical organization
CREATE TABLE IF NOT EXISTS program_classifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    program_id UUID REFERENCES programs(id) ON DELETE CASCADE,
    classification_system VARCHAR(50) NOT NULL, -- 'cip', 'isced', 'custom', 'noc'
    code VARCHAR(20) NOT NULL,
    title VARCHAR(255) NOT NULL,
    title_fr VARCHAR(255),
    description TEXT,
    level INTEGER DEFAULT 1, -- Hierarchy level (1 = top level)
    parent_code VARCHAR(20),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    UNIQUE(program_id, classification_system, code)
);

-- User program preferences
CREATE TABLE IF NOT EXISTS user_program_preferences (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    
    -- Location preferences
    preferred_countries VARCHAR(2)[] DEFAULT ARRAY['CA'],
    preferred_provinces VARCHAR(50)[] DEFAULT ARRAY[],
    preferred_cities VARCHAR(100)[] DEFAULT ARRAY[],
    max_distance_km INTEGER,
    willing_to_relocate BOOLEAN DEFAULT false,
    
    -- Program preferences
    preferred_languages VARCHAR(10)[] DEFAULT ARRAY['en'],
    program_types VARCHAR(50)[] DEFAULT ARRAY[],
    program_levels VARCHAR(50)[] DEFAULT ARRAY[],
    fields_of_interest VARCHAR(100)[] DEFAULT ARRAY[],
    delivery_modes VARCHAR(50)[] DEFAULT ARRAY['in-person'],
    
    -- Duration and timing
    max_duration_months INTEGER,
    min_duration_months INTEGER,
    preferred_start_terms VARCHAR(20)[] DEFAULT ARRAY['fall'],
    part_time_acceptable BOOLEAN DEFAULT false,
    
    -- Financial constraints
    max_budget DECIMAL(10,2),
    budget_currency VARCHAR(3) DEFAULT 'CAD',
    financial_aid_required BOOLEAN DEFAULT false,
    scholarship_priority BOOLEAN DEFAULT false,
    
    -- Academic preferences
    min_employment_rate DECIMAL(3,2),
    internship_preference VARCHAR(20) DEFAULT 'optional', -- 'required', 'preferred', 'optional', 'none'
    coop_preference VARCHAR(20) DEFAULT 'optional',
    
    -- Career alignment
    target_career_fields VARCHAR(100)[] DEFAULT ARRAY[],
    salary_expectations JSONB DEFAULT '{}',
    work_environment_preferences JSONB DEFAULT '{}',
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    UNIQUE(user_id)
);

-- User program interactions (for recommendation engine)
CREATE TABLE IF NOT EXISTS user_program_interactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    program_id UUID REFERENCES programs(id) ON DELETE CASCADE,
    
    -- Interaction details
    interaction_type VARCHAR(50) NOT NULL, -- 'viewed', 'saved', 'applied', 'dismissed', 'shared', 'compared'
    interaction_duration_seconds INTEGER,
    interaction_source VARCHAR(50), -- 'search', 'recommendation', 'direct_link', 'comparison'
    
    -- Context data
    search_query TEXT,
    search_filters JSONB,
    page_position INTEGER,
    session_id UUID,
    
    -- User feedback
    rating INTEGER CHECK (rating BETWEEN 1 AND 5),
    feedback_text TEXT,
    relevance_score DECIMAL(3,2),
    
    -- Additional metadata
    device_type VARCHAR(20),
    user_agent TEXT,
    ip_address INET,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Indexes will be created below
    INDEX(user_id, created_at),
    INDEX(program_id, interaction_type),
    INDEX(session_id)
);

-- Saved programs (user's saved list)
CREATE TABLE IF NOT EXISTS user_saved_programs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    program_id UUID REFERENCES programs(id) ON DELETE CASCADE,
    
    -- User annotations
    personal_notes TEXT,
    priority_level INTEGER DEFAULT 1 CHECK (priority_level BETWEEN 1 AND 5),
    application_status VARCHAR(50) DEFAULT 'interested', -- 'interested', 'applying', 'applied', 'accepted', 'rejected', 'enrolled'
    application_deadline DATE,
    reminder_date DATE,
    
    -- Tags for organization
    user_tags VARCHAR(50)[] DEFAULT ARRAY[],
    
    -- Metadata
    saved_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    UNIQUE(user_id, program_id)
);

-- Program comparison sessions
CREATE TABLE IF NOT EXISTS program_comparisons (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    session_id UUID NOT NULL,
    program_ids UUID[] NOT NULL,
    comparison_criteria VARCHAR(50)[] DEFAULT ARRAY[],
    comparison_notes TEXT,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Search cache for performance optimization
CREATE TABLE IF NOT EXISTS program_search_cache (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    search_hash VARCHAR(64) NOT NULL UNIQUE,
    search_params JSONB NOT NULL,
    results JSONB NOT NULL,
    result_count INTEGER NOT NULL,
    
    -- Cache metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    hit_count INTEGER DEFAULT 0,
    last_hit TIMESTAMP WITH TIME ZONE,
    
    INDEX(search_hash),
    INDEX(expires_at)
);

-- Program recommendations for users
CREATE TABLE IF NOT EXISTS user_program_recommendations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    program_id UUID REFERENCES programs(id) ON DELETE CASCADE,
    
    -- Recommendation scoring
    recommendation_score DECIMAL(5,4) NOT NULL,
    confidence_level DECIMAL(3,2),
    recommendation_type VARCHAR(50), -- 'personality_match', 'career_alignment', 'collaborative', 'content_based'
    
    -- Explanation
    recommendation_reasons JSONB DEFAULT '[]',
    explanation_text TEXT,
    
    -- Performance tracking
    shown_to_user BOOLEAN DEFAULT false,
    user_interaction BOOLEAN DEFAULT false,
    user_rating INTEGER CHECK (user_rating BETWEEN 1 AND 5),
    
    -- Metadata
    generated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE,
    model_version VARCHAR(20),
    
    -- Constraints
    UNIQUE(user_id, program_id, generated_at::date),
    INDEX(user_id, recommendation_score DESC),
    INDEX(program_id, recommendation_score DESC)
);

-- Data source synchronization tracking
CREATE TABLE IF NOT EXISTS data_source_sync_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_name VARCHAR(100) NOT NULL,
    sync_type VARCHAR(50) NOT NULL, -- 'full', 'incremental', 'health_check'
    
    -- Sync results
    status VARCHAR(20) NOT NULL, -- 'success', 'partial', 'failed'
    records_processed INTEGER DEFAULT 0,
    records_created INTEGER DEFAULT 0,
    records_updated INTEGER DEFAULT 0,
    records_deleted INTEGER DEFAULT 0,
    errors_encountered INTEGER DEFAULT 0,
    
    -- Timing
    started_at TIMESTAMP WITH TIME ZONE NOT NULL,
    completed_at TIMESTAMP WITH TIME ZONE,
    duration_seconds INTEGER,
    
    -- Details
    error_details JSONB DEFAULT '[]',
    sync_metadata JSONB DEFAULT '{}',
    
    INDEX(source_name, started_at),
    INDEX(status, started_at)
);

-- Create indexes for optimal performance

-- Institution indexes
CREATE INDEX IF NOT EXISTS idx_institutions_type ON institutions(institution_type);
CREATE INDEX IF NOT EXISTS idx_institutions_location ON institutions(country, province_state, city);
CREATE INDEX IF NOT EXISTS idx_institutions_active ON institutions(active) WHERE active = true;
CREATE INDEX IF NOT EXISTS idx_institutions_source ON institutions(source_system, source_id);

-- Program indexes
CREATE INDEX IF NOT EXISTS idx_programs_institution ON programs(institution_id);
CREATE INDEX IF NOT EXISTS idx_programs_type_level ON programs(program_type, level);
CREATE INDEX IF NOT EXISTS idx_programs_cip ON programs(cip_code) WHERE cip_code IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_programs_active ON programs(active) WHERE active = true;
CREATE INDEX IF NOT EXISTS idx_programs_source ON programs(source_system, source_id);
CREATE INDEX IF NOT EXISTS idx_programs_search ON programs USING gin(search_vector);
CREATE INDEX IF NOT EXISTS idx_programs_title_trgm ON programs USING gin(title gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_programs_field_study ON programs(field_of_study) WHERE field_of_study IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_programs_duration ON programs(duration_months) WHERE duration_months IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_programs_employment_rate ON programs(employment_rate) WHERE employment_rate IS NOT NULL;

-- Program classification indexes
CREATE INDEX IF NOT EXISTS idx_classifications_program ON program_classifications(program_id);
CREATE INDEX IF NOT EXISTS idx_classifications_system_code ON program_classifications(classification_system, code);
CREATE INDEX IF NOT EXISTS idx_classifications_hierarchy ON program_classifications(classification_system, level, parent_code);

-- User interaction indexes
CREATE INDEX IF NOT EXISTS idx_user_interactions_user_date ON user_program_interactions(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_user_interactions_program_type ON user_program_interactions(program_id, interaction_type);
CREATE INDEX IF NOT EXISTS idx_user_interactions_session ON user_program_interactions(session_id, created_at);

-- User preferences and saved programs indexes
CREATE INDEX IF NOT EXISTS idx_user_preferences_user ON user_program_preferences(user_id);
CREATE INDEX IF NOT EXISTS idx_saved_programs_user ON user_saved_programs(user_id, saved_at DESC);
CREATE INDEX IF NOT EXISTS idx_saved_programs_status ON user_saved_programs(user_id, application_status);

-- Recommendation indexes
CREATE INDEX IF NOT EXISTS idx_recommendations_user_score ON user_program_recommendations(user_id, recommendation_score DESC);
CREATE INDEX IF NOT EXISTS idx_recommendations_active ON user_program_recommendations(user_id, expires_at) WHERE expires_at > NOW();

-- Create views for common queries

-- Active programs with institution details
CREATE OR REPLACE VIEW active_programs AS
SELECT 
    p.*,
    i.name as institution_name,
    i.name_fr as institution_name_fr,
    i.city,
    i.province_state,
    i.country,
    i.website_url as institution_website
FROM programs p
JOIN institutions i ON p.institution_id = i.id
WHERE p.active = true AND i.active = true;

-- Program search view with full-text search optimization
CREATE OR REPLACE VIEW searchable_programs AS
SELECT 
    p.id,
    p.title,
    p.title_fr,
    p.description,
    p.description_fr,
    p.program_type,
    p.level,
    p.duration_months,
    p.language,
    p.cip_code,
    p.field_of_study,
    p.employment_rate,
    p.tuition_domestic,
    p.search_vector,
    i.name as institution_name,
    i.name_fr as institution_name_fr,
    i.city,
    i.province_state,
    i.country,
    i.institution_type
FROM active_programs p
JOIN institutions i ON p.institution_id = i.id;

-- User program interaction summary
CREATE OR REPLACE VIEW user_interaction_summary AS
SELECT 
    user_id,
    COUNT(*) as total_interactions,
    COUNT(DISTINCT program_id) as unique_programs_viewed,
    COUNT(*) FILTER (WHERE interaction_type = 'saved') as programs_saved,
    COUNT(*) FILTER (WHERE interaction_type = 'applied') as applications,
    AVG(rating) FILTER (WHERE rating IS NOT NULL) as average_rating,
    MAX(created_at) as last_interaction
FROM user_program_interactions
GROUP BY user_id;

-- Create triggers for automatic timestamp updates

-- Function to update timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply timestamp triggers
CREATE TRIGGER update_institutions_updated_at BEFORE UPDATE ON institutions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_programs_updated_at BEFORE UPDATE ON programs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_preferences_updated_at BEFORE UPDATE ON user_program_preferences
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_saved_programs_updated_at BEFORE UPDATE ON user_saved_programs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Create function for program search with ranking
CREATE OR REPLACE FUNCTION search_programs(
    search_text TEXT DEFAULT '',
    program_types TEXT[] DEFAULT ARRAY[]::TEXT[],
    levels TEXT[] DEFAULT ARRAY[]::TEXT[],
    countries TEXT[] DEFAULT ARRAY[]::TEXT[],
    provinces TEXT[] DEFAULT ARRAY[]::TEXT[],
    languages TEXT[] DEFAULT ARRAY[]::TEXT[],
    max_duration INTEGER DEFAULT NULL,
    min_employment_rate DECIMAL DEFAULT NULL,
    limit_count INTEGER DEFAULT 20,
    offset_count INTEGER DEFAULT 0
)
RETURNS TABLE (
    id UUID,
    title TEXT,
    institution_name TEXT,
    city TEXT,
    province_state TEXT,
    program_type TEXT,
    level TEXT,
    duration_months INTEGER,
    employment_rate DECIMAL,
    search_rank REAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        sp.id,
        sp.title,
        sp.institution_name,
        sp.city,
        sp.province_state,
        sp.program_type,
        sp.level,
        sp.duration_months,
        sp.employment_rate,
        CASE 
            WHEN search_text = '' THEN 1.0
            ELSE ts_rank(sp.search_vector, plainto_tsquery('english', search_text))
        END as search_rank
    FROM searchable_programs sp
    WHERE 
        (search_text = '' OR sp.search_vector @@ plainto_tsquery('english', search_text))
        AND (array_length(program_types, 1) IS NULL OR sp.program_type = ANY(program_types))
        AND (array_length(levels, 1) IS NULL OR sp.level = ANY(levels))
        AND (array_length(countries, 1) IS NULL OR sp.country = ANY(countries))
        AND (array_length(provinces, 1) IS NULL OR sp.province_state = ANY(provinces))
        AND (array_length(languages, 1) IS NULL OR sp.language && languages)
        AND (max_duration IS NULL OR sp.duration_months <= max_duration)
        AND (min_employment_rate IS NULL OR sp.employment_rate >= min_employment_rate)
    ORDER BY search_rank DESC, sp.title
    LIMIT limit_count OFFSET offset_count;
END;
$$ LANGUAGE plpgsql;

-- Create materialized view for program statistics (refreshed daily)
CREATE MATERIALIZED VIEW IF NOT EXISTS program_statistics AS
SELECT 
    COUNT(*) as total_programs,
    COUNT(DISTINCT institution_id) as total_institutions,
    COUNT(*) FILTER (WHERE program_type = 'technical') as technical_programs,
    COUNT(*) FILTER (WHERE program_type = 'academic') as academic_programs,
    COUNT(*) FILTER (WHERE level = 'diploma') as diploma_programs,
    COUNT(*) FILTER (WHERE level = 'bachelor') as bachelor_programs,
    COUNT(*) FILTER (WHERE level = 'master') as master_programs,
    AVG(duration_months) FILTER (WHERE duration_months IS NOT NULL) as avg_duration_months,
    AVG(employment_rate) FILTER (WHERE employment_rate IS NOT NULL) as avg_employment_rate,
    COUNT(DISTINCT cip_code) FILTER (WHERE cip_code IS NOT NULL) as unique_cip_codes,
    MAX(updated_at) as last_data_update
FROM programs
WHERE active = true;

-- Create index on materialized view
CREATE UNIQUE INDEX ON program_statistics ((true));

-- Grant permissions (adjust according to your user roles)
-- GRANT SELECT ON ALL TABLES IN SCHEMA public TO orientor_read_user;
-- GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO orientor_app_user;
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO orientor_admin_user;

-- Add comments for documentation
COMMENT ON TABLE institutions IS 'Educational institutions (CEGEPs, universities, colleges)';
COMMENT ON TABLE programs IS 'Academic programs offered by institutions';
COMMENT ON TABLE program_classifications IS 'Hierarchical classification of programs using various systems (CIP, ISCED, etc.)';
COMMENT ON TABLE user_program_preferences IS 'User preferences for program search and recommendations';
COMMENT ON TABLE user_program_interactions IS 'Track user interactions with programs for analytics and recommendations';
COMMENT ON TABLE user_saved_programs IS 'Programs saved by users for future reference';
COMMENT ON TABLE user_program_recommendations IS 'AI-generated program recommendations for users';
COMMENT ON TABLE program_search_cache IS 'Cache for search results to improve performance';
COMMENT ON TABLE data_source_sync_log IS 'Log of data synchronization operations from external sources';

-- Sample data for testing (optional - remove in production)
/*
INSERT INTO institutions (name, institution_type, country, province_state, city, source_system, source_id) VALUES
('Dawson College', 'cegep', 'CA', 'QC', 'Montreal', 'sample', 'dawson_001'),
('McGill University', 'university', 'CA', 'QC', 'Montreal', 'sample', 'mcgill_001'),
('Université de Montréal', 'university', 'CA', 'QC', 'Montreal', 'sample', 'udem_001');

INSERT INTO programs (title, institution_id, program_type, level, duration_months, cip_code, source_system, source_id)
SELECT 
    'Computer Science Technology',
    i.id,
    'technical',
    'diploma',
    36,
    '11.0201',
    'sample',
    'cst_001'
FROM institutions i WHERE i.name = 'Dawson College';
*/