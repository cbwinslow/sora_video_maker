# Automated Code Quality & Issue Management System

## Overview

This document describes the comprehensive automated system for code quality management, error fixing, and issue tracking.

## Components

### 1. Auto Fix Error Script (`scripts/auto_fix_errors.py`)

Automatically fixes code quality issues in three tiers:

**EASY Tier (Auto-fixable)**:
- Trailing whitespace (W291, W293)
- Unused imports (F401)
- Blank line spacing (E302, E303)

**MEDIUM Tier (Auto-fixable)**:
- Code formatting (black)
- Import sorting (isort)
- Line length issues (E501)

**HARD Tier (Manual review required)**:
- Logic errors (F811, F541)
- Security issues (Bandit findings)
- Complex refactoring

#### Usage

```bash
# Analyze only
python scripts/auto_fix_errors.py --analyze-only --report quality_report.md

# Fix easy issues
python scripts/auto_fix_errors.py --tier easy

# Fix medium issues
python scripts/auto_fix_errors.py --tier medium

# Fix all auto-fixable issues
python scripts/auto_fix_errors.py --tier all
```

### 2. Codebase Analyzer (`scripts/codebase_analyzer.py`)

Provides "CEO mode" big-picture analysis:

- Architecture overview
- Dependency mapping
- Agent communication patterns
- Test coverage analysis
- Strategic recommendations

#### Usage

```bash
# Generate analysis
python scripts/codebase_analyzer.py --output analysis.md

# JSON format
python scripts/codebase_analyzer.py --format json --output analysis.json
```

### 3. GitHub Actions Workflows

#### Auto Fix Workflow (`.github/workflows/auto_fix.yml`)

- **Trigger**: Manual dispatch or daily schedule
- **Actions**:
  - Runs auto-fix script
  - Commits changes
  - Creates PR with fixes
  - Uploads quality report

#### Code Analysis Workflow (`.github/workflows/code_analysis.yml`)

- **Trigger**: Push, PR, weekly schedule
- **Actions**:
  - Runs codebase analyzer
  - Runs quality analyzer
  - Comments on PRs with analysis
  - Creates issues for critical findings

### 4. GitHub Issue Templates

Located in `.github/ISSUE_TEMPLATE/`:

- **bug_report.yml**: Bug reports with severity tracking
- **feature_request.yml**: Feature requests with priority
- **code_quality.yml**: Code quality issues with auto-fix flag
- **documentation.yml**: Documentation issues

### 5. CodeRabbit Configuration (`.coderabbit.yaml`)

Configured for:
- Path-specific review instructions
- Security-first approach
- Agent-specific review patterns
- Test-specific guidelines
- Priority-based feedback

## Workflow Integration

### Daily Operations

1. **Automated Daily Fixes** (2 AM UTC)
   - Auto-fix workflow runs
   - Creates PR if changes needed
   - Quality report generated

2. **Weekly Analysis** (Monday 9 AM UTC)
   - Codebase analyzer runs
   - Strategic report generated
   - Issues created for critical findings

### Development Workflow

1. **Developer makes changes**
2. **Push to branch**
3. **CI runs**:
   - Test suite
   - Linting
   - Security scan
   - Code analysis
4. **CodeRabbit reviews**
5. **Analysis comments added to PR**
6. **Developer addresses feedback**
7. **Merge when ready**

### Issue Management

1. **Automated detection** (via workflows)
2. **Issue created** (using templates)
3. **Labeled and triaged** (auto-labels)
4. **Assigned to milestone** (manual)
5. **Auto-fix attempts** (if easy/medium)
6. **Manual review** (if hard)
7. **Close when fixed**

## Configuration

### Environment Variables

No special environment variables required. Uses GitHub Actions secrets:
- `GITHUB_TOKEN` (automatically provided)

### Dependencies

Install all tools:

```bash
pip install flake8 black isort pylint bandit safety autoflake
```

### Manual Execution

Run quality checks locally before pushing:

```bash
# Full analysis
python scripts/codebase_analyzer.py
python scripts/auto_fix_errors.py --analyze-only

# Apply fixes
python scripts/auto_fix_errors.py --tier easy
git add -A
git commit -m "chore: auto-fix code quality issues"

# Run tests
./run_tests.sh --coverage
```

## Best Practices

### For Developers

1. **Run local checks** before pushing
2. **Review auto-fix changes** before committing
3. **Address hard issues** manually
4. **Keep PRs focused** on single concerns
5. **Use issue templates** for consistency

### For Maintainers

1. **Review weekly reports** for trends
2. **Triage issues** promptly
3. **Update workflows** as needed
4. **Monitor auto-fix PRs** for accuracy
5. **Adjust CodeRabbit config** based on team needs

### For CodeRabbit Integration

1. **Tag @coderabbit** in PR comments for re-review
2. **Use `@coderabbit pause`** to temporarily disable
3. **Check `.coderabbit.yaml`** for review instructions
4. **Request specific reviews**: `@coderabbit review agents/`

## Integration with Other Tools

### OpenRouter SDK Integration

For LLM-powered analysis (future enhancement):

```python
import openai

# Configure OpenRouter endpoint
openai.api_base = "https://openrouter.ai/api/v1"
openai.api_key = os.getenv("OPENROUTER_API_KEY")

# Use free models for code analysis
response = openai.ChatCompletion.create(
    model="meta-llama/llama-3-8b-instruct:free",
    messages=[{
        "role": "user",
        "content": "Analyze this code for issues: ..."
    }]
)
```

### Ollama Integration

For local LLM analysis:

```python
import requests

def analyze_with_ollama(code: str) -> str:
    """Use Ollama for code analysis"""
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "codellama",
            "prompt": f"Analyze this code:\n\n{code}",
            "stream": False
        }
    )
    return response.json()["response"]
```

## Troubleshooting

### Auto-fix workflow fails

Check:
- Dependencies installed correctly
- File permissions
- Git configuration

### Analysis takes too long

Optimize:
- Exclude large directories
- Use caching
- Run on schedule only

### Too many false positives

Adjust:
- Linter configurations
- CodeRabbit settings
- Issue templates

## Future Enhancements

1. **LLM-powered code review**
   - Use OpenRouter free models
   - Use Ollama for local analysis
   - Generate smart suggestions

2. **Advanced metrics**
   - Code complexity tracking
   - Performance regression detection
   - Security vulnerability trends

3. **Auto-merge for trivial fixes**
   - Whitespace-only changes
   - Import sorting
   - Documentation fixes

4. **Integration with project management**
   - Link issues to epics
   - Track velocity
   - Generate reports

## Support

For issues with this system:

1. Check existing issues
2. Review workflow logs
3. Test scripts locally
4. Create issue using templates
5. Tag relevant maintainers

## Related Documentation

- [TASKS.md](../TASKS.md) - Overall task tracking
- [COMPREHENSIVE_TESTING.md](../docs/COMPREHENSIVE_TESTING.md) - Testing guide
- [GitHub Actions Docs](https://docs.github.com/en/actions)
- [CodeRabbit Docs](https://docs.coderabbit.ai/)

---

**Last Updated**: 2026-02-02
**Maintainer**: GitHub Copilot + @cbwinslow
