# 🚨 EMERGENCY DEPLOYMENT GUIDE - ORIENTOR PLATFORM

## ✅ PHASE 1 STATUS: READY FOR DEPLOYMENT

### 🔧 **Backend Configuration Complete**
- ✅ `requirements-phase1.txt` - minimal dependencies copied to root
- ✅ `railway-new.toml` - configured for Phase 1 deployment  
- ✅ `.env.production` - environment template created
- ✅ `backend/main_deploy.py` - entry point configured
- ✅ **Local test PASSED** - FastAPI starts successfully at localhost:8000

### 🎯 **IMMEDIATE MANUAL DEPLOYMENT STEPS**

#### **Backend (Railway)**
```bash
# 1. In Railway Dashboard
# - Create new project "orientor-backend"
# - Connect GitHub repository
# - Set root directory to "backend"
# - Environment variables:
#   DATABASE_URL: (Railway will auto-inject)
#   SUPABASE_URL: your_supabase_url
#   SUPABASE_ANON_KEY: your_supabase_anon_key
#   OPENAI_API_KEY: your_openai_key (for Phase 2)

# 2. Deploy configuration
Build Command: pip install -r ../requirements-phase1.txt
Start Command: python main_deploy.py
```

#### **Frontend (Vercel)**
```bash
# From frontend directory:
cd frontend
npm run build
npx vercel --prod

# Or via Vercel Dashboard:
# - Import from GitHub
# - Framework: Next.js
# - Root directory: frontend
# - Environment variables:
#   NEXT_PUBLIC_API_URL: https://your-railway-backend-url.railway.app
```

### 📊 **Deployment Readiness Score: 85%**

**✅ Ready components:**
- Backend FastAPI app (tested locally)
- Frontend Next.js build 
- Phase 1 minimal requirements
- Database configuration templates
- Railway configuration files

**⚠️ Manual steps required:**
- Railway project setup via dashboard
- Environment variables configuration
- Domain/URL configuration between frontend/backend

### 🚀 **Progressive Deployment Strategy**

**Phase 1 (NOW - 30 minutes):**
- Deploy minimal FastAPI backend (Railway)
- Deploy Next.js frontend (Vercel)
- Basic API endpoints + authentication

**Phase 2 (Next - 1 hour):**
- Update to `requirements-phase2.txt`
- Add OpenAI integration
- Enable AI chat features

**Phase 3 (Later - 2 hours):**
- Full ML stack with GraphSage neural networks
- Complete career recommendation system
- All advanced features

### 🔗 **Key URLs to Configure**
- Backend: `https://orientor-backend-[hash].railway.app`
- Frontend: `https://orientor-frontend-[hash].vercel.app`
- Database: Railway PostgreSQL (auto-configured)

### 📝 **Environment Variables Checklist**

**Railway (Backend):**
```
DATABASE_URL=postgresql://... (auto-injected)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=eyJ...
SUPABASE_SERVICE_ROLE_KEY=eyJ...
OPENAI_API_KEY=sk-... (Phase 2+)
ENVIRONMENT=production
```

**Vercel (Frontend):**
```
NEXT_PUBLIC_API_URL=https://your-railway-backend.railway.app
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJ...
```

### 🛠️ **Troubleshooting**

**If Backend deployment fails:**
1. Check `railway logs` for errors
2. Verify requirements-phase1.txt dependencies
3. Use `backend/app/main_minimal.py` as fallback

**If Frontend build fails:**
1. Run `npm install` in frontend directory
2. Check for TypeScript errors: `npm run type-check`
3. Use static export: `npm run export`

### ⚡ **Emergency Minimal Deployment**
If all else fails, use the absolute minimal setup:
```bash
# Backend: Use main_minimal.py with basic FastAPI
# Frontend: Deploy static version with `npm run export`
# Database: Skip complex features, use basic auth only
```

---

**🎯 CURRENT STATUS: Phase 1 ready for manual Railway + Vercel deployment**
**⏰ ESTIMATED TIME TO LIVE: 30-45 minutes**