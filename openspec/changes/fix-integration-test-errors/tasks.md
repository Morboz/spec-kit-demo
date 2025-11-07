# Tasks: Fix Integration Test Errors

## Task List

### 1. Fix test_ai_stress.py
**Status:** Pending
**Priority:** High
**Effort:** Medium

Fix all 7 failing tests in test_ai_stress.py:
- Replace `game_state.initialize(n)` with proper GameState initialization using constructor and `add_player()`
- Replace `game_state.advance_turn()` with `game_state.next_turn()`
- Fix variable scope error for `games_completed` in `test_system_stability_under_prolonged_load`
- Ensure all test methods work correctly

**Validation:** Run `uv run pytest tests/integration/test_ai_stress.py -v`

### 2. Fix test_all_modes.py
**Status:** Pending
**Priority:** High
**Effort:** Medium

Fix all tests that use the incorrect GameState API:
- Fix `test_game_state_isolation_between_modes`
- Fix `test_complete_single_ai_game_flow`
- Fix `test_complete_three_ai_game_flow`
- Fix `test_spectate_mode_fully_autonomous`
- Any other affected tests

**Validation:** Run `uv run pytest tests/integration/test_all_modes.py -v`

### 3. Fix other integration test files
**Status:** Pending
**Priority:** Medium
**Effort:** TBD

Check and fix:
- `tests/integration/test_game_performance.py`
- `tests/integration/test_complete_game_flow.py`

**Validation:** Run all affected test files

### 4. Run full integration test suite
**Status:** Pending
**Priority:** High
**Effort:** Low

Execute complete integration test suite to ensure all fixes work:
- Run all tests in `tests/integration/`
- Verify no new failures introduced
- Confirm test coverage is maintained

**Validation:** `uv run pytest tests/integration/ -v`

## Dependencies

- Task 1 must complete before Task 4
- Task 2 can run in parallel with Task 1
- Task 3 depends on understanding from Tasks 1-2

## Estimated Time

- Total: 2-3 hours
- Task 1: 1 hour
- Task 2: 1 hour
- Task 3: 30 minutes
- Task 4: 30 minutes
