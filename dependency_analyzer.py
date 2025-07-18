#!/usr/bin/env python3
"""
Comprehensive Dependency Analyzer for Orientor Project
Analyzes all import/require statements and file dependencies
"""

import os
import re
import json
import ast
import glob
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from collections import defaultdict, deque

class DependencyAnalyzer:
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.all_files = set()
        self.used_files = set()
        self.dependency_graph = defaultdict(set)
        self.reverse_dependency_graph = defaultdict(set)
        self.orphaned_files = set()
        self.config_referenced_files = set()
        
        # Track different file types
        self.python_files = set()
        self.typescript_files = set()
        self.javascript_files = set()
        self.json_files = set()
        self.css_files = set()
        self.static_files = set()
        self.test_files = set()
        
        # Entry points
        self.entry_points = {
            'frontend': 'frontend/src/app/page.tsx',
            'backend': 'backend/app/main.py'
        }
        
    def discover_all_files(self):
        """Discover all files in the project"""
        patterns = [
            '**/*.py', '**/*.ts', '**/*.tsx', '**/*.js', '**/*.jsx',
            '**/*.json', '**/*.css', '**/*.scss', '**/*.md',
            '**/*.html', '**/*.png', '**/*.jpg', '**/*.jpeg',
            '**/*.gif', '**/*.svg', '**/*.ico', '**/*.woff',
            '**/*.woff2', '**/*.ttf', '**/*.otf', '**/*.pdf'
        ]
        
        for pattern in patterns:
            for file_path in self.project_root.glob(pattern):
                if file_path.is_file() and not self._should_ignore(file_path):
                    rel_path = file_path.relative_to(self.project_root)
                    self.all_files.add(str(rel_path))
                    self._categorize_file(rel_path)
                    
    def _should_ignore(self, file_path: Path) -> bool:
        """Check if file should be ignored"""
        ignore_patterns = [
            'node_modules', '.git', '__pycache__', '.pytest_cache',
            '.mypy_cache', '.vercel', '.next', 'build', 'dist',
            '.env', '.env.local', '.env.production', '.env.development',
            'mlruns', '.swarm', 'memory/backups', 'logs'
        ]
        
        path_str = str(file_path)
        return any(pattern in path_str for pattern in ignore_patterns)
    
    def _categorize_file(self, file_path: Path):
        """Categorize files by type"""
        suffix = file_path.suffix.lower()
        path_str = str(file_path)
        
        if suffix == '.py':
            self.python_files.add(path_str)
        elif suffix in ['.ts', '.tsx']:
            self.typescript_files.add(path_str)
        elif suffix in ['.js', '.jsx']:
            self.javascript_files.add(path_str)
        elif suffix == '.json':
            self.json_files.add(path_str)
        elif suffix in ['.css', '.scss', '.module.css']:
            self.css_files.add(path_str)
        elif suffix in ['.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico', '.woff', '.woff2', '.ttf', '.otf']:
            self.static_files.add(path_str)
        
        # Mark test files
        if any(test_indicator in path_str.lower() for test_indicator in ['test', 'spec', '__tests__']):
            self.test_files.add(path_str)
    
    def analyze_python_imports(self, file_path: str) -> Set[str]:
        """Analyze Python imports and return referenced files"""
        dependencies = set()
        
        try:
            with open(self.project_root / file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Parse Python AST
            try:
                tree = ast.parse(content)
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            deps = self._resolve_python_import(alias.name, file_path)
                            dependencies.update(deps)
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            deps = self._resolve_python_import(node.module, file_path)
                            dependencies.update(deps)
                            
            except SyntaxError:
                # Fall back to regex parsing for syntax errors
                dependencies.update(self._parse_python_imports_regex(content, file_path))
                
        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")
            
        return dependencies
    
    def _resolve_python_import(self, module_name: str, current_file: str) -> Set[str]:
        """Resolve Python import to actual file paths"""
        dependencies = set()
        
        if module_name.startswith('.'):
            # Relative import
            current_dir = Path(current_file).parent
            if module_name.startswith('..'):
                # Go up directories
                levels = len(module_name) - len(module_name.lstrip('.'))
                target_dir = current_dir
                for _ in range(levels - 1):
                    target_dir = target_dir.parent
                module_path = module_name.lstrip('.')
            else:
                # Same directory
                target_dir = current_dir
                module_path = module_name.lstrip('.')
            
            if module_path:
                possible_paths = [
                    target_dir / f"{module_path}.py",
                    target_dir / module_path / "__init__.py"
                ]
            else:
                possible_paths = [target_dir / "__init__.py"]
                
            for path in possible_paths:
                if (self.project_root / path).exists():
                    dependencies.add(str(path))
                    
        else:
            # Absolute import from project
            module_parts = module_name.split('.')
            
            # Try different base directories
            base_dirs = ['backend', 'backend/app', 'frontend/src', '.']
            
            for base_dir in base_dirs:
                base_path = Path(base_dir)
                
                # Try direct file
                file_path = base_path / '/'.join(module_parts[1:]) if module_parts[0] == 'app' else base_path / '/'.join(module_parts)
                
                possible_paths = [
                    f"{file_path}.py",
                    f"{file_path}/__init__.py"
                ]
                
                for path in possible_paths:
                    if (self.project_root / path).exists():
                        dependencies.add(str(path))
                        
        return dependencies
    
    def _parse_python_imports_regex(self, content: str, file_path: str) -> Set[str]:
        """Parse Python imports using regex as fallback"""
        dependencies = set()
        
        # Match import statements
        import_patterns = [
            r'^\s*import\s+([^\s#]+)',
            r'^\s*from\s+([^\s#]+)\s+import',
        ]
        
        for line in content.split('\n'):
            for pattern in import_patterns:
                match = re.match(pattern, line)
                if match:
                    module_name = match.group(1)
                    deps = self._resolve_python_import(module_name, file_path)
                    dependencies.update(deps)
                    
        return dependencies
    
    def analyze_typescript_imports(self, file_path: str) -> Set[str]:
        """Analyze TypeScript/JavaScript imports and return referenced files"""
        dependencies = set()
        
        try:
            with open(self.project_root / file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Parse import statements
            import_patterns = [
                r'import\s+.*?\s+from\s+["\']([^"\']+)["\']',
                r'import\s+["\']([^"\']+)["\']',
                r'require\s*\(\s*["\']([^"\']+)["\']\s*\)',
                r'import\s*\(\s*["\']([^"\']+)["\']\s*\)',
                r'@import\s+["\']([^"\']+)["\']',  # CSS imports
            ]
            
            for pattern in import_patterns:
                matches = re.findall(pattern, content)
                for match in matches:
                    deps = self._resolve_typescript_import(match, file_path)
                    dependencies.update(deps)
                    
        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")
            
        return dependencies
    
    def _resolve_typescript_import(self, import_path: str, current_file: str) -> Set[str]:
        """Resolve TypeScript import to actual file paths"""
        dependencies = set()
        
        if import_path.startswith('.'):
            # Relative import
            current_dir = Path(current_file).parent
            resolved_path = (current_dir / import_path).resolve()
            
            # Try different extensions
            extensions = ['', '.ts', '.tsx', '.js', '.jsx', '.json', '.css', '.scss', '.module.css']
            
            for ext in extensions:
                test_path = resolved_path.with_suffix(ext)
                rel_path = test_path.relative_to(self.project_root)
                
                if test_path.exists():
                    dependencies.add(str(rel_path))
                    break
                    
                # Try as directory with index file
                if (test_path / 'index.ts').exists():
                    dependencies.add(str((test_path / 'index.ts').relative_to(self.project_root)))
                    break
                elif (test_path / 'index.tsx').exists():
                    dependencies.add(str((test_path / 'index.tsx').relative_to(self.project_root)))
                    break
                elif (test_path / 'index.js').exists():
                    dependencies.add(str((test_path / 'index.js').relative_to(self.project_root)))
                    break
                    
        elif import_path.startswith('@/'):
            # Absolute import with @ alias (usually src/)
            src_path = Path('frontend/src') / import_path[2:]
            
            extensions = ['', '.ts', '.tsx', '.js', '.jsx', '.json', '.css', '.scss', '.module.css']
            
            for ext in extensions:
                test_path = self.project_root / src_path.with_suffix(ext)
                
                if test_path.exists():
                    dependencies.add(str(src_path.with_suffix(ext)))
                    break
                    
        return dependencies
    
    def analyze_json_references(self, file_path: str) -> Set[str]:
        """Analyze JSON files for file references"""
        dependencies = set()
        
        try:
            with open(self.project_root / file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Parse JSON
            try:
                data = json.loads(content)
                dependencies.update(self._extract_file_references_from_json(data, file_path))
            except json.JSONDecodeError:
                # Fall back to regex search for file paths
                file_patterns = [
                    r'["\']([^"\']*\.[a-zA-Z0-9]+)["\']',  # Files with extensions
                    r'["\'](\./[^"\']+)["\']',  # Relative paths
                    r'["\'](\.\./[^"\']+)["\']',  # Parent directory paths
                ]
                
                for pattern in file_patterns:
                    matches = re.findall(pattern, content)
                    for match in matches:
                        if self._looks_like_file_path(match):
                            resolved = self._resolve_json_reference(match, file_path)
                            dependencies.update(resolved)
                            
        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")
            
        return dependencies
    
    def _extract_file_references_from_json(self, data, current_file: str) -> Set[str]:
        """Extract file references from JSON data"""
        dependencies = set()
        
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, str) and self._looks_like_file_path(value):
                    resolved = self._resolve_json_reference(value, current_file)
                    dependencies.update(resolved)
                elif isinstance(value, (dict, list)):
                    dependencies.update(self._extract_file_references_from_json(value, current_file))
                    
        elif isinstance(data, list):
            for item in data:
                dependencies.update(self._extract_file_references_from_json(item, current_file))
                
        return dependencies
    
    def _looks_like_file_path(self, path: str) -> bool:
        """Check if string looks like a file path"""
        if not path:
            return False
            
        # Skip URLs
        if path.startswith(('http://', 'https://', 'ftp://')):
            return False
            
        # Skip node modules
        if 'node_modules' in path:
            return False
            
        # Check for file extensions or relative paths
        return (
            '.' in path and (
                path.endswith(('.js', '.ts', '.tsx', '.jsx', '.json', '.css', '.scss', '.png', '.jpg', '.svg', '.ico', '.woff', '.woff2', '.ttf', '.otf')) or
                path.startswith(('./', '../')) or
                '/' in path
            )
        )
    
    def _resolve_json_reference(self, ref_path: str, current_file: str) -> Set[str]:
        """Resolve JSON file reference to actual file paths"""
        dependencies = set()
        
        if ref_path.startswith('.'):
            # Relative path
            current_dir = Path(current_file).parent
            resolved_path = (current_dir / ref_path).resolve()
            
            try:
                rel_path = resolved_path.relative_to(self.project_root)
                if (self.project_root / rel_path).exists():
                    dependencies.add(str(rel_path))
            except ValueError:
                # Path is outside project root
                pass
                
        else:
            # Try as absolute path from project root
            if (self.project_root / ref_path).exists():
                dependencies.add(ref_path)
                
        return dependencies
    
    def analyze_config_files(self):
        """Analyze configuration files for file references"""
        config_files = [
            'package.json',
            'frontend/package.json',
            'backend/requirements.txt',
            'next.config.js',
            'tailwind.config.js',
            'tsconfig.json',
            'frontend/tsconfig.json',
            'vercel.json',
            'docker-compose.yml',
            'backend/docker-compose.yml',
            'Procfile',
            'railway.toml',
            'alembic.ini',
            'backend/alembic.ini'
        ]
        
        for config_file in config_files:
            if (self.project_root / config_file).exists():
                self.used_files.add(config_file)
                
                if config_file.endswith('.json'):
                    deps = self.analyze_json_references(config_file)
                    self.config_referenced_files.update(deps)
                    self.dependency_graph[config_file].update(deps)
                elif config_file.endswith('.js'):
                    deps = self.analyze_typescript_imports(config_file)
                    self.config_referenced_files.update(deps)
                    self.dependency_graph[config_file].update(deps)
    
    def trace_dependencies_from_entry_points(self):
        """Trace all dependencies from entry points"""
        visited = set()
        
        for entry_name, entry_path in self.entry_points.items():
            if (self.project_root / entry_path).exists():
                self._trace_dependencies_recursive(entry_path, visited)
                
    def _trace_dependencies_recursive(self, file_path: str, visited: set):
        """Recursively trace dependencies"""
        if file_path in visited:
            return
            
        visited.add(file_path)
        self.used_files.add(file_path)
        
        # Analyze based on file type
        if file_path.endswith('.py'):
            deps = self.analyze_python_imports(file_path)
        elif file_path.endswith(('.ts', '.tsx', '.js', '.jsx')):
            deps = self.analyze_typescript_imports(file_path)
        elif file_path.endswith('.json'):
            deps = self.analyze_json_references(file_path)
        else:
            deps = set()
            
        self.dependency_graph[file_path].update(deps)
        
        # Add reverse dependencies
        for dep in deps:
            self.reverse_dependency_graph[dep].add(file_path)
            
        # Recursively trace dependencies
        for dep in deps:
            if dep not in visited:
                self._trace_dependencies_recursive(dep, visited)
                
    def find_orphaned_files(self):
        """Find files that are not referenced anywhere"""
        # Files that are used directly or referenced
        all_used = set()
        all_used.update(self.used_files)
        all_used.update(self.config_referenced_files)
        
        # Add all dependencies
        for deps in self.dependency_graph.values():
            all_used.update(deps)
            
        # Find orphaned files
        self.orphaned_files = self.all_files - all_used
        
        # Remove certain files that are legitimately standalone
        legitimate_standalone = set()
        for file_path in self.orphaned_files:
            if any(pattern in file_path.lower() for pattern in [
                'readme', 'license', 'changelog', 'todo', 'note',
                'example', 'demo', 'test', 'spec', 'backup',
                'migration', 'seed', 'fixture', 'script',
                '.md', '.txt', '.log', '.env', '.gitignore',
                'dockerfile', 'procfile', 'requirements',
                'package.json', 'tsconfig.json', 'next.config'
            ]):
                legitimate_standalone.add(file_path)
                
        self.orphaned_files -= legitimate_standalone
        
    def generate_report(self) -> dict:
        """Generate comprehensive dependency report"""
        return {
            'summary': {
                'total_files': len(self.all_files),
                'used_files': len(self.used_files),
                'orphaned_files': len(self.orphaned_files),
                'dependency_relationships': len(self.dependency_graph),
                'file_types': {
                    'python': len(self.python_files),
                    'typescript': len(self.typescript_files),
                    'javascript': len(self.javascript_files),
                    'json': len(self.json_files),
                    'css': len(self.css_files),
                    'static': len(self.static_files),
                    'test': len(self.test_files)
                }
            },
            'entry_points': self.entry_points,
            'dependency_graph': {k: list(v) for k, v in self.dependency_graph.items()},
            'reverse_dependencies': {k: list(v) for k, v in self.reverse_dependency_graph.items()},
            'orphaned_files': sorted(list(self.orphaned_files)),
            'config_referenced_files': sorted(list(self.config_referenced_files)),
            'used_files': sorted(list(self.used_files)),
            'file_categories': {
                'python': sorted(list(self.python_files)),
                'typescript': sorted(list(self.typescript_files)),
                'javascript': sorted(list(self.javascript_files)),
                'json': sorted(list(self.json_files)),
                'css': sorted(list(self.css_files)),
                'static': sorted(list(self.static_files)),
                'test': sorted(list(self.test_files))
            }
        }
    
    def analyze(self):
        """Run complete dependency analysis"""
        print("🔍 Discovering all files...")
        self.discover_all_files()
        
        print("📋 Analyzing configuration files...")
        self.analyze_config_files()
        
        print("🔗 Tracing dependencies from entry points...")
        self.trace_dependencies_from_entry_points()
        
        print("🏝️ Finding orphaned files...")
        self.find_orphaned_files()
        
        print("📊 Generating report...")
        return self.generate_report()


def main():
    """Main function to run dependency analysis"""
    project_root = "."
    
    analyzer = DependencyAnalyzer(project_root)
    report = analyzer.analyze()
    
    # Save report to file
    with open('dependency_analysis_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    # Print summary
    print("\n" + "="*60)
    print("📊 DEPENDENCY ANALYSIS SUMMARY")
    print("="*60)
    print(f"Total files found: {report['summary']['total_files']}")
    print(f"Files in use: {report['summary']['used_files']}")
    print(f"Orphaned files: {report['summary']['orphaned_files']}")
    print(f"Dependency relationships: {report['summary']['dependency_relationships']}")
    
    print("\n📁 File Types:")
    for file_type, count in report['summary']['file_types'].items():
        print(f"  {file_type}: {count}")
    
    print("\n🏝️ Orphaned Files (potentially safe to remove):")
    for file_path in report['orphaned_files'][:20]:  # Show first 20
        print(f"  {file_path}")
    
    if len(report['orphaned_files']) > 20:
        print(f"  ... and {len(report['orphaned_files']) - 20} more")
    
    print(f"\n📄 Full report saved to: dependency_analysis_report.json")


if __name__ == "__main__":
    main()