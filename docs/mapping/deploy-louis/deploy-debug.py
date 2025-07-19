#!/usr/bin/env python3
"""
Railway Deployment Debugging Tool
Systematic approach to identify and fix deployment issues
"""

import os
import sys
import json
import subprocess
import argparse
from pathlib import Path
from typing import Dict, List, Optional

class RailwayDeployDebugger:
    def __init__(self, phase: int = 1):
        self.phase = phase
        self.project_root = Path(__file__).parent
        self.backend_path = self.project_root / "backend"
        self.results = {}
        
    def log(self, message: str, level: str = "INFO"):
        """Enhanced logging with colors"""
        colors = {
            "INFO": "\033[94m",    # Blue
            "SUCCESS": "\033[92m", # Green
            "WARNING": "\033[93m", # Yellow
            "ERROR": "\033[91m",   # Red
            "RESET": "\033[0m"     # Reset
        }
        color = colors.get(level, colors["INFO"])
        print(f"{color}[{level}]{colors['RESET']} {message}")
    
    def check_files(self) -> Dict[str, bool]:
        """Check if required files exist"""
        self.log("🔍 Checking required files...")
        
        required_files = {
            f"requirements-phase{self.phase}.txt": self.project_root / f"requirements-phase{self.phase}.txt",
            "railway-new.toml": self.project_root / "railway-new.toml",
            "backend/main_deploy.py": self.backend_path / "main_deploy.py",
            "backend/app/main.py": self.backend_path / "app" / "main.py",
            ".env.supabase": self.project_root / ".env.supabase"
        }
        
        results = {}
        for name, path in required_files.items():
            exists = path.exists()
            results[name] = exists
            status = "✅" if exists else "❌"
            self.log(f"{status} {name}: {'Found' if exists else 'Missing'}")
        
        return results
    
    def test_imports(self) -> Dict[str, bool]:
        """Test Python imports for current phase"""
        self.log(f"🐍 Testing Python imports for Phase {self.phase}...")
        
        # Define imports by phase
        phase_imports = {
            1: ["fastapi", "uvicorn", "sqlalchemy", "psycopg2", "pydantic_settings"],
            2: ["openai", "numpy", "alembic"],
            3: ["torch", "torch_geometric", "sentence_transformers", "scipy", "sklearn", "transformers"]
        }
        
        results = {}
        for phase in range(1, self.phase + 1):
            for module in phase_imports.get(phase, []):
                try:
                    __import__(module)
                    results[module] = True
                    self.log(f"✅ {module}: Available")
                except ImportError:
                    results[module] = False
                    self.log(f"❌ {module}: Missing", "ERROR")
        
        return results
    
    def validate_config(self) -> Dict[str, bool]:
        """Validate configuration files"""
        self.log("⚙️ Validating configuration...")
        
        results = {}
        
        # Check railway-new.toml
        railway_config = self.project_root / "railway-new.toml"
        if railway_config.exists():
            content = railway_config.read_text()
            results["railway_toml_valid"] = f"requirements-phase{self.phase}.txt" in content or "requirements-simple.txt" in content
            results["railway_has_start_command"] = "startCommand" in content
        else:
            results["railway_toml_valid"] = False
            results["railway_has_start_command"] = False
        
        # Check environment variables
        env_file = self.project_root / ".env.supabase"
        if env_file.exists():
            env_content = env_file.read_text()
            results["has_database_url"] = "SUPABASE_DATABASE_URL" in env_content
            results["has_supabase_keys"] = "SUPABASE_ANON_KEY" in env_content
        else:
            results["has_database_url"] = False
            results["has_supabase_keys"] = False
        
        for key, value in results.items():
            status = "✅" if value else "❌"
            self.log(f"{status} {key.replace('_', ' ').title()}: {'Valid' if value else 'Invalid'}")
        
        return results
    
    def test_local_startup(self) -> bool:
        """Test if the app can start locally"""
        self.log("🚀 Testing local app startup...")
        
        try:
            # Change to backend directory
            os.chdir(self.backend_path)
            
            # Test import of main FastAPI app
            sys.path.insert(0, str(self.backend_path / "app"))
            from main import app
            
            self.log("✅ FastAPI app imported successfully", "SUCCESS")
            return True
            
        except ImportError as e:
            self.log(f"❌ FastAPI import failed: {e}", "ERROR")
            return False
        except Exception as e:
            self.log(f"❌ App startup failed: {e}", "ERROR")
            return False
    
    def generate_minimal_main(self) -> None:
        """Generate a minimal main.py for debugging"""
        self.log("🔧 Generating minimal main.py for debugging...")
        
        minimal_main = self.backend_path / "app" / "main_minimal.py"
        content = '''#!/usr/bin/env python3
"""
Minimal FastAPI app for Railway deployment debugging
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Orientor Platform - Minimal",
    description="Minimal deployment for debugging",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Orientor Platform - Minimal Deployment",
        "status": "healthy",
        "phase": "debug",
        "environment": os.getenv("RAILWAY_ENVIRONMENT", "local")
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "database": "not_configured_yet",
        "features": ["basic_api"]
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
'''
        minimal_main.write_text(content)
        self.log(f"✅ Created {minimal_main}")
    
    def run_diagnosis(self) -> Dict:
        """Run complete diagnosis"""
        self.log(f"🔬 Starting Railway Deployment Diagnosis - Phase {self.phase}")
        
        diagnosis = {
            "phase": self.phase,
            "files": self.check_files(),
            "imports": self.test_imports(),
            "config": self.validate_config(),
            "startup": self.test_local_startup()
        }
        
        # Calculate overall health
        all_checks = []
        all_checks.extend(diagnosis["files"].values())
        all_checks.extend(diagnosis["imports"].values())
        all_checks.extend(diagnosis["config"].values())
        all_checks.append(diagnosis["startup"])
        
        success_rate = sum(all_checks) / len(all_checks) * 100
        diagnosis["success_rate"] = success_rate
        
        self.log(f"📊 Overall Success Rate: {success_rate:.1f}%")
        
        if success_rate < 70:
            self.log("⚠️ Deployment likely to fail - needs fixes", "WARNING")
            self.generate_minimal_main()
        elif success_rate < 90:
            self.log("🔶 Deployment might have issues - review warnings", "WARNING")
        else:
            self.log("🎉 Deployment looks good!", "SUCCESS")
        
        return diagnosis
    
    def suggest_fixes(self, diagnosis: Dict) -> List[str]:
        """Suggest fixes based on diagnosis"""
        fixes = []
        
        # File fixes
        if not diagnosis["files"].get("backend/app/main.py"):
            fixes.append("Create backend/app/main.py or use main_minimal.py")
        
        # Import fixes
        missing_imports = [k for k, v in diagnosis["imports"].items() if not v]
        if missing_imports:
            fixes.append(f"Install missing packages: pip install {' '.join(missing_imports)}")
        
        # Config fixes
        if not diagnosis["config"].get("has_database_url"):
            fixes.append("Add SUPABASE_DATABASE_URL to .env.supabase")
        
        return fixes

def main():
    parser = argparse.ArgumentParser(description="Railway Deployment Debugger")
    parser.add_argument("--phase", type=int, default=1, choices=[1, 2, 3],
                       help="Deployment phase (1=minimal, 2=+AI, 3=+ML)")
    parser.add_argument("--output", type=str, help="Save diagnosis to JSON file")
    
    args = parser.parse_args()
    
    debugger = RailwayDeployDebugger(phase=args.phase)
    diagnosis = debugger.run_diagnosis()
    
    # Suggest fixes
    fixes = debugger.suggest_fixes(diagnosis)
    if fixes:
        debugger.log("🔧 Suggested fixes:")
        for i, fix in enumerate(fixes, 1):
            debugger.log(f"  {i}. {fix}")
    
    # Save results
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(diagnosis, f, indent=2)
        debugger.log(f"💾 Diagnosis saved to {args.output}")

if __name__ == "__main__":
    main()