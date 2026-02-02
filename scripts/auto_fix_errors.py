#!/usr/bin/env python3
"""
Automated Code Quality Fixer

Categorizes and fixes code quality issues in tiers:
- EASY: Whitespace, trailing spaces, unused imports
- MEDIUM: Code formatting, import sorting
- HARD: Logic errors, security issues (manual review)

Usage:
    python scripts/auto_fix_errors.py --tier easy
    python scripts/auto_fix_errors.py --tier medium
    python scripts/auto_fix_errors.py --tier all
    python scripts/auto_fix_errors.py --analyze-only
"""

import os
import sys
import subprocess
import json
import argparse
from pathlib import Path
from typing import Dict, List, Tuple
import re


class CodeQualityFixer:
    """Automated code quality fixer with tiered approach"""
    
    def __init__(self, root_dir: str = "."):
        self.root_dir = Path(root_dir)
        self.python_dirs = ["agents", "scripts", "crews", "tests"]
        self.python_files = ["main.py"]
        
        self.easy_fixes = []
        self.medium_fixes = []
        self.hard_fixes = []
        
    def analyze(self) -> Dict[str, List]:
        """Analyze codebase and categorize issues"""
        print("🔍 Analyzing codebase for issues...")
        
        # Run flake8
        flake8_issues = self._run_flake8()
        
        # Run pylint
        pylint_issues = self._run_pylint()
        
        # Run bandit (security)
        bandit_issues = self._run_bandit()
        
        # Categorize issues
        self._categorize_issues(flake8_issues, pylint_issues, bandit_issues)
        
        return {
            'easy': self.easy_fixes,
            'medium': self.medium_fixes,
            'hard': self.hard_fixes
        }
    
    def _run_flake8(self) -> List[Dict]:
        """Run flake8 and parse results"""
        issues = []
        
        try:
            targets = self.python_dirs + self.python_files
            cmd = [
                'python', '-m', 'flake8',
                *targets,
                '--format=json',
                '--max-line-length=127',
                '--extend-ignore=E501'
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=self.root_dir
            )
            
            # Parse output
            for line in result.stdout.split('\n'):
                if line.strip():
                    try:
                        # flake8 doesn't have native JSON, parse text output
                        match = re.match(r'(.+):(\d+):(\d+): ([A-Z]\d+) (.+)', line)
                        if match:
                            issues.append({
                                'file': match.group(1),
                                'line': int(match.group(2)),
                                'column': int(match.group(3)),
                                'code': match.group(4),
                                'message': match.group(5),
                                'tool': 'flake8'
                            })
                    except:
                        pass
            
        except Exception as e:
            print(f"⚠️  Error running flake8: {e}")
        
        return issues
    
    def _run_pylint(self) -> List[Dict]:
        """Run pylint and parse results"""
        issues = []
        
        try:
            targets = self.python_dirs + self.python_files
            cmd = [
                'python', '-m', 'pylint',
                *targets,
                '--output-format=json',
                '--max-line-length=127',
                '--disable=C0111,R0903,R0913'
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=self.root_dir
            )
            
            if result.stdout:
                try:
                    data = json.loads(result.stdout)
                    for item in data:
                        issues.append({
                            'file': item.get('path'),
                            'line': item.get('line'),
                            'column': item.get('column'),
                            'code': item.get('message-id'),
                            'message': item.get('message'),
                            'tool': 'pylint'
                        })
                except:
                    pass
            
        except Exception as e:
            print(f"⚠️  Error running pylint: {e}")
        
        return issues
    
    def _run_bandit(self) -> List[Dict]:
        """Run bandit security scanner"""
        issues = []
        
        try:
            targets = self.python_dirs + self.python_files
            cmd = [
                'python', '-m', 'bandit',
                '-r', *self.python_dirs,
                '-f', 'json',
                '--skip', 'B101,B601'
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=self.root_dir
            )
            
            if result.stdout:
                try:
                    data = json.loads(result.stdout)
                    for item in data.get('results', []):
                        issues.append({
                            'file': item.get('filename'),
                            'line': item.get('line_number'),
                            'column': 0,
                            'code': item.get('test_id'),
                            'message': item.get('issue_text'),
                            'severity': item.get('issue_severity'),
                            'tool': 'bandit'
                        })
                except:
                    pass
        
        except Exception as e:
            print(f"⚠️  Error running bandit: {e}")
        
        return issues
    
    def _categorize_issues(self, flake8_issues, pylint_issues, bandit_issues):
        """Categorize issues into easy/medium/hard"""
        
        # Easy fixes - whitespace, trailing spaces, unused imports
        easy_codes = ['W291', 'W293', 'W391', 'F401', 'E302', 'E303', 'E231']
        
        # Medium fixes - formatting, docstrings
        medium_codes = ['E128', 'E501', 'C0103', 'C0114', 'C0115', 'C0116']
        
        # Hard fixes - logic, security
        hard_codes = ['F811', 'F541', 'E722', 'W0612', 'R0913', 'R0914']
        
        for issue in flake8_issues + pylint_issues:
            code = issue.get('code', '')
            
            if any(code.startswith(ec) for ec in easy_codes):
                self.easy_fixes.append(issue)
            elif any(code.startswith(mc) for mc in medium_codes):
                self.medium_fixes.append(issue)
            else:
                self.hard_fixes.append(issue)
        
        # All security issues are hard
        self.hard_fixes.extend(bandit_issues)
    
    def fix_easy(self) -> int:
        """Auto-fix easy issues"""
        print("\n🔧 Fixing EASY issues...")
        
        fixed_count = 0
        
        # Fix trailing whitespace and blank line whitespace
        fixed_count += self._fix_whitespace()
        
        # Remove unused imports with autoflake
        fixed_count += self._remove_unused_imports()
        
        # Fix spacing issues
        fixed_count += self._fix_spacing()
        
        print(f"✅ Fixed {fixed_count} easy issues")
        return fixed_count
    
    def fix_medium(self) -> int:
        """Auto-fix medium issues"""
        print("\n🔧 Fixing MEDIUM issues...")
        
        fixed_count = 0
        
        # Run black for formatting
        fixed_count += self._run_black()
        
        # Run isort for import sorting
        fixed_count += self._run_isort()
        
        print(f"✅ Fixed {fixed_count} medium issues")
        return fixed_count
    
    def _fix_whitespace(self) -> int:
        """Fix trailing whitespace and blank line whitespace"""
        fixed = 0
        
        for pydir in self.python_dirs:
            dir_path = self.root_dir / pydir
            if not dir_path.exists():
                continue
            
            for py_file in dir_path.rglob('*.py'):
                try:
                    with open(py_file, 'r') as f:
                        lines = f.readlines()
                    
                    new_lines = []
                    changed = False
                    
                    for line in lines:
                        # Remove trailing whitespace
                        new_line = line.rstrip() + '\n' if line.endswith('\n') else line.rstrip()
                        if new_line != line:
                            changed = True
                        new_lines.append(new_line)
                    
                    if changed:
                        with open(py_file, 'w') as f:
                            f.writelines(new_lines)
                        fixed += 1
                        print(f"  ✓ Fixed whitespace in {py_file.relative_to(self.root_dir)}")
                
                except Exception as e:
                    print(f"  ✗ Error fixing {py_file}: {e}")
        
        return fixed
    
    def _remove_unused_imports(self) -> int:
        """Remove unused imports using autoflake"""
        fixed = 0
        
        try:
            # Install autoflake if not present
            subprocess.run(
                ['pip', 'install', '-q', 'autoflake'],
                capture_output=True
            )
            
            targets = []
            for pydir in self.python_dirs:
                dir_path = self.root_dir / pydir
                if dir_path.exists():
                    targets.extend(dir_path.rglob('*.py'))
            
            for target in targets:
                result = subprocess.run(
                    [
                        'python', '-m', 'autoflake',
                        '--in-place',
                        '--remove-unused-variables',
                        '--remove-all-unused-imports',
                        str(target)
                    ],
                    capture_output=True,
                    cwd=self.root_dir
                )
                
                if result.returncode == 0:
                    fixed += 1
            
            print(f"  ✓ Removed unused imports from {fixed} files")
        
        except Exception as e:
            print(f"  ✗ Error removing unused imports: {e}")
        
        return fixed
    
    def _fix_spacing(self) -> int:
        """Fix basic spacing issues"""
        # This would be handled by black, so we return 0
        return 0
    
    def _run_black(self) -> int:
        """Run black formatter"""
        fixed = 0
        
        try:
            targets = self.python_dirs + self.python_files
            
            result = subprocess.run(
                [
                    'python', '-m', 'black',
                    '--line-length', '127',
                    '--quiet',
                    *targets
                ],
                capture_output=True,
                cwd=self.root_dir
            )
            
            if result.returncode == 0:
                print(f"  ✓ Formatted code with black")
                fixed = 1
        
        except Exception as e:
            print(f"  ✗ Error running black: {e}")
        
        return fixed
    
    def _run_isort(self) -> int:
        """Run isort for import sorting"""
        fixed = 0
        
        try:
            targets = self.python_dirs + self.python_files
            
            result = subprocess.run(
                [
                    'python', '-m', 'isort',
                    '--profile', 'black',
                    '--line-length', '127',
                    *targets
                ],
                capture_output=True,
                cwd=self.root_dir
            )
            
            if result.returncode == 0:
                print(f"  ✓ Sorted imports with isort")
                fixed = 1
        
        except Exception as e:
            print(f"  ✗ Error running isort: {e}")
        
        return fixed
    
    def generate_report(self, issues: Dict[str, List]) -> str:
        """Generate markdown report of issues"""
        
        report = "# Code Quality Analysis Report\n\n"
        report += f"**Generated**: {subprocess.check_output(['date']).decode().strip()}\n\n"
        
        report += "## Summary\n\n"
        report += f"- 🟢 EASY fixes: {len(issues['easy'])}\n"
        report += f"- 🟡 MEDIUM fixes: {len(issues['medium'])}\n"
        report += f"- 🔴 HARD fixes: {len(issues['hard'])}\n"
        report += f"- **Total**: {len(issues['easy']) + len(issues['medium']) + len(issues['hard'])}\n\n"
        
        for tier, tier_issues in [('EASY', issues['easy']), ('MEDIUM', issues['medium']), ('HARD', issues['hard'])]:
            if tier_issues:
                report += f"## {tier} Issues\n\n"
                
                # Group by file
                by_file = {}
                for issue in tier_issues:
                    file = issue.get('file', 'unknown')
                    if file not in by_file:
                        by_file[file] = []
                    by_file[file].append(issue)
                
                for file, file_issues in sorted(by_file.items()):
                    report += f"### `{file}`\n\n"
                    for issue in file_issues[:10]:  # Limit to first 10 per file
                        line = issue.get('line', '?')
                        code = issue.get('code', '?')
                        message = issue.get('message', 'No message')
                        report += f"- Line {line}: `{code}` - {message}\n"
                    
                    if len(file_issues) > 10:
                        report += f"- ... and {len(file_issues) - 10} more issues\n"
                    report += "\n"
        
        return report


def main():
    parser = argparse.ArgumentParser(description='Automated Code Quality Fixer')
    parser.add_argument(
        '--tier',
        choices=['easy', 'medium', 'hard', 'all'],
        default='easy',
        help='Which tier of fixes to apply'
    )
    parser.add_argument(
        '--analyze-only',
        action='store_true',
        help='Only analyze, do not fix'
    )
    parser.add_argument(
        '--report',
        type=str,
        help='Output report to file'
    )
    
    args = parser.parse_args()
    
    fixer = CodeQualityFixer()
    
    # Analyze
    issues = fixer.analyze()
    
    # Generate report
    report = fixer.generate_report(issues)
    
    if args.report:
        with open(args.report, 'w') as f:
            f.write(report)
        print(f"\n📄 Report saved to {args.report}")
    else:
        print("\n" + report)
    
    # Fix if requested
    if not args.analyze_only:
        if args.tier in ['easy', 'all']:
            fixer.fix_easy()
        
        if args.tier in ['medium', 'all']:
            fixer.fix_medium()
        
        if args.tier == 'hard':
            print("\n⚠️  HARD fixes require manual review")
            print("Please review the report and fix issues manually")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
