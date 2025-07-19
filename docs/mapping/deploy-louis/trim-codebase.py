#!/usr/bin/env python3
"""
Systematic Codebase Trimming Tool
Iteratively reduce complexity for successful Railway deployment
"""

import os
import shutil
import json
from pathlib import Path
from typing import Dict, List, Set

class CodebaseTrimmer:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.backend_path = self.project_root / "backend"
        self.trimmed_dirs = []
        
    def log(self, message: str, level: str = "INFO"):
        """Enhanced logging"""
        colors = {
            "INFO": "\033[94m",
            "SUCCESS": "\033[92m",
            "WARNING": "\033[93m",
            "ERROR": "\033[91m",
            "RESET": "\033[0m"
        }
        color = colors.get(level, colors["INFO"])
        print(f"{color}[{level}]{colors['RESET']} {message}")
    
    def analyze_dependencies(self) -> Dict[str, Set[str]]:
        """Analyze which files depend on what"""
        self.log("🔍 Analyzing codebase dependencies...")
        
        dependencies = {
            "ml_heavy": {
                "backend/app/services/GNN/",
                "backend/app/services/esco_embedding_service384.py",
                "backend/app/services/Oasisembedding_service.py",
                "backend/dev/"
            },
            "ai_services": {
                "backend/app/services/ai_chat_service.py",
                "backend/app/services/openai_service.py",
                "backend/app/routers/ai_chat.py"
            },
            "advanced_features": {
                "backend/app/routers/competence_tree.py",
                "backend/app/routers/vectors.py",
                "backend/app/routers/school_programs.py",
                "backend/app/services/competence_tree_service.py"
            },
            "assessment_features": {
                "backend/app/routers/hexaco.py",
                "backend/app/routers/holland.py",
                "backend/app/services/hexaco_service.py",
                "backend/app/services/holland_service.py"
            },
            "core_essential": {
                "backend/app/main.py",
                "backend/app/core/",
                "backend/app/models/user.py",
                "backend/app/routers/auth.py",
                "backend/app/routers/profiles.py"
            }
        }
        
        return dependencies
    
    def create_phase_configs(self) -> None:
        """Create phase-specific configuration files"""
        self.log("📋 Creating phase configuration files...")
        
        phases = {
            "phase1": {
                "name": "Minimal Viable Deployment",
                "description": "Core API + Database only",
                "include": ["core_essential"],
                "exclude": ["ml_heavy", "ai_services", "advanced_features", "assessment_features"],
                "requirements": "requirements-phase1.txt"
            },
            "phase2": {
                "name": "Basic AI Features",
                "description": "Core + AI Chat",
                "include": ["core_essential", "ai_services"],
                "exclude": ["ml_heavy", "advanced_features", "assessment_features"],
                "requirements": "requirements-phase2.txt"
            },
            "phase3": {
                "name": "Full Platform",
                "description": "All features enabled",
                "include": ["core_essential", "ai_services", "advanced_features", "assessment_features", "ml_heavy"],
                "exclude": [],
                "requirements": "requirements-phase3.txt"
            }
        }
        
        for phase_name, config in phases.items():
            config_file = self.project_root / f"{phase_name}-config.json"
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
            self.log(f"✅ Created {config_file}")
    
    def backup_original(self) -> Path:
        """Create backup of original codebase"""
        backup_dir = self.project_root / "backup-original"
        if not backup_dir.exists():
            self.log("💾 Creating backup of original codebase...")
            shutil.copytree(self.backend_path, backup_dir / "backend", ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
            self.log(f"✅ Backup created at {backup_dir}")
        return backup_dir
    
    def trim_for_phase(self, phase: int) -> None:
        """Trim codebase for specific phase"""
        self.log(f"✂️ Trimming codebase for Phase {phase}...")
        
        # Load phase config
        config_file = self.project_root / f"phase{phase}-config.json"
        if not config_file.exists():
            self.log("❌ Phase config not found. Run create_phase_configs() first.", "ERROR")
            return
        
        with open(config_file) as f:
            config = json.load(f)
        
        dependencies = self.analyze_dependencies()
        
        # Create trimmed directory
        trimmed_dir = self.project_root / f"backend-phase{phase}"
        if trimmed_dir.exists():
            shutil.rmtree(trimmed_dir)
        
        # Copy core structure
        shutil.copytree(self.backend_path, trimmed_dir, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
        
        # Remove excluded components
        for exclude_category in config["exclude"]:
            if exclude_category in dependencies:
                for path_pattern in dependencies[exclude_category]:
                    full_path = trimmed_dir / Path(path_pattern).relative_to(Path("backend"))
                    if full_path.exists():
                        if full_path.is_dir():
                            shutil.rmtree(full_path)
                            self.log(f"🗑️ Removed directory: {path_pattern}")
                        else:
                            full_path.unlink()
                            self.log(f"🗑️ Removed file: {path_pattern}")
        
        # Create simplified main.py for this phase
        self.create_phase_main(trimmed_dir, phase)
        
        self.log(f"✅ Phase {phase} codebase created at {trimmed_dir}")
    
    def create_phase_main(self, trimmed_dir: Path, phase: int) -> None:
        """Create phase-specific main.py"""
        main_file = trimmed_dir / "app" / "main.py"
        
        if phase == 1:
            # Minimal main.py
            content = '''#!/usr/bin/env python3
"""
Orientor Platform - Phase 1: Minimal Viable Deployment
Core API + Database connectivity only
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Orientor Platform",
    description="AI-Driven Career Guidance Platform - Phase 1",
    version="1.0.0-phase1"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import core routers only
try:
    from routers import auth, profiles
    app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
    app.include_router(profiles.router, prefix="/api/profiles", tags=["profiles"])
    logger.info("✅ Core routers loaded successfully")
except ImportError as e:
    logger.warning(f"⚠️ Some routers not available: {e}")

@app.get("/")
async def root():
    return {
        "message": "Orientor Platform - Phase 1",
        "status": "healthy",
        "phase": "minimal_viable_deployment",
        "features": ["auth", "profiles", "database"]
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "phase": 1}
'''
        
        elif phase == 2:
            # Phase 2 with AI
            content = '''#!/usr/bin/env python3
"""
Orientor Platform - Phase 2: Basic AI Features
Core API + Database + AI Chat
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Orientor Platform",
    description="AI-Driven Career Guidance Platform - Phase 2",
    version="1.0.0-phase2"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import available routers
try:
    from routers import auth, profiles
    app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
    app.include_router(profiles.router, prefix="/api/profiles", tags=["profiles"])
    logger.info("✅ Core routers loaded")
except ImportError as e:
    logger.warning(f"⚠️ Core routers issue: {e}")

try:
    from routers import ai_chat
    app.include_router(ai_chat.router, prefix="/api/ai", tags=["ai_chat"])
    logger.info("✅ AI chat router loaded")
except ImportError as e:
    logger.warning(f"⚠️ AI chat not available: {e}")

@app.get("/")
async def root():
    return {
        "message": "Orientor Platform - Phase 2",
        "status": "healthy",
        "phase": "basic_ai_features",
        "features": ["auth", "profiles", "database", "ai_chat"]
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "phase": 2}
'''
        
        else:  # phase == 3
            # Keep original main.py for phase 3
            return
        
        main_file.write_text(content)
        self.log(f"✅ Created phase {phase} main.py")
    
    def test_phase(self, phase: int) -> bool:
        """Test if a trimmed phase works"""
        self.log(f"🧪 Testing Phase {phase} deployment...")
        
        trimmed_dir = self.project_root / f"backend-phase{phase}"
        if not trimmed_dir.exists():
            self.log("❌ Trimmed directory not found", "ERROR")
            return False
        
        # Test import
        try:
            import sys
            sys.path.insert(0, str(trimmed_dir / "app"))
            
            # Try to import the main app
            from main import app
            self.log(f"✅ Phase {phase} imports successfully", "SUCCESS")
            return True
            
        except ImportError as e:
            self.log(f"❌ Phase {phase} import failed: {e}", "ERROR")
            return False
    
    def run_progressive_trim(self) -> None:
        """Run complete progressive trimming process"""
        self.log("🚀 Starting Progressive Codebase Trimming")
        
        # Step 1: Backup
        self.backup_original()
        
        # Step 2: Create configs
        self.create_phase_configs()
        
        # Step 3: Trim each phase
        for phase in [1, 2, 3]:
            self.trim_for_phase(phase)
            
            # Test the phase
            success = self.test_phase(phase)
            status = "✅ READY" if success else "❌ NEEDS WORK"
            self.log(f"Phase {phase}: {status}")
        
        self.log("🎉 Progressive trimming complete!")
        self.log("📋 Next steps:")
        self.log("  1. Test Phase 1: python deploy-debug.py --phase 1")
        self.log("  2. Deploy Phase 1 to Railway")
        self.log("  3. If successful, move to Phase 2")

def main():
    trimmer = CodebaseTrimmer()
    trimmer.run_progressive_trim()

if __name__ == "__main__":
    main()