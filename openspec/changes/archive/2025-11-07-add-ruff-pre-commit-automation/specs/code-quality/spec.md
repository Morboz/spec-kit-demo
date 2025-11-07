# code-quality Specification

## Purpose
Introduce modern Python code quality tooling with ruff and pre-commit automation to improve developer experience and code consistency.

## What Changes
- Replace flake8 with ruff for faster linting and auto-fixing
- Add pre-commit hooks for automated code quality checks
- Integrate ruff, black, and mypy into pre-commit workflow
- Update project configuration and documentation
- Maintain full backward compatibility with existing tools

## Why
The current code quality setup has several limitations:
1. **Manual process**: Developers must remember to run flake8, black, and mypy manually
2. **Performance**: flake8 is slower than modern alternatives like ruff
3. **Consistency**: No automated enforcement leads to inconsistent code style
4. **Developer experience**: Manual corrections are time-consuming and error-prone

Ruff provides 10-100x faster linting with auto-fixing capabilities, while pre-commit hooks ensure code quality standards are enforced automatically before commits. This improves both developer productivity and code consistency across the project.

## ADDED Requirements

### Requirement: Ruff linting and formatting integration
Ruff SHALL replace flake8 as the primary Python linter, providing fast code quality checks and automatic fixes while maintaining compatibility with black formatting standards.

#### Scenario: Ruff automatically detects and fixes code issues
**Given:** A developer modifies Python source code
**When:** `uv run ruff check` is executed or pre-commit hooks run
**Then:** Ruff detects code style issues, potential bugs, and import problems
**Expected:** Auto-fixable issues are resolved with `uv run ruff check --fix`, maintaining 88-character line length and Python 3.11+ compatibility

### Requirement: Pre-commit hooks automation
Pre-commit hooks SHALL automatically run code quality checks before each git commit to ensure code quality standards are enforced.

#### Scenario: Pre-commit hooks run before git commit
**Given:** A developer attempts to commit changes with `git commit`
**When:** Pre-commit hooks execute
**Then:** Ruff linting, black formatting, and mypy type checking run automatically
**Expected:** Commit is blocked if critical issues exist, auto-fixable issues are resolved, and clear feedback is provided

### Requirement: Development workflow integration
The new tooling SHALL integrate seamlessly with the existing uv-based development workflow.

#### Scenario: New developer sets up development environment
**Given:** A fresh clone of the repository
**When:** Developer runs `uv sync --dev` and `pre-commit install`
**Then:** All necessary tools are installed and pre-commit hooks are configured
**Expected:** `pre-commit run --all-files` validates the entire codebase and documentation explains the complete workflow

### Requirement: Backward compatibility with existing tools
The transition to ruff SHALL maintain full backward compatibility with existing development processes and tooling.

#### Scenario: Existing development workflow remains functional
**Given:** Current black and mypy configuration
**When:** Ruff is added to the project
**Then:** Black formatting (88 characters) and mypy strict type checking continue unchanged
**Expected:** No breaking changes to existing CI/CD pipelines or development workflows

### Requirement: Performance and developer experience
Ruff and pre-commit hooks SHALL provide superior performance and developer experience compared to the current flake8 setup.

#### Scenario: Fast feedback during development
**Given:** Typical code changes in a single file
**When:** Ruff checks are executed
**Then:** Results are returned in under 200ms
**Expected:** Pre-commit hooks complete in under 2 seconds for small commits, with 80%+ of issues auto-fixable

## MODIFIED Requirements

### Requirement: Code quality tools configuration
The project configuration SHALL be updated to include ruff settings while removing flake8 configuration.

#### Scenario: Updated pyproject.toml configuration
**Given:** Existing pyproject.toml with flake8 configuration
**When:** Configuration is updated
**Then:** `[tool.ruff]` section replaces `[tool.flake8]` section with equivalent rules
**Expected:** Pre-commit configuration is added in separate `.pre-commit-config.yaml` file

### Requirement: Development dependencies
Development dependencies SHALL be updated to include ruff and pre-commit while removing flake8.

#### Scenario: Updated dependency management
**Given:** Current `[project.optional-dependencies]` with flake8
**When:** Dependencies are updated
**Then:** `ruff>=0.1.0` and `pre-commit>=3.0.0` are added, flake8 is removed
**Expected:** Black, mypy, and pytest dependencies remain unchanged