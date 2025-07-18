#!/usr/bin/env python3
"""
Focused analysis of unused files in the Orientor project
"""

import json
import os
from pathlib import Path
from typing import Set, List, Dict
import subprocess

class UnusedFilesAnalyzer:
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.dependency_report = None
        self.load_dependency_report()
        
    def load_dependency_report(self):
        """Load the dependency analysis report"""
        try:
            with open(self.project_root / 'dependency_analysis_report.json', 'r') as f:
                self.dependency_report = json.load(f)
        except FileNotFoundError:
            print("❌ Please run dependency_analyzer.py first")
            exit(1)
    
    def analyze_git_tracked_files(self) -> Set[str]:
        """Get list of files tracked by git"""
        try:
            result = subprocess.run(
                ['git', 'ls-files'],
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            return set(result.stdout.strip().split('\n'))
        except subprocess.SubprocessError:
            return set()
    
    def categorize_orphaned_files(self) -> Dict[str, List[str]]:
        """Categorize orphaned files by type and safety to remove"""
        orphaned_files = set(self.dependency_report['orphaned_files'])
        
        categories = {
            'safe_to_remove': [],
            'documentation': [],
            'configuration': [],
            'test_files': [],
            'data_files': [],
            'migration_files': [],
            'backup_files': [],
            'static_assets': [],
            'notebooks': [],
            'requires_review': []
        }
        
        for file_path in orphaned_files:
            file_lower = file_path.lower()
            
            # Safe to remove - clearly unused
            if any(pattern in file_lower for pattern in [
                'backup', 'old', 'copy', 'tmp', 'temp', 'cache',
                '.bak', '.orig', '.swp', '.tmp', 'unused'
            ]):
                categories['safe_to_remove'].append(file_path)
            
            # Documentation files
            elif any(pattern in file_lower for pattern in [
                'readme', 'todo', 'note', 'doc', 'guide', 'plan',
                'spec', 'analysis', 'report', 'summary', 'log'
            ]) or file_path.endswith('.md'):
                categories['documentation'].append(file_path)
            
            # Configuration files
            elif any(pattern in file_lower for pattern in [
                'config', 'settings', 'env', 'ini', 'toml',
                'yaml', 'yml', 'json'
            ]) and not file_path.endswith(('.py', '.ts', '.tsx', '.js', '.jsx')):
                categories['configuration'].append(file_path)
            
            # Test files
            elif any(pattern in file_lower for pattern in [
                'test', 'spec', '__tests__', 'tests'
            ]):
                categories['test_files'].append(file_path)
            
            # Data files
            elif any(pattern in file_lower for pattern in [
                'data', 'dataset', 'csv', 'json', 'sql', 'db',
                'sqlite', 'sample', 'seed', 'fixture'
            ]):
                categories['data_files'].append(file_path)
            
            # Migration files
            elif any(pattern in file_lower for pattern in [
                'migration', 'alembic', 'version'
            ]):
                categories['migration_files'].append(file_path)
            
            # Static assets
            elif any(file_path.endswith(ext) for ext in [
                '.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico',
                '.woff', '.woff2', '.ttf', '.otf', '.pdf'
            ]):
                categories['static_assets'].append(file_path)
            
            # Notebooks
            elif file_path.endswith('.ipynb'):
                categories['notebooks'].append(file_path)
            
            # Requires review
            else:
                categories['requires_review'].append(file_path)
        
        return categories
    
    def find_potentially_used_files(self) -> Dict[str, List[str]]:
        """Find files that might be used but not detected by static analysis"""
        orphaned_files = set(self.dependency_report['orphaned_files'])
        potentially_used = {
            'dynamic_imports': [],
            'string_references': [],
            'template_files': [],
            'runtime_loaded': []
        }
        
        # Check for dynamic imports in used files
        used_files = self.dependency_report['used_files']
        
        for used_file in used_files:
            try:
                file_path = self.project_root / used_file
                if file_path.exists():
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                    # Look for string references to orphaned files
                    for orphaned_file in orphaned_files:
                        file_name = Path(orphaned_file).name
                        if file_name in content:
                            potentially_used['string_references'].append(orphaned_file)
                            
            except Exception as e:
                continue
        
        return potentially_used
    
    def generate_detailed_report(self) -> Dict:
        """Generate a detailed report of unused files"""
        git_tracked = self.analyze_git_tracked_files()
        categorized = self.categorize_orphaned_files()
        potentially_used = self.find_potentially_used_files()
        
        # Statistics
        total_files = self.dependency_report['summary']['total_files']
        used_files = self.dependency_report['summary']['used_files']
        orphaned_files = self.dependency_report['summary']['orphaned_files']
        
        return {
            'statistics': {
                'total_files': total_files,
                'used_files': used_files,
                'orphaned_files': orphaned_files,
                'usage_percentage': round((used_files / total_files) * 100, 2),
                'git_tracked_files': len(git_tracked),
                'git_tracked_orphaned': len([f for f in self.dependency_report['orphaned_files'] if f in git_tracked])
            },
            'categorized_orphaned_files': categorized,
            'potentially_used_files': potentially_used,
            'safe_removal_candidates': {
                'definitely_safe': categorized['safe_to_remove'],
                'probably_safe': categorized['backup_files'],
                'documentation_files': categorized['documentation'],
                'old_migrations': [f for f in categorized['migration_files'] if 'old' in f.lower() or 'backup' in f.lower()],
                'test_files': categorized['test_files']
            }
        }
    
    def create_cleanup_script(self, report: Dict):
        """Create a bash script to safely remove unused files"""
        script_content = """#!/bin/bash
# Generated cleanup script for Orientor project
# Review each section before running

echo "🧹 Orientor Project Cleanup Script"
echo "=================================="
echo ""

# Create backup before cleanup
echo "📦 Creating backup..."
mkdir -p cleanup_backup
cp -r . cleanup_backup/ 2>/dev/null || echo "Backup creation failed"

echo ""
echo "🔍 Files to be removed:"
echo ""

# Function to safely remove file
safe_remove() {
    local file="$1"
    if [ -f "$file" ]; then
        echo "Removing: $file"
        rm "$file"
    elif [ -d "$file" ]; then
        echo "Removing directory: $file"
        rm -rf "$file"
    else
        echo "File not found: $file"
    fi
}

# Definitely safe to remove
echo "📁 Definitely safe to remove:"
"""
        
        for file_path in report['safe_removal_candidates']['definitely_safe']:
            script_content += f'safe_remove "{file_path}"\n'
        
        script_content += """
echo ""
echo "📄 Documentation files (review before removing):"
"""
        
        for file_path in report['safe_removal_candidates']['documentation_files'][:10]:  # Limit to first 10
            script_content += f'# safe_remove "{file_path}"\n'
        
        script_content += """
echo ""
echo "🧪 Test files (review before removing):"
"""
        
        for file_path in report['safe_removal_candidates']['test_files'][:10]:  # Limit to first 10
            script_content += f'# safe_remove "{file_path}"\n'
        
        script_content += """
echo ""
echo "✅ Cleanup completed!"
echo "📊 Summary:"
echo "- Created backup in cleanup_backup/"
echo "- Removed definitely safe files"
echo "- Review commented sections before uncommenting"
echo ""
echo "🔧 Next steps:"
echo "1. Test the application to ensure nothing is broken"
echo "2. Run git status to see changes"
echo "3. Commit changes if everything works"
echo "4. Remove backup directory if satisfied"
"""
        
        # Write cleanup script
        with open(self.project_root / 'cleanup_unused_files.sh', 'w') as f:
            f.write(script_content)
        
        os.chmod(self.project_root / 'cleanup_unused_files.sh', 0o755)
    
    def analyze(self):
        """Run complete unused files analysis"""
        print("🔍 Analyzing unused files...")
        
        report = self.generate_detailed_report()
        
        # Save detailed report
        with open(self.project_root / 'unused_files_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        # Create cleanup script
        self.create_cleanup_script(report)
        
        # Print summary
        print("\n" + "="*60)
        print("📊 UNUSED FILES ANALYSIS SUMMARY")
        print("="*60)
        
        stats = report['statistics']
        print(f"Total files in project: {stats['total_files']}")
        print(f"Files actually used: {stats['used_files']} ({stats['usage_percentage']}%)")
        print(f"Orphaned files: {stats['orphaned_files']}")
        print(f"Git tracked files: {stats['git_tracked_files']}")
        print(f"Git tracked orphaned: {stats['git_tracked_orphaned']}")
        
        print("\n📂 Categorized Orphaned Files:")
        for category, files in report['categorized_orphaned_files'].items():
            if files:
                print(f"  {category}: {len(files)} files")
        
        print("\n✅ Safe Removal Candidates:")
        safe_candidates = report['safe_removal_candidates']
        total_safe = sum(len(files) for files in safe_candidates.values())
        print(f"  Total safe to remove: {total_safe} files")
        
        for category, files in safe_candidates.items():
            if files:
                print(f"  {category}: {len(files)} files")
        
        print("\n📋 Files Generated:")
        print("  - unused_files_report.json: Detailed analysis report")
        print("  - cleanup_unused_files.sh: Automated cleanup script")
        
        print("\n⚠️  IMPORTANT:")
        print("  1. Review the unused_files_report.json before cleanup")
        print("  2. Test the cleanup script in a safe environment first")
        print("  3. Make sure to backup before running cleanup")
        
        return report

def main():
    """Main function"""
    analyzer = UnusedFilesAnalyzer(".")
    analyzer.analyze()

if __name__ == "__main__":
    main()