# Add Ruff and Pre-commit Automation

## Overview
This proposal introduces ruff as a modern Python linter/formatter and pre-commit hooks to automate code quality checks before commits. The change will replace the existing flake8 setup while maintaining compatibility with black formatting and mypy type checking.

## Why
The current code quality setup has several limitations:
1. **Manual process**: Developers must remember to run flake8, black, and mypy manually
2. **Performance**: flake8 is slower than modern alternatives like ruff
3. **Consistency**: No automated enforcement leads to inconsistent code style
4. **Developer experience**: Manual corrections are time-consuming and error-prone

Ruff provides 10-100x faster linting with auto-fixing capabilities, while pre-commit hooks ensure code quality standards are enforced automatically before commits. This improves both developer productivity and code consistency across the project.

## What Changes
- Replace flake8 with ruff for faster linting and auto-fixing
- Add pre-commit hooks for automated code quality checks
- Integrate ruff, black, and mypy into pre-commit workflow
- Update project configuration and documentation
- Maintain full backward compatibility with existing tools

## Problem Statement
The current code quality setup uses separate tools (black, flake8, mypy) that must be run manually. There is no automated enforcement of code quality standards before commits, leading to:

- Inconsistent code style between commits
- Manual effort to run all quality checks
- Potential for linting issues to reach the repository
- No automated formatting before commits

## Proposed Solution
1. **Replace flake8 with ruff** - Modern, fast Python linter that can handle many flake8 rules plus additional checks
2. **Add pre-commit hooks** - Automated checks that run before each commit
3. **Integrate with uv workflow** - Ensure compatibility with existing uv-based development setup
4. **Maintain existing tooling** - Keep black and mypy, but integrate them into pre-commit flow

## Benefits
- **Speed**: Ruff is 10-100x faster than flake8
- **Automation**: Pre-commit hooks ensure code quality before commits
- **Developer Experience**: Automatic formatting and linting on save/stage
- **Consistency**: Enforced code style across all contributions
- **Integration**: Seamless uv compatibility

## Scope
- Add ruff configuration to pyproject.toml
- Replace flake8 with ruff in dev dependencies
- Add .pre-commit-config.yaml configuration
- Integrate black, ruff, and mypy into pre-commit hooks
- Update documentation and development workflows