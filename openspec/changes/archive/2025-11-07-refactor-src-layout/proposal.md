# Refactor to Proper Src Layout Structure

## Why
The current project structure does not follow Python's standard src layout convention. Source files are directly under `src/` without a package directory, and `pyproject.toml` is missing the required package configuration. This creates import issues and doesn't follow uv/Python packaging best practices.

## What Changes
- **Create proper package structure**: Move all source code from `src/` to `src/blokus_game/`
- **Update pyproject.toml**: Add proper src layout configuration with package directory mapping
- **Fix import statements**: Update all Python files to use package imports (`from blokus_game import ...`)
- **Update tests**: Fix test imports to reference the new package structure
- **Update configuration**: Adjust tool configurations (coverage, mypy, etc.) for new layout
- **Create separate branch**: All changes will be made on a feature branch for safety

## Impact
- **Affected specs**: `project-structure` (new capability for proper Python packaging)
- **Affected code**: All Python files in src/ and tests/ directories
- **Breaking change**: Yes - imports will change throughout the codebase
- **Tooling impact**: pytest, coverage, mypy, ruff configurations need updates

## Benefits
- Proper Python package structure following uv/PEP standards
- Cleaner separation between package and project files
- Better import resolution and IDE support
- Compliance with Python packaging best practices
- Improved maintainability and onboarding experience