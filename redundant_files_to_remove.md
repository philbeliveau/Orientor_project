# Redundant Backend Files - Safe for Removal

## Legacy Main Files (No Production Impact)

### Phase 1 Legacy Files
- `backend/main_phase1_simple.py` - Superseded by Phase 2
- `backend/main_phase1.py` - Original Phase 1 implementation
- `backend/main_phase1_deploy.py` - Phase 1 deployment wrapper

### Phase 2 Development/Legacy Files  
- `backend/main_phase2_minimal.py` - Superseded by main_deploy.py
- `backend/main_phase2_minimal_fixed.py` - Previous production version
- `backend/main_phase2_chunk1.py` - Development iteration
- `backend/main_phase2_deploy.py` - Legacy deployment wrapper
- `backend/main_phase2_minimal_deploy.py` - Legacy deployment wrapper
- `backend/main_with_auth.py` - Development version with auth testing

### Other Development Files
- `backend/main_minimal.py` - Early minimal version
- `backend/run.py` - Development runner script
- `backend/run_local.py` - Local development script

## Production Files (DO NOT REMOVE)

### Active Production
- `backend/main_deploy.py` - **CURRENT PRODUCTION** (Railway nixpacks.toml)
- `backend/main_phase2_real.py` - **PHASE 3 READY** (Full platform)

### Supporting Production Files
- `backend/nixpacks.toml` - Railway deployment configuration
- `backend/requirements.txt` - Production dependencies
- `backend/requirements-phase2-real.txt` - Phase 3 dependencies

## Removal Impact Analysis

**Safe to Remove:** All legacy files listed above
- No production dependencies
- Not referenced in deployment configs  
- Superseded by current implementations

**Storage Savings:** ~500KB+ in backend code cleanup
**Maintenance Benefit:** Reduces confusion about which files are active

## Recommended Cleanup Command

```bash
# Remove Phase 1 legacy files
rm backend/main_phase1*.py

# Remove Phase 2 development files  
rm backend/main_phase2_minimal*.py
rm backend/main_phase2_chunk1.py
rm backend/main_phase2_deploy.py
rm backend/main_with_auth.py

# Remove other development files
rm backend/main_minimal.py
rm backend/run*.py
```

**Note:** Only remove after confirming production deployment works with current CORS fixes.