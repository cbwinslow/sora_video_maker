#!/usr/bin/env python3
"""
Codebase Big Picture Analyzer ("CEO Mode")

Provides high-level architecture analysis and strategic assessment of the codebase.
Identifies patterns, dependencies, and potential issues at the system level.

Usage:
    python scripts/codebase_analyzer.py
    python scripts/codebase_analyzer.py --output report.md
    python scripts/codebase_analyzer.py --format json
"""

import os
import sys
import json
import argparse
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import defaultdict
import ast
import re


class CodebaseAnalyzer:
    """Analyzes codebase architecture and patterns"""
    
    def __init__(self, root_dir: str = "."):
        self.root_dir = Path(root_dir)
        self.modules = {}
        self.dependencies = defaultdict(set)
        self.agents = []
        self.crews = []
        self.scripts = []
        self.tests = []
        
    def analyze(self) -> Dict:
        """Perform comprehensive codebase analysis"""
        print("🔍 Analyzing codebase architecture...")
        
        # Scan structure
        self._scan_structure()
        
        # Analyze dependencies
        self._analyze_dependencies()
        
        # Analyze agents
        self._analyze_agents()
        
        # Analyze tests
        self._analyze_tests()
        
        # Generate insights
        insights = self._generate_insights()
        
        return {
            'structure': self._get_structure_summary(),
            'dependencies': self._get_dependency_summary(),
            'agents': self._get_agent_summary(),
            'tests': self._get_test_summary(),
            'insights': insights,
            'recommendations': self._generate_recommendations()
        }
    
    def _scan_structure(self):
        """Scan project structure"""
        
        # Find all Python files
        for py_file in self.root_dir.rglob('*.py'):
            rel_path = py_file.relative_to(self.root_dir)
            
            # Categorize
            if 'agents/' in str(rel_path):
                self.agents.append(str(rel_path))
            elif 'crews/' in str(rel_path):
                self.crews.append(str(rel_path))
            elif 'scripts/' in str(rel_path):
                self.scripts.append(str(rel_path))
            elif 'tests/' in str(rel_path):
                self.tests.append(str(rel_path))
            
            # Parse module
            try:
                with open(py_file, 'r') as f:
                    tree = ast.parse(f.read(), filename=str(py_file))
                    self.modules[str(rel_path)] = {
                        'classes': [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)],
                        'functions': [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)],
                        'imports': self._extract_imports(tree),
                        'lines': len(f.readlines())
                    }
            except:
                pass
    
    def _extract_imports(self, tree) -> List[str]:
        """Extract import statements"""
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)
        return imports
    
    def _analyze_dependencies(self):
        """Analyze module dependencies"""
        
        for module, info in self.modules.items():
            for imp in info['imports']:
                # Check if it's an internal import
                if any(imp.startswith(prefix) for prefix in ['agents', 'scripts', 'crews']):
                    self.dependencies[module].add(imp)
    
    def _analyze_agents(self):
        """Analyze agent patterns"""
        pass  # Placeholder for agent-specific analysis
    
    def _analyze_tests(self):
        """Analyze test coverage patterns"""
        pass  # Placeholder for test analysis
    
    def _get_structure_summary(self) -> Dict:
        """Get structure summary"""
        return {
            'agents': len(self.agents),
            'crews': len(self.crews),
            'scripts': len(self.scripts),
            'tests': len(self.tests),
            'total_modules': len(self.modules),
            'total_classes': sum(len(m['classes']) for m in self.modules.values()),
            'total_functions': sum(len(m['functions']) for m in self.modules.values()),
            'total_lines': sum(m.get('lines', 0) for m in self.modules.values())
        }
    
    def _get_dependency_summary(self) -> Dict:
        """Get dependency summary"""
        
        # Find most depended-on modules
        dependency_counts = defaultdict(int)
        for deps in self.dependencies.values():
            for dep in deps:
                dependency_counts[dep] += 1
        
        return {
            'total_dependencies': len(self.dependencies),
            'most_depended_on': sorted(
                dependency_counts.items(),
                key=lambda x: x[1],
                reverse=True
            )[:10]
        }
    
    def _get_agent_summary(self) -> Dict:
        """Get agent summary"""
        return {
            'total_agents': len(self.agents),
            'agents': self.agents,
            'communication_patterns': self._detect_communication_patterns()
        }
    
    def _get_test_summary(self) -> Dict:
        """Get test summary"""
        test_types = {
            'unit': len([t for t in self.tests if 'unit' in t]),
            'integration': len([t for t in self.tests if 'integration' in t]),
            'other': len([t for t in self.tests if 'unit' not in t and 'integration' not in t])
        }
        
        return {
            'total_tests': len(self.tests),
            'test_types': test_types,
            'test_files': self.tests
        }
    
    def _detect_communication_patterns(self) -> List[str]:
        """Detect agent communication patterns"""
        patterns = []
        
        # Check for common patterns
        if any('trending_topics' in str(a) for a in self.agents):
            patterns.append('Research Agent Pattern')
        
        if any('generation' in str(a) for a in self.agents):
            patterns.append('Generation Agent Pattern')
        
        if any('upload' in str(a) for a in self.agents):
            patterns.append('Upload Agent Pattern')
        
        if len(self.crews) > 0:
            patterns.append('Crew Coordination Pattern')
        
        return patterns
    
    def _generate_insights(self) -> List[str]:
        """Generate strategic insights"""
        insights = []
        
        structure = self._get_structure_summary()
        
        # Size insights
        if structure['total_lines'] > 10000:
            insights.append(f"📊 Large codebase ({structure['total_lines']} lines) - consider modularization")
        
        # Agent insights
        if structure['agents'] < 5:
            insights.append("🤖 Small agent system - good for maintainability")
        elif structure['agents'] > 10:
            insights.append("🤖 Large agent system - ensure proper coordination")
        
        # Test insights
        test_ratio = structure['tests'] / max(structure['total_modules'], 1)
        if test_ratio < 0.5:
            insights.append(f"⚠️ Low test coverage ({test_ratio:.1%}) - consider adding more tests")
        elif test_ratio > 0.8:
            insights.append(f"✅ Good test coverage ({test_ratio:.1%})")
        
        # Dependency insights
        if len(self.dependencies) > 20:
            insights.append("🔗 Complex dependency graph - potential for circular dependencies")
        
        return insights
    
    def _generate_recommendations(self) -> List[Dict]:
        """Generate actionable recommendations"""
        recommendations = []
        
        structure = self._get_structure_summary()
        
        # Testing recommendations
        if structure['tests'] < structure['agents'] + structure['scripts']:
            recommendations.append({
                'priority': 'HIGH',
                'category': 'Testing',
                'title': 'Increase Test Coverage',
                'description': 'Add more tests to cover agents and scripts',
                'action': 'Create unit tests for each agent and integration tests for workflows'
            })
        
        # Documentation recommendations
        if not (self.root_dir / 'docs').exists():
            recommendations.append({
                'priority': 'MEDIUM',
                'category': 'Documentation',
                'title': 'Add Documentation',
                'description': 'Create comprehensive documentation',
                'action': 'Add docs/ directory with architecture and API documentation'
            })
        
        # Agent coordination recommendations
        if len(self.agents) > 3 and len(self.crews) == 0:
            recommendations.append({
                'priority': 'HIGH',
                'category': 'Architecture',
                'title': 'Add Agent Coordination',
                'description': 'Multiple agents without crew coordination',
                'action': 'Implement crew pattern for multi-agent orchestration'
            })
        
        # CI/CD recommendations
        if not (self.root_dir / '.github' / 'workflows').exists():
            recommendations.append({
                'priority': 'HIGH',
                'category': 'DevOps',
                'title': 'Add CI/CD Pipeline',
                'description': 'No GitHub Actions workflows found',
                'action': 'Create workflows for testing, linting, and deployment'
            })
        
        return recommendations
    
    def generate_markdown_report(self, analysis: Dict) -> str:
        """Generate markdown report"""
        
        report = "# Codebase Architecture Analysis\n\n"
        report += "**Big Picture Strategic Assessment**\n\n"
        report += "---\n\n"
        
        # Executive Summary
        report += "## 📊 Executive Summary\n\n"
        structure = analysis['structure']
        report += f"- **Total Modules**: {structure['total_modules']}\n"
        report += f"- **Agents**: {structure['agents']}\n"
        report += f"- **Crews**: {structure['crews']}\n"
        report += f"- **Scripts**: {structure['scripts']}\n"
        report += f"- **Tests**: {structure['tests']}\n"
        report += f"- **Total Lines of Code**: {structure['total_lines']:,}\n"
        report += f"- **Classes**: {structure['total_classes']}\n"
        report += f"- **Functions**: {structure['total_functions']}\n\n"
        
        # Agent Architecture
        report += "## 🤖 Agent Architecture\n\n"
        agent_summary = analysis['agents']
        report += f"**Total Agents**: {agent_summary['total_agents']}\n\n"
        report += "**Communication Patterns Detected**:\n"
        for pattern in agent_summary['communication_patterns']:
            report += f"- {pattern}\n"
        report += "\n"
        
        # Dependencies
        report += "## 🔗 Dependencies\n\n"
        dep_summary = analysis['dependencies']
        report += f"**Total Dependencies**: {dep_summary['total_dependencies']}\n\n"
        if dep_summary['most_depended_on']:
            report += "**Most Depended-On Modules**:\n"
            for module, count in dep_summary['most_depended_on'][:5]:
                report += f"- `{module}` ({count} dependencies)\n"
        report += "\n"
        
        # Testing
        report += "## 🧪 Testing Overview\n\n"
        test_summary = analysis['tests']
        report += f"**Total Test Files**: {test_summary['total_tests']}\n\n"
        report += "**Test Distribution**:\n"
        for test_type, count in test_summary['test_types'].items():
            report += f"- {test_type.title()}: {count}\n"
        report += "\n"
        
        # Insights
        report += "## 💡 Strategic Insights\n\n"
        for insight in analysis['insights']:
            report += f"{insight}\n\n"
        
        # Recommendations
        report += "## 🎯 Recommendations\n\n"
        for rec in analysis['recommendations']:
            report += f"### {rec['priority']}: {rec['title']}\n\n"
            report += f"**Category**: {rec['category']}\n\n"
            report += f"**Description**: {rec['description']}\n\n"
            report += f"**Action**: {rec['action']}\n\n"
        
        # Architecture Diagram
        report += "## 📐 Architecture Overview\n\n"
        report += "```\n"
        report += "┌─────────────────────────────────────┐\n"
        report += "│     Main Orchestrator (main.py)    │\n"
        report += "└──────────────┬──────────────────────┘\n"
        report += "               │\n"
        report += "      ┌────────┴─────────┐\n"
        report += "      │                  │\n"
        report += "┌─────▼──────┐    ┌──────▼──────┐\n"
        report += "│   Agents   │    │    Crews    │\n"
        report += "│  (6 total) │    │  (2 total)  │\n"
        report += "└────────────┘    └─────────────┘\n"
        report += "      │                  │\n"
        report += "      └────────┬─────────┘\n"
        report += "               │\n"
        report += "      ┌────────▼──────────┐\n"
        report += "      │   Scripts/Utils   │\n"
        report += f"      │   ({structure['scripts']} modules)    │\n"
        report += "      └───────────────────┘\n"
        report += "```\n\n"
        
        return report


def main():
    parser = argparse.ArgumentParser(description='Codebase Architecture Analyzer')
    parser.add_argument(
        '--output',
        type=str,
        help='Output file for report'
    )
    parser.add_argument(
        '--format',
        choices=['markdown', 'json'],
        default='markdown',
        help='Output format'
    )
    
    args = parser.parse_args()
    
    analyzer = CodebaseAnalyzer()
    analysis = analyzer.analyze()
    
    if args.format == 'json':
        output = json.dumps(analysis, indent=2)
    else:
        output = analyzer.generate_markdown_report(analysis)
    
    if args.output:
        with open(args.output, 'w') as f:
            f.write(output)
        print(f"\n✅ Report saved to {args.output}")
    else:
        print("\n" + output)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
