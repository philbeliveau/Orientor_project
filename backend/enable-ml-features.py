#!/usr/bin/env python3
"""
Smart ML feature enablement script
Merges ML dependencies efficiently to minimize Railway build time
"""

import shutil
import os
from pathlib import Path

def enable_ml_features():
    """Enable ML features by merging requirements files efficiently"""
    
    print("🔄 Enabling ML features for profiles router...")
    
    # Check if ML requirements exist
    if not os.path.exists("requirements-ml-active.txt"):
        print("❌ requirements-ml-active.txt not found")
        return False
    
    # Read current requirements
    with open("requirements.txt", "r") as f:
        core_reqs = f.read()
    
    # Read ML requirements
    with open("requirements-ml-active.txt", "r") as f:
        ml_reqs = f.read()
    
    # Create backup
    shutil.copy("requirements.txt", "requirements.txt.backup")
    print("📋 Backed up requirements.txt")
    
    # Merge requirements intelligently
    merged_content = core_reqs.rstrip() + "\n\n# === ML FEATURES ENABLED ===\n" + ml_reqs
    
    # Write merged requirements
    with open("requirements.txt", "w") as f:
        f.write(merged_content)
    
    print("✅ ML features enabled in requirements.txt")
    print("⚡ Next deployment will include:")
    print("   - UserProfile embedding generation")
    print("   - Peer matching capabilities") 
    print("   - SavedRecommendation ML features")
    print("   - CPU-optimized torch (~500MB vs 2GB)")
    print()
    print("🚀 Expected Railway build time: 3-5 minutes (vs 10+ with GPU torch)")
    
    return True

def disable_ml_features():
    """Restore core requirements without ML"""
    if os.path.exists("requirements.txt.backup"):
        shutil.copy("requirements.txt.backup", "requirements.txt")
        print("✅ ML features disabled, core requirements restored")
    else:
        print("❌ No backup found")

def main():
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "disable":
        disable_ml_features()
    else:
        enable_ml_features()

if __name__ == "__main__":
    main()