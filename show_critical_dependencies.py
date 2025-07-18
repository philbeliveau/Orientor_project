#!/usr/bin/env python3
"""
Show critical dependencies and files that are actually used
"""

import json
from pathlib import Path

def load_reports():
    """Load all analysis reports"""
    reports = {}
    
    try:
        with open('dependency_analysis_report.json', 'r') as f:
            reports['dependencies'] = json.load(f)
    except FileNotFoundError:
        print("❌ dependency_analysis_report.json not found")
        return None
    
    try:
        with open('unused_files_report.json', 'r') as f:
            reports['unused'] = json.load(f)
    except FileNotFoundError:
        print("❌ unused_files_report.json not found")
        return None
    
    return reports

def show_used_files_by_category(reports):
    """Show which files are actually used, categorized"""
    used_files = set(reports['dependencies']['used_files'])
    
    categories = {
        'Frontend Entry & Components': [],
        'Backend Main & Routers': [],
        'Backend Services': [],
        'Backend Models': [],
        'Backend Utils': [],
        'Configuration': [],
        'Other': []
    }
    
    for file in used_files:
        if file.startswith('frontend/src/app/'):
            categories['Frontend Entry & Components'].append(file)
        elif file.startswith('backend/app/routers/'):
            categories['Backend Main & Routers'].append(file)
        elif file.startswith('backend/app/services/'):
            categories['Backend Services'].append(file)
        elif file.startswith('backend/app/models/'):
            categories['Backend Models'].append(file)
        elif file.startswith('backend/app/utils/'):
            categories['Backend Utils'].append(file)
        elif file.startswith('backend/app/main.py') or file.startswith('backend/app/core/'):
            categories['Backend Main & Routers'].append(file)
        elif any(config in file for config in ['config', 'json', 'js', 'toml']):
            categories['Configuration'].append(file)
        else:
            categories['Other'].append(file)
    
    print("🔍 FILES ACTUALLY USED IN THE APPLICATION")
    print("=" * 60)
    
    for category, files in categories.items():
        if files:
            print(f"\n📂 {category} ({len(files)} files):")
            for file in sorted(files):
                print(f"  ✅ {file}")

def show_safe_to_remove(reports):
    """Show files that are safe to remove"""
    safe_files = reports['unused']['safe_removal_candidates']
    
    print("\n\n🗑️ SAFE TO REMOVE FILES")
    print("=" * 60)
    
    total_safe = sum(len(files) for files in safe_files.values())
    print(f"Total files safe to remove: {total_safe}")
    
    for category, files in safe_files.items():
        if files:
            print(f"\n📁 {category.replace('_', ' ').title()} ({len(files)} files):")
            for file in files[:5]:  # Show first 5
                print(f"  🗑️  {file}")
            if len(files) > 5:
                print(f"     ... and {len(files) - 5} more")

def show_dependency_statistics(reports):
    """Show key statistics"""
    stats = reports['unused']['statistics']
    
    print("\n\n📊 KEY STATISTICS")
    print("=" * 60)
    print(f"Total files in project: {stats['total_files']}")
    print(f"Actually used files: {stats['used_files']} ({stats['usage_percentage']:.1f}%)")
    print(f"Orphaned files: {stats['orphaned_files']}")
    print(f"Git tracked files: {stats['git_tracked_files']}")
    
    # Calculate potential cleanup impact
    safe_count = sum(len(files) for files in reports['unused']['safe_removal_candidates'].values())
    total_orphaned = stats['orphaned_files']
    
    print(f"\n💾 CLEANUP POTENTIAL:")
    print(f"Files safe to remove immediately: {safe_count}")
    print(f"Files requiring review: {total_orphaned - safe_count}")
    print(f"Potential reduction: {(safe_count / stats['total_files']) * 100:.1f}% (immediate)")
    print(f"Maximum reduction: {(total_orphaned / stats['total_files']) * 100:.1f}% (after review)")

def show_critical_paths(reports):
    """Show most critical dependency paths"""
    deps = reports['dependencies']
    
    print("\n\n🔗 CRITICAL DEPENDENCY PATHS")
    print("=" * 60)
    
    # Find files with most dependencies
    dependency_counts = {}
    for file, file_deps in deps['dependency_graph'].items():
        if file_deps:
            dependency_counts[file] = len(file_deps)
    
    if dependency_counts:
        print("\n📈 Files with most dependencies:")
        top_deps = sorted(dependency_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        for file, count in top_deps:
            print(f"  📄 {file}: {count} dependencies")
    
    # Find files most depended upon
    reverse_deps = deps['reverse_dependencies']
    if reverse_deps:
        print("\n📈 Most depended-upon files:")
        top_reverse = sorted(reverse_deps.items(), key=lambda x: len(x[1]), reverse=True)[:5]
        for file, dependents in top_reverse:
            print(f"  📄 {file}: used by {len(dependents)} files")

def main():
    """Main function"""
    reports = load_reports()
    if not reports:
        print("❌ Could not load analysis reports. Please run dependency_analyzer.py first.")
        return
    
    show_dependency_statistics(reports)
    show_used_files_by_category(reports)
    show_safe_to_remove(reports)
    show_critical_paths(reports)
    
    print("\n\n🎯 NEXT STEPS:")
    print("1. Review the files listed above")
    print("2. Run cleanup_unused_files.sh to remove safe files")
    print("3. Manually review files requiring attention")
    print("4. Test the application after cleanup")
    print("5. Consider the cleanup recommendations in DEPENDENCY_ANALYSIS_SUMMARY.md")

if __name__ == "__main__":
    main()