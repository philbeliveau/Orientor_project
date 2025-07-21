# Error Registry and Solutions

This document tracks critical errors encountered during the Orientor platform migration and their solutions to prevent recurring issues.

## Error Categories

### 🔴 PENDING CONFIRMATION
Issues that have been fixed but are awaiting user confirmation before being marked as resolved.

### ✅ RESOLVED  
Issues that have been confirmed fixed by the user.

### 🔄 IN PROGRESS
Issues currently being worked on.

---

## RESOLVED

### ERROR-001: Authentication Type Mismatch (User Object vs Dictionary)
**Date**: 2025-07-21  
**Status**: ✅ RESOLVED  
**Confirmed**: 2025-07-21 - User confirmed `/careers/saved` returns 200 OK  
**Severity**: High  
**Component**: Authentication/Database Integration  

**Problem Description**:
The `/careers/saved` endpoint was failing with `'dict' object has no attribute 'id'` error. The authentication function `get_current_user_with_onboarding` was returning a dictionary with user information, but the `get_saved_recommendations` function expected an actual SQLAlchemy User model object.

**Error Manifestation**:
```
ERROR: 'dict' object has no attribute 'id'
File "/app/app/routers/space.py", line 139, in get_saved_recommendations
    SavedRecommendation.user_id == current_user.id
                                   ^^^^^^^^^^^^^^^
AttributeError: 'dict' object has no attribute 'id'
```

**Root Cause**:
Inconsistent authentication pattern - some functions return User objects, others return dictionaries. The space router expects SQLAlchemy model objects for database queries.

**Solution Applied**:
Modified `/careers/saved` endpoint to:
1. Decode authorization token manually
2. Fetch actual User object from database using user_id
3. Pass real User object to `get_saved_recommendations`

**Code Pattern to Follow**:
```python
# CORRECT: Fetch actual User object for database operations
token = authorization.split(" ")[1]
decoded = base64.b64decode(token).decode()
email, user_id, onboarding_completed, timestamp = decoded.split(":", 3)

db = next(get_db())
current_user = db.query(User).filter(User.id == int(user_id)).first()
if not current_user:
    raise HTTPException(status_code=401, detail="User not found")

# INCORRECT: Using dict object for database queries
current_user = {"id": user_id, "email": email}  # This will fail
```

**Prevention Strategy**:
- Always verify what type authentication functions return (dict vs User object)
- For database operations requiring relationships, always fetch the actual SQLAlchemy model
- Document clearly in function signatures what type is returned
- Consider creating a unified authentication decorator that returns User objects

**Files Modified**:
- `backend/main_deploy.py`: Lines 2037-2067

**Commits**:
- `57977e1b`: Fix User object issue - fetch actual User from database instead of dict

**CONFIRMED WORKING**: `/careers/saved` returns 200 OK with proper user data

---

## PENDING COMPLETION

### ERROR-005: Profiles Router - ML Dependencies Required for Full Functionality
**Date**: 2025-07-21  
**Status**: 🟡 PENDING COMPLETION - BASIC FUNCTIONALITY WORKING  
**Severity**: Medium  
**Component**: Profiles Router + ML Pipeline  

**Problem Description**:
Profiles router requires heavy ML dependencies (torch, transformers, sentence-transformers) for embedding generation and peer matching functionality. These dependencies cause slow Railway builds and deployment complexity.

**Business Logic Context**:
- User profile updates trigger embedding regeneration for similarity matching
- Embeddings power peer recommendations and compatibility scores  
- ML pipeline is core to user experience, not optional feature

**Current Status**:
- ✅ Basic profile CRUD (GET /profiles/me, PUT /profiles/update) works without ML
- ✅ Graceful degradation when ML services unavailable
- ❌ No peer matching or embedding-based recommendations
- ❌ Heavy dependencies (torch ~2GB) cause slow builds

**Implementation Strategy**:
```python
# Current working fallbacks:
if OASIS_EMBEDDING_AVAILABLE:
    # Full ML pipeline with embeddings
else:
    # Basic profile updates only
```

**Required for Full Implementation**:
```python
# Add to requirements.txt when ready:
torch>=2.0.0              # ~2GB - Core ML functionality
transformers>=4.20.0      # ~500MB - BERT models
sentence-transformers>=2.2.0  # ~300MB - Semantic embeddings  
scikit-learn>=1.3.0       # ~200MB - Similarity calculations
```

**Files Modified**:
- `backend/app/routers/profiles.py` - Graceful ML fallbacks implemented
- `backend/main_deploy.py` - Import error handling added

**Next Steps When Ready**:
1. Add ML dependencies to requirements.txt (expect 5-10 min builds)
2. Monitor Railway memory usage during build
3. Test full embedding pipeline end-to-end
4. Verify peer matching and recommendations work

**Note**: Deferred to focus on lightweight features first. Profiles basic functionality works without ML.

---

## IN PROGRESS

### ERROR-002: Missing Pandas Dependency for Profiles Router
**Date**: 2025-07-21  
**Status**: 🔄 IN PROGRESS  
**Severity**: Medium  
**Component**: Dependencies/Profiles Router  

**Problem Description**:
Profiles router fails to import due to missing pandas dependency: `No module named 'pandas'`

**Error Manifestation**:
```
ERROR:root:❌ Profiles router import failed: No module named 'pandas'
```

**Impact**: Profiles router not available, health check shows `"profiles": false`

**Investigation**: Checking if pandas is required dependency and if it should be added to requirements

### ERROR-003: JWT Authentication Issues on Jobs Endpoint  
**Date**: 2025-07-21  
**Status**: 🔄 IN PROGRESS  
**Severity**: Medium  
**Component**: Authentication/Jobs Router  

**Problem Description**:
`/api/v1/jobs/saved` returns 401 Unauthorized with "JWT decode error: Not enough segments"

**Error Manifestation**:
```
ERROR:app.routers.user:JWT decode error: Not enough segments
INFO:app.utils.database:HTTPException from endpoint: Could not validate credentials
```

**Investigation**: Different authentication pattern between direct endpoints vs aliases

### ERROR-004: SYSTEMIC Authentication Architecture Mismatch (CRITICAL)
**Date**: 2025-07-21  
**Status**: 🔴 CRITICAL SYSTEMIC ISSUE  
**Severity**: Critical  
**Component**: Entire Authentication System  

**Problem Description**:
The system has **two incompatible authentication patterns** throughout the codebase:
- `main_deploy.py`: Uses base64 tokens, returns dict objects  
- All `app/routers/*.py`: Use JWT tokens, expect User objects

**Error Manifestation**:
- 50+ router endpoints will fail with `AttributeError: 'dict' object has no attribute 'id'`
- Router dependency injection incompatible with main_deploy auth system

**Critical Impact**:
- **ALL included routers** (profiles, space, jobs) have this vulnerability
- Any future router integration will face same issue
- Production deployment risk: HIGH

**Missing Dependencies Found**:
- `torch` (PyTorch) - used in 15+ files
- `matplotlib`, `seaborn`, `scikit-learn` - missing from requirements.txt

**Required Systematic Fix**:
1. **Standardize authentication** - choose one pattern
2. **Add missing ML dependencies** to requirements.txt  
3. **Test all router endpoints** with current auth
4. **Create unified auth decorator** for consistency

**Files Affected**: 40+ router files, all main_deploy endpoints

---

## Prevention Checklist

Before implementing new authentication-dependent endpoints:

1. [ ] Verify what type the authentication function returns (dict vs User object)
2. [ ] If database relationships are needed, ensure User object is fetched from DB
3. [ ] Test authentication flow with actual user tokens
4. [ ] Check that all `.id`, `.email`, etc. attribute accesses work
5. [ ] Test both valid and invalid authentication scenarios
6. [ ] Verify CORS headers are properly configured for frontend domains

## Common Patterns

### ✅ Correct Authentication for Database Operations
```python
@app.get("/endpoint")
async def endpoint(authorization: Optional[str] = Header(None)):
    # Decode token
    token = authorization.split(" ")[1]
    decoded = base64.b64decode(token).decode()
    email, user_id, onboarding_completed, timestamp = decoded.split(":", 3)
    
    # Fetch actual User object
    db = next(get_db())
    current_user = db.query(User).filter(User.id == int(user_id)).first()
    if not current_user:
        raise HTTPException(status_code=401, detail="User not found")
    
    # Use with database operations
    return db.query(SomeModel).filter(SomeModel.user_id == current_user.id).all()
```

### ❌ Incorrect Pattern (Will Cause Errors)
```python
@app.get("/endpoint")
async def endpoint(current_user = Depends(get_current_user_with_onboarding)):
    # current_user is a dict, not a User object
    # This will fail: current_user.id
    return db.query(SomeModel).filter(SomeModel.user_id == current_user.id).all()
```