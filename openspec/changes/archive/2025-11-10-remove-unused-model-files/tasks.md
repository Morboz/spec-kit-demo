# Tasks: Remove Unused Model Files

## Implementation Tasks

### 1. Verify Usage Patterns (COMPLETED)
- [x] Comprehensive search of codebase for imports of `game_stats.py`
- [x] Comprehensive search of codebase for imports of `turn_controller.py`
- [x] Confirm no production (non-test) files import these modules
- [x] Document all test files that will be affected

### 2. Update Test Files
- [x] Remove or update `tests/unit/test_game_stats.py` (dedicated test file for unused module)
- [x] Remove or update `tests/unit/test_turn_controller.py` (dedicated test file for unused module)
- [x] Update `tests/integration/test_spectate.py` to remove `game_stats` imports
- [x] Update `tests/unit/test_ai_edge_cases.py` to remove `turn_controller` imports
- [x] Update `tests/integration/test_ai_basic.py` to remove `turn_controller` imports
- [x] Update `tests/integration/test_spectate.py` to remove `turn_controller` imports
- [x] Run test suite to ensure all tests still pass after updates

### 3. Remove Unused Model Files
- [x] Remove `src/blokus_game/models/game_stats.py`
- [x] Remove `src/blokus_game/models/turn_controller.py`
- [x] Update `src/blokus_game/models/__init__.py` if it references these files
- [x] Check for any other references in model initialization files

### 4. Validation and Quality Assurance
- [x] Run full test suite: `uv run pytest`
- [x] Run code quality checks: `uv run ruff check .` and `uv run black .`
- [x] Run type checking: `uv run mypy .`
- [x] Manual smoke test of all game modes (Single AI, Three AI, Spectate)
- [x] Verify application starts and runs without import errors
- [x] Check that build process completes successfully

### 5. Documentation Updates
- [x] Update any project documentation that references the removed files
- [x] Update `CLAUDE.md` if it contains references to the removed models
- [x] Verify `openspec/project.md` model structure section is accurate
- [x] Commit changes with appropriate commit message

## Dependencies

- **Task 2 depends on Task 1**: Must verify usage patterns before updating tests
- **Task 3 depends on Task 2**: Must update tests before removing files to avoid broken test suite
- **Task 4 depends on Task 3**: Must remove files before running final validation
- **Task 5 depends on Task 4**: Must validate functionality before finalizing documentation

## Notes

- This is a low-risk change as no production code imports these modules
- Focus on maintaining test coverage for core functionality while removing tests of unused code
- Keep git history clean by removing test files that only test unused functionality
- Validate thoroughly to ensure no hidden dependencies were missed
