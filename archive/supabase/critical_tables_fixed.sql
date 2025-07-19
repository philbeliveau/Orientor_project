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

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: programs; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.programs (
    id uuid DEFAULT uuid_generate_v4() NOT NULL,
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
-- Name: saved_recommendations id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.saved_recommendations ALTER COLUMN id SET DEFAULT nextval('public.saved_recommendations_id_seq'::regclass);


--
-- Name: user_profiles id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_profiles ALTER COLUMN id SET DEFAULT nextval('public.user_profiles_id_seq'::regclass);


--
-- Name: user_skills id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_skills ALTER COLUMN id SET DEFAULT nextval('public.user_skills_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


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
-- Name: saved_recommendations saved_recommendations_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.saved_recommendations
    ADD CONSTRAINT saved_recommendations_pkey PRIMARY KEY (id);


--
-- Name: saved_recommendations uq_user_oasis_code; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.saved_recommendations
    ADD CONSTRAINT uq_user_oasis_code UNIQUE (user_id, oasis_code);


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
-- Name: ix_saved_recommendations_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_saved_recommendations_id ON public.saved_recommendations USING btree (id);


--
-- Name: ix_saved_recommendations_user_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_saved_recommendations_user_id ON public.saved_recommendations USING btree (user_id);


--
-- Name: ix_user_profiles_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_user_profiles_id ON public.user_profiles USING btree (id);


--
-- Name: ix_user_skills_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_user_skills_id ON public.user_skills USING btree (id);


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
-- Name: programs update_programs_updated_at; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER update_programs_updated_at BEFORE UPDATE ON public.programs FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: programs programs_institution_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.programs
    ADD CONSTRAINT programs_institution_id_fkey FOREIGN KEY (institution_id) REFERENCES public.institutions(id) ON DELETE CASCADE;


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
-- Name: user_profiles user_profiles_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_profiles
    ADD CONSTRAINT user_profiles_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: user_skills user_skills_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_skills
    ADD CONSTRAINT user_skills_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- PostgreSQL database dump complete
--

