# Standardized Deployment Guide: Critical Design Principles

This guide ensures all features are deployed following standardized patterns that prevent critical errors and maintain system stability.

## 🎯 Core Principle: "Design Once, Deploy Safely"

Every feature implementation must follow these critical design patterns to prevent systemic failures and ensure smooth deployment.

---

## 🔐 Authentication Standard (CRITICAL)

### **UNIFIED AUTHENTICATION PATTERN**
All endpoints MUST use the unified authentication system that:
- Accepts base64 tokens (frontend compatibility)
- Returns proper SQLAlchemy User objects (database compatibility)
- Provides consistent dependency injection across all routers

### **✅ CORRECT Implementation Pattern**
```python
from app.utils.auth import get_current_user_unified

@router.get("/endpoint")
async def endpoint_function(
    current_user: User = Depends(get_current_user_unified),
    db: Session = Depends(get_db)
):
    # current_user is guaranteed to be a User object with .id, .email attributes
    return db.query(SomeModel).filter(SomeModel.user_id == current_user.id).all()
```

### **❌ FORBIDDEN Patterns**
```python
# DON'T USE - Returns dict, causes AttributeError
current_user = Depends(get_current_user_with_onboarding)

# DON'T USE - JWT-only, incompatible with frontend
current_user = Depends(get_current_user)

# DON'T USE - Manual token parsing, error-prone
authorization: Optional[str] = Header(None)
```

---

## 📦 Dependency Management Standards

### **Gradual Dependency Management Strategy**

#### **Three-Tier Requirements System**
1. **`requirements.txt`** - Core packages (always installed, fast builds)
2. **`requirements-core.txt`** - Backup/reference of essential packages  
3. **`requirements-ml.txt`** - Heavy ML packages (added gradually per feature)

#### **Before Adding New Dependencies**

1. **Classify the Dependency**
   ```bash
   # Check package size and necessity
   pip show package_name
   # Small essential packages (<50MB) → requirements.txt
   # Heavy ML packages (>50MB) → requirements-ml.txt initially
   ```

2. **Test Locally First**
   ```bash
   # Test with new dependency
   pip install package_name
   python -c "from your.new.module import your_function"
   ```

3. **Gradual Deployment Process**
   ```bash
   # Phase 1: Test locally with heavy packages
   pip install -r requirements-ml.txt
   
   # Phase 2: Move only needed packages to requirements.txt
   # Copy specific lines from requirements-ml.txt to requirements.txt
   
   # Phase 3: Deploy and monitor build time
   git commit -m "Add package_name for feature_x"
   # Monitor Railway build time and memory usage
   ```

#### **Railway Build Time Management**
- **Target**: Keep builds under 3 minutes
- **Memory Limit**: Stay under 6GB during build (8GB max)
- **Strategy**: Add 1-2 heavy packages per deployment cycle

### **✅ APPROVED Dependencies**
Always use these established libraries:
```txt
# Database & ORM
sqlalchemy>=2.0.23
psycopg2-binary>=2.9.10

# ML & Data Processing  
torch>=2.0.0
pandas>=2.0.0
numpy>=1.26.2
scikit-learn>=1.3.0

# Web Framework
fastapi>=0.104.1
uvicorn>=0.24.0

# Authentication
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4
```

### **⚠️ WARNING: Heavy Dependencies**
If your feature needs libraries not in requirements.txt:
1. **Document the necessity** in your PR
2. **Add to requirements.txt** before implementation
3. **Test Railway memory impact** (8GB limit)

---

## 🏗️ Router Implementation Standards

### **Standard Router Template**
```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

# Use unified imports
from app.utils.database import get_db
from app.utils.auth import get_current_user_unified
from app.models import User, YourModel
from app.schemas.your_schema import YourSchema

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/your-feature",
    tags=["your-feature"],
    dependencies=[Depends(get_current_user_unified)]
)

@router.get("/endpoint", response_model=List[YourSchema])
async def get_your_data(
    current_user: User = Depends(get_current_user_unified),
    db: Session = Depends(get_db)
):
    """Clear docstring describing functionality"""
    try:
        # Implementation
        return db.query(YourModel).filter(YourModel.user_id == current_user.id).all()
    except Exception as e:
        logger.error(f"Error in get_your_data: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
```

### **Router Integration Checklist**
- [ ] Uses `get_current_user_unified` for authentication
- [ ] Includes proper error handling and logging
- [ ] Has clear docstrings and type hints
- [ ] Follows consistent naming conventions
- [ ] Tests both authenticated and unauthenticated access

---

## 🚀 Deployment Process Standards

### **Phase 1: Pre-Deployment Validation**

1. **Local Testing Protocol**
   ```bash
   # 1. Clean install dependencies
   pip install -r requirements.txt
   
   # 2. Test authentication endpoints
   curl -H "Authorization: Bearer <base64_token>" http://localhost:8000/your-endpoint
   
   # 3. Verify database connections
   python -c "from app.utils.database import get_db; next(get_db())"
   
   # 4. Check all imports
   python -c "from app.routers.your_router import router"
   ```

2. **Integration Testing**
   ```bash
   # Test with main_deploy.py inclusion
   # Verify router appears in health check
   curl http://localhost:8000/health
   ```

### **Phase 2: Railway Deployment**

1. **Dependency Verification**
   - Monitor Railway build logs for dependency installation
   - Check for memory usage during pip install (8GB limit)
   - Verify no missing dependency errors

2. **Health Check Validation**
   ```bash
   # Verify router is included and working
   curl https://orientor-backend-production-7c13.up.railway.app/health
   
   # Should show your router: "your_feature": true
   ```

3. **Frontend Integration Test**
   ```bash
   # Test from Vercel frontend domain
   curl -H "Authorization: Bearer <base64_token>" \
        https://orientor-backend-production-7c13.up.railway.app/api/v1/your-endpoint
   ```

### **Phase 3: Production Validation**

1. **CORS Verification**
   - Test from https://navigoproject.vercel.app
   - Verify no CORS blocking errors
   - Check browser network tab for proper responses

2. **Error Monitoring**
   - Watch Railway logs for authentication errors
   - Monitor for 500 errors vs proper 401/404
   - Check database connection stability

---

## 🛡️ Security Standards

### **Authentication Security**
- ✅ Always validate tokens before database queries
- ✅ Return proper HTTP status codes (401, 403, 404)
- ✅ Never expose user data in error messages
- ✅ Log security events without exposing sensitive data

### **Database Security**
- ✅ Use parameterized queries (SQLAlchemy ORM)
- ✅ Filter data by authenticated user ID
- ✅ Validate all input data with Pydantic schemas
- ✅ Handle database connection failures gracefully

### **CORS Security**
```python
# Standard CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://navigoproject.vercel.app",
        "https://*.vercel.app",
        "http://localhost:3000"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"]
)
```

---

## 📊 Monitoring and Debugging Standards

### **Standard Logging Pattern**
```python
import logging
logger = logging.getLogger(__name__)

# Log levels usage:
logger.info("✅ Successful operation")      # Success operations
logger.warning("⚠️ Recoverable issue")     # Warnings
logger.error("❌ Operation failed")        # Errors  
logger.debug("🔍 Debug information")       # Debug only
```

### **Error Handling Pattern**
```python
try:
    # Operation
    result = database_operation()
    logger.info(f"✅ Operation successful: {operation_type}")
    return result
except SpecificException as e:
    logger.error(f"❌ Specific error in {operation_type}: {e}")
    raise HTTPException(status_code=400, detail=f"Specific error: {str(e)}")
except Exception as e:
    logger.error(f"❌ Unexpected error in {operation_type}: {e}")
    raise HTTPException(status_code=500, detail="Internal server error")
```

---

## 🔄 Rollback Procedures

### **Immediate Rollback Triggers**
- Import errors preventing startup
- Authentication failures blocking all users
- Database connection failures
- Memory exhaustion on Railway

### **Rollback Commands**
```bash
# Revert to previous working commit
git revert <commit_hash>
git push origin stability

# Monitor Railway deployment
# Check health endpoint returns to normal
curl https://orientor-backend-production-7c13.up.railway.app/health
```

---

## 📋 Pre-Deployment Checklist

### **Code Quality Checklist**
- [ ] Follows unified authentication pattern
- [ ] All dependencies in requirements.txt
- [ ] Proper error handling and logging
- [ ] Type hints and docstrings complete
- [ ] No hardcoded secrets or credentials

### **Testing Checklist**
- [ ] Local testing with base64 authentication
- [ ] Database operations work correctly
- [ ] Error scenarios handled gracefully
- [ ] CORS compatibility verified
- [ ] Memory usage acceptable

### **Deployment Checklist**
- [ ] Health check includes new router
- [ ] No import errors in Railway logs
- [ ] Frontend can access endpoints
- [ ] Error registry updated with new patterns
- [ ] Documentation updated

---

## 🎯 Success Metrics

### **Deployment Success Indicators**
- ✅ Health check shows all routers: `true`
- ✅ No 500 errors in Railway logs
- ✅ Frontend integration works without CORS errors
- ✅ Authentication returns proper 401 errors (not 500)
- ✅ Database queries execute successfully

### **Performance Metrics**
- ✅ Railway memory usage < 6GB (safe margin)
- ✅ Response times < 2 seconds for typical queries
- ✅ No dependency installation timeouts
- ✅ Build time < 5 minutes

---

## 📚 Reference Implementation

See `ERROR_REGISTRY.md` for examples of:
- ✅ Resolved authentication patterns
- ❌ Common pitfalls to avoid
- 🔧 Debugging approaches that work

**Key Principle**: When in doubt, follow the patterns that work. Don't reinvent authentication, database connections, or error handling. Use the established, tested patterns documented in this guide.

---

## 🚨 Emergency Contacts

**If deployment fails:**
1. Check `ERROR_REGISTRY.md` for similar issues
2. Revert to last working commit immediately
3. Document new error patterns for future prevention
4. Fix systematically, not with quick hacks

**Remember**: A failed deployment caught early is better than a working deployment that breaks later. Follow the checklist religiously.