#!/usr/bin/env python3
"""
Railway-compatible sequence fix runner
"""
import subprocess
import sys
import os

def main():
    print("🚀 Starting database sequence fix on Railway...")
    
    # Make sure we're in the right directory
    if os.path.exists('fix_sequences.py'):
        print("✅ Found fix_sequences.py")
        
        # Run the fix script
        try:
            result = subprocess.run([sys.executable, 'fix_sequences.py'], 
                                  capture_output=True, text=True)
            
            print("STDOUT:", result.stdout)
            if result.stderr:
                print("STDERR:", result.stderr)
                
            if result.returncode == 0:
                print("✅ Database sequence fix completed successfully")
            else:
                print(f"❌ Sequence fix failed with code {result.returncode}")
                
        except Exception as e:
            print(f"❌ Error running sequence fix: {e}")
    else:
        print("❌ fix_sequences.py not found")

if __name__ == '__main__':
    main()