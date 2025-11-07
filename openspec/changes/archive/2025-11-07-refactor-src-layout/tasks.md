## 1. Preparation
- [x] 1.1 Create feature branch `refactor/src-layout-migration`
- [x] 1.2 Backup current working state
- [x] 1.3 Document current import structure for reference

## 2. Create Package Structure
- [x] 2.1 Create `src/blokus_game/` directory
- [x] 2.2 Create `__init__.py` in `src/blokus_game/`
- [x] 2.3 Create `__init__.py` files in all subdirectories (game, ui, models, services, config)
- [x] 2.4 Move all source files maintaining directory structure
  - [x] 2.4.1 Move `src/main.py` → `src/blokus_game/main.py`
  - [x] 2.4.2 Move `src/game/` → `src/blokus_game/game/`
  - [x] 2.4.3 Move `src/ui/` → `src/blokus_game/ui/`
  - [x] 2.4.4 Move `src/models/` → `src/blokus_game/models/`
  - [x] 2.4.5 Move `src/services/` → `src/blokus_game/services/`
  - [x] 2.4.6 Move `src/config/` → `src/blokus_game/config/`

## 3. Update pyproject.toml
- [x] 3.1 Add package directory configuration: `[tool.setuptools.package-dir]`
- [x] 3.2 Update coverage source path: `source = ["src/blokus_game"]`
- [x] 3.3 Validate pyproject.toml syntax

## 4. Fix Import Statements
- [x] 4.1 Update imports in `src/blokus_game/main.py`
- [x] 4.2 Update imports in `src/blokus_game/game/` modules
- [x] 4.3 Update imports in `src/blokus_game/ui/` modules
- [x] 4.4 Update imports in `src/blokus_game/models/` modules
- [x] 4.5 Update imports in `src/blokus_game/services/` modules
- [x] 4.6 Update imports in `src/blokus_game/config/` modules

## 5. Update Test Imports
- [x] 5.1 Update imports in `tests/unit/` test files
- [x] 5.2 Update imports in `tests/integration/` test files
- [x] 5.3 Update test configuration files if needed

## 6. Update Tooling Configurations
- [x] 6.1 Update mypy configuration for new package structure
- [x] 6.2 Update ruff configuration if needed
- [x] 6.3 Update any other tool configurations

## 7. Validation
- [x] 7.1 Run `uv run ruff check .` - should pass
- [x] 7.2 Run `uv run black .` - should format correctly
- [x] 7.3 Run `uv run mypy .` - should pass type checking
- [x] 7.4 Run `uv run pytest` - all tests should pass
- [x] 7.5 Run `uv run pytest --cov=src/blokus_game` - coverage should work
- [x] 7.6 Test manual import of package: `python -c "import blokus_game"`

## 8. Documentation Updates
- [x] 8.1 Update README.md if it references file structure
- [x] 8.2 Update any development documentation
- [x] 8.3 Update CLAUDE.md project structure section

## 9. Cleanup
- [x] 9.1 Remove empty old directories
- [x] 9.2 Validate no old imports remain
- [x] 9.3 Final test run with all checks passing