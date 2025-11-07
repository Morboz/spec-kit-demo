# Development Guide

This document covers the development workflow and tooling for the blokus-step-by-step project.

## Prerequisites

- Python 3.11+
- uv (recommended package manager)
- Git

## Quick Start

1. **Clone and setup**:
   ```bash
   git clone <repository-url>
   cd blokus-step-by-step
   uv sync --dev
   pre-commit install
   ```

2. **Run the game**:
   ```bash
   uv run python src/main.py
   ```

3. **Run tests**:
   ```bash
   uv run pytest
   ```

## Development Workflow

### Code Quality Tools

This project uses modern Python tooling for code quality:

- **Black**: Code formatting (88 character line length)
- **Ruff**: Fast linting and auto-fixing (replaces flake8)
- **MyPy**: Strict type checking
- **Pre-commit**: Automated hooks that run before each commit

### Manual Quality Checks

```bash
# Lint and auto-fix issues
uv run ruff check --fix .

# Format code
uv run black .

# Type checking
uv run mypy .

# Run all quality checks
pre-commit run --all-files
```

### Pre-commit Hooks

Pre-commit hooks automatically run when you `git commit`. They include:

1. **Trailing whitespace removal**
2. **End-of-file fixer**
3. **Black formatting**
4. **Ruff linting with auto-fix**
5. **Ruff formatting**
6. **MyPy type checking**

If any check fails, the commit will be blocked until the issues are resolved.

### Testing

```bash
# Run all tests
uv run pytest

# Run specific test types
uv run pytest tests/unit/
uv run pytest tests/integration/
uv run pytest tests/contract/

# Run with coverage
uv run pytest --cov=src --cov-report=html
```

## Performance Guidelines

- **Ruff execution**: < 200ms for typical file changes
- **Pre-commit hooks**: < 2 seconds for small commits
- **Auto-fix rate**: 80%+ of issues are automatically fixed

## Common Issues and Solutions

### Pre-commit Troubleshooting

1. **Hooks not running**:
   ```bash
   pre-commit install
   ```

2. **Hook timeout**:
   ```bash
   pre-commit run --all-files
   ```

3. **Mypy errors**:
   - Missing type annotations are expected during transition
   - Focus on new code following strict typing guidelines

### Ruff Migration Notes

- **W503 rule**: No longer needed (ruff handles this automatically)
- **Import sorting**: Now handled by ruff's isort integration
- **Auto-fixing**: Many issues are fixed automatically with `--fix`

## Code Style Guidelines

- **Line length**: 88 characters
- **Import style**: Automatic sorting via ruff
- **Type hints**: Strict enforcement with MyPy
- **Documentation**: Follow Google-style docstrings

## Git Workflow

1. Create feature branch from main
2. Make changes (pre-commit hooks run automatically)
3. Manual quality checks if needed
4. Run tests: `uv run pytest`
5. Commit with conventional format
6. Create pull request

## IDE Integration

### VSCode

Add to `.vscode/settings.json`:
```json
{
    "python.defaultInterpreterPath": ".venv/bin/python",
    "python.formatting.provider": "black",
    "python.linting.enabled": true,
    "python.linting.ruffEnabled": true,
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.organizeImports": true
    }
}
```

### PyCharm

- Configure Black as external formatter
- Enable Ruff as external linter
- Set MyPy type checker

## Dependency Management

```bash
# Add new dependency
uv add <package>

# Add dev dependency
uv add --dev <package>

# Update dependencies
uv lock --upgrade

# Remove dependency
uv remove <package>
```

## Troubleshooting

### Dependency Issues

```bash
# Re-sync environment
uv sync --dev

# Clear cache
uv cache clean

# Rebuild from scratch
rm -rf .venv
uv sync --dev
```

### Pre-commit Issues

```bash
# Reinstall hooks
pre-commit uninstall
pre-commit install

# Clear cache
pre-commit clean
```

## Project Structure

```
src/                    # Source code
├── models/            # Data models
├── services/          # Business logic
├── ui/               # User interface
├── config/           # Configuration
└── game/             # Game logic

tests/                 # Test files
├── unit/            # Unit tests
├── integration/     # Integration tests
└── contract/        # Contract tests

docs/                 # Documentation
```

## Getting Help

- Check this guide first
- Review existing code for patterns
- Run `uv run ruff check --help` for ruff options
- Check pre-commit documentation for hook configuration
