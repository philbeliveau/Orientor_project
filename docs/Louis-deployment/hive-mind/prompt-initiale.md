  ORIENTOR PLATFORM MIGRATION ANALYSIS - CRITICAL PRODUCTION TASK

  PROJECT OVERVIEW

  Orientor is an AI-powered career guidance platform helping users with personality assessments, job recommendations, skill development, and career planning. The platform
  consists of:
  - Backend: FastAPI + SQLAlchemy + PostgreSQL (deployed on Railway)
  - Frontend: Next.js React application (deployed on Vercel at navigoproject.vercel.app)
  - Database: PostgreSQL with 30+ models including users, profiles, assessments, jobs, skills

DEPLOYMENT INFRASTRUCTURE

  Current Deployment Environment:
  - Backend: Deployed on Railway (main_deploy.py currently in production)
  - Frontend: Deployed on Vercel (navigoproject.vercel.app)
  - Database: PostgreSQL hosted on Railway (same environment as backend)
  - Configuration: Environment variables managed through Railway dashboard
  - Domain: Backend accessible at orientor-backend-production-7c13.up.railway.app

  Migration Considerations:
  - Database and backend are co-located on Railway for optimal performance
  - No cross-cloud latency issues between backend and database
  - Railway's automatic deployments from git commits enable rapid iteration
  - Vercel frontend can seamlessly connect to Railway backend APIs
  - Database migrations can be executed directly in Railway environment
  - Rollback capabilities available through Railway's deployment history

  CURRENT CRITICAL SITUATION

  The production deployment is running on main_deploy.py (2000+ lines) which contains mostly FALLBACK endpoints with hardcoded mock data. The real application architecture
  exists in app/main.py with 40+ specialized routers using actual database operations, but it's not deployed.

  Frontend is experiencing multiple 404 errors:
  - /profiles/me - User profile management (CRITICAL - breaks user experience)
  - /space/skills - Skills management system
  - /api/v1/socratic-chat/send - AI chat functionality
  - /insight/get - Philosophical insights feature
  - /api/v1/education/metadata - Education system data
  - External API calls to navigoproject.vercel.app competence tree

  Working vs Broken:
  - ✅ Authentication, onboarding, HEXACO/Holland assessments use real database
  - ❌ User profiles, job recommendations, progress tracking, courses = fake data
  - ❌ Skills management, chat systems, education metadata = missing entirely

  CODEBASE ARCHITECTURE

  Key Router Files (app/routers/):
  - profiles.py - User profile CRUD with embeddings/ML integration
  - jobs.py - Job recommendations and saved jobs management
  - space.py - Skills tracking and notes management
  - socratic_chat.py - AI-powered career conversations
  - education.py - Education metadata and course management
  - career_goals.py - Goal setting and tracking
  - user_progress.py - Progress analytics and milestones

  Database Models (app/models/):
  - Core: User, UserProfile, UserSkill
  - Assessments: PersonalityAssessment, PersonalityResponse, PersonalityProfile
  - Jobs: SavedJob, UserRecommendation
  - Progress: UserProgress, UserJourneyMilestone
  - Chat: ChatMessage, Conversation, ConversationShare

  MIGRATION CHALLENGE

  Need to systematically replace main_deploy.py fallback endpoints with real routers from app/main.py WITHOUT breaking production. This requires:
  1. Understanding router dependencies and import chains
  2. Identifying missing database tables/columns for each router
  3. Assessing integration risks (high/medium/low)
  4. Creating safe rollback strategies for each phase
  5. Prioritizing based on frontend user impact

  ANALYSIS REQUIREMENTS

  1. ROUTER DEPENDENCY ANALYSIS
  - Map import dependencies between routers
  - Identify circular dependency risks
  - Document shared services and utilities each router needs
  - Classify routers as: Independent, Dependent, or Core Infrastructure

  2. DATABASE SCHEMA VALIDATION
  - Cross-reference each router's model requirements against current database
  - Identify missing tables, columns, or constraints
  - Assess data migration needs for each router
  - Document foreign key relationships and potential cascade issues

  3. RISK ASSESSMENT MATRIX
  - Categorize each router integration as High/Medium/Low risk
  - Factors: complexity, dependencies, database changes, user impact
  - High Risk: Complex ML pipelines, external API dependencies
  - Low Risk: Simple CRUD operations, no external dependencies

  4. PHASED MIGRATION STRATEGY
  - Phase 1A (Critical): Fix immediate 404s affecting core user flows
  - Phase 1B (High): Replace fake data with real database operations
  - Phase 2A (Medium): Add missing functionality for complete user experience
  - Phase 2B (Low): Optional features and advanced functionality

  5. FRONTEND IMPACT ASSESSMENT
  - Map each 404 error to specific user journey breakpoints
  - Prioritize fixes based on user experience severity
  - Identify API contract changes that could break frontend

  DELIVERABLE REQUIREMENTS

  Provide a comprehensive migration roadmap including:

  EXECUTIVE SUMMARY
  - Current state assessment
  - Key risks and mitigation strategies
  - Recommended migration sequence
  - Timeline estimates for each phase

  DETAILED IMPLEMENTATION PLAN
  - Exact order of router integrations with justification
  - Prerequisites and dependencies for each step
  - Database migration scripts needed
  - Rollback procedures for each phase
  - Testing checkpoints and validation criteria

  RISK MITIGATION STRATEGIES
  - Backup and rollback plans
  - Canary deployment approaches
  - Monitoring and alerting recommendations
  - Contingency plans for high-risk integrations

  RESOURCE REQUIREMENTS
  - Development time estimates
  - Database maintenance windows needed
  - Testing environment requirements
  - Coordination between frontend/backend teams

  The goal is to transition from the current fallback system to the full-featured application architecture while maintaining 100% uptime and user experience quality.