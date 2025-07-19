# 🚀 Railway Deployment Debug & Trim Guide

## 🎯 Quick Start

### Step 1: Run Diagnosis
```bash
# Test current state
python deploy-debug.py --phase 1

# Save detailed diagnosis
python deploy-debug.py --phase 1 --output diagnosis.json
```

### Step 2: If Diagnosis Fails, Trim Codebase
```bash
# Create progressive deployment phases
python trim-codebase.py
```

### Step 3: Test Each Phase
```bash
# Test Phase 1 (minimal)
python deploy-debug.py --phase 1

# Test Phase 2 (+ AI)
python deploy-debug.py --phase 2

# Test Phase 3 (full)
python deploy-debug.py --phase 3
```

## 📋 Deployment Phases

### 🟢 Phase 1: Minimal Viable Deployment
- **Goal**: Get basic API running on Railway
- **Features**: Auth, Profiles, Database
- **Size**: ~50MB
- **Time**: 2-3 minutes build
- **Requirements**: `requirements-phase1.txt`

**Deploy Command:**
```bash
# Update railway-new.toml to use phase1
# Then deploy
railway up
```

### 🟡 Phase 2: Basic AI Features  
- **Goal**: Add OpenAI integration
- **Features**: Phase 1 + AI Chat
- **Size**: ~100MB
- **Time**: 3-5 minutes build
- **Requirements**: `requirements-phase2.txt`

### 🔴 Phase 3: Full Platform
- **Goal**: Complete feature set
- **Features**: Everything including ML
- **Size**: ~500MB
- **Time**: 5-10 minutes build
- **Requirements**: `requirements-phase3.txt`

## 🔧 Debugging Workflow

### 1. Initial Diagnosis
```bash
python deploy-debug.py --phase 1
```

**Common Issues & Fixes:**
- ❌ **Missing main.py**: Use generated `main_minimal.py`
- ❌ **Import errors**: Install missing packages
- ❌ **Database config**: Check `.env.supabase`

### 2. Progressive Testing
Start with Phase 1, then gradually add complexity:

```bash
# Phase 1: Minimal
cp backend-phase1/app/main.py backend/app/main.py
python deploy-debug.py --phase 1

# If successful, move to Phase 2
cp backend-phase2/app/main.py backend/app/main.py
python deploy-debug.py --phase 2
```

### 3. Railway Configuration
Update `railway-new.toml` for each phase:

```toml
# Phase 1
buildCommand = "pip install -r requirements-phase1.txt"

# Phase 2  
buildCommand = "pip install -r requirements-phase2.txt"

# Phase 3
buildCommand = "pip install -r requirements-phase3.txt"
```

## 🎯 Success Criteria

### Phase 1 Ready ✅
- All file checks pass
- Basic imports work
- Local startup succeeds
- Database connection configured

### Phase 2 Ready ✅
- Phase 1 + OpenAI imports
- AI chat endpoints work
- Memory usage < 2GB

### Phase 3 Ready ✅
- All ML dependencies install
- Models load successfully
- Total memory < 4GB

## 🆘 Emergency Minimal Deployment

If everything fails, use the absolute minimal setup:

```bash
# Use the generated minimal main.py
cp backend/app/main_minimal.py backend/app/main.py

# Use minimal requirements
cp requirements-phase1.txt requirements-simple.txt

# Deploy
railway up
```

This should give you a working "Hello World" API to build from.

## 📊 Monitoring Deployment

### Local Testing
```bash
# Test locally first
cd backend
python main_deploy.py
```

### Railway Logs
```bash
# Monitor deployment
railway logs

# Follow real-time
railway logs --follow
```

### Health Checks
- GET `/` - Basic status
- GET `/health` - Detailed health check
- GET `/docs` - API documentation

## 🔄 Iteration Strategy

1. **Start Minimal**: Always begin with Phase 1
2. **Test Locally**: Ensure it works before deploying
3. **Deploy & Monitor**: Watch Railway logs carefully
4. **Add Features**: Only move to next phase if current works
5. **Rollback Plan**: Keep previous working phase ready

## 📈 Expected Timeline

- **Phase 1**: 30 minutes to working deployment
- **Phase 2**: +1 hour to add AI features  
- **Phase 3**: +2 hours to add full ML stack

Total: **~3-4 hours** for complete progressive deployment.