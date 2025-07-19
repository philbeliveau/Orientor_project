# Backend Architecture - Detailed Service Mapping

## 🔧 **Backend Architecture Overview**

```mermaid
graph TB
    %% Main FastAPI Application
    FASTAPI[🚀 FastAPI Application] --> MAIN[📋 main.py]
    MAIN --> MIDDLEWARE[🔧 Middleware Layer]
    MAIN --> ROUTERS[🌐 Router Layer - 35+ Routers]
    
    %% Middleware
    MIDDLEWARE --> CORS[🌍 CORS Middleware]
    MIDDLEWARE --> AUTH_MIDDLEWARE[🔐 Auth Middleware]
    MIDDLEWARE --> LOGGING[📋 Logging Middleware]
    
    %% Authentication Routers
    ROUTERS --> AUTH_ROUTERS[🔐 Authentication]
    AUTH_ROUTERS --> USER_ROUTER[👤 user.py]
    AUTH_ROUTERS --> PROFILES_ROUTER[📝 profiles.py]
    AUTH_ROUTERS --> ONBOARD_ROUTER[🚀 onboarding.py]
    AUTH_ROUTERS --> AVATAR_ROUTER[🎭 avatar.py]
    
    %% Chat & Communication Routers
    ROUTERS --> CHAT_ROUTERS[💬 Chat & Communication]
    CHAT_ROUTERS --> CHAT_ROUTER[💭 chat.py]
    CHAT_ROUTERS --> ENHANCED_ROUTER[⚡ enhanced_chat.py]
    CHAT_ROUTERS --> SOCRATIC_ROUTER[🤔 socratic_chat.py]
    CHAT_ROUTERS --> CONV_ROUTER[📋 conversations.py]
    CHAT_ROUTERS --> MSG_ROUTER[📨 messages.py]
    CHAT_ROUTERS --> ANALYTICS_ROUTER[📊 chat_analytics.py]
    CHAT_ROUTERS --> JOB_CHAT_ROUTER[💼 job_chat.py]
    
    %% Career & Skills Routers
    ROUTERS --> CAREER_ROUTERS[🌳 Career & Skills]
    CAREER_ROUTERS --> CAREERS_ROUTER[🎯 careers.py]
    CAREER_ROUTERS --> TREE_ROUTER[🌲 tree.py]
    CAREER_ROUTERS --> COMPETENCE_ROUTER[🌿 competence_tree.py]
    CAREER_ROUTERS --> PATHS_ROUTER[🛤️ tree_paths.py]
    CAREER_ROUTERS --> JOBS_ROUTER[💼 jobs.py]
    CAREER_ROUTERS --> REC_ROUTER[📋 recommendations.py]
    CAREER_ROUTERS --> PROGRESSION_ROUTER[📈 career_progression.py]
    CAREER_ROUTERS --> GOALS_ROUTER[🎯 career_goals.py]
    CAREER_ROUTERS --> NOTES_ROUTER[📝 node_notes.py]
    CAREER_ROUTERS --> PROGRESS_ROUTER[📊 user_progress.py]
    
    %% Assessment Routers
    ROUTERS --> ASSESS_ROUTERS[📊 Assessments]
    ASSESS_ROUTERS --> HEXACO_ROUTER[🧠 hexaco_test.py]
    ASSESS_ROUTERS --> HOLLAND_ROUTER[🔍 holland_test.py]
    ASSESS_ROUTERS --> REFLECTION_ROUTER[🪞 reflection_router.py]
    ASSESS_ROUTERS --> INSIGHT_ROUTER[💡 insight_router.py]
    
    %% Education Routers
    ROUTERS --> EDU_ROUTERS[🎓 Education]
    EDU_ROUTERS --> EDUCATION_ROUTER[📚 education.py]
    EDU_ROUTERS --> SCHOOL_ROUTER[🏫 school_programs.py]
    EDU_ROUTERS --> COURSES_ROUTER[📝 courses.py]
    EDU_ROUTERS --> PROG_REC_ROUTER[📋 program_recommendations.py]
    
    %% Social Routers
    ROUTERS --> SOCIAL_ROUTERS[👥 Social]
    SOCIAL_ROUTERS --> PEERS_ROUTER[🤝 peers.py]
    SOCIAL_ROUTERS --> SHARE_ROUTER[📤 share.py]
    SOCIAL_ROUTERS --> SPACE_ROUTER[🌌 space.py]
    SOCIAL_ROUTERS --> USERS_ROUTER[👥 users.py]
    
    %% AI Integration Routers
    ROUTERS --> AI_ROUTERS[🤖 AI Integration]
    AI_ROUTERS --> ORIENTATOR_ROUTER[🤖 orientator.py]
    AI_ROUTERS --> LLM_ADVISOR_ROUTER[🧠 llm_career_advisor.py]
    AI_ROUTERS --> VECTOR_ROUTER[🔍 vector_search.py]
    
    %% Utility Routers
    ROUTERS --> UTIL_ROUTERS[🔧 Utilities]
    UTIL_ROUTERS --> TEST_ROUTER[🧪 test.py]
    UTIL_ROUTERS --> RESUME_ROUTER[📄 resume.py]
    
    %% Models Layer
    FASTAPI --> MODELS[🗃️ Models Layer - 25+ Models]
    
    %% Core Models
    MODELS --> CORE_MODELS[👤 Core Models]
    CORE_MODELS --> USER_MODEL[👤 user.py - 50+ relationships]
    CORE_MODELS --> PROFILE_MODEL[📝 user_profile.py]
    CORE_MODELS --> SKILL_MODEL[⚡ user_skill.py]
    CORE_MODELS --> REPRESENTATION_MODEL[🧠 user_representation.py]
    CORE_MODELS --> PROGRESS_MODEL[📊 user_progress.py]
    CORE_MODELS --> NOTE_MODEL[📝 user_note.py]
    
    %% Chat Models
    MODELS --> CHAT_MODELS[💬 Chat Models]
    CHAT_MODELS --> CONVERSATION_MODEL[📋 conversation.py]
    CHAT_MODELS --> MESSAGE_MODEL[📨 message.py]
    CHAT_MODELS --> CHAT_MSG_MODEL[💭 chat_message.py]
    CHAT_MODELS --> MSG_COMP_MODEL[🧩 message_component.py]
    CHAT_MODELS --> CONV_CAT_MODEL[📂 conversation_category.py]
    CHAT_MODELS --> CONV_SHARE_MODEL[📤 conversation_share.py]
    CHAT_MODELS --> ANALYTICS_MODEL[📊 user_chat_analytics.py]
    
    %% Career Models
    MODELS --> CAREER_MODELS[🌳 Career Models]
    CAREER_MODELS --> CAREER_GOAL_MODEL[🎯 career_goal.py]
    CAREER_MODELS --> SAVED_REC_MODEL[⭐ saved_recommendation.py]
    CAREER_MODELS --> TREE_PATH_MODEL[🛤️ tree_path.py]
    CAREER_MODELS --> NODE_NOTE_MODEL[📝 node_note.py]
    CAREER_MODELS --> USER_REC_MODEL[📋 user_recommendation.py]
    CAREER_MODELS --> SKILL_TREE_MODEL[🌲 user_skill_tree.py]
    
    %% Assessment Models
    MODELS --> ASSESS_MODELS[📊 Assessment Models]
    ASSESS_MODELS --> PERSONALITY_MODEL[🧠 personality_profiles.py]
    ASSESS_MODELS --> REFLECTION_MODEL[🪞 reflection.py]
    ASSESS_MODELS --> SUGGESTED_PEERS_MODEL[🤝 suggested_peers.py]
    
    %% Education Models
    MODELS --> EDU_MODELS[🎓 Education Models]
    EDU_MODELS --> COURSE_MODEL[📝 course.py]
    EDU_MODELS --> SCHOOL_PROGRAM_MODEL[🏫 school_program.py]
    
    %% AI Models
    MODELS --> AI_MODELS[🤖 AI Models]
    AI_MODELS --> TOOL_INVOCATION_MODEL[🔨 tool_invocation.py]
    AI_MODELS --> JOURNEY_MODEL[🗺️ user_journey_milestone.py]
    
    %% Services Layer
    FASTAPI --> SERVICES[🛠️ Services Layer - 30+ Services]
    
    %% AI Services
    SERVICES --> AI_SERVICES[🤖 AI Services]
    AI_SERVICES --> ORIENTATOR_SERVICE[🤖 orientator_ai_service.py]
    AI_SERVICES --> TOOL_REGISTRY[🔨 tool_registry.py]
    AI_SERVICES --> LLM_SERVICE[🧠 llm_service.py]
    AI_SERVICES --> LLM_ANALYSIS[📊 llm_analysis_service.py]
    
    %% Embedding Services
    SERVICES --> EMBED_SERVICES[📊 Embedding Services]
    EMBED_SERVICES --> ESCO_EMBED[📈 esco_embedding_service384.py]
    EMBED_SERVICES --> OASIS_EMBED[🔍 Oasisembedding_service.py]
    EMBED_SERVICES --> ESCO_INTEGRATION[🔗 esco_integration_service.py]
    EMBED_SERVICES --> ESCO_FORMAT[📝 esco_formatting_service.py]
    
    %% Neural Network Services
    SERVICES --> NEURAL_SERVICES[🕸️ Neural Network Services]
    NEURAL_SERVICES --> GRAPHSAGE[🕸️ GraphSage.py]
    NEURAL_SERVICES --> GRAPHSAGE_LLM[🤖 graphsage_llm_integration.py]
    
    %% Tree Generation Services
    SERVICES --> TREE_SERVICES[🌳 Tree Services]
    TREE_SERVICES --> COMPETENCE_TREE[🌿 competenceTree.py]
    TREE_SERVICES --> OCCUPATION_TREE[💼 occupationTree.py]
    TREE_SERVICES --> LLM_CAREER_TREE[🌳 LLMcareerTree.py]
    TREE_SERVICES --> LLM_SKILLS_TREE[⚡ LLMskillsTree.py]
    TREE_SERVICES --> LLM_COMPETENCE[🌿 LLMcompetence_service.py]
    
    %% Assessment Services
    SERVICES --> ASSESS_SERVICES[📊 Assessment Services]
    ASSESS_SERVICES --> HEXACO_SERVICE[🧠 hexaco_service.py]
    ASSESS_SERVICES --> LLM_HEXACO[🧠 LLMhexaco_service.py]
    ASSESS_SERVICES --> LLM_HOLLAND[🔍 LLMholland_service.py]
    ASSESS_SERVICES --> HEXACO_SCORING[📈 hexaco_scoring_service.py]
    
    %% Career Services
    SERVICES --> CAREER_SERVICES[🎯 Career Services]
    CAREER_SERVICES --> CAREER_PROGRESSION[📈 career_progression_service.py]
    CAREER_SERVICES --> SWIPE_REC[📱 Swipe_career_recommendation_service.py]
    CAREER_SERVICES --> LLM_COMPATIBILITY[🤝 LLMcompatibility_service.py]
    CAREER_SERVICES --> JOB_CARD_LLM[💼 job_card_llm_service.py]
    
    %% Chat Services
    SERVICES --> CHAT_SERVICES[💬 Chat Services]
    CHAT_SERVICES --> ENHANCED_CHAT[⚡ enhanced_chat_service.py]
    CHAT_SERVICES --> SOCRATIC_CHAT[🤔 socratic_chat_service.py]
    CHAT_SERVICES --> CHAT_MESSAGE[📨 chat_message_service.py]
    CHAT_SERVICES --> CONVERSATION[📋 conversation_service.py]
    CHAT_SERVICES --> CATEGORY[📂 category_service.py]
    CHAT_SERVICES --> ANALYTICS[📊 analytics_service.py]
    
    %% Social Services
    SERVICES --> SOCIAL_SERVICES[👥 Social Services]
    SOCIAL_SERVICES --> PEER_MATCHING[🤝 peer_matching_service.py]
    SOCIAL_SERVICES --> SHARE_SERVICE[📤 share_service.py]
    
    %% Education Services
    SERVICES --> EDU_SERVICES[🎓 Education Services]
    EDU_SERVICES --> COURSE_ANALYSIS[📊 course_analysis_service.py]
    EDU_SERVICES --> LLM_COURSE[📝 llm_course_service.py]
    EDU_SERVICES --> SCHOOL_PROGRAMS[🏫 school_programs_service.py]
    EDU_SERVICES --> SCHOOL_INGESTION[📥 school_programs_ingestion.py]
    EDU_SERVICES --> PROGRAM_MATCHING[🎯 program_matching_service.py]
    
    %% Utility Services
    SERVICES --> UTIL_SERVICES[🔧 Utility Services]
    UTIL_SERVICES --> AVATAR_SERVICE[🎭 avatar_service.py]
    
    %% Database Layer
    FASTAPI --> DATABASE[🗄️ Database Layer]
    DATABASE --> DB_UTILS[🔧 Database Utils]
    DATABASE --> MIGRATIONS[📦 Alembic Migrations]
    
    %% Database Utils
    DB_UTILS --> DB_CONNECTION[🔗 database.py]
    DB_UTILS --> DB_BASE[🏗️ base.py]
    
    %% Migrations
    MIGRATIONS --> MIGRATION_FILES[📄 25+ Migration Files]
    MIGRATION_FILES --> CREATE_USERS[👤 create_users_table.py]
    MIGRATION_FILES --> ORIENTATOR_TABLES[🤖 add_orientator_ai_tables.py]
    MIGRATION_FILES --> CHAT_TABLES[💬 add_chat_persistence_tables.py]
    MIGRATION_FILES --> SPACE_TABLES[🌌 add_space_feature_tables.py]
    MIGRATION_FILES --> VECTOR_EMBED[📊 add_vector_embeddings.py]
    MIGRATION_FILES --> ONBOARD_COL[🚀 add_onboarding_completed_column.py]
    MIGRATION_FILES --> SCHOOL_TABLES[🏫 add_school_programs_tables.py]
    MIGRATION_FILES --> TREE_TABLES[🌳 add_interactive_tree_tables.py]
    MIGRATION_FILES --> COURSE_TABLES[📝 add_course_analysis_tables.py]
    
    %% Configuration
    FASTAPI --> CONFIG[⚙️ Configuration]
    CONFIG --> CORE_CONFIG[🏗️ Core Config]
    CONFIG --> UTILS[🔧 Utils]
    
    %% Core Config
    CORE_CONFIG --> CONFIG_PY[⚙️ config.py]
    CORE_CONFIG --> CACHE_PY[⚡ cache.py]
    
    %% Utils
    UTILS --> LOGGING_CONFIG[📋 logging_config.py]
    UTILS --> MESSAGING[📨 messaging.py]
    UTILS --> EMBEDDINGS[📊 embeddings_v1.py]
    
    classDef routers fill:#e3f2fd,stroke:#0d47a1,stroke-width:2px
    classDef models fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    classDef services fill:#e8f5e8,stroke:#1b5e20,stroke-width:2px
    classDef database fill:#fff3e0,stroke:#e65100,stroke-width:2px
    classDef config fill:#fce4ec,stroke:#880e4f,stroke-width:2px
    classDef core fill:#f1f8e9,stroke:#33691e,stroke-width:2px
    
    class AUTH_ROUTERS,CHAT_ROUTERS,CAREER_ROUTERS,ASSESS_ROUTERS,EDU_ROUTERS,SOCIAL_ROUTERS,AI_ROUTERS,UTIL_ROUTERS routers
    class CORE_MODELS,CHAT_MODELS,CAREER_MODELS,ASSESS_MODELS,EDU_MODELS,AI_MODELS models
    class AI_SERVICES,EMBED_SERVICES,NEURAL_SERVICES,TREE_SERVICES,ASSESS_SERVICES,CAREER_SERVICES,CHAT_SERVICES,SOCIAL_SERVICES,EDU_SERVICES,UTIL_SERVICES services
    class DATABASE,DB_UTILS,MIGRATIONS database
    class CONFIG,CORE_CONFIG,UTILS config
    class FASTAPI,MAIN,MIDDLEWARE core
```

## 🌐 **Router Layer Mapping (35+ Routers)**

### **Authentication & User Management**
| Router | Endpoints | Description |
|--------|-----------|-------------|
| `user.py` | `/auth/*`, `/user/*` | Authentication, JWT management, user CRUD |
| `profiles.py` | `/api/v1/profiles/*` | User profile management |
| `onboarding.py` | `/onboarding/*` | User onboarding flow |
| `avatar.py` | `/api/v1/avatar/*` | Avatar management and customization |

### **Chat & Communication System**
| Router | Endpoints | Description |
|--------|-----------|-------------|
| `chat.py` | `/chat/*` | Basic chat functionality |
| `enhanced_chat.py` | `/api/v1/enhanced-chat/*` | Advanced chat with AI tools |
| `socratic_chat.py` | `/socratic-chat/*` | Socratic questioning mode |
| `conversations.py` | `/conversations/*` | Conversation management |
| `messages.py` | `/messages/*` | Message handling and storage |
| `chat_analytics.py` | `/chat-analytics/*` | Chat usage analytics |
| `job_chat.py` | `/job-chat/*` | Job-specific chat features |

### **Career & Skills System**
| Router | Endpoints | Description |
|--------|-----------|-------------|
| `careers.py` | `/careers/*` | Career exploration and data |
| `tree.py` | `/tree/*` | Basic tree functionality |
| `competence_tree.py` | `/api/v1/competence-tree/*` | Interactive competence trees |
| `tree_paths.py` | `/tree-paths/*` | Tree navigation tracking |
| `jobs.py` | `/api/v1/jobs/*` | Job recommendations and data |
| `recommendations.py` | `/recommendations/*` | General recommendations |
| `career_progression.py` | `/api/v1/career-progression/*` | Career advancement paths |
| `career_goals.py` | `/career-goals/*` | Goal setting and tracking |
| `node_notes.py` | `/node-notes/*` | User annotations on tree nodes |
| `user_progress.py` | `/user-progress/*` | Progress tracking |

### **Assessment System**
| Router | Endpoints | Description |
|--------|-----------|-------------|
| `hexaco_test.py` | `/hexaco-test/*` | HEXACO personality assessment |
| `holland_test.py` | `/holland-test/*` | Holland Code interest assessment |
| `reflection_router.py` | `/reflection/*` | Self-reflection exercises |
| `insight_router.py` | `/insights/*` | AI-generated insights |

### **Education & Programs**
| Router | Endpoints | Description |
|--------|-----------|-------------|
| `education.py` | `/education/*` | Education dashboard and data |
| `school_programs.py` | `/school-programs/*` | School program information |
| `courses.py` | `/courses/*` | Course management and analysis |
| `program_recommendations.py` | `/api/v1/program-recommendations/*` | Program matching |

### **Social Features**
| Router | Endpoints | Description |
|--------|-----------|-------------|
| `peers.py` | `/peers/*` | Peer matching and networking |
| `share.py` | `/share/*` | Content sharing features |
| `space.py` | `/space/*` | Personal career space |
| `users.py` | `/api/v1/users/*` | User management |

### **AI Integration**
| Router | Endpoints | Description |
|--------|-----------|-------------|
| `orientator.py` | `/api/orientator/*` | Main AI assistant interface |
| `llm_career_advisor.py` | `/llm-career-advisor/*` | LLM-powered career advice |
| `vector_search.py` | `/vector-search/*` | Semantic search functionality |

## 🗃️ **Models Layer (25+ Models)**

### **Core User Models**
- **user.py** - Central user model with 50+ relationships
- **user_profile.py** - User demographics and preferences
- **user_skill.py** - Skill assessments and competencies
- **user_representation.py** - AI embeddings and vectors
- **user_progress.py** - Journey and milestone tracking
- **user_note.py** - User-generated notes and annotations

### **Communication Models**
- **conversation.py** - Chat conversation containers
- **message.py** - Individual message storage
- **chat_message.py** - Enhanced chat messages with tools
- **message_component.py** - Structured message components
- **conversation_category.py** - Chat organization
- **conversation_share.py** - Sharing functionality
- **user_chat_analytics.py** - Usage analytics

### **Career & Skills Models**
- **career_goal.py** - User career objectives
- **saved_recommendation.py** - Bookmarked recommendations
- **tree_path.py** - Tree navigation history
- **node_note.py** - Tree node annotations
- **user_recommendation.py** - Personalized recommendations
- **user_skill_tree.py** - Custom skill trees

### **Assessment Models**
- **personality_profiles.py** - HEXACO and other assessments
- **reflection.py** - Self-reflection responses
- **suggested_peers.py** - Peer matching data

### **Education Models**
- **course.py** - User course information
- **school_program.py** - Available educational programs

### **AI Integration Models**
- **tool_invocation.py** - AI tool usage tracking
- **user_journey_milestone.py** - AI-tracked progress

## 🛠️ **Services Layer (30+ Services)**

### **AI & ML Services**
- **orientator_ai_service.py** - Core AI conversation engine
- **tool_registry.py** - AI tool management and invocation
- **llm_service.py** - Language model integration
- **llm_analysis_service.py** - Content analysis services

### **Embedding Services**
- **esco_embedding_service384.py** - ESCO skills embeddings
- **Oasisembedding_service.py** - OASIS job embeddings
- **esco_integration_service.py** - ESCO data integration
- **esco_formatting_service.py** - ESCO data formatting

### **Neural Network Services**
- **GraphSage.py** - Graph neural network implementation
- **graphsage_llm_integration.py** - GNN-LLM integration

### **Tree Generation Services**
- **competenceTree.py** - Competence tree generation
- **occupationTree.py** - Occupation tree creation
- **LLMcareerTree.py** - LLM-powered career trees
- **LLMskillsTree.py** - LLM-powered skills trees
- **LLMcompetence_service.py** - LLM competence analysis

### **Assessment Services**
- **hexaco_service.py** - HEXACO test processing
- **LLMhexaco_service.py** - LLM-enhanced HEXACO analysis
- **LLMholland_service.py** - LLM-enhanced Holland analysis
- **hexaco_scoring_service.py** - HEXACO scoring algorithms

### **Career Services**
- **career_progression_service.py** - Career path analysis
- **Swipe_career_recommendation_service.py** - Swipeable recommendations
- **LLMcompatibility_service.py** - Career compatibility analysis
- **job_card_llm_service.py** - Job card generation

### **Communication Services**
- **enhanced_chat_service.py** - Advanced chat features
- **socratic_chat_service.py** - Socratic questioning
- **chat_message_service.py** - Message processing
- **conversation_service.py** - Conversation management
- **category_service.py** - Chat categorization
- **analytics_service.py** - Usage analytics

### **Social Services**
- **peer_matching_service.py** - Peer recommendation engine
- **share_service.py** - Content sharing logic

### **Education Services**
- **course_analysis_service.py** - Course content analysis
- **llm_course_service.py** - LLM course recommendations
- **school_programs_service.py** - Program data management
- **school_programs_ingestion.py** - Program data import
- **program_matching_service.py** - Program recommendation engine

## 🗄️ **Database Layer**

### **Connection Management**
- **database.py** - Railway-optimized connection pooling
- **base.py** - SQLAlchemy base model definitions

### **Migration System (25+ Files)**
- **create_users_table.py** - Initial user table creation
- **add_orientator_ai_tables.py** - AI system tables
- **add_chat_persistence_tables.py** - Chat system tables
- **add_space_feature_tables.py** - Career space features
- **add_vector_embeddings.py** - Vector storage support
- **add_onboarding_completed_column.py** - Onboarding tracking
- **add_school_programs_tables.py** - Education system tables
- **add_interactive_tree_tables.py** - Tree interaction tracking
- **add_course_analysis_tables.py** - Course analysis features

### **Configuration & Utilities**
- **config.py** - Environment and database configuration
- **cache.py** - Caching layer management
- **logging_config.py** - Structured logging setup
- **messaging.py** - Message processing utilities
- **embeddings_v1.py** - Embedding utilities

This backend architecture provides a robust, scalable foundation for the Orientor platform with clear separation of concerns, comprehensive AI integration, and efficient data management.