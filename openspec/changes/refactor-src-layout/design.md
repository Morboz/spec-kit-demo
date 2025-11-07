## Context
The current project structure has Python files directly under `src/` without a package directory. This violates Python packaging standards and creates import issues. The project needs to be migrated to proper src layout where all source code lives under `src/blokus_game/` with proper `__init__.py` files.

## Goals / Non-Goals
- Goals: Migrate to standard Python src layout, fix all imports, update tooling configurations
- Non-Goals: Change functionality, refactor architecture, modify game logic

## Decisions
- Decision: Use `blokus_game` as package name (matches project name `blokus-step-by-step`)
- Rationale: Clear, descriptive, follows Python naming conventions
- Decision: Perform migration on separate branch
- Rationale: Safety, allows review before merging to main
- Decision: Update all import statements to use package imports
- Rationale: Proper Python package structure and explicit imports

## Migration Strategy
1. Create new package structure under `src/blokus_game/`
2. Move all source files maintaining directory structure
3. Add `__init__.py` files to make directories proper Python packages
4. Update `pyproject.toml` with proper package configuration
5. Fix all import statements throughout codebase
6. Update test configurations and imports
7. Update tooling configurations (coverage, mypy, etc.)
8. Validate all tests pass with new structure

## Risks / Trade-offs
- Risk: Import breaking changes throughout codebase
- Mitigation: Systematic update of all imports and comprehensive testing
- Risk: Tooling configuration errors
- Mitigation: Update all tool configs and validate with test runs
- Trade-off: Temporary complexity during migration vs long-term maintainability

## Open Questions
- Should we use `blokus_game` or `blokus` as package name? (leaning toward `blokus_game`)
- Any external tools/scripts that reference current structure that need updates?