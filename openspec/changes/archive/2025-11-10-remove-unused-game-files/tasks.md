# Tasks: Remove Unused Game Files

## Ordered Task List

### 1. Identify Dependent Tests
- [x] Search for all test files that import game_loop.py
- [x] Search for all test files that import ai_game_initializer.py
- [x] Search for all test files that import score_history.py
- [x] Document which tests need to be updated vs removed

### 2. Remove Unused Files
- [x] Delete `src/blokus_game/game/game_loop.py`
- [x] Delete `src/blokus_game/game/ai_game_initializer.py`
- [x] Delete `src/blokus_game/game/score_history.py`

### 3. Update Test Files
- [x] Remove or update tests in test_complete_score_system.py (removed entire file)
- [x] Remove or update tests in test_complete_game_flow.py (removed entire file)
- [x] Remove or update tests in test_turn_flow.py (removed GameLoop-specific tests)
- [x] Remove or update tests in test_complete_end_game_flow.py (removed entire file)
- [x] Remove or update tests in test_ai_basic.py (removed AIGameInitializer test class)
- [x] Remove any other test files that exclusively test deleted classes

### 4. Validation and Testing
- [x] Run `uv run ruff check .` to verify no import errors
- [x] Run `uv run mypy .` to verify type checking passes
- [x] Run `uv run pytest` to verify all tests pass
- [x] Start the application to verify it runs correctly
- [x] Test all game modes (Single AI, Three AI, Spectate, Multiplayer)

### 5. Code Quality Checks
- [x] Run `uv run black .` to ensure formatting
- [x] Run pre-commit hooks
- [x] Verify git status shows only expected changes

## Dependencies

**Dependencies**: None (can be completed independently)

**Blocking**: None

## Validation Criteria

### Success Criteria
- All three unused files are deleted
- No import errors in the application
- All tests pass after cleanup
- Application functionality remains unchanged
- Code quality checks pass

### Failure Criteria
- Import errors when running the application
- Broken test references
- Reduced application functionality
- Code quality check failures
