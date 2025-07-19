--
-- PostgreSQL database dump
--

-- Dumped from database version 17.3
-- Dumped by pg_dump version 17.3

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: pg_trgm; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS pg_trgm WITH SCHEMA public;


--
-- Name: EXTENSION pg_trgm; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON EXTENSION pg_trgm IS 'text similarity measurement and index searching based on trigrams';


--
-- Name: uuid-ossp; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS "uuid-ossp" WITH SCHEMA public;


--
-- Name: EXTENSION "uuid-ossp"; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON EXTENSION "uuid-ossp" IS 'generate universally unique identifiers (UUIDs)';


--
-- Name: vector; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS vector WITH SCHEMA public;


--
-- Name: EXTENSION vector; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON EXTENSION vector IS 'vector data type and ivfflat and hnsw access methods';


--
-- Name: calculate_skill_match_score(jsonb, jsonb); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.calculate_skill_match_score(user_skills jsonb, role_skills jsonb) RETURNS numeric
    LANGUAGE plpgsql
    AS $$
DECLARE
    match_score DECIMAL := 0;
    skill_count INTEGER := 0;
    user_level DECIMAL;
    role_level DECIMAL;
    skill_name TEXT;
BEGIN
    -- Compare each skill
    FOR skill_name IN SELECT jsonb_object_keys(role_skills)
    LOOP
        role_level := (role_skills->>skill_name)::DECIMAL;
        user_level := COALESCE((user_skills->>skill_name)::DECIMAL, 0);
        
        -- Calculate match (penalize gaps more than surplus)
        IF user_level >= role_level THEN
            match_score := match_score + 1;
        ELSE
            match_score := match_score + (user_level / NULLIF(role_level, 0));
        END IF;
        
        skill_count := skill_count + 1;
    END LOOP;
    
    -- Return average match score
    RETURN CASE 
        WHEN skill_count > 0 THEN match_score / skill_count
        ELSE 0
    END;
END;
$$;


--
-- Name: search_programs(text, text[], text[], text[], text[], text[], integer, numeric, integer, integer); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.search_programs(search_text text DEFAULT ''::text, program_types text[] DEFAULT ARRAY[]::text[], levels text[] DEFAULT ARRAY[]::text[], countries text[] DEFAULT ARRAY[]::text[], provinces text[] DEFAULT ARRAY[]::text[], languages text[] DEFAULT ARRAY[]::text[], max_duration integer DEFAULT NULL::integer, min_employment_rate numeric DEFAULT NULL::numeric, limit_count integer DEFAULT 20, offset_count integer DEFAULT 0) RETURNS TABLE(id uuid, title text, institution_name text, city text, province_state text, program_type text, level text, duration_months integer, employment_rate numeric, search_rank real)
    LANGUAGE plpgsql
    AS $$
        BEGIN
            RETURN QUERY
            SELECT 
                p.id,
                p.title::TEXT,
                i.name::TEXT as institution_name,
                i.city::TEXT,
                i.province_state::TEXT,
                p.program_type::TEXT,
                p.level::TEXT,
                p.duration_months,
                p.employment_rate,
                CASE 
                    WHEN search_text = '' THEN 1.0::REAL
                    ELSE ts_rank(p.search_vector, plainto_tsquery('english', search_text))
                END as search_rank
            FROM programs p
            JOIN institutions i ON p.institution_id = i.id
            WHERE 
                p.active = true AND i.active = true
                AND (search_text = '' OR p.search_vector @@ plainto_tsquery('english', search_text))
                AND (array_length(program_types, 1) IS NULL OR p.program_type = ANY(program_types))
                AND (array_length(levels, 1) IS NULL OR p.level = ANY(levels))
                AND (array_length(countries, 1) IS NULL OR i.country = ANY(countries))
                AND (array_length(provinces, 1) IS NULL OR i.province_state = ANY(provinces))
                AND (array_length(languages, 1) IS NULL OR (p.language::TEXT[] && languages))
                AND (max_duration IS NULL OR p.duration_months <= max_duration)
                AND (min_employment_rate IS NULL OR p.employment_rate >= min_employment_rate)
            ORDER BY search_rank DESC, p.title
            LIMIT limit_count OFFSET offset_count;
        END;
        $$;


--
-- Name: update_updated_at_column(); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.update_updated_at_column() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$;


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


--
-- Name: behavioral_signals; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.behavioral_signals (
    id integer NOT NULL,
    user_id integer NOT NULL,
    signal_type character varying(50) NOT NULL,
    signal_data jsonb NOT NULL,
    confidence_score double precision,
    context_metadata jsonb DEFAULT '{}'::jsonb,
    detected_at timestamp with time zone DEFAULT now() NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT behavioral_signals_confidence_score_check CHECK (((confidence_score >= (0)::double precision) AND (confidence_score <= (1)::double precision))),
    CONSTRAINT behavioral_signals_signal_type_check CHECK (((signal_type)::text = ANY ((ARRAY['response_timing'::character varying, 'navigation_pattern'::character varying, 'choice_pattern'::character varying])::text[])))
);


--
-- Name: behavioral_signals_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.behavioral_signals_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: behavioral_signals_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.behavioral_signals_id_seq OWNED BY public.behavioral_signals.id;


--
-- Name: career_fit_analyses; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.career_fit_analyses (
    id integer NOT NULL,
    user_id integer,
    saved_recommendation_id integer,
    skill_match_score numeric(3,2),
    education_match_score numeric(3,2),
    experience_match_score numeric(3,2),
    personality_match_score numeric(3,2),
    overall_fit_score numeric(3,2),
    skill_gaps jsonb DEFAULT '[]'::jsonb,
    education_gap text,
    experience_gap_years integer,
    certification_gaps jsonb DEFAULT '[]'::jsonb,
    estimated_preparation_months integer,
    recommended_pathway text,
    milestone_timeline jsonb DEFAULT '[]'::jsonb,
    total_education_cost numeric(10,2),
    opportunity_cost numeric(10,2),
    break_even_years numeric(3,1),
    roi_10_year numeric(10,2),
    barriers_analysis text,
    strengths_alignment text,
    recommendation_rationale text,
    alternative_paths text,
    analysis_version character varying(20) DEFAULT '1.0'::character varying,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);


--
-- Name: TABLE career_fit_analyses; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.career_fit_analyses IS 'Detailed career fit analysis results comparing users to saved jobs';


--
-- Name: career_fit_analyses_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.career_fit_analyses_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: career_fit_analyses_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.career_fit_analyses_id_seq OWNED BY public.career_fit_analyses.id;


--
-- Name: career_goals; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.career_goals (
    id integer NOT NULL,
    user_id integer NOT NULL,
    esco_occupation_id character varying,
    oasis_code character varying,
    title character varying NOT NULL,
    description text,
    target_date timestamp without time zone,
    is_active boolean,
    progress_percentage double precision,
    created_at timestamp without time zone,
    updated_at timestamp without time zone,
    achieved_at timestamp without time zone,
    source character varying,
    source_metadata text
);


--
-- Name: career_goals_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.career_goals_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: career_goals_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.career_goals_id_seq OWNED BY public.career_goals.id;


--
-- Name: career_milestones; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.career_milestones (
    id integer NOT NULL,
    goal_id integer NOT NULL,
    skill_id character varying NOT NULL,
    skill_name character varying NOT NULL,
    tier_level integer NOT NULL,
    is_completed boolean,
    confidence_score double precision,
    created_at timestamp without time zone,
    completed_at timestamp without time zone,
    xp_value integer,
    xp_awarded boolean
);


--
-- Name: career_milestones_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.career_milestones_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: career_milestones_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.career_milestones_id_seq OWNED BY public.career_milestones.id;


--
-- Name: career_profile_aggregates; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.career_profile_aggregates (
    id integer NOT NULL,
    user_id integer NOT NULL,
    aggregate_type character varying(50) NOT NULL,
    time_period character varying(50),
    cognitive_preferences json,
    work_style_preferences json,
    subject_affinities json,
    career_readiness_signals json,
    esco_path_suggestions json,
    contradiction_flags json,
    confidence_metrics json,
    last_updated timestamp with time zone DEFAULT now(),
    created_at timestamp with time zone DEFAULT now()
);


--
-- Name: career_profile_aggregates_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.career_profile_aggregates_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: career_profile_aggregates_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.career_profile_aggregates_id_seq OWNED BY public.career_profile_aggregates.id;


--
-- Name: career_signals; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.career_signals (
    id integer NOT NULL,
    user_id integer NOT NULL,
    course_id integer,
    signal_type character varying(100) NOT NULL,
    strength_score double precision NOT NULL,
    evidence_source text NOT NULL,
    pattern_metadata json,
    esco_skill_mapping json,
    trend_analysis json,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);


--
-- Name: career_signals_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.career_signals_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: career_signals_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.career_signals_id_seq OWNED BY public.career_signals.id;


--
-- Name: chat_messages; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.chat_messages (
    id integer NOT NULL,
    conversation_id integer NOT NULL,
    role character varying(20) NOT NULL,
    content text NOT NULL,
    tokens_used integer,
    message_metadata jsonb,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    model_used character varying(50),
    response_time_ms integer,
    CONSTRAINT chat_messages_role_check CHECK (((role)::text = ANY ((ARRAY['user'::character varying, 'assistant'::character varying, 'system'::character varying])::text[])))
);


--
-- Name: chat_messages_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.chat_messages_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: chat_messages_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.chat_messages_id_seq OWNED BY public.chat_messages.id;


--
-- Name: conversation_categories; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.conversation_categories (
    id integer NOT NULL,
    user_id integer NOT NULL,
    name character varying(100) NOT NULL,
    description text,
    color character varying(7),
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);


--
-- Name: conversation_categories_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.conversation_categories_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: conversation_categories_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.conversation_categories_id_seq OWNED BY public.conversation_categories.id;


--
-- Name: conversation_logs; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.conversation_logs (
    id integer NOT NULL,
    user_id integer NOT NULL,
    course_id integer NOT NULL,
    session_id character varying(255) NOT NULL,
    question_intent character varying(100) NOT NULL,
    question_text text NOT NULL,
    response text,
    extracted_insights json,
    sentiment_analysis json,
    career_implications json,
    llm_metadata json,
    created_at timestamp with time zone DEFAULT now()
);


--
-- Name: conversation_logs_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.conversation_logs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: conversation_logs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.conversation_logs_id_seq OWNED BY public.conversation_logs.id;


--
-- Name: conversation_shares; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.conversation_shares (
    id integer NOT NULL,
    conversation_id integer NOT NULL,
    share_token character varying(100) NOT NULL,
    is_public boolean DEFAULT false,
    password_hash character varying(255),
    expires_at timestamp with time zone,
    view_count integer DEFAULT 0,
    created_at timestamp with time zone DEFAULT now(),
    last_accessed_at timestamp with time zone
);


--
-- Name: conversation_shares_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.conversation_shares_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: conversation_shares_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.conversation_shares_id_seq OWNED BY public.conversation_shares.id;


--
-- Name: conversations; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.conversations (
    id integer NOT NULL,
    user_id integer NOT NULL,
    title character varying(255) NOT NULL,
    auto_generated_title boolean DEFAULT true,
    category_id integer,
    is_favorite boolean DEFAULT false,
    is_archived boolean DEFAULT false,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    last_message_at timestamp with time zone,
    message_count integer DEFAULT 0,
    total_tokens_used integer DEFAULT 0
);


--
-- Name: conversations_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.conversations_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: conversations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.conversations_id_seq OWNED BY public.conversations.id;


--
-- Name: courses; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.courses (
    id integer NOT NULL,
    user_id integer NOT NULL,
    course_name character varying(255) NOT NULL,
    course_code character varying(50),
    semester character varying(50),
    year integer,
    professor character varying(255),
    subject_category character varying(50),
    grade character varying(10),
    credits integer,
    description text,
    learning_outcomes json,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);


--
-- Name: courses_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.courses_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: courses_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.courses_id_seq OWNED BY public.courses.id;


--
-- Name: developmental_milestones; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.developmental_milestones (
    id integer NOT NULL,
    user_id integer NOT NULL,
    milestone_type character varying(50) NOT NULL,
    milestone_description text NOT NULL,
    achievement_date timestamp with time zone NOT NULL,
    confidence_level double precision,
    supporting_evidence jsonb,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT developmental_milestones_confidence_level_check CHECK (((confidence_level >= (0)::double precision) AND (confidence_level <= (1)::double precision))),
    CONSTRAINT developmental_milestones_milestone_type_check CHECK (((milestone_type)::text = ANY ((ARRAY['identity_exploration'::character varying, 'value_clarification'::character varying, 'commitment_formation'::character varying])::text[])))
);


--
-- Name: developmental_milestones_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.developmental_milestones_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: developmental_milestones_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.developmental_milestones_id_seq OWNED BY public.developmental_milestones.id;


--
-- Name: esco_job_requirements; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.esco_job_requirements (
    id integer NOT NULL,
    oasis_code character varying(255) NOT NULL,
    entry_level_education character varying(100),
    entry_experience_years integer DEFAULT 0,
    entry_certifications jsonb DEFAULT '[]'::jsonb,
    entry_portfolio_required boolean DEFAULT false,
    typical_education_level character varying(100),
    alternative_pathways jsonb DEFAULT '[]'::jsonb,
    continuing_education text,
    specialization_options jsonb DEFAULT '[]'::jsonb,
    essential_skills jsonb DEFAULT '[]'::jsonb,
    optional_skills jsonb DEFAULT '[]'::jsonb,
    transferable_skills jsonb DEFAULT '[]'::jsonb,
    emerging_skills jsonb DEFAULT '[]'::jsonb,
    entry_level_titles jsonb DEFAULT '[]'::jsonb,
    mid_career_titles jsonb DEFAULT '[]'::jsonb,
    senior_titles jsonb DEFAULT '[]'::jsonb,
    lateral_moves jsonb DEFAULT '[]'::jsonb,
    sector_classification character varying(100),
    isco_code character varying(10),
    growth_rate numeric(5,2),
    automation_risk numeric(3,2),
    remote_work_percentage numeric(3,2),
    typical_years_to_entry integer,
    education_cost_estimate numeric(10,2),
    average_starting_salary numeric(10,2),
    salary_growth_curve jsonb,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);


--
-- Name: TABLE esco_job_requirements; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.esco_job_requirements IS 'Extended ESCO job requirements for career fit analysis';


--
-- Name: esco_job_requirements_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.esco_job_requirements_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: esco_job_requirements_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.esco_job_requirements_id_seq OWNED BY public.esco_job_requirements.id;


--
-- Name: gca_choices; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.gca_choices (
    id integer NOT NULL,
    title character varying(250) NOT NULL,
    question_id integer NOT NULL,
    sort_idx integer NOT NULL,
    active integer NOT NULL,
    r numeric(4,2) NOT NULL,
    i numeric(4,2) NOT NULL,
    a numeric(4,2) NOT NULL,
    s numeric(4,2) NOT NULL,
    e numeric(4,2) NOT NULL,
    c numeric(4,2) NOT NULL
);


--
-- Name: gca_holland_questions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.gca_holland_questions (
    id integer NOT NULL,
    question text NOT NULL,
    personality_code character(1) NOT NULL,
    CONSTRAINT gca_holland_questions_personality_code_check CHECK ((personality_code = ANY (ARRAY['R'::bpchar, 'I'::bpchar, 'A'::bpchar, 'S'::bpchar, 'E'::bpchar, 'C'::bpchar])))
);


--
-- Name: gca_holland_questions_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.gca_holland_questions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: gca_holland_questions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.gca_holland_questions_id_seq OWNED BY public.gca_holland_questions.id;


--
-- Name: gca_personalities; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.gca_personalities (
    id character varying(1) NOT NULL,
    initial character varying(1) NOT NULL,
    title character varying(100) NOT NULL,
    alias character varying(100) NOT NULL,
    description text NOT NULL
);


--
-- Name: gca_questions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.gca_questions (
    id integer NOT NULL,
    title character varying(250) NOT NULL,
    test_id integer NOT NULL,
    chapter_number integer NOT NULL,
    sort_idx integer NOT NULL,
    active integer NOT NULL
);


--
-- Name: gca_results; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.gca_results (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    attempt_id uuid NOT NULL,
    test_id integer NOT NULL,
    r_score numeric(5,2) NOT NULL,
    i_score numeric(5,2) NOT NULL,
    a_score numeric(5,2) NOT NULL,
    s_score numeric(5,2) NOT NULL,
    e_score numeric(5,2) NOT NULL,
    c_score numeric(5,2) NOT NULL,
    top_3_code character(3) NOT NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    user_id integer
);


--
-- Name: gca_tests; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.gca_tests (
    id integer NOT NULL,
    title character varying(250) NOT NULL,
    description text NOT NULL,
    seo_code character varying(100) NOT NULL,
    video_url text NOT NULL,
    image_url text NOT NULL,
    chapter_count integer NOT NULL,
    question_count integer NOT NULL,
    active integer NOT NULL
);


--
-- Name: gca_users_answers; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.gca_users_answers (
    id character varying(36) NOT NULL,
    attempt_id character varying(36) NOT NULL,
    user_id character varying(36),
    test_id integer NOT NULL,
    question_id integer NOT NULL,
    choice_id integer NOT NULL,
    created_at timestamp with time zone DEFAULT (CURRENT_TIMESTAMP AT TIME ZONE 'America/Montreal'::text) NOT NULL
);


--
-- Name: institutions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.institutions (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    name character varying(255) NOT NULL,
    name_fr character varying(255),
    institution_type character varying(50) NOT NULL,
    country character varying(2) DEFAULT 'CA'::character varying NOT NULL,
    province_state character varying(50),
    city character varying(100),
    postal_code character varying(20),
    website_url text,
    accreditation_status character varying(100),
    student_count integer,
    established_year integer,
    languages_offered character varying(10)[] DEFAULT ARRAY['en'::text],
    contact_info jsonb DEFAULT '{}'::jsonb,
    geographic_coordinates point,
    source_system character varying(50) NOT NULL,
    source_id character varying(100) NOT NULL,
    source_url text,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    last_synced timestamp with time zone DEFAULT now(),
    active boolean DEFAULT true,
    CONSTRAINT institutions_institution_type_check CHECK (((institution_type)::text = ANY ((ARRAY['cegep'::character varying, 'university'::character varying, 'college'::character varying])::text[])))
);


--
-- Name: llm_descriptions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.llm_descriptions (
    id integer NOT NULL,
    node_id character varying(255) NOT NULL,
    user_id integer NOT NULL,
    node_type character varying(50) NOT NULL,
    description text NOT NULL,
    prompt_template character varying(100),
    model_version character varying(50),
    created_at timestamp with time zone DEFAULT now(),
    expires_at timestamp with time zone,
    CONSTRAINT check_node_type CHECK (((node_type)::text = ANY ((ARRAY['skill'::character varying, 'occupation'::character varying, 'skillgroup'::character varying])::text[])))
);


--
-- Name: llm_descriptions_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.llm_descriptions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: llm_descriptions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.llm_descriptions_id_seq OWNED BY public.llm_descriptions.id;


--
-- Name: message_components; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.message_components (
    id integer NOT NULL,
    message_id integer,
    component_type character varying(50) NOT NULL,
    component_data jsonb NOT NULL,
    tool_source character varying(50),
    created_at timestamp with time zone DEFAULT now(),
    actions jsonb,
    saved boolean DEFAULT false,
    component_metadata jsonb
);


--
-- Name: message_components_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.message_components_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: message_components_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.message_components_id_seq OWNED BY public.message_components.id;


--
-- Name: messages; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.messages (
    message_id integer NOT NULL,
    sender_id integer NOT NULL,
    recipient_id integer NOT NULL,
    body text NOT NULL,
    "timestamp" timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: message_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.message_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: message_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.message_id_seq OWNED BY public.messages.message_id;


--
-- Name: messages_message_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.messages_message_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: messages_message_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.messages_message_id_seq OWNED BY public.messages.message_id;


--
-- Name: node_notes; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.node_notes (
    id character varying NOT NULL,
    user_id integer,
    node_id character varying,
    action_index integer,
    note_text text,
    created_at timestamp without time zone DEFAULT now(),
    updated_at timestamp without time zone DEFAULT now()
);


--
-- Name: personality_assessments; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.personality_assessments (
    id integer NOT NULL,
    user_id integer NOT NULL,
    assessment_type character varying(50) NOT NULL,
    assessment_version character varying(20) NOT NULL,
    session_id uuid DEFAULT gen_random_uuid() NOT NULL,
    status character varying(20) DEFAULT 'in_progress'::character varying NOT NULL,
    started_at timestamp with time zone DEFAULT now() NOT NULL,
    completed_at timestamp with time zone,
    total_items integer,
    completed_items integer DEFAULT 0,
    validity_flags jsonb DEFAULT '{}'::jsonb,
    metadata jsonb DEFAULT '{}'::jsonb,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT personality_assessments_assessment_type_check CHECK (((assessment_type)::text = ANY (ARRAY[('big_five'::character varying)::text, ('hexaco'::character varying)::text, ('social_emotional'::character varying)::text, ('cognitive_style'::character varying)::text, ('values'::character varying)::text, ('onboarding'::character varying)::text]))),
    CONSTRAINT personality_assessments_status_check CHECK (((status)::text = ANY ((ARRAY['in_progress'::character varying, 'completed'::character varying, 'abandoned'::character varying])::text[]))),
    CONSTRAINT personality_assessments_total_items_check CHECK ((total_items > 0))
);


--
-- Name: personality_assessments_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.personality_assessments_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: personality_assessments_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.personality_assessments_id_seq OWNED BY public.personality_assessments.id;


--
-- Name: personality_embeddings; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.personality_embeddings (
    id integer NOT NULL,
    user_id integer NOT NULL,
    embedding_type character varying(50) NOT NULL,
    embedding_vector double precision[] NOT NULL,
    generation_method character varying(100) NOT NULL,
    model_version character varying(50) NOT NULL,
    quality_score double precision,
    source_data_hash character varying(64),
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT personality_embeddings_embedding_type_check CHECK (((embedding_type)::text = ANY ((ARRAY['personality_384'::character varying, 'big_five_384'::character varying, 'hexaco_384'::character varying, 'social_emotional_384'::character varying])::text[]))),
    CONSTRAINT personality_embeddings_quality_score_check CHECK (((quality_score >= (0)::double precision) AND (quality_score <= (1)::double precision)))
);


--
-- Name: personality_embeddings_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.personality_embeddings_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: personality_embeddings_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.personality_embeddings_id_seq OWNED BY public.personality_embeddings.id;


--
-- Name: personality_profiles; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.personality_profiles (
    id integer NOT NULL,
    user_id integer NOT NULL,
    assessment_id integer,
    profile_type character varying(50) NOT NULL,
    language character varying(10),
    scores jsonb NOT NULL,
    confidence_intervals jsonb,
    reliability_estimates jsonb,
    percentile_ranks jsonb,
    narrative_description text,
    assessment_version character varying(20) NOT NULL,
    computed_at timestamp with time zone DEFAULT now() NOT NULL,
    expires_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT personality_profiles_language_check CHECK (((language)::text = ANY ((ARRAY['en'::character varying, 'fr'::character varying])::text[]))),
    CONSTRAINT personality_profiles_profile_type_check CHECK (((profile_type)::text = ANY ((ARRAY['big_five'::character varying, 'hexaco'::character varying, 'social_emotional'::character varying, 'cognitive_style'::character varying, 'values'::character varying])::text[])))
);


--
-- Name: personality_profiles_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.personality_profiles_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: personality_profiles_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.personality_profiles_id_seq OWNED BY public.personality_profiles.id;


--
-- Name: personality_responses; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.personality_responses (
    id integer NOT NULL,
    assessment_id integer NOT NULL,
    item_id character varying(100) NOT NULL,
    item_type character varying(50) NOT NULL,
    response_value jsonb NOT NULL,
    response_time_ms integer,
    revision_count integer DEFAULT 0,
    confidence_level integer,
    behavioral_metadata jsonb DEFAULT '{}'::jsonb,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT personality_responses_confidence_level_check CHECK (((confidence_level >= 1) AND (confidence_level <= 5))),
    CONSTRAINT personality_responses_item_type_check CHECK (((item_type)::text = ANY ((ARRAY['likert'::character varying, 'scenario'::character varying, 'ranking'::character varying, 'open_ended'::character varying])::text[]))),
    CONSTRAINT personality_responses_response_time_ms_check CHECK ((response_time_ms >= 0))
);


--
-- Name: personality_responses_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.personality_responses_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: personality_responses_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.personality_responses_id_seq OWNED BY public.personality_responses.id;


--
-- Name: personality_trends; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.personality_trends (
    id integer NOT NULL,
    user_id integer NOT NULL,
    trait_name character varying(50) NOT NULL,
    trend_type character varying(30) NOT NULL,
    trend_parameters jsonb NOT NULL,
    trend_strength double precision,
    time_window_start timestamp with time zone NOT NULL,
    time_window_end timestamp with time zone NOT NULL,
    computed_at timestamp with time zone DEFAULT now() NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT personality_trends_trend_type_check CHECK (((trend_type)::text = ANY ((ARRAY['linear'::character varying, 'quadratic'::character varying, 'change_point'::character varying])::text[])))
);


--
-- Name: personality_trends_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.personality_trends_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: personality_trends_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.personality_trends_id_seq OWNED BY public.personality_trends.id;


--
-- Name: program_recommendations; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.program_recommendations (
    id integer NOT NULL,
    goal_id integer NOT NULL,
    program_name character varying(500) NOT NULL,
    institution character varying(500) NOT NULL,
    institution_type character varying(50),
    program_code character varying(100),
    duration character varying(100),
    admission_requirements jsonb,
    match_score numeric(3,2),
    cost_estimate numeric(10,2),
    location jsonb,
    intake_dates jsonb,
    created_at timestamp with time zone DEFAULT now(),
    CONSTRAINT check_match_score_range CHECK (((match_score >= (0)::numeric) AND (match_score <= (1)::numeric)))
);


--
-- Name: program_recommendations_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.program_recommendations_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: program_recommendations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.program_recommendations_id_seq OWNED BY public.program_recommendations.id;


--
-- Name: programs; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.programs (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    title character varying(255) NOT NULL,
    title_fr character varying(255),
    description text,
    description_fr text,
    institution_id uuid,
    program_type character varying(50) NOT NULL,
    level character varying(50) NOT NULL,
    field_of_study character varying(100),
    field_of_study_fr character varying(100),
    duration_months integer,
    credits numeric(5,2),
    semester_count integer,
    language character varying(10)[] DEFAULT ARRAY['en'::text],
    delivery_mode character varying(50) DEFAULT 'in-person'::character varying,
    cip_code character varying(10),
    isced_code character varying(10),
    noc_code character varying(10),
    program_code character varying(20),
    admission_requirements jsonb DEFAULT '[]'::jsonb,
    prerequisite_courses jsonb DEFAULT '[]'::jsonb,
    min_gpa numeric(3,2),
    language_requirements jsonb DEFAULT '{}'::jsonb,
    curriculum_outline jsonb DEFAULT '{}'::jsonb,
    internship_required boolean DEFAULT false,
    coop_available boolean DEFAULT false,
    thesis_required boolean DEFAULT false,
    career_outcomes jsonb DEFAULT '[]'::jsonb,
    employment_rate numeric(3,2),
    average_salary_range jsonb DEFAULT '{}'::jsonb,
    top_employers jsonb DEFAULT '[]'::jsonb,
    tuition_domestic numeric(10,2),
    tuition_international numeric(10,2),
    fees_additional jsonb DEFAULT '{}'::jsonb,
    financial_aid_available boolean DEFAULT false,
    scholarships_available jsonb DEFAULT '[]'::jsonb,
    application_deadline date,
    application_method character varying(100),
    application_fee numeric(8,2),
    application_requirements jsonb DEFAULT '[]'::jsonb,
    source_system character varying(50) NOT NULL,
    source_id character varying(100) NOT NULL,
    source_url text,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    last_synced timestamp with time zone DEFAULT now(),
    active boolean DEFAULT true,
    search_vector tsvector GENERATED ALWAYS AS (((setweight(to_tsvector('english'::regconfig, (COALESCE(title, ''::character varying))::text), 'A'::"char") || setweight(to_tsvector('english'::regconfig, COALESCE(description, ''::text)), 'B'::"char")) || setweight(to_tsvector('english'::regconfig, (COALESCE(field_of_study, ''::character varying))::text), 'C'::"char"))) STORED,
    CONSTRAINT programs_duration_months_check CHECK ((duration_months > 0)),
    CONSTRAINT programs_employment_rate_check CHECK (((employment_rate >= (0)::numeric) AND (employment_rate <= (1)::numeric))),
    CONSTRAINT programs_level_check CHECK (((level)::text = ANY ((ARRAY['certificate'::character varying, 'diploma'::character varying, 'associate'::character varying, 'bachelor'::character varying, 'master'::character varying, 'phd'::character varying, 'professional'::character varying])::text[])))
);


--
-- Name: psychological_insights; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.psychological_insights (
    id integer NOT NULL,
    user_id integer NOT NULL,
    course_id integer NOT NULL,
    insight_type character varying(100) NOT NULL,
    insight_value json NOT NULL,
    confidence_score double precision,
    evidence_source text,
    esco_mapping json,
    extracted_at timestamp with time zone DEFAULT now(),
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);


--
-- Name: psychological_insights_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.psychological_insights_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: psychological_insights_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.psychological_insights_id_seq OWNED BY public.psychological_insights.id;


--
-- Name: public_feed; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.public_feed (
    id integer NOT NULL,
    event_type character varying NOT NULL,
    domain character varying,
    "timestamp" timestamp without time zone DEFAULT now()
);


--
-- Name: public_feed_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.public_feed_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: public_feed_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.public_feed_id_seq OWNED BY public.public_feed.id;


--
-- Name: saved_jobs; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.saved_jobs (
    id integer NOT NULL,
    user_id integer NOT NULL,
    esco_id character varying(255) NOT NULL,
    job_title character varying(500) NOT NULL,
    skills_required jsonb,
    discovery_source character varying(50) DEFAULT 'tree'::character varying,
    tree_graph_id uuid,
    relevance_score numeric(3,2),
    saved_at timestamp with time zone DEFAULT now(),
    metadata jsonb DEFAULT '{}'::jsonb
);


--
-- Name: saved_jobs_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.saved_jobs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: saved_jobs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.saved_jobs_id_seq OWNED BY public.saved_jobs.id;


--
-- Name: saved_recommendations; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.saved_recommendations (
    id integer NOT NULL,
    user_id integer NOT NULL,
    oasis_code character varying NOT NULL,
    label character varying NOT NULL,
    description text,
    main_duties text,
    role_creativity double precision,
    role_leadership double precision,
    role_digital_literacy double precision,
    role_critical_thinking double precision,
    role_problem_solving double precision,
    saved_at timestamp with time zone DEFAULT now() NOT NULL,
    analytical_thinking double precision,
    attention_to_detail double precision,
    collaboration double precision,
    adaptability double precision,
    independence double precision,
    evaluation double precision,
    decision_making double precision,
    stress_tolerance double precision,
    all_fields json,
    personal_analysis text,
    entry_qualifications text,
    suggested_improvements text,
    source_type character varying(20) DEFAULT 'esco'::character varying,
    graphsage_top_skills jsonb,
    feasibility_analysis jsonb,
    time_to_qualification integer,
    education_required character varying(100),
    match_score numeric(3,2),
    source_tool character varying(50),
    conversation_id integer,
    component_type character varying(50),
    component_data jsonb,
    interaction_metadata jsonb
);


--
-- Name: COLUMN saved_recommendations.source_type; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.saved_recommendations.source_type IS 'Job data source: esco or oasis';


--
-- Name: COLUMN saved_recommendations.graphsage_top_skills; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.saved_recommendations.graphsage_top_skills IS 'Top skills extracted via GraphSAGE for OaSIS jobs';


--
-- Name: saved_recommendations_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.saved_recommendations_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: saved_recommendations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.saved_recommendations_id_seq OWNED BY public.saved_recommendations.id;


--
-- Name: skills_to_domains; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.skills_to_domains (
    skill_id character varying NOT NULL,
    domain character varying
);


--
-- Name: strengths_reflection_responses; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.strengths_reflection_responses (
    id integer NOT NULL,
    user_id integer NOT NULL,
    question_id integer NOT NULL,
    prompt_text text NOT NULL,
    response text,
    response_time_ms integer,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: strengths_reflection_responses_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.strengths_reflection_responses_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: strengths_reflection_responses_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.strengths_reflection_responses_id_seq OWNED BY public.strengths_reflection_responses.id;


--
-- Name: suggested_peers; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.suggested_peers (
    user_id integer NOT NULL,
    suggested_id integer NOT NULL,
    similarity double precision,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone
);


--
-- Name: tool_invocations; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.tool_invocations (
    id integer NOT NULL,
    conversation_id integer,
    tool_name character varying(50) NOT NULL,
    input_params jsonb,
    output_data jsonb,
    execution_time_ms integer,
    success character varying(20),
    error_message character varying(500),
    relevance_score double precision,
    user_id integer,
    created_at timestamp with time zone DEFAULT now()
);


--
-- Name: tool_invocations_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.tool_invocations_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: tool_invocations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.tool_invocations_id_seq OWNED BY public.tool_invocations.id;


--
-- Name: tree_generations; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.tree_generations (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id integer NOT NULL,
    anchor_skills jsonb NOT NULL,
    graph_data jsonb NOT NULL,
    generation_options jsonb,
    created_at timestamp with time zone DEFAULT now(),
    expires_at timestamp with time zone,
    access_count integer DEFAULT 0,
    last_accessed_at timestamp with time zone
);


--
-- Name: tree_paths; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.tree_paths (
    id uuid NOT NULL,
    user_id integer,
    tree_type character varying,
    tree_json json,
    name character varying,
    created_at timestamp without time zone DEFAULT now()
);


--
-- Name: user_chat_analytics; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.user_chat_analytics (
    id integer NOT NULL,
    user_id integer NOT NULL,
    date date NOT NULL,
    messages_sent integer DEFAULT 0,
    conversations_started integer DEFAULT 0,
    total_tokens_used integer DEFAULT 0,
    avg_response_time_ms integer DEFAULT 0,
    most_used_category_id integer,
    created_at timestamp with time zone DEFAULT now()
);


--
-- Name: user_chat_analytics_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.user_chat_analytics_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: user_chat_analytics_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.user_chat_analytics_id_seq OWNED BY public.user_chat_analytics.id;


--
-- Name: user_journey_milestones; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.user_journey_milestones (
    id integer NOT NULL,
    user_id integer,
    milestone_type character varying(50) NOT NULL,
    milestone_data jsonb NOT NULL,
    title character varying(255) NOT NULL,
    description text,
    category character varying(50),
    progress_percentage double precision DEFAULT 0.0,
    status character varying(20) DEFAULT 'active'::character varying,
    source_type character varying(50),
    source_id integer,
    conversation_id integer,
    achieved_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    ai_insights jsonb,
    next_steps jsonb
);


--
-- Name: user_journey_milestones_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.user_journey_milestones_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: user_journey_milestones_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.user_journey_milestones_id_seq OWNED BY public.user_journey_milestones.id;


--
-- Name: user_notes; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.user_notes (
    id integer NOT NULL,
    user_id integer NOT NULL,
    saved_recommendation_id integer,
    content text NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: user_notes_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.user_notes_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: user_notes_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.user_notes_id_seq OWNED BY public.user_notes.id;


--
-- Name: user_profiles; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.user_profiles (
    id integer NOT NULL,
    user_id integer,
    favorite_movie character varying(255),
    favorite_book character varying(255),
    favorite_celebrities text,
    learning_style character varying(50),
    interests text,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone,
    name character varying,
    age integer,
    sex character varying,
    major character varying,
    year integer,
    gpa double precision,
    hobbies text,
    country character varying,
    state_province character varying,
    unique_quality text,
    story text,
    job_title character varying(255),
    industry character varying(255),
    years_experience integer,
    education_level character varying(255),
    career_goals text,
    skills text[],
    embedding public.vector(1024),
    personal_analysis text,
    oasis_profile text,
    oasis_embedding public.vector(384),
    esco_occupation_profile text,
    esco_skillsgroup_profile text,
    esco_skill_profile text,
    esco_full_profile text,
    esco_embedding_occupation public.vector(384),
    esco_embedding_skillsgroup public.vector(384),
    esco_embedding_skill public.vector(384),
    esco_embedding public.vector(384),
    top3_recommendedjobs character varying,
    philosophical_description character varying,
    personality_embedding double precision[],
    big_five_embedding double precision[],
    social_emotional_embedding double precision[],
    cognitive_style_embedding double precision[],
    values_embedding double precision[],
    compatibility_vector jsonb,
    completed_courses text[],
    certifications jsonb DEFAULT '[]'::jsonb,
    portfolio_url character varying(500),
    research_experience boolean DEFAULT false,
    internship_experience jsonb DEFAULT '[]'::jsonb,
    expected_graduation_date date,
    current_debt numeric(10,2) DEFAULT 0,
    financial_support jsonb DEFAULT '{}'::jsonb,
    minimum_salary_requirement numeric(10,2),
    relocation_willingness boolean DEFAULT false,
    available_study_years integer DEFAULT 4,
    part_time_work_needed boolean DEFAULT false,
    family_obligations jsonb DEFAULT '{}'::jsonb,
    career_urgency integer,
    skill_learning_rate jsonb DEFAULT '{}'::jsonb,
    preferred_learning_methods text[] DEFAULT ARRAY['online'::text, 'classroom'::text],
    skill_confidence_levels jsonb DEFAULT '{}'::jsonb,
    CONSTRAINT user_profiles_career_urgency_check CHECK (((career_urgency >= 1) AND (career_urgency <= 5)))
);


--
-- Name: COLUMN user_profiles.embedding; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.user_profiles.embedding IS '768-dimensional embedding vector from all-mpnet-base-v2 model';


--
-- Name: COLUMN user_profiles.career_urgency; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.user_profiles.career_urgency IS 'How urgently user needs income: 1=relaxed, 5=urgent';


--
-- Name: COLUMN user_profiles.skill_learning_rate; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.user_profiles.skill_learning_rate IS 'Self-assessed learning speed per skill (1-5 scale)';


--
-- Name: user_profiles_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.user_profiles_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: user_profiles_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.user_profiles_id_seq OWNED BY public.user_profiles.id;


--
-- Name: user_program_preferences; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.user_program_preferences (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    user_id integer,
    preferred_countries character varying(2)[] DEFAULT ARRAY['CA'::text],
    preferred_provinces character varying(50)[] DEFAULT ARRAY[]::character varying[],
    preferred_cities character varying(100)[] DEFAULT ARRAY[]::character varying[],
    max_distance_km integer,
    willing_to_relocate boolean DEFAULT false,
    preferred_languages character varying(10)[] DEFAULT ARRAY['en'::text],
    program_types character varying(50)[] DEFAULT ARRAY[]::character varying[],
    program_levels character varying(50)[] DEFAULT ARRAY[]::character varying[],
    fields_of_interest character varying(100)[] DEFAULT ARRAY[]::character varying[],
    delivery_modes character varying(50)[] DEFAULT ARRAY['in-person'::text],
    max_duration_months integer,
    min_duration_months integer,
    preferred_start_terms character varying(20)[] DEFAULT ARRAY['fall'::text],
    part_time_acceptable boolean DEFAULT false,
    max_budget numeric(10,2),
    budget_currency character varying(3) DEFAULT 'CAD'::character varying,
    financial_aid_required boolean DEFAULT false,
    scholarship_priority boolean DEFAULT false,
    min_employment_rate numeric(3,2),
    internship_preference character varying(20) DEFAULT 'optional'::character varying,
    coop_preference character varying(20) DEFAULT 'optional'::character varying,
    target_career_fields character varying(100)[] DEFAULT ARRAY[]::character varying[],
    salary_expectations jsonb DEFAULT '{}'::jsonb,
    work_environment_preferences jsonb DEFAULT '{}'::jsonb,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);


--
-- Name: user_progress; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.user_progress (
    id character varying DEFAULT gen_random_uuid() NOT NULL,
    user_id integer,
    total_xp integer,
    level integer,
    last_completed_node character varying,
    completed_actions json,
    last_updated timestamp without time zone DEFAULT now()
);


--
-- Name: user_recommendations; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.user_recommendations (
    id integer NOT NULL,
    user_id integer,
    oasis_code character varying NOT NULL,
    label character varying NOT NULL,
    swiped_right boolean DEFAULT false,
    created_at timestamp with time zone DEFAULT now()
);


--
-- Name: user_recommendations_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.user_recommendations_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: user_recommendations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.user_recommendations_id_seq OWNED BY public.user_recommendations.id;


--
-- Name: user_representation; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.user_representation (
    id integer NOT NULL,
    user_id integer NOT NULL,
    generated_at timestamp with time zone DEFAULT now() NOT NULL,
    source character varying(50) NOT NULL,
    format_version character varying(10) DEFAULT 'v1'::character varying NOT NULL,
    data jsonb NOT NULL,
    summary text,
    notes text,
    avatar_description text,
    avatar_image_url text,
    avatar_name text
);


--
-- Name: user_representation_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.user_representation_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: user_representation_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.user_representation_id_seq OWNED BY public.user_representation.id;


--
-- Name: user_skill_graphs; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.user_skill_graphs (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id integer,
    root_skill_id character varying NOT NULL,
    graph_name text,
    created_at timestamp without time zone DEFAULT now()
);


--
-- Name: user_skill_nodes; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.user_skill_nodes (
    id integer NOT NULL,
    graph_id uuid,
    skill_id character varying NOT NULL,
    skill_label text NOT NULL,
    challenge text,
    xp_reward integer DEFAULT 10,
    visible boolean DEFAULT true,
    revealed boolean DEFAULT false,
    state character varying DEFAULT 'locked'::character varying,
    notes text,
    unlocked_at timestamp without time zone
);


--
-- Name: user_skill_nodes_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.user_skill_nodes_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: user_skill_nodes_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.user_skill_nodes_id_seq OWNED BY public.user_skill_nodes.id;


--
-- Name: user_skill_trees; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.user_skill_trees (
    id integer NOT NULL,
    user_id integer,
    graph_id uuid NOT NULL,
    tree_data jsonb NOT NULL,
    created_at timestamp without time zone DEFAULT now()
);


--
-- Name: user_skill_trees_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.user_skill_trees_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: user_skill_trees_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.user_skill_trees_id_seq OWNED BY public.user_skill_trees.id;


--
-- Name: user_skills; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.user_skills (
    id integer NOT NULL,
    user_id integer,
    creativity double precision,
    leadership double precision,
    digital_literacy double precision,
    critical_thinking double precision,
    problem_solving double precision,
    last_updated timestamp with time zone DEFAULT now(),
    analytical_thinking double precision,
    attention_to_detail double precision,
    collaboration double precision,
    adaptability double precision,
    independence double precision,
    evaluation double precision,
    decision_making double precision,
    stress_tolerance double precision
);


--
-- Name: COLUMN user_skills.analytical_thinking; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.user_skills.analytical_thinking IS 'User''s analytical thinking score (0-5)';


--
-- Name: COLUMN user_skills.attention_to_detail; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.user_skills.attention_to_detail IS 'User''s attention to detail score (0-5)';


--
-- Name: COLUMN user_skills.collaboration; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.user_skills.collaboration IS 'User''s collaboration score (0-5)';


--
-- Name: COLUMN user_skills.adaptability; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.user_skills.adaptability IS 'User''s adaptability score (0-5)';


--
-- Name: COLUMN user_skills.independence; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.user_skills.independence IS 'User''s independence score (0-5)';


--
-- Name: COLUMN user_skills.evaluation; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.user_skills.evaluation IS 'User''s evaluation score (0-5)';


--
-- Name: COLUMN user_skills.decision_making; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.user_skills.decision_making IS 'User''s decision making score (0-5)';


--
-- Name: COLUMN user_skills.stress_tolerance; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.user_skills.stress_tolerance IS 'User''s stress tolerance score (0-5)';


--
-- Name: user_skills_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.user_skills_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: user_skills_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.user_skills_id_seq OWNED BY public.user_skills.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.users (
    id integer NOT NULL,
    email character varying NOT NULL,
    hashed_password character varying NOT NULL,
    created_at timestamp with time zone DEFAULT now()
);


--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: behavioral_signals id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.behavioral_signals ALTER COLUMN id SET DEFAULT nextval('public.behavioral_signals_id_seq'::regclass);


--
-- Name: career_fit_analyses id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.career_fit_analyses ALTER COLUMN id SET DEFAULT nextval('public.career_fit_analyses_id_seq'::regclass);


--
-- Name: career_goals id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.career_goals ALTER COLUMN id SET DEFAULT nextval('public.career_goals_id_seq'::regclass);


--
-- Name: career_milestones id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.career_milestones ALTER COLUMN id SET DEFAULT nextval('public.career_milestones_id_seq'::regclass);


--
-- Name: career_profile_aggregates id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.career_profile_aggregates ALTER COLUMN id SET DEFAULT nextval('public.career_profile_aggregates_id_seq'::regclass);


--
-- Name: career_signals id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.career_signals ALTER COLUMN id SET DEFAULT nextval('public.career_signals_id_seq'::regclass);


--
-- Name: chat_messages id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.chat_messages ALTER COLUMN id SET DEFAULT nextval('public.chat_messages_id_seq'::regclass);


--
-- Name: conversation_categories id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.conversation_categories ALTER COLUMN id SET DEFAULT nextval('public.conversation_categories_id_seq'::regclass);


--
-- Name: conversation_logs id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.conversation_logs ALTER COLUMN id SET DEFAULT nextval('public.conversation_logs_id_seq'::regclass);


--
-- Name: conversation_shares id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.conversation_shares ALTER COLUMN id SET DEFAULT nextval('public.conversation_shares_id_seq'::regclass);


--
-- Name: conversations id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.conversations ALTER COLUMN id SET DEFAULT nextval('public.conversations_id_seq'::regclass);


--
-- Name: courses id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.courses ALTER COLUMN id SET DEFAULT nextval('public.courses_id_seq'::regclass);


--
-- Name: developmental_milestones id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.developmental_milestones ALTER COLUMN id SET DEFAULT nextval('public.developmental_milestones_id_seq'::regclass);


--
-- Name: esco_job_requirements id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.esco_job_requirements ALTER COLUMN id SET DEFAULT nextval('public.esco_job_requirements_id_seq'::regclass);


--
-- Name: gca_holland_questions id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.gca_holland_questions ALTER COLUMN id SET DEFAULT nextval('public.gca_holland_questions_id_seq'::regclass);


--
-- Name: llm_descriptions id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.llm_descriptions ALTER COLUMN id SET DEFAULT nextval('public.llm_descriptions_id_seq'::regclass);


--
-- Name: message_components id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.message_components ALTER COLUMN id SET DEFAULT nextval('public.message_components_id_seq'::regclass);


--
-- Name: messages message_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.messages ALTER COLUMN message_id SET DEFAULT nextval('public.message_id_seq'::regclass);


--
-- Name: personality_assessments id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.personality_assessments ALTER COLUMN id SET DEFAULT nextval('public.personality_assessments_id_seq'::regclass);


--
-- Name: personality_embeddings id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.personality_embeddings ALTER COLUMN id SET DEFAULT nextval('public.personality_embeddings_id_seq'::regclass);


--
-- Name: personality_profiles id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.personality_profiles ALTER COLUMN id SET DEFAULT nextval('public.personality_profiles_id_seq'::regclass);


--
-- Name: personality_responses id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.personality_responses ALTER COLUMN id SET DEFAULT nextval('public.personality_responses_id_seq'::regclass);


--
-- Name: personality_trends id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.personality_trends ALTER COLUMN id SET DEFAULT nextval('public.personality_trends_id_seq'::regclass);


--
-- Name: program_recommendations id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.program_recommendations ALTER COLUMN id SET DEFAULT nextval('public.program_recommendations_id_seq'::regclass);


--
-- Name: psychological_insights id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.psychological_insights ALTER COLUMN id SET DEFAULT nextval('public.psychological_insights_id_seq'::regclass);


--
-- Name: public_feed id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.public_feed ALTER COLUMN id SET DEFAULT nextval('public.public_feed_id_seq'::regclass);


--
-- Name: saved_jobs id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.saved_jobs ALTER COLUMN id SET DEFAULT nextval('public.saved_jobs_id_seq'::regclass);


--
-- Name: saved_recommendations id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.saved_recommendations ALTER COLUMN id SET DEFAULT nextval('public.saved_recommendations_id_seq'::regclass);


--
-- Name: strengths_reflection_responses id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.strengths_reflection_responses ALTER COLUMN id SET DEFAULT nextval('public.strengths_reflection_responses_id_seq'::regclass);


--
-- Name: tool_invocations id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tool_invocations ALTER COLUMN id SET DEFAULT nextval('public.tool_invocations_id_seq'::regclass);


--
-- Name: user_chat_analytics id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_chat_analytics ALTER COLUMN id SET DEFAULT nextval('public.user_chat_analytics_id_seq'::regclass);


--
-- Name: user_journey_milestones id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_journey_milestones ALTER COLUMN id SET DEFAULT nextval('public.user_journey_milestones_id_seq'::regclass);


--
-- Name: user_notes id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_notes ALTER COLUMN id SET DEFAULT nextval('public.user_notes_id_seq'::regclass);


--
-- Name: user_profiles id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_profiles ALTER COLUMN id SET DEFAULT nextval('public.user_profiles_id_seq'::regclass);


--
-- Name: user_recommendations id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_recommendations ALTER COLUMN id SET DEFAULT nextval('public.user_recommendations_id_seq'::regclass);


--
-- Name: user_representation id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_representation ALTER COLUMN id SET DEFAULT nextval('public.user_representation_id_seq'::regclass);


--
-- Name: user_skill_nodes id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_skill_nodes ALTER COLUMN id SET DEFAULT nextval('public.user_skill_nodes_id_seq'::regclass);


--
-- Name: user_skill_trees id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_skill_trees ALTER COLUMN id SET DEFAULT nextval('public.user_skill_trees_id_seq'::regclass);


--
-- Name: user_skills id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_skills ALTER COLUMN id SET DEFAULT nextval('public.user_skills_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: behavioral_signals behavioral_signals_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.behavioral_signals
    ADD CONSTRAINT behavioral_signals_pkey PRIMARY KEY (id);


--
-- Name: career_fit_analyses career_fit_analyses_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.career_fit_analyses
    ADD CONSTRAINT career_fit_analyses_pkey PRIMARY KEY (id);


--
-- Name: career_fit_analyses career_fit_analyses_user_id_saved_recommendation_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.career_fit_analyses
    ADD CONSTRAINT career_fit_analyses_user_id_saved_recommendation_id_key UNIQUE (user_id, saved_recommendation_id);


--
-- Name: career_goals career_goals_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.career_goals
    ADD CONSTRAINT career_goals_pkey PRIMARY KEY (id);


--
-- Name: career_milestones career_milestones_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.career_milestones
    ADD CONSTRAINT career_milestones_pkey PRIMARY KEY (id);


--
-- Name: career_profile_aggregates career_profile_aggregates_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.career_profile_aggregates
    ADD CONSTRAINT career_profile_aggregates_pkey PRIMARY KEY (id);


--
-- Name: career_signals career_signals_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.career_signals
    ADD CONSTRAINT career_signals_pkey PRIMARY KEY (id);


--
-- Name: chat_messages chat_messages_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.chat_messages
    ADD CONSTRAINT chat_messages_pkey PRIMARY KEY (id);


--
-- Name: conversation_categories conversation_categories_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.conversation_categories
    ADD CONSTRAINT conversation_categories_pkey PRIMARY KEY (id);


--
-- Name: conversation_categories conversation_categories_user_id_name_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.conversation_categories
    ADD CONSTRAINT conversation_categories_user_id_name_key UNIQUE (user_id, name);


--
-- Name: conversation_logs conversation_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.conversation_logs
    ADD CONSTRAINT conversation_logs_pkey PRIMARY KEY (id);


--
-- Name: conversation_shares conversation_shares_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.conversation_shares
    ADD CONSTRAINT conversation_shares_pkey PRIMARY KEY (id);


--
-- Name: conversation_shares conversation_shares_share_token_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.conversation_shares
    ADD CONSTRAINT conversation_shares_share_token_key UNIQUE (share_token);


--
-- Name: conversations conversations_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.conversations
    ADD CONSTRAINT conversations_pkey PRIMARY KEY (id);


--
-- Name: courses courses_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.courses
    ADD CONSTRAINT courses_pkey PRIMARY KEY (id);


--
-- Name: developmental_milestones developmental_milestones_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.developmental_milestones
    ADD CONSTRAINT developmental_milestones_pkey PRIMARY KEY (id);


--
-- Name: esco_job_requirements esco_job_requirements_oasis_code_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.esco_job_requirements
    ADD CONSTRAINT esco_job_requirements_oasis_code_key UNIQUE (oasis_code);


--
-- Name: esco_job_requirements esco_job_requirements_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.esco_job_requirements
    ADD CONSTRAINT esco_job_requirements_pkey PRIMARY KEY (id);


--
-- Name: gca_choices gca_choices_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.gca_choices
    ADD CONSTRAINT gca_choices_pkey PRIMARY KEY (id);


--
-- Name: gca_holland_questions gca_holland_questions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.gca_holland_questions
    ADD CONSTRAINT gca_holland_questions_pkey PRIMARY KEY (id);


--
-- Name: gca_personalities gca_personalities_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.gca_personalities
    ADD CONSTRAINT gca_personalities_pkey PRIMARY KEY (id);


--
-- Name: gca_questions gca_questions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.gca_questions
    ADD CONSTRAINT gca_questions_pkey PRIMARY KEY (id);


--
-- Name: gca_results gca_results_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.gca_results
    ADD CONSTRAINT gca_results_pkey PRIMARY KEY (id);


--
-- Name: gca_tests gca_tests_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.gca_tests
    ADD CONSTRAINT gca_tests_pkey PRIMARY KEY (id);


--
-- Name: gca_users_answers gca_users_answers_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.gca_users_answers
    ADD CONSTRAINT gca_users_answers_pkey PRIMARY KEY (id);


--
-- Name: institutions institutions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.institutions
    ADD CONSTRAINT institutions_pkey PRIMARY KEY (id);


--
-- Name: institutions institutions_source_system_source_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.institutions
    ADD CONSTRAINT institutions_source_system_source_id_key UNIQUE (source_system, source_id);


--
-- Name: llm_descriptions llm_descriptions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.llm_descriptions
    ADD CONSTRAINT llm_descriptions_pkey PRIMARY KEY (id);


--
-- Name: message_components message_components_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.message_components
    ADD CONSTRAINT message_components_pkey PRIMARY KEY (id);


--
-- Name: messages messages_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.messages
    ADD CONSTRAINT messages_pkey PRIMARY KEY (message_id);


--
-- Name: node_notes node_notes_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.node_notes
    ADD CONSTRAINT node_notes_pkey PRIMARY KEY (id);


--
-- Name: personality_assessments personality_assessments_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.personality_assessments
    ADD CONSTRAINT personality_assessments_pkey PRIMARY KEY (id);


--
-- Name: personality_assessments personality_assessments_session_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.personality_assessments
    ADD CONSTRAINT personality_assessments_session_id_key UNIQUE (session_id);


--
-- Name: personality_embeddings personality_embeddings_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.personality_embeddings
    ADD CONSTRAINT personality_embeddings_pkey PRIMARY KEY (id);


--
-- Name: personality_profiles personality_profiles_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.personality_profiles
    ADD CONSTRAINT personality_profiles_pkey PRIMARY KEY (id);


--
-- Name: personality_profiles personality_profiles_user_id_profile_type_assessment_versio_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.personality_profiles
    ADD CONSTRAINT personality_profiles_user_id_profile_type_assessment_versio_key UNIQUE (user_id, profile_type, assessment_version);


--
-- Name: personality_responses personality_responses_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.personality_responses
    ADD CONSTRAINT personality_responses_pkey PRIMARY KEY (id);


--
-- Name: personality_trends personality_trends_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.personality_trends
    ADD CONSTRAINT personality_trends_pkey PRIMARY KEY (id);


--
-- Name: program_recommendations program_recommendations_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.program_recommendations
    ADD CONSTRAINT program_recommendations_pkey PRIMARY KEY (id);


--
-- Name: programs programs_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.programs
    ADD CONSTRAINT programs_pkey PRIMARY KEY (id);


--
-- Name: programs programs_source_system_source_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.programs
    ADD CONSTRAINT programs_source_system_source_id_key UNIQUE (source_system, source_id);


--
-- Name: psychological_insights psychological_insights_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.psychological_insights
    ADD CONSTRAINT psychological_insights_pkey PRIMARY KEY (id);


--
-- Name: public_feed public_feed_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.public_feed
    ADD CONSTRAINT public_feed_pkey PRIMARY KEY (id);


--
-- Name: saved_jobs saved_jobs_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.saved_jobs
    ADD CONSTRAINT saved_jobs_pkey PRIMARY KEY (id);


--
-- Name: saved_recommendations saved_recommendations_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.saved_recommendations
    ADD CONSTRAINT saved_recommendations_pkey PRIMARY KEY (id);


--
-- Name: skills_to_domains skills_to_domains_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.skills_to_domains
    ADD CONSTRAINT skills_to_domains_pkey PRIMARY KEY (skill_id);


--
-- Name: strengths_reflection_responses strengths_reflection_responses_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.strengths_reflection_responses
    ADD CONSTRAINT strengths_reflection_responses_pkey PRIMARY KEY (id);


--
-- Name: suggested_peers suggested_peers_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.suggested_peers
    ADD CONSTRAINT suggested_peers_pkey PRIMARY KEY (user_id, suggested_id);


--
-- Name: tool_invocations tool_invocations_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tool_invocations
    ADD CONSTRAINT tool_invocations_pkey PRIMARY KEY (id);


--
-- Name: tree_generations tree_generations_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tree_generations
    ADD CONSTRAINT tree_generations_pkey PRIMARY KEY (id);


--
-- Name: tree_paths tree_paths_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tree_paths
    ADD CONSTRAINT tree_paths_pkey PRIMARY KEY (id);


--
-- Name: llm_descriptions uq_node_user_description; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.llm_descriptions
    ADD CONSTRAINT uq_node_user_description UNIQUE (node_id, user_id);


--
-- Name: saved_jobs uq_user_job; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.saved_jobs
    ADD CONSTRAINT uq_user_job UNIQUE (user_id, esco_id);


--
-- Name: saved_recommendations uq_user_oasis_code; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.saved_recommendations
    ADD CONSTRAINT uq_user_oasis_code UNIQUE (user_id, oasis_code);


--
-- Name: user_chat_analytics user_chat_analytics_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_chat_analytics
    ADD CONSTRAINT user_chat_analytics_pkey PRIMARY KEY (id);


--
-- Name: user_chat_analytics user_chat_analytics_user_id_date_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_chat_analytics
    ADD CONSTRAINT user_chat_analytics_user_id_date_key UNIQUE (user_id, date);


--
-- Name: user_journey_milestones user_journey_milestones_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_journey_milestones
    ADD CONSTRAINT user_journey_milestones_pkey PRIMARY KEY (id);


--
-- Name: user_notes user_notes_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_notes
    ADD CONSTRAINT user_notes_pkey PRIMARY KEY (id);


--
-- Name: user_profiles user_profiles_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_profiles
    ADD CONSTRAINT user_profiles_pkey PRIMARY KEY (id);


--
-- Name: user_profiles user_profiles_user_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_profiles
    ADD CONSTRAINT user_profiles_user_id_key UNIQUE (user_id);


--
-- Name: user_program_preferences user_program_preferences_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_program_preferences
    ADD CONSTRAINT user_program_preferences_pkey PRIMARY KEY (id);


--
-- Name: user_program_preferences user_program_preferences_user_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_program_preferences
    ADD CONSTRAINT user_program_preferences_user_id_key UNIQUE (user_id);


--
-- Name: user_progress user_progress_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_progress
    ADD CONSTRAINT user_progress_pkey PRIMARY KEY (id);


--
-- Name: user_progress user_progress_user_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_progress
    ADD CONSTRAINT user_progress_user_id_key UNIQUE (user_id);


--
-- Name: user_recommendations user_recommendations_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_recommendations
    ADD CONSTRAINT user_recommendations_pkey PRIMARY KEY (id);


--
-- Name: user_representation user_representation_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_representation
    ADD CONSTRAINT user_representation_pkey PRIMARY KEY (id);


--
-- Name: user_skill_graphs user_skill_graphs_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_skill_graphs
    ADD CONSTRAINT user_skill_graphs_pkey PRIMARY KEY (id);


--
-- Name: user_skill_nodes user_skill_nodes_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_skill_nodes
    ADD CONSTRAINT user_skill_nodes_pkey PRIMARY KEY (id);


--
-- Name: user_skill_trees user_skill_trees_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_skill_trees
    ADD CONSTRAINT user_skill_trees_pkey PRIMARY KEY (id);


--
-- Name: user_skills user_skills_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_skills
    ADD CONSTRAINT user_skills_pkey PRIMARY KEY (id);


--
-- Name: user_skills user_skills_user_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_skills
    ADD CONSTRAINT user_skills_user_id_key UNIQUE (user_id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: fk_gca_choices_question_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX fk_gca_choices_question_id ON public.gca_choices USING btree (question_id);


--
-- Name: fk_questions_test_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX fk_questions_test_id ON public.gca_questions USING btree (test_id);


--
-- Name: fk_users_answers_choice_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX fk_users_answers_choice_id ON public.gca_users_answers USING btree (choice_id);


--
-- Name: fk_users_answers_question_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX fk_users_answers_question_id ON public.gca_users_answers USING btree (question_id);


--
-- Name: fk_users_answers_test_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX fk_users_answers_test_id ON public.gca_users_answers USING btree (test_id);


--
-- Name: fk_users_answers_user_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX fk_users_answers_user_id ON public.gca_users_answers USING btree (user_id);


--
-- Name: idx_assessments_session; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_assessments_session ON public.personality_assessments USING btree (session_id);


--
-- Name: idx_assessments_user; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_assessments_user ON public.personality_assessments USING btree (user_id);


--
-- Name: idx_chat_messages_conversation_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_chat_messages_conversation_id ON public.chat_messages USING btree (conversation_id);


--
-- Name: idx_chat_messages_created_at; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_chat_messages_created_at ON public.chat_messages USING btree (created_at);


--
-- Name: idx_conversation_categories_user_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_conversation_categories_user_id ON public.conversation_categories USING btree (user_id);


--
-- Name: idx_conversation_shares_conversation; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_conversation_shares_conversation ON public.conversation_shares USING btree (conversation_id);


--
-- Name: idx_conversation_shares_token; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_conversation_shares_token ON public.conversation_shares USING btree (share_token);


--
-- Name: idx_conversations_created_at; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_conversations_created_at ON public.conversations USING btree (created_at);


--
-- Name: idx_conversations_is_archived; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_conversations_is_archived ON public.conversations USING btree (is_archived);


--
-- Name: idx_conversations_is_favorite; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_conversations_is_favorite ON public.conversations USING btree (is_favorite);


--
-- Name: idx_conversations_user_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_conversations_user_id ON public.conversations USING btree (user_id);


--
-- Name: idx_embeddings_type; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_embeddings_type ON public.personality_embeddings USING btree (embedding_type);


--
-- Name: idx_embeddings_user; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_embeddings_user ON public.personality_embeddings USING btree (user_id);


--
-- Name: idx_esco_requirements_code; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_esco_requirements_code ON public.esco_job_requirements USING btree (oasis_code);


--
-- Name: idx_esco_requirements_education; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_esco_requirements_education ON public.esco_job_requirements USING btree (entry_level_education);


--
-- Name: idx_esco_requirements_sector; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_esco_requirements_sector ON public.esco_job_requirements USING btree (sector_classification);


--
-- Name: idx_fit_analyses_recommendation; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_fit_analyses_recommendation ON public.career_fit_analyses USING btree (saved_recommendation_id);


--
-- Name: idx_fit_analyses_scores; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_fit_analyses_scores ON public.career_fit_analyses USING btree (overall_fit_score DESC);


--
-- Name: idx_fit_analyses_user; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_fit_analyses_user ON public.career_fit_analyses USING btree (user_id);


--
-- Name: idx_gca_results_user_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_gca_results_user_id ON public.gca_results USING btree (user_id);


--
-- Name: idx_institutions_active; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_institutions_active ON public.institutions USING btree (active) WHERE (active = true);


--
-- Name: idx_institutions_location; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_institutions_location ON public.institutions USING btree (country, province_state, city);


--
-- Name: idx_institutions_source; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_institutions_source ON public.institutions USING btree (source_system, source_id);


--
-- Name: idx_institutions_type; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_institutions_type ON public.institutions USING btree (institution_type);


--
-- Name: idx_llm_descriptions_node_user; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_llm_descriptions_node_user ON public.llm_descriptions USING btree (node_id, user_id);


--
-- Name: idx_milestones_user; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_milestones_user ON public.developmental_milestones USING btree (user_id);


--
-- Name: idx_profiles_type; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_profiles_type ON public.personality_profiles USING btree (profile_type);


--
-- Name: idx_profiles_user; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_profiles_user ON public.personality_profiles USING btree (user_id);


--
-- Name: idx_programs_active; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_programs_active ON public.programs USING btree (active) WHERE (active = true);


--
-- Name: idx_programs_cip; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_programs_cip ON public.programs USING btree (cip_code) WHERE (cip_code IS NOT NULL);


--
-- Name: idx_programs_institution; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_programs_institution ON public.programs USING btree (institution_id);


--
-- Name: idx_programs_search; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_programs_search ON public.programs USING gin (search_vector);


--
-- Name: idx_programs_source; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_programs_source ON public.programs USING btree (source_system, source_id);


--
-- Name: idx_programs_title_trgm; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_programs_title_trgm ON public.programs USING gin (title public.gin_trgm_ops);


--
-- Name: idx_programs_type_level; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_programs_type_level ON public.programs USING btree (program_type, level);


--
-- Name: idx_responses_assessment; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_responses_assessment ON public.personality_responses USING btree (assessment_id);


--
-- Name: idx_saved_jobs_user_source; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_saved_jobs_user_source ON public.saved_jobs USING btree (user_id, discovery_source);


--
-- Name: idx_signals_type; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_signals_type ON public.behavioral_signals USING btree (signal_type);


--
-- Name: idx_signals_user; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_signals_user ON public.behavioral_signals USING btree (user_id);


--
-- Name: idx_tree_generations_user_created; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_tree_generations_user_created ON public.tree_generations USING btree (user_id, created_at);


--
-- Name: idx_trends_user; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_trends_user ON public.personality_trends USING btree (user_id);


--
-- Name: idx_user_chat_analytics_user_date; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_user_chat_analytics_user_date ON public.user_chat_analytics USING btree (user_id, date);


--
-- Name: idx_user_profiles_career_urgency; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_user_profiles_career_urgency ON public.user_profiles USING btree (career_urgency) WHERE (career_urgency IS NOT NULL);


--
-- Name: idx_user_profiles_compatibility_vector; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_user_profiles_compatibility_vector ON public.user_profiles USING gin (compatibility_vector);


--
-- Name: idx_user_profiles_education_level; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_user_profiles_education_level ON public.user_profiles USING btree (education_level);


--
-- Name: idx_user_profiles_embedding; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_user_profiles_embedding ON public.user_profiles USING ivfflat (embedding public.vector_cosine_ops) WITH (lists='100');


--
-- Name: idx_user_profiles_gpa; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_user_profiles_gpa ON public.user_profiles USING btree (gpa) WHERE (gpa IS NOT NULL);


--
-- Name: ix_career_goals_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_career_goals_id ON public.career_goals USING btree (id);


--
-- Name: ix_career_milestones_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_career_milestones_id ON public.career_milestones USING btree (id);


--
-- Name: ix_career_profile_aggregates_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_career_profile_aggregates_id ON public.career_profile_aggregates USING btree (id);


--
-- Name: ix_career_profile_aggregates_user_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_career_profile_aggregates_user_id ON public.career_profile_aggregates USING btree (user_id);


--
-- Name: ix_career_signals_course_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_career_signals_course_id ON public.career_signals USING btree (course_id);


--
-- Name: ix_career_signals_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_career_signals_id ON public.career_signals USING btree (id);


--
-- Name: ix_career_signals_user_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_career_signals_user_id ON public.career_signals USING btree (user_id);


--
-- Name: ix_conversation_logs_course_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_conversation_logs_course_id ON public.conversation_logs USING btree (course_id);


--
-- Name: ix_conversation_logs_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_conversation_logs_id ON public.conversation_logs USING btree (id);


--
-- Name: ix_conversation_logs_session_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_conversation_logs_session_id ON public.conversation_logs USING btree (session_id);


--
-- Name: ix_conversation_logs_user_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_conversation_logs_user_id ON public.conversation_logs USING btree (user_id);


--
-- Name: ix_courses_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_courses_id ON public.courses USING btree (id);


--
-- Name: ix_courses_user_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_courses_user_id ON public.courses USING btree (user_id);


--
-- Name: ix_gca_choices_question_sort_active; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_gca_choices_question_sort_active ON public.gca_choices USING btree (question_id, sort_idx, active);


--
-- Name: ix_gca_tests_active; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_gca_tests_active ON public.gca_tests USING btree (active);


--
-- Name: ix_message_components_component_type; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_message_components_component_type ON public.message_components USING btree (component_type);


--
-- Name: ix_message_components_message_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_message_components_message_id ON public.message_components USING btree (message_id);


--
-- Name: ix_message_components_tool_source; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_message_components_tool_source ON public.message_components USING btree (tool_source);


--
-- Name: ix_messages_recipient_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_messages_recipient_id ON public.messages USING btree (recipient_id);


--
-- Name: ix_messages_sender_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_messages_sender_id ON public.messages USING btree (sender_id);


--
-- Name: ix_messages_timestamp; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_messages_timestamp ON public.messages USING btree ("timestamp");


--
-- Name: ix_node_notes_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_node_notes_id ON public.node_notes USING btree (id);


--
-- Name: ix_node_notes_node_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_node_notes_node_id ON public.node_notes USING btree (node_id);


--
-- Name: ix_program_recommendations_goal_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_program_recommendations_goal_id ON public.program_recommendations USING btree (goal_id);


--
-- Name: ix_psychological_insights_course_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_psychological_insights_course_id ON public.psychological_insights USING btree (course_id);


--
-- Name: ix_psychological_insights_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_psychological_insights_id ON public.psychological_insights USING btree (id);


--
-- Name: ix_psychological_insights_user_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_psychological_insights_user_id ON public.psychological_insights USING btree (user_id);


--
-- Name: ix_questions_test_chapter_sort_active; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_questions_test_chapter_sort_active ON public.gca_questions USING btree (test_id, chapter_number, sort_idx, active);


--
-- Name: ix_saved_jobs_esco_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_saved_jobs_esco_id ON public.saved_jobs USING btree (esco_id);


--
-- Name: ix_saved_jobs_user_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_saved_jobs_user_id ON public.saved_jobs USING btree (user_id);


--
-- Name: ix_saved_recommendations_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_saved_recommendations_id ON public.saved_recommendations USING btree (id);


--
-- Name: ix_saved_recommendations_user_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_saved_recommendations_user_id ON public.saved_recommendations USING btree (user_id);


--
-- Name: ix_suggested_peers_suggested_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_suggested_peers_suggested_id ON public.suggested_peers USING btree (suggested_id);


--
-- Name: ix_suggested_peers_user_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_suggested_peers_user_id ON public.suggested_peers USING btree (user_id);


--
-- Name: ix_tool_invocations_conversation_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_tool_invocations_conversation_id ON public.tool_invocations USING btree (conversation_id);


--
-- Name: ix_tool_invocations_tool_name; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_tool_invocations_tool_name ON public.tool_invocations USING btree (tool_name);


--
-- Name: ix_tool_invocations_user_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_tool_invocations_user_id ON public.tool_invocations USING btree (user_id);


--
-- Name: ix_tree_paths_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_tree_paths_id ON public.tree_paths USING btree (id);


--
-- Name: ix_user_journey_milestones_milestone_type; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_user_journey_milestones_milestone_type ON public.user_journey_milestones USING btree (milestone_type);


--
-- Name: ix_user_journey_milestones_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_user_journey_milestones_status ON public.user_journey_milestones USING btree (status);


--
-- Name: ix_user_journey_milestones_user_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_user_journey_milestones_user_id ON public.user_journey_milestones USING btree (user_id);


--
-- Name: ix_user_notes_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_user_notes_id ON public.user_notes USING btree (id);


--
-- Name: ix_user_profiles_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_user_profiles_id ON public.user_profiles USING btree (id);


--
-- Name: ix_user_progress_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_user_progress_id ON public.user_progress USING btree (id);


--
-- Name: ix_user_recommendations_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_user_recommendations_id ON public.user_recommendations USING btree (id);


--
-- Name: ix_user_skills_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_user_skills_id ON public.user_skills USING btree (id);


--
-- Name: ix_users_answers_attempt_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_users_answers_attempt_id ON public.gca_users_answers USING btree (attempt_id);


--
-- Name: ix_users_answers_created_at; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_users_answers_created_at ON public.gca_users_answers USING btree (created_at);


--
-- Name: ix_users_email; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX ix_users_email ON public.users USING btree (email);


--
-- Name: ix_users_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_users_id ON public.users USING btree (id);


--
-- Name: user_profiles_embedding_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX user_profiles_embedding_idx ON public.user_profiles USING ivfflat (embedding public.vector_cosine_ops) WITH (lists='100');


--
-- Name: career_fit_analyses update_career_fit_analyses_updated_at; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER update_career_fit_analyses_updated_at BEFORE UPDATE ON public.career_fit_analyses FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: esco_job_requirements update_esco_requirements_updated_at; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER update_esco_requirements_updated_at BEFORE UPDATE ON public.esco_job_requirements FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: institutions update_institutions_updated_at; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER update_institutions_updated_at BEFORE UPDATE ON public.institutions FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: programs update_programs_updated_at; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER update_programs_updated_at BEFORE UPDATE ON public.programs FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: user_program_preferences update_user_preferences_updated_at; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER update_user_preferences_updated_at BEFORE UPDATE ON public.user_program_preferences FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: behavioral_signals behavioral_signals_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.behavioral_signals
    ADD CONSTRAINT behavioral_signals_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: career_fit_analyses career_fit_analyses_saved_recommendation_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.career_fit_analyses
    ADD CONSTRAINT career_fit_analyses_saved_recommendation_id_fkey FOREIGN KEY (saved_recommendation_id) REFERENCES public.saved_recommendations(id) ON DELETE CASCADE;


--
-- Name: career_fit_analyses career_fit_analyses_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.career_fit_analyses
    ADD CONSTRAINT career_fit_analyses_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: career_goals career_goals_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.career_goals
    ADD CONSTRAINT career_goals_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: career_milestones career_milestones_goal_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.career_milestones
    ADD CONSTRAINT career_milestones_goal_id_fkey FOREIGN KEY (goal_id) REFERENCES public.career_goals(id);


--
-- Name: career_profile_aggregates career_profile_aggregates_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.career_profile_aggregates
    ADD CONSTRAINT career_profile_aggregates_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: career_signals career_signals_course_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.career_signals
    ADD CONSTRAINT career_signals_course_id_fkey FOREIGN KEY (course_id) REFERENCES public.courses(id);


--
-- Name: career_signals career_signals_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.career_signals
    ADD CONSTRAINT career_signals_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: chat_messages chat_messages_conversation_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.chat_messages
    ADD CONSTRAINT chat_messages_conversation_id_fkey FOREIGN KEY (conversation_id) REFERENCES public.conversations(id) ON DELETE CASCADE;


--
-- Name: conversation_categories conversation_categories_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.conversation_categories
    ADD CONSTRAINT conversation_categories_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: conversation_logs conversation_logs_course_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.conversation_logs
    ADD CONSTRAINT conversation_logs_course_id_fkey FOREIGN KEY (course_id) REFERENCES public.courses(id);


--
-- Name: conversation_logs conversation_logs_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.conversation_logs
    ADD CONSTRAINT conversation_logs_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: conversation_shares conversation_shares_conversation_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.conversation_shares
    ADD CONSTRAINT conversation_shares_conversation_id_fkey FOREIGN KEY (conversation_id) REFERENCES public.conversations(id) ON DELETE CASCADE;


--
-- Name: conversations conversations_category_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.conversations
    ADD CONSTRAINT conversations_category_id_fkey FOREIGN KEY (category_id) REFERENCES public.conversation_categories(id) ON DELETE SET NULL;


--
-- Name: conversations conversations_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.conversations
    ADD CONSTRAINT conversations_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: courses courses_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.courses
    ADD CONSTRAINT courses_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: developmental_milestones developmental_milestones_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.developmental_milestones
    ADD CONSTRAINT developmental_milestones_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: gca_results fk_gca_results_user_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.gca_results
    ADD CONSTRAINT fk_gca_results_user_id FOREIGN KEY (user_id) REFERENCES public.user_profiles(user_id);


--
-- Name: tree_paths fk_tree_paths_user_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tree_paths
    ADD CONSTRAINT fk_tree_paths_user_id FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: gca_choices gca_choices_question_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.gca_choices
    ADD CONSTRAINT gca_choices_question_id_fkey FOREIGN KEY (question_id) REFERENCES public.gca_questions(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: gca_questions gca_questions_test_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.gca_questions
    ADD CONSTRAINT gca_questions_test_id_fkey FOREIGN KEY (test_id) REFERENCES public.gca_tests(id);


--
-- Name: gca_results gca_results_test_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.gca_results
    ADD CONSTRAINT gca_results_test_id_fkey FOREIGN KEY (test_id) REFERENCES public.gca_tests(id);


--
-- Name: gca_users_answers gca_users_answers_choice_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.gca_users_answers
    ADD CONSTRAINT gca_users_answers_choice_id_fkey FOREIGN KEY (choice_id) REFERENCES public.gca_choices(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: gca_users_answers gca_users_answers_question_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.gca_users_answers
    ADD CONSTRAINT gca_users_answers_question_id_fkey FOREIGN KEY (question_id) REFERENCES public.gca_questions(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: gca_users_answers gca_users_answers_test_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.gca_users_answers
    ADD CONSTRAINT gca_users_answers_test_id_fkey FOREIGN KEY (test_id) REFERENCES public.gca_tests(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: llm_descriptions llm_descriptions_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.llm_descriptions
    ADD CONSTRAINT llm_descriptions_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: message_components message_components_message_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.message_components
    ADD CONSTRAINT message_components_message_id_fkey FOREIGN KEY (message_id) REFERENCES public.chat_messages(id) ON DELETE CASCADE;


--
-- Name: messages messages_recipient_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.messages
    ADD CONSTRAINT messages_recipient_id_fkey FOREIGN KEY (recipient_id) REFERENCES public.users(id);


--
-- Name: messages messages_sender_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.messages
    ADD CONSTRAINT messages_sender_id_fkey FOREIGN KEY (sender_id) REFERENCES public.users(id);


--
-- Name: node_notes node_notes_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.node_notes
    ADD CONSTRAINT node_notes_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: personality_assessments personality_assessments_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.personality_assessments
    ADD CONSTRAINT personality_assessments_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: personality_embeddings personality_embeddings_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.personality_embeddings
    ADD CONSTRAINT personality_embeddings_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: personality_profiles personality_profiles_assessment_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.personality_profiles
    ADD CONSTRAINT personality_profiles_assessment_id_fkey FOREIGN KEY (assessment_id) REFERENCES public.personality_assessments(id) ON DELETE SET NULL;


--
-- Name: personality_profiles personality_profiles_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.personality_profiles
    ADD CONSTRAINT personality_profiles_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: personality_responses personality_responses_assessment_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.personality_responses
    ADD CONSTRAINT personality_responses_assessment_id_fkey FOREIGN KEY (assessment_id) REFERENCES public.personality_assessments(id) ON DELETE CASCADE;


--
-- Name: personality_trends personality_trends_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.personality_trends
    ADD CONSTRAINT personality_trends_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: programs programs_institution_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.programs
    ADD CONSTRAINT programs_institution_id_fkey FOREIGN KEY (institution_id) REFERENCES public.institutions(id) ON DELETE CASCADE;


--
-- Name: psychological_insights psychological_insights_course_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.psychological_insights
    ADD CONSTRAINT psychological_insights_course_id_fkey FOREIGN KEY (course_id) REFERENCES public.courses(id);


--
-- Name: psychological_insights psychological_insights_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.psychological_insights
    ADD CONSTRAINT psychological_insights_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: saved_jobs saved_jobs_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.saved_jobs
    ADD CONSTRAINT saved_jobs_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: saved_recommendations saved_recommendations_conversation_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.saved_recommendations
    ADD CONSTRAINT saved_recommendations_conversation_id_fkey FOREIGN KEY (conversation_id) REFERENCES public.conversations(id);


--
-- Name: saved_recommendations saved_recommendations_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.saved_recommendations
    ADD CONSTRAINT saved_recommendations_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: strengths_reflection_responses strengths_reflection_responses_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.strengths_reflection_responses
    ADD CONSTRAINT strengths_reflection_responses_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: suggested_peers suggested_peers_suggested_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.suggested_peers
    ADD CONSTRAINT suggested_peers_suggested_id_fkey FOREIGN KEY (suggested_id) REFERENCES public.users(id);


--
-- Name: suggested_peers suggested_peers_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.suggested_peers
    ADD CONSTRAINT suggested_peers_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: tool_invocations tool_invocations_conversation_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tool_invocations
    ADD CONSTRAINT tool_invocations_conversation_id_fkey FOREIGN KEY (conversation_id) REFERENCES public.conversations(id) ON DELETE CASCADE;


--
-- Name: tool_invocations tool_invocations_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tool_invocations
    ADD CONSTRAINT tool_invocations_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: tree_generations tree_generations_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tree_generations
    ADD CONSTRAINT tree_generations_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: tree_paths tree_paths_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tree_paths
    ADD CONSTRAINT tree_paths_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: user_chat_analytics user_chat_analytics_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_chat_analytics
    ADD CONSTRAINT user_chat_analytics_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: user_journey_milestones user_journey_milestones_conversation_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_journey_milestones
    ADD CONSTRAINT user_journey_milestones_conversation_id_fkey FOREIGN KEY (conversation_id) REFERENCES public.conversations(id) ON DELETE SET NULL;


--
-- Name: user_journey_milestones user_journey_milestones_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_journey_milestones
    ADD CONSTRAINT user_journey_milestones_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: user_notes user_notes_saved_recommendation_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_notes
    ADD CONSTRAINT user_notes_saved_recommendation_id_fkey FOREIGN KEY (saved_recommendation_id) REFERENCES public.saved_recommendations(id);


--
-- Name: user_notes user_notes_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_notes
    ADD CONSTRAINT user_notes_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: user_profiles user_profiles_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_profiles
    ADD CONSTRAINT user_profiles_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: user_program_preferences user_program_preferences_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_program_preferences
    ADD CONSTRAINT user_program_preferences_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: user_progress user_progress_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_progress
    ADD CONSTRAINT user_progress_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: user_recommendations user_recommendations_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_recommendations
    ADD CONSTRAINT user_recommendations_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: user_representation user_representation_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_representation
    ADD CONSTRAINT user_representation_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: user_skill_graphs user_skill_graphs_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_skill_graphs
    ADD CONSTRAINT user_skill_graphs_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: user_skill_nodes user_skill_nodes_graph_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_skill_nodes
    ADD CONSTRAINT user_skill_nodes_graph_id_fkey FOREIGN KEY (graph_id) REFERENCES public.user_skill_graphs(id);


--
-- Name: user_skill_trees user_skill_trees_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_skill_trees
    ADD CONSTRAINT user_skill_trees_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: user_skills user_skills_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_skills
    ADD CONSTRAINT user_skills_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- PostgreSQL database dump complete
--

