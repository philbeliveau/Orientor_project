        79    
        80 +  ## PENDING COMPLETION
        81 +  
        82 +  ### ERROR-005: Profiles Router - ML Dependencies Required for Full Functionality
        83 +  **Date**: 2025-07-21  
        84 +  **Status**: 🟡 PENDING COMPLETION - BASIC FUNCTIONALITY WORKING  
        85 +  **Severity**: Medium  
        86 +  **Component**: Profiles Router + ML Pipeline  
        87 +  
        88 +  **Problem Description**:
        89 +  Profiles router requires heavy ML dependencies (torch, transformers, sentence-transformers) for embedding generation and peer matching functionality. These 
           + dependencies cause slow Railway builds and deployment complexity.
        90 +  
        91 +  **Business Logic Context**:
        92 +  - User profile updates trigger embedding regeneration for similarity matching
        93 +  - Embeddings power peer recommendations and compatibility scores  
        94 +  - ML pipeline is core to user experience, not optional feature
        95 +  
        96 +  **Current Status**:
        97 +  - ✅ Basic profile CRUD (GET /profiles/me, PUT /profiles/update) works without ML
        98 +  - ✅ Graceful degradation when ML services unavailable
        99 +  - ❌ No peer matching or embedding-based recommendations
       100 +  - ❌ Heavy dependencies (torch ~2GB) cause slow builds
       101 +  
       102 +  **Implementation Strategy**:
       103 +  ```python
       104 +  # Current working fallbacks:
       105 +  if OASIS_EMBEDDING_AVAILABLE:
       106 +      # Full ML pipeline with embeddings
       107 +  else:
       108 +      # Basic profile updates only
       109 +  ```
       110 +  
       111 +  **Required for Full Implementation**:
       112 +  ```python
       113 +  # Add to requirements.txt when ready:
       114 +  torch>=2.0.0              # ~2GB - Core ML functionality
       115 +  transformers>=4.20.0      # ~500MB - BERT models
       116 +  sentence-transformers>=2.2.0  # ~300MB - Semantic embeddings  
       117 +  scikit-learn>=1.3.0       # ~200MB - Similarity calculations
       118 +  ```
       119 +  
       120 +  **Files Modified**:
       121 +  - `backend/app/routers/profiles.py` - Graceful ML fallbacks implemented
       122 +  - `backend/main_deploy.py` - Import error handling added
       123 +  
       124 +  **Next Steps When Ready**:
       125 +  1. Add ML dependencies to requirements.txt (expect 5-10 min builds)
       126 +  2. Monitor Railway memory usage during build
       127 +  3. Test full embedding pipeline end-to-end
       128 +  4. Verify peer matching and recommendations work