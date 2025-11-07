# Fix Integration Test Errors

## Problem Statement

The integration tests in `tests/integration/test_ai_stress.py` and related files are failing due to API mismatches between test code and the actual GameState implementation. The tests use non-existent methods:

1. `GameState.initialize(n_players)` - This method does not exist in the actual GameState class
2. `GameState.advance_turn()` - This method is called but doesn't exist; the actual method is `next_turn()`
3. Variable scope errors - Variables used before assignment in closure contexts

## Root Cause Analysis

**Not a source code bug** - The GameState implementation is correct. The issue is that:
- Tests were written with incorrect API assumptions
- GameState uses a constructor-based initialization pattern, not an `initialize()` method
- GameState has `next_turn()` method, not `advance_turn()`
- Some tests have Python variable scope issues in nested functions

## Impact

- **7 tests failing** in test_ai_stress.py (100% failure rate)
- **Tests in other integration files** also affected
- Integration test suite is completely non-functional
- Cannot validate concurrent AI game behavior

## Solution Approach

This is a **test fix** task, not a source code change. The solution is to:

1. Replace `GameState.initialize(n_players)` with proper constructor initialization
2. Replace `GameState.advance_turn()` with `GameState.next_turn()`
3. Fix variable scope issues in test code
4. Update all affected integration test files

## Affected Files

- `tests/integration/test_ai_stress.py` (7 tests)
- `tests/integration/test_all_modes.py` (multiple tests)
- `tests/integration/test_game_performance.py` (TBD)
- `tests/integration/test_complete_game_flow.py` (TBD)

## Validation

All integration tests should pass after fixes are applied. The test suite should:
- Successfully run all concurrent AI stress tests
- Validate game state progression correctly
- Demonstrate proper memory isolation between games
