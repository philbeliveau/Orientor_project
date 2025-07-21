# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 🎯 **Current Project Context: Orientor Platform Migration**

### **Project Overview**
We are migrating the Orientor career guidance platform from a fallback deployment system to a full-featured production architecture. The platform helps users with career recommendations, job matching, and skills assessment through AI-powered tools.

### **Current Phase: 1A - Critical Router Integration**
- **Objective**: Fix critical 404 errors breaking user experience
- **Status**: Implementing unified authentication system for Railway + Vercel deployment
- **Architecture**: FastAPI backend (Railway) + Next.js frontend (Vercel)

### **Key Files to Reference**

#### **📋 Critical Documentation** (Read These First)
- `docs/Louis-deployment/hive-mind/to-read/ERROR_REGISTRY.md` - All known issues and solutions
- `docs/Louis-deployment/hive-mind/to-read/STANDARDIZED_DEPLOYMENT_GUIDE.md` - Deployment standards and patterns
- `docs/Louis-deployment/hive-mind/ORIENTOR_MIGRATION_ROADMAP.md` - Complete migration strategy

#### **⚙️ Core Backend Files**
- `backend/main_deploy.py` - Main Railway deployment file with router integrations
- `backend/app/utils/auth.py` - Unified authentication system (base64 tokens → User objects)
- `backend/requirements.txt` - Core dependencies only (optimized for fast builds)
- `backend/requirements-ml.txt` - Heavy ML packages (added gradually per feature)

#### **🔧 Configuration Files**
- `backend/requirements-core.txt` - Essential packages reference
- `vercel.json` - Frontend deployment config with API proxying
- `frontend/next.config.js` - Next.js optimization settings

#### **📊 Migration Status**
- ✅ Phase 1A: Core routers (space, jobs) integrated with unified auth
- ✅ Fixed authentication architecture mismatch (dict vs User objects)
- ✅ Optimized dependency management for fast Railway builds
- 🔄 Currently: Testing unified auth deployment and endpoint functionality
- 📅 Next: Gradual ML dependency addition as features require

#### **🚨 Known Critical Issues**
- Authentication pattern inconsistency across routers (systematically fixed)
- Missing heavy dependencies causing import failures (gradual deployment strategy implemented)
- CORS and 500 errors on frontend endpoints (resolved with unified auth)

#### **🎯 Immediate Goals**
1. Verify unified authentication works in production
2. Test `/careers/saved` and `/api/v1/jobs/saved` endpoints
3. Monitor Railway build performance with optimized requirements
4. Update error registry with confirmed solutions

### **Deployment Notes**
- Our goal is to get the libraries required by my colleague installed with minimal build time
- Documentation for the complete deployment plan is available in the hive-mind
- Follow practices outlined in standardized_deployment_guide.md for consistent and efficient library installation

[Rest of the file remains unchanged]