-- Schema for missing tables in Supabase
-- Generated for migration

ALTER TABLE IF EXISTS ONLY public.user_skills DROP CONSTRAINT IF EXISTS user_skills_user_id_fkey;
ALTER TABLE IF EXISTS ONLY public.user_skill_trees DROP CONSTRAINT IF EXISTS user_skill_trees_user_id_fkey;
ALTER TABLE IF EXISTS ONLY public.user_skill_nodes DROP CONSTRAINT IF EXISTS user_skill_nodes_graph_id_fkey;
ALTER TABLE IF EXISTS ONLY public.user_skill_graphs DROP CONSTRAINT IF EXISTS user_skill_graphs_user_id_fkey;
ALTER TABLE IF EXISTS ONLY public.user_representation DROP CONSTRAINT IF EXISTS user_representation_user_id_fkey;
ALTER TABLE IF EXISTS ONLY public.user_recommendations DROP CONSTRAINT IF EXISTS user_recommendations_user_id_fkey;
ALTER TABLE IF EXISTS ONLY public.user_progress DROP CONSTRAINT IF EXISTS user_progress_user_id_fkey;
ALTER TABLE IF EXISTS ONLY public.user_program_preferences DROP CONSTRAINT IF EXISTS user_program_preferences_user_id_fkey;
ALTER TABLE IF EXISTS ONLY public.user_profiles DROP CONSTRAINT IF EXISTS user_profiles_user_id_fkey;
ALTER TABLE IF EXISTS ONLY public.user_notes DROP CONSTRAINT IF EXISTS user_notes_user_id_fkey;
ALTER TABLE IF EXISTS ONLY public.user_notes DROP CONSTRAINT IF EXISTS user_notes_saved_recommendation_id_fkey;
ALTER TABLE IF EXISTS ONLY public.user_journey_milestones DROP CONSTRAINT IF EXISTS user_journey_milestones_user_id_fkey;
ALTER TABLE IF EXISTS ONLY public.user_journey_milestones DROP CONSTRAINT IF EXISTS user_journey_milestones_conversation_id_fkey;
ALTER TABLE IF EXISTS ONLY public.user_chat_analytics DROP CONSTRAINT IF EXISTS user_chat_analytics_user_id_fkey;
ALTER TABLE IF EXISTS ONLY public.tree_paths DROP CONSTRAINT IF EXISTS tree_paths_user_id_fkey;
ALTER TABLE IF EXISTS ONLY public.tree_generations DROP CONSTRAINT IF EXISTS tree_generations_user_id_fkey;
ALTER TABLE IF EXISTS ONLY public.tool_invocations DROP CONSTRAINT IF EXISTS tool_invocations_user_id_fkey;
ALTER TABLE IF EXISTS ONLY public.tool_invocations DROP CONSTRAINT IF EXISTS tool_invocations_conversation_id_fkey;
ALTER TABLE IF EXISTS ONLY public.suggested_peers DROP CONSTRAINT IF EXISTS suggested_peers_user_id_fkey;
ALTER TABLE IF EXISTS ONLY public.suggested_peers DROP CONSTRAINT IF EXISTS suggested_peers_suggested_id_fkey;
ALTER TABLE IF EXISTS ONLY public.strengths_reflection_responses DROP CONSTRAINT IF EXISTS strengths_reflection_responses_user_id_fkey;
ALTER TABLE IF EXISTS ONLY public.saved_recommendations DROP CONSTRAINT IF EXISTS saved_recommendations_user_id_fkey;
ALTER TABLE IF EXISTS ONLY public.saved_recommendations DROP CONSTRAINT IF EXISTS saved_recommendations_conversation_id_fkey;
ALTER TABLE IF EXISTS ONLY public.saved_jobs DROP CONSTRAINT IF EXISTS saved_jobs_user_id_fkey;
ALTER TABLE IF EXISTS ONLY public.psychological_insights DROP CONSTRAINT IF EXISTS psychological_insights_user_id_fkey;
ALTER TABLE IF EXISTS ONLY public.psychological_insights DROP CONSTRAINT IF EXISTS psychological_insights_course_id_fkey;
ALTER TABLE IF EXISTS ONLY public.programs DROP CONSTRAINT IF EXISTS programs_institution_id_fkey;
ALTER TABLE IF EXISTS ONLY public.personality_trends DROP CONSTRAINT IF EXISTS personality_trends_user_id_fkey;
ALTER TABLE IF EXISTS ONLY public.personality_responses DROP CONSTRAINT IF EXISTS personality_responses_assessment_id_fkey;
ALTER TABLE IF EXISTS ONLY public.personality_profiles DROP CONSTRAINT IF EXISTS personality_profiles_user_id_fkey;
ALTER TABLE IF EXISTS ONLY public.personality_profiles DROP CONSTRAINT IF EXISTS personality_profiles_assessment_id_fkey;
ALTER TABLE IF EXISTS ONLY public.personality_embeddings DROP CONSTRAINT IF EXISTS personality_embeddings_user_id_fkey;
ALTER TABLE IF EXISTS ONLY public.personality_assessments DROP CONSTRAINT IF EXISTS personality_assessments_user_id_fkey;
ALTER TABLE IF EXISTS ONLY public.node_notes DROP CONSTRAINT IF EXISTS node_notes_user_id_fkey;
ALTER TABLE IF EXISTS ONLY public.messages DROP CONSTRAINT IF EXISTS messages_sender_id_fkey;
ALTER TABLE IF EXISTS ONLY public.messages DROP CONSTRAINT IF EXISTS messages_recipient_id_fkey;
ALTER TABLE IF EXISTS ONLY public.message_components DROP CONSTRAINT IF EXISTS message_components_message_id_fkey;
ALTER TABLE IF EXISTS ONLY public.llm_descriptions DROP CONSTRAINT IF EXISTS llm_descriptions_user_id_fkey;
ALTER TABLE IF EXISTS ONLY public.gca_users_answers DROP CONSTRAINT IF EXISTS gca_users_answers_test_id_fkey;
ALTER TABLE IF EXISTS ONLY public.gca_users_answers DROP CONSTRAINT IF EXISTS gca_users_answers_question_id_fkey;
ALTER TABLE IF EXISTS ONLY public.gca_users_answers DROP CONSTRAINT IF EXISTS gca_users_answers_choice_id_fkey;
ALTER TABLE IF EXISTS ONLY public.tree_paths DROP CONSTRAINT IF EXISTS fk_tree_paths_user_id;
ALTER TABLE IF EXISTS ONLY public.chat_messages DROP CONSTRAINT IF EXISTS chat_messages_conversation_id_fkey;
ALTER TABLE IF EXISTS ONLY public.users DROP CONSTRAINT IF EXISTS users_pkey;
ALTER TABLE IF EXISTS ONLY public.user_skills DROP CONSTRAINT IF EXISTS user_skills_user_id_key;
ALTER TABLE IF EXISTS ONLY public.user_skills DROP CONSTRAINT IF EXISTS user_skills_pkey;
ALTER TABLE IF EXISTS ONLY public.user_skill_trees DROP CONSTRAINT IF EXISTS user_skill_trees_pkey;
ALTER TABLE IF EXISTS ONLY public.user_skill_nodes DROP CONSTRAINT IF EXISTS user_skill_nodes_pkey;
ALTER TABLE IF EXISTS ONLY public.user_skill_graphs DROP CONSTRAINT IF EXISTS user_skill_graphs_pkey;
ALTER TABLE IF EXISTS ONLY public.user_representation DROP CONSTRAINT IF EXISTS user_representation_pkey;
ALTER TABLE IF EXISTS ONLY public.user_recommendations DROP CONSTRAINT IF EXISTS user_recommendations_pkey;
ALTER TABLE IF EXISTS ONLY public.user_progress DROP CONSTRAINT IF EXISTS user_progress_user_id_key;
ALTER TABLE IF EXISTS ONLY public.user_progress DROP CONSTRAINT IF EXISTS user_progress_pkey;
ALTER TABLE IF EXISTS ONLY public.user_program_preferences DROP CONSTRAINT IF EXISTS user_program_preferences_user_id_key;
ALTER TABLE IF EXISTS ONLY public.user_program_preferences DROP CONSTRAINT IF EXISTS user_program_preferences_pkey;
ALTER TABLE IF EXISTS ONLY public.user_profiles DROP CONSTRAINT IF EXISTS user_profiles_user_id_key;
ALTER TABLE IF EXISTS ONLY public.user_profiles DROP CONSTRAINT IF EXISTS user_profiles_pkey;
ALTER TABLE IF EXISTS ONLY public.user_notes DROP CONSTRAINT IF EXISTS user_notes_pkey;
ALTER TABLE IF EXISTS ONLY public.user_journey_milestones DROP CONSTRAINT IF EXISTS user_journey_milestones_pkey;
ALTER TABLE IF EXISTS ONLY public.user_chat_analytics DROP CONSTRAINT IF EXISTS user_chat_analytics_user_id_date_key;
ALTER TABLE IF EXISTS ONLY public.user_chat_analytics DROP CONSTRAINT IF EXISTS user_chat_analytics_pkey;
ALTER TABLE IF EXISTS ONLY public.saved_recommendations DROP CONSTRAINT IF EXISTS uq_user_oasis_code;
ALTER TABLE IF EXISTS ONLY public.saved_jobs DROP CONSTRAINT IF EXISTS uq_user_job;
ALTER TABLE IF EXISTS ONLY public.llm_descriptions DROP CONSTRAINT IF EXISTS uq_node_user_description;
ALTER TABLE IF EXISTS ONLY public.tree_paths DROP CONSTRAINT IF EXISTS tree_paths_pkey;
ALTER TABLE IF EXISTS ONLY public.tree_generations DROP CONSTRAINT IF EXISTS tree_generations_pkey;
ALTER TABLE IF EXISTS ONLY public.tool_invocations DROP CONSTRAINT IF EXISTS tool_invocations_pkey;
ALTER TABLE IF EXISTS ONLY public.suggested_peers DROP CONSTRAINT IF EXISTS suggested_peers_pkey;
ALTER TABLE IF EXISTS ONLY public.strengths_reflection_responses DROP CONSTRAINT IF EXISTS strengths_reflection_responses_pkey;
ALTER TABLE IF EXISTS ONLY public.skills_to_domains DROP CONSTRAINT IF EXISTS skills_to_domains_pkey;
ALTER TABLE IF EXISTS ONLY public.saved_recommendations DROP CONSTRAINT IF EXISTS saved_recommendations_pkey;
ALTER TABLE IF EXISTS ONLY public.saved_jobs DROP CONSTRAINT IF EXISTS saved_jobs_pkey;
ALTER TABLE IF EXISTS ONLY public.public_feed DROP CONSTRAINT IF EXISTS public_feed_pkey;
ALTER TABLE IF EXISTS ONLY public.psychological_insights DROP CONSTRAINT IF EXISTS psychological_insights_pkey;
ALTER TABLE IF EXISTS ONLY public.programs DROP CONSTRAINT IF EXISTS programs_source_system_source_id_key;
ALTER TABLE IF EXISTS ONLY public.programs DROP CONSTRAINT IF EXISTS programs_pkey;
ALTER TABLE IF EXISTS ONLY public.program_recommendations DROP CONSTRAINT IF EXISTS program_recommendations_pkey;
ALTER TABLE IF EXISTS ONLY public.personality_trends DROP CONSTRAINT IF EXISTS personality_trends_pkey;
ALTER TABLE IF EXISTS ONLY public.personality_responses DROP CONSTRAINT IF EXISTS personality_responses_pkey;
ALTER TABLE IF EXISTS ONLY public.personality_profiles DROP CONSTRAINT IF EXISTS personality_profiles_user_id_profile_type_assessment_versio_key;
ALTER TABLE IF EXISTS ONLY public.personality_profiles DROP CONSTRAINT IF EXISTS personality_profiles_pkey;
ALTER TABLE IF EXISTS ONLY public.personality_embeddings DROP CONSTRAINT IF EXISTS personality_embeddings_pkey;
ALTER TABLE IF EXISTS ONLY public.personality_assessments DROP CONSTRAINT IF EXISTS personality_assessments_session_id_key;
ALTER TABLE IF EXISTS ONLY public.personality_assessments DROP CONSTRAINT IF EXISTS personality_assessments_pkey;
ALTER TABLE IF EXISTS ONLY public.node_notes DROP CONSTRAINT IF EXISTS node_notes_pkey;
ALTER TABLE IF EXISTS ONLY public.messages DROP CONSTRAINT IF EXISTS messages_pkey;
ALTER TABLE IF EXISTS ONLY public.message_components DROP CONSTRAINT IF EXISTS message_components_pkey;
ALTER TABLE IF EXISTS ONLY public.llm_descriptions DROP CONSTRAINT IF EXISTS llm_descriptions_pkey;
ALTER TABLE IF EXISTS ONLY public.institutions DROP CONSTRAINT IF EXISTS institutions_source_system_source_id_key;
ALTER TABLE IF EXISTS ONLY public.institutions DROP CONSTRAINT IF EXISTS institutions_pkey;
ALTER TABLE IF EXISTS ONLY public.gca_users_answers DROP CONSTRAINT IF EXISTS gca_users_answers_pkey;
ALTER TABLE IF EXISTS ONLY public.chat_messages DROP CONSTRAINT IF EXISTS chat_messages_pkey;
ALTER TABLE IF EXISTS public.users ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.user_skills ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.user_skill_trees ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.user_skill_nodes ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.user_representation ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.user_recommendations ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.user_profiles ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.user_notes ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.user_journey_milestones ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.user_chat_analytics ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.tool_invocations ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.strengths_reflection_responses ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.saved_recommendations ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.saved_jobs ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.public_feed ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.psychological_insights ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.program_recommendations ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.personality_trends ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.personality_responses ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.personality_profiles ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.personality_embeddings ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.personality_assessments ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.messages ALTER COLUMN message_id DROP DEFAULT;
ALTER TABLE IF EXISTS public.message_components ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.llm_descriptions ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.chat_messages ALTER COLUMN id DROP DEFAULT;
CREATE SEQUENCE public.chat_messages_id_seq
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

CREATE SEQUENCE public.llm_descriptions_id_seq
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

CREATE SEQUENCE public.message_components_id_seq
CREATE TABLE public.messages (
    message_id integer NOT NULL,
    sender_id integer NOT NULL,
    recipient_id integer NOT NULL,
    body text NOT NULL,
    "timestamp" timestamp with time zone DEFAULT now() NOT NULL
);

CREATE SEQUENCE public.messages_message_id_seq
CREATE TABLE public.node_notes (
    id character varying NOT NULL,
    user_id integer,
    node_id character varying,
    action_index integer,
    note_text text,
    created_at timestamp without time zone DEFAULT now(),
    updated_at timestamp without time zone DEFAULT now()
);

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

CREATE SEQUENCE public.personality_assessments_id_seq
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

CREATE SEQUENCE public.personality_embeddings_id_seq
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

CREATE SEQUENCE public.personality_profiles_id_seq
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

CREATE SEQUENCE public.personality_responses_id_seq
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

CREATE SEQUENCE public.personality_trends_id_seq
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

CREATE SEQUENCE public.program_recommendations_id_seq
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

CREATE SEQUENCE public.psychological_insights_id_seq
CREATE TABLE public.public_feed (
    id integer NOT NULL,
    event_type character varying NOT NULL,
    domain character varying,
    "timestamp" timestamp without time zone DEFAULT now()
);

CREATE SEQUENCE public.public_feed_id_seq
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

CREATE SEQUENCE public.saved_jobs_id_seq
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

CREATE SEQUENCE public.saved_recommendations_id_seq
CREATE TABLE public.skills_to_domains (
    skill_id character varying NOT NULL,
    domain character varying
);

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

CREATE SEQUENCE public.strengths_reflection_responses_id_seq
CREATE TABLE public.suggested_peers (
    user_id integer NOT NULL,
    suggested_id integer NOT NULL,
    similarity double precision,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone
);

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

CREATE SEQUENCE public.tool_invocations_id_seq
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

CREATE TABLE public.tree_paths (
    id uuid NOT NULL,
    user_id integer,
    tree_type character varying,
    tree_json json,
    name character varying,
    created_at timestamp without time zone DEFAULT now()
);

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

CREATE SEQUENCE public.user_chat_analytics_id_seq
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

CREATE SEQUENCE public.user_journey_milestones_id_seq
CREATE TABLE public.user_notes (
    id integer NOT NULL,
    user_id integer NOT NULL,
    saved_recommendation_id integer,
    content text NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);

CREATE SEQUENCE public.user_notes_id_seq
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

CREATE SEQUENCE public.user_profiles_id_seq
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

CREATE TABLE public.user_progress (
    id character varying DEFAULT gen_random_uuid() NOT NULL,
    user_id integer,
    total_xp integer,
    level integer,
    last_completed_node character varying,
    completed_actions json,
    last_updated timestamp without time zone DEFAULT now()
);

CREATE TABLE public.user_recommendations (
    id integer NOT NULL,
    user_id integer,
    oasis_code character varying NOT NULL,
    label character varying NOT NULL,
    swiped_right boolean DEFAULT false,
    created_at timestamp with time zone DEFAULT now()
);

CREATE SEQUENCE public.user_recommendations_id_seq
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

CREATE SEQUENCE public.user_representation_id_seq
CREATE TABLE public.user_skill_graphs (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id integer,
    root_skill_id character varying NOT NULL,
    graph_name text,
    created_at timestamp without time zone DEFAULT now()
);

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

CREATE SEQUENCE public.user_skill_nodes_id_seq
CREATE TABLE public.user_skill_trees (
    id integer NOT NULL,
    user_id integer,
    graph_id uuid NOT NULL,
    tree_data jsonb NOT NULL,
    created_at timestamp without time zone DEFAULT now()
);

CREATE SEQUENCE public.user_skill_trees_id_seq
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

CREATE SEQUENCE public.user_skills_id_seq
CREATE TABLE public.users (
    id integer NOT NULL,
    email character varying NOT NULL,
    hashed_password character varying NOT NULL,
    created_at timestamp with time zone DEFAULT now()
);

CREATE SEQUENCE public.users_id_seq
ALTER TABLE ONLY public.chat_messages ALTER COLUMN id SET DEFAULT nextval('public.chat_messages_id_seq'::regclass);
ALTER TABLE ONLY public.llm_descriptions ALTER COLUMN id SET DEFAULT nextval('public.llm_descriptions_id_seq'::regclass);
ALTER TABLE ONLY public.message_components ALTER COLUMN id SET DEFAULT nextval('public.message_components_id_seq'::regclass);
ALTER TABLE ONLY public.messages ALTER COLUMN message_id SET DEFAULT nextval('public.message_id_seq'::regclass);
ALTER TABLE ONLY public.personality_assessments ALTER COLUMN id SET DEFAULT nextval('public.personality_assessments_id_seq'::regclass);
ALTER TABLE ONLY public.personality_embeddings ALTER COLUMN id SET DEFAULT nextval('public.personality_embeddings_id_seq'::regclass);
ALTER TABLE ONLY public.personality_profiles ALTER COLUMN id SET DEFAULT nextval('public.personality_profiles_id_seq'::regclass);
ALTER TABLE ONLY public.personality_responses ALTER COLUMN id SET DEFAULT nextval('public.personality_responses_id_seq'::regclass);
ALTER TABLE ONLY public.personality_trends ALTER COLUMN id SET DEFAULT nextval('public.personality_trends_id_seq'::regclass);
ALTER TABLE ONLY public.program_recommendations ALTER COLUMN id SET DEFAULT nextval('public.program_recommendations_id_seq'::regclass);
ALTER TABLE ONLY public.psychological_insights ALTER COLUMN id SET DEFAULT nextval('public.psychological_insights_id_seq'::regclass);
ALTER TABLE ONLY public.public_feed ALTER COLUMN id SET DEFAULT nextval('public.public_feed_id_seq'::regclass);
ALTER TABLE ONLY public.saved_jobs ALTER COLUMN id SET DEFAULT nextval('public.saved_jobs_id_seq'::regclass);
ALTER TABLE ONLY public.saved_recommendations ALTER COLUMN id SET DEFAULT nextval('public.saved_recommendations_id_seq'::regclass);
ALTER TABLE ONLY public.strengths_reflection_responses ALTER COLUMN id SET DEFAULT nextval('public.strengths_reflection_responses_id_seq'::regclass);
ALTER TABLE ONLY public.tool_invocations ALTER COLUMN id SET DEFAULT nextval('public.tool_invocations_id_seq'::regclass);
ALTER TABLE ONLY public.user_chat_analytics ALTER COLUMN id SET DEFAULT nextval('public.user_chat_analytics_id_seq'::regclass);
ALTER TABLE ONLY public.user_journey_milestones ALTER COLUMN id SET DEFAULT nextval('public.user_journey_milestones_id_seq'::regclass);
ALTER TABLE ONLY public.user_notes ALTER COLUMN id SET DEFAULT nextval('public.user_notes_id_seq'::regclass);
ALTER TABLE ONLY public.user_profiles ALTER COLUMN id SET DEFAULT nextval('public.user_profiles_id_seq'::regclass);
ALTER TABLE ONLY public.user_recommendations ALTER COLUMN id SET DEFAULT nextval('public.user_recommendations_id_seq'::regclass);
ALTER TABLE ONLY public.user_representation ALTER COLUMN id SET DEFAULT nextval('public.user_representation_id_seq'::regclass);
ALTER TABLE ONLY public.user_skill_nodes ALTER COLUMN id SET DEFAULT nextval('public.user_skill_nodes_id_seq'::regclass);
ALTER TABLE ONLY public.user_skill_trees ALTER COLUMN id SET DEFAULT nextval('public.user_skill_trees_id_seq'::regclass);
ALTER TABLE ONLY public.user_skills ALTER COLUMN id SET DEFAULT nextval('public.user_skills_id_seq'::regclass);
ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);
ALTER TABLE ONLY public.chat_messages
ALTER TABLE ONLY public.gca_users_answers
ALTER TABLE ONLY public.institutions
ALTER TABLE ONLY public.institutions
ALTER TABLE ONLY public.llm_descriptions
ALTER TABLE ONLY public.message_components
ALTER TABLE ONLY public.messages
ALTER TABLE ONLY public.node_notes
ALTER TABLE ONLY public.personality_assessments
ALTER TABLE ONLY public.personality_assessments
ALTER TABLE ONLY public.personality_embeddings
ALTER TABLE ONLY public.personality_profiles
ALTER TABLE ONLY public.personality_profiles
ALTER TABLE ONLY public.personality_responses
ALTER TABLE ONLY public.personality_trends
ALTER TABLE ONLY public.program_recommendations
ALTER TABLE ONLY public.programs
ALTER TABLE ONLY public.programs
ALTER TABLE ONLY public.psychological_insights
ALTER TABLE ONLY public.public_feed
ALTER TABLE ONLY public.saved_jobs
ALTER TABLE ONLY public.saved_recommendations
ALTER TABLE ONLY public.skills_to_domains
ALTER TABLE ONLY public.strengths_reflection_responses
ALTER TABLE ONLY public.suggested_peers
ALTER TABLE ONLY public.tool_invocations
ALTER TABLE ONLY public.tree_generations
ALTER TABLE ONLY public.tree_paths
ALTER TABLE ONLY public.llm_descriptions
ALTER TABLE ONLY public.saved_jobs
ALTER TABLE ONLY public.saved_recommendations
ALTER TABLE ONLY public.user_chat_analytics
ALTER TABLE ONLY public.user_chat_analytics
ALTER TABLE ONLY public.user_journey_milestones
ALTER TABLE ONLY public.user_notes
ALTER TABLE ONLY public.user_profiles
ALTER TABLE ONLY public.user_profiles
ALTER TABLE ONLY public.user_program_preferences
ALTER TABLE ONLY public.user_program_preferences
ALTER TABLE ONLY public.user_progress
ALTER TABLE ONLY public.user_progress
ALTER TABLE ONLY public.user_recommendations
ALTER TABLE ONLY public.user_representation
ALTER TABLE ONLY public.user_skill_graphs
ALTER TABLE ONLY public.user_skill_nodes
ALTER TABLE ONLY public.user_skill_trees
ALTER TABLE ONLY public.user_skills
ALTER TABLE ONLY public.user_skills
ALTER TABLE ONLY public.users
CREATE INDEX fk_users_answers_choice_id ON public.gca_users_answers USING btree (choice_id);
CREATE INDEX fk_users_answers_question_id ON public.gca_users_answers USING btree (question_id);
CREATE INDEX fk_users_answers_test_id ON public.gca_users_answers USING btree (test_id);
CREATE INDEX fk_users_answers_user_id ON public.gca_users_answers USING btree (user_id);
CREATE INDEX idx_assessments_session ON public.personality_assessments USING btree (session_id);
CREATE INDEX idx_assessments_user ON public.personality_assessments USING btree (user_id);
CREATE INDEX idx_chat_messages_conversation_id ON public.chat_messages USING btree (conversation_id);
CREATE INDEX idx_chat_messages_created_at ON public.chat_messages USING btree (created_at);
CREATE INDEX idx_embeddings_type ON public.personality_embeddings USING btree (embedding_type);
CREATE INDEX idx_embeddings_user ON public.personality_embeddings USING btree (user_id);
CREATE INDEX idx_institutions_active ON public.institutions USING btree (active) WHERE (active = true);
CREATE INDEX idx_institutions_location ON public.institutions USING btree (country, province_state, city);
CREATE INDEX idx_institutions_source ON public.institutions USING btree (source_system, source_id);
CREATE INDEX idx_institutions_type ON public.institutions USING btree (institution_type);
CREATE INDEX idx_llm_descriptions_node_user ON public.llm_descriptions USING btree (node_id, user_id);
CREATE INDEX idx_profiles_type ON public.personality_profiles USING btree (profile_type);
CREATE INDEX idx_profiles_user ON public.personality_profiles USING btree (user_id);
CREATE INDEX idx_programs_active ON public.programs USING btree (active) WHERE (active = true);
CREATE INDEX idx_programs_cip ON public.programs USING btree (cip_code) WHERE (cip_code IS NOT NULL);
CREATE INDEX idx_programs_institution ON public.programs USING btree (institution_id);
CREATE INDEX idx_programs_search ON public.programs USING gin (search_vector);
CREATE INDEX idx_programs_source ON public.programs USING btree (source_system, source_id);
CREATE INDEX idx_programs_title_trgm ON public.programs USING gin (title public.gin_trgm_ops);
CREATE INDEX idx_programs_type_level ON public.programs USING btree (program_type, level);
CREATE INDEX idx_responses_assessment ON public.personality_responses USING btree (assessment_id);
CREATE INDEX idx_saved_jobs_user_source ON public.saved_jobs USING btree (user_id, discovery_source);
CREATE INDEX idx_tree_generations_user_created ON public.tree_generations USING btree (user_id, created_at);
CREATE INDEX idx_trends_user ON public.personality_trends USING btree (user_id);
CREATE INDEX idx_user_chat_analytics_user_date ON public.user_chat_analytics USING btree (user_id, date);
CREATE INDEX idx_user_profiles_career_urgency ON public.user_profiles USING btree (career_urgency) WHERE (career_urgency IS NOT NULL);
CREATE INDEX idx_user_profiles_compatibility_vector ON public.user_profiles USING gin (compatibility_vector);
CREATE INDEX idx_user_profiles_education_level ON public.user_profiles USING btree (education_level);
CREATE INDEX idx_user_profiles_embedding ON public.user_profiles USING ivfflat (embedding public.vector_cosine_ops) WITH (lists='100');
CREATE INDEX idx_user_profiles_gpa ON public.user_profiles USING btree (gpa) WHERE (gpa IS NOT NULL);
CREATE INDEX ix_message_components_component_type ON public.message_components USING btree (component_type);
CREATE INDEX ix_message_components_message_id ON public.message_components USING btree (message_id);
CREATE INDEX ix_message_components_tool_source ON public.message_components USING btree (tool_source);
CREATE INDEX ix_messages_recipient_id ON public.messages USING btree (recipient_id);
CREATE INDEX ix_messages_sender_id ON public.messages USING btree (sender_id);
CREATE INDEX ix_messages_timestamp ON public.messages USING btree ("timestamp");
CREATE INDEX ix_node_notes_id ON public.node_notes USING btree (id);
CREATE INDEX ix_node_notes_node_id ON public.node_notes USING btree (node_id);
CREATE INDEX ix_program_recommendations_goal_id ON public.program_recommendations USING btree (goal_id);
CREATE INDEX ix_psychological_insights_course_id ON public.psychological_insights USING btree (course_id);
CREATE INDEX ix_psychological_insights_id ON public.psychological_insights USING btree (id);
CREATE INDEX ix_psychological_insights_user_id ON public.psychological_insights USING btree (user_id);
CREATE INDEX ix_saved_jobs_esco_id ON public.saved_jobs USING btree (esco_id);
CREATE INDEX ix_saved_jobs_user_id ON public.saved_jobs USING btree (user_id);
CREATE INDEX ix_saved_recommendations_id ON public.saved_recommendations USING btree (id);
CREATE INDEX ix_saved_recommendations_user_id ON public.saved_recommendations USING btree (user_id);
CREATE INDEX ix_suggested_peers_suggested_id ON public.suggested_peers USING btree (suggested_id);
CREATE INDEX ix_suggested_peers_user_id ON public.suggested_peers USING btree (user_id);
CREATE INDEX ix_tool_invocations_conversation_id ON public.tool_invocations USING btree (conversation_id);
CREATE INDEX ix_tool_invocations_tool_name ON public.tool_invocations USING btree (tool_name);
CREATE INDEX ix_tool_invocations_user_id ON public.tool_invocations USING btree (user_id);
CREATE INDEX ix_tree_paths_id ON public.tree_paths USING btree (id);
CREATE INDEX ix_user_journey_milestones_milestone_type ON public.user_journey_milestones USING btree (milestone_type);
CREATE INDEX ix_user_journey_milestones_status ON public.user_journey_milestones USING btree (status);
CREATE INDEX ix_user_journey_milestones_user_id ON public.user_journey_milestones USING btree (user_id);
CREATE INDEX ix_user_notes_id ON public.user_notes USING btree (id);
CREATE INDEX ix_user_profiles_id ON public.user_profiles USING btree (id);
CREATE INDEX ix_user_progress_id ON public.user_progress USING btree (id);
CREATE INDEX ix_user_recommendations_id ON public.user_recommendations USING btree (id);
CREATE INDEX ix_user_skills_id ON public.user_skills USING btree (id);
CREATE INDEX ix_users_answers_attempt_id ON public.gca_users_answers USING btree (attempt_id);
CREATE INDEX ix_users_answers_created_at ON public.gca_users_answers USING btree (created_at);
CREATE INDEX ix_users_id ON public.users USING btree (id);
CREATE INDEX user_profiles_embedding_idx ON public.user_profiles USING ivfflat (embedding public.vector_cosine_ops) WITH (lists='100');
CREATE TRIGGER update_institutions_updated_at BEFORE UPDATE ON public.institutions FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();
CREATE TRIGGER update_programs_updated_at BEFORE UPDATE ON public.programs FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();
CREATE TRIGGER update_user_preferences_updated_at BEFORE UPDATE ON public.user_program_preferences FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();
ALTER TABLE ONLY public.chat_messages
ALTER TABLE ONLY public.tree_paths
ALTER TABLE ONLY public.gca_users_answers
ALTER TABLE ONLY public.gca_users_answers
ALTER TABLE ONLY public.gca_users_answers
ALTER TABLE ONLY public.llm_descriptions
ALTER TABLE ONLY public.message_components
ALTER TABLE ONLY public.messages
ALTER TABLE ONLY public.messages
ALTER TABLE ONLY public.node_notes
ALTER TABLE ONLY public.personality_assessments
ALTER TABLE ONLY public.personality_embeddings
ALTER TABLE ONLY public.personality_profiles
ALTER TABLE ONLY public.personality_profiles
ALTER TABLE ONLY public.personality_responses
ALTER TABLE ONLY public.personality_trends
ALTER TABLE ONLY public.programs
ALTER TABLE ONLY public.psychological_insights
ALTER TABLE ONLY public.psychological_insights
ALTER TABLE ONLY public.saved_jobs
ALTER TABLE ONLY public.saved_recommendations
ALTER TABLE ONLY public.saved_recommendations
ALTER TABLE ONLY public.strengths_reflection_responses
ALTER TABLE ONLY public.suggested_peers
ALTER TABLE ONLY public.suggested_peers
ALTER TABLE ONLY public.tool_invocations
ALTER TABLE ONLY public.tool_invocations
ALTER TABLE ONLY public.tree_generations
ALTER TABLE ONLY public.tree_paths
ALTER TABLE ONLY public.user_chat_analytics
ALTER TABLE ONLY public.user_journey_milestones
ALTER TABLE ONLY public.user_journey_milestones
ALTER TABLE ONLY public.user_notes
ALTER TABLE ONLY public.user_notes
ALTER TABLE ONLY public.user_profiles
ALTER TABLE ONLY public.user_program_preferences
ALTER TABLE ONLY public.user_progress
ALTER TABLE ONLY public.user_recommendations
ALTER TABLE ONLY public.user_representation
ALTER TABLE ONLY public.user_skill_graphs
ALTER TABLE ONLY public.user_skill_nodes
ALTER TABLE ONLY public.user_skill_trees
ALTER TABLE ONLY public.user_skills