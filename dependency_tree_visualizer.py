#!/usr/bin/env python3
"""
Dependency Tree Visualizer - Creates a visual representation of the dependency tree
"""

import json
from pathlib import Path
from typing import Dict, Set, List
import subprocess

class DependencyTreeVisualizer:
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
    
    def create_dependency_tree(self, start_file: str, visited: Set[str] = None, level: int = 0) -> List[str]:
        """Create a visual dependency tree from a starting file"""
        if visited is None:
            visited = set()
        
        if start_file in visited or level > 10:  # Prevent infinite recursion
            return []
        
        visited.add(start_file)
        tree_lines = []
        
        # Add current file
        indent = "  " * level
        if level == 0:
            tree_lines.append(f"📁 {start_file}")
        else:
            tree_lines.append(f"{indent}├── {Path(start_file).name}")
        
        # Add dependencies
        dependencies = self.dependency_report['dependency_graph'].get(start_file, [])
        for i, dep in enumerate(dependencies):
            is_last = i == len(dependencies) - 1
            prefix = "└──" if is_last else "├──"
            tree_lines.append(f"{indent}  {prefix} {Path(dep).name}")
            
            # Recursively add subdependencies
            sub_tree = self.create_dependency_tree(dep, visited.copy(), level + 1)
            tree_lines.extend(sub_tree)
        
        return tree_lines
    
    def analyze_critical_paths(self) -> Dict[str, List[str]]:
        """Analyze critical dependency paths"""
        critical_paths = {}
        
        # Find most imported files
        reverse_deps = self.dependency_report['reverse_dependencies']
        
        # Sort by number of files that depend on them
        most_depended_on = sorted(
            reverse_deps.items(),
            key=lambda x: len(x[1]),
            reverse=True
        )[:10]
        
        critical_paths['most_depended_on'] = [
            {'file': file, 'dependent_count': len(dependents), 'dependents': dependents}
            for file, dependents in most_depended_on
        ]
        
        # Find deepest dependency chains
        deepest_chains = []
        for start_file in self.dependency_report['entry_points'].values():
            if start_file in self.dependency_report['dependency_graph']:
                chain = self._find_deepest_chain(start_file, set())
                if chain:
                    deepest_chains.append({
                        'entry_point': start_file,
                        'chain': chain,
                        'depth': len(chain)
                    })
        
        critical_paths['deepest_chains'] = sorted(deepest_chains, key=lambda x: x['depth'], reverse=True)[:5]
        
        return critical_paths
    
    def _find_deepest_chain(self, file: str, visited: Set[str]) -> List[str]:
        """Find the deepest dependency chain from a file"""
        if file in visited:
            return []
        
        visited.add(file)
        dependencies = self.dependency_report['dependency_graph'].get(file, [])
        
        if not dependencies:
            return [file]
        
        deepest = []
        for dep in dependencies:
            chain = self._find_deepest_chain(dep, visited.copy())
            if len(chain) > len(deepest):
                deepest = chain
        
        return [file] + deepest
    
    def generate_visual_report(self) -> str:
        """Generate a comprehensive visual report"""
        report_lines = []
        
        # Header
        report_lines.extend([
            "📊 ORIENTOR PROJECT DEPENDENCY ANALYSIS",
            "=" * 60,
            "",
            f"🔍 Analysis Summary:",
            f"  Total files: {self.dependency_report['summary']['total_files']}",
            f"  Used files: {self.dependency_report['summary']['used_files']} ({self.dependency_report['summary']['used_files'] / self.dependency_report['summary']['total_files'] * 100:.1f}%)",
            f"  Orphaned files: {self.dependency_report['summary']['orphaned_files']}",
            f"  Dependency relationships: {self.dependency_report['summary']['dependency_relationships']}",
            "",
        ])
        
        # File type breakdown
        report_lines.extend([
            "📁 File Types:",
            ""
        ])
        
        for file_type, count in self.dependency_report['summary']['file_types'].items():
            report_lines.append(f"  {file_type:12} : {count:4} files")
        
        report_lines.append("")
        
        # Entry points and their dependency trees
        report_lines.extend([
            "🌳 DEPENDENCY TREES FROM ENTRY POINTS",
            "=" * 60,
            ""
        ])
        
        for entry_name, entry_file in self.dependency_report['entry_points'].items():
            report_lines.append(f"🚀 {entry_name.upper()} Entry Point:")
            if entry_file in self.dependency_report['dependency_graph']:
                tree = self.create_dependency_tree(entry_file)
                report_lines.extend(tree[:20])  # Limit to first 20 lines
                if len(tree) > 20:
                    report_lines.append(f"  ... and {len(tree) - 20} more dependencies")
            else:
                report_lines.append(f"  No dependencies found for {entry_file}")
            report_lines.append("")
        
        # Critical paths analysis
        critical_paths = self.analyze_critical_paths()
        
        report_lines.extend([
            "🔗 CRITICAL DEPENDENCY ANALYSIS",
            "=" * 60,
            "",
            "📈 Most Depended-On Files:",
            ""
        ])
        
        for item in critical_paths['most_depended_on']:
            report_lines.append(f"  📄 {item['file']}")
            report_lines.append(f"     Used by {item['dependent_count']} files")
            report_lines.append("")
        
        report_lines.extend([
            "🔄 Deepest Dependency Chains:",
            ""
        ])
        
        for chain_info in critical_paths['deepest_chains']:
            report_lines.append(f"  🔗 From {chain_info['entry_point']} (depth: {chain_info['depth']}):")
            for i, file in enumerate(chain_info['chain']):
                indent = "    " + "  " * i
                report_lines.append(f"{indent}→ {Path(file).name}")
            report_lines.append("")
        
        # Orphaned files summary
        report_lines.extend([
            "🏝️ ORPHANED FILES SUMMARY",
            "=" * 60,
            "",
            f"Total orphaned files: {len(self.dependency_report['orphaned_files'])}",
            "",
            "Top 20 orphaned files:",
            ""
        ])
        
        for file in self.dependency_report['orphaned_files'][:20]:
            report_lines.append(f"  🗑️  {file}")
        
        if len(self.dependency_report['orphaned_files']) > 20:
            report_lines.append(f"  ... and {len(self.dependency_report['orphaned_files']) - 20} more")
        
        report_lines.extend([
            "",
            "📋 RECOMMENDATIONS",
            "=" * 60,
            "",
            "1. 🧹 CLEANUP ACTIONS:",
            "   - Run cleanup_unused_files.sh to remove safe files",
            "   - Review orphaned files in unused_files_report.json",
            "   - Remove outdated migration files",
            "   - Clean up backup and temporary files",
            "",
            "2. 🔧 OPTIMIZATION OPPORTUNITIES:",
            "   - Consider breaking down large files with many dependencies",
            "   - Review circular dependencies if any exist",
            "   - Consolidate similar utility files",
            "",
            "3. 📊 MAINTENANCE:",
            "   - Regularly run dependency analysis",
            "   - Monitor for new orphaned files",
            "   - Keep documentation up to date",
            "",
            "4. 🎯 FOCUS AREAS:",
            "   - Core files that many others depend on should be stable",
            "   - Entry points should have clear, minimal dependencies",
            "   - Test files should be comprehensive but not excessive",
            "",
            "Generated by Orientor Project Dependency Analyzer",
            f"Report timestamp: {subprocess.run(['date'], capture_output=True, text=True).stdout.strip()}",
            ""
        ])
        
        return "\n".join(report_lines)
    
    def save_report(self, filename: str = "dependency_tree_report.txt"):
        """Save the visual report to a file"""
        report_content = self.generate_visual_report()
        
        with open(self.project_root / filename, 'w') as f:
            f.write(report_content)
        
        print(f"📄 Visual report saved to: {filename}")
        return report_content

def main():
    """Main function"""
    visualizer = DependencyTreeVisualizer(".")
    report = visualizer.save_report()
    
    # Print first part of report to console
    lines = report.split('\n')
    for line in lines[:50]:  # Show first 50 lines
        print(line)
    
    if len(lines) > 50:
        print(f"\n... and {len(lines) - 50} more lines in the full report")

if __name__ == "__main__":
    main()