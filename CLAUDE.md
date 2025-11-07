<!-- OPENSPEC:START -->
# OpenSpec Instructions

These instructions are for AI assistants working in this project.

Always open `@/openspec/AGENTS.md` when the request:
- Mentions planning or proposals (words like proposal, spec, change, plan)
- Introduces new capabilities, breaking changes, architecture shifts, or big performance/security work
- Sounds ambiguous and you need the authoritative spec before coding

Use `@/openspec/AGENTS.md` to learn:
- How to create and apply change proposals
- Spec format and conventions
- Project structure and guidelines

Keep this managed block so 'openspec update' can refresh the instructions.

<!-- OPENSPEC:END -->

# blokus-step-by-step Development Guidelines

Auto-generated from all feature plans. Last updated: 2025-10-30

## Active Technologies
- Python 3.11+ + tkinter (standard library), pytest (testing) (001-fix-piece-placement)
- N/A (in-memory game state, no persistence required) (001-fix-piece-placement)
- In-memory game state (no persistence required) (003-fix-ai-player)

- Python 3.11+ (portable, rapid prototyping, good game libraries) + tkinter (standard library, no external dependencies, sufficient for 2D board game) (001-blokus-multiplayer)

## Project Structure

```text
src/
tests/
```

## Commands

```bash
# Development setup
uv sync --dev              # Install all dependencies
pre-commit install         # Install git hooks

# Code quality checks
uv run ruff check .        # Run ruff linting
uv run ruff check --fix .  # Auto-fix ruff issues
uv run black .             # Format code with black
uv run mypy .              # Run type checking
pre-commit run --all-files # Run all pre-commit hooks

# Testing
uv run pytest              # Run all tests
uv run pytest tests/unit/ # Run unit tests only
uv run pytest tests/integration/ # Run integration tests only
```

## Code Style

- **Line Length**: 88 characters (Black default)
- **Python Version**: 3.11+ (minimum version check enforced)
- **Formatting**: Black for automatic formatting
- **Linting**: Ruff with auto-fixing (replaces flake8)
- **Type Hints**: Strict mypy enforcement
- **Import Sorting**: Ruff's isort integration
- **Pre-commit**: Automated hooks run before each commit

**Quality Workflow**:
1. Code changes trigger pre-commit hooks automatically
2. Ruff fixes auto-fixable issues instantly
3. Black ensures consistent formatting
4. Mypy validates type annotations
5. Commit only succeeds if all checks pass

## Recent Changes
- 003-fix-ai-player: Added Python 3.11+ + tkinter (standard library), pytest (testing)
- 002-ai-battle-mode: Added Python 3.11+ + tkinter (standard library)
- 001-fix-piece-placement: Added Python 3.11+ + tkinter (standard library), pytest (testing)


<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
