# Fix Unit Test Failures

## Why
Running `uv run pytest tests/unit` revealed 7 failing tests out of 309 total tests. All failures were test issues, NOT source code defects. This needs to be fixed to ensure 100% test pass rate.

## What Changes
- Fixed test_ai_elapsed_time_tracking to use monkey-patching during calculation
- Fixed 6 test_ai_strategy_flip.py tests to use coordinates attribute in MockPiece
- All changes are in test files only - source code remains unchanged

## Problem
Running `uv run pytest tests/unit` revealed 7 failing tests out of 309 total tests:
- 1 test in test_ai_performance.py (test_ai_elapsed_time_tracking)
- 6 tests in test_ai_strategy_flip.py (all flip-related tests)

## Root Cause Analysis
All failures were test issues, NOT source code defects:

### test_ai_elapsed_time_tracking
- **Issue**: Test expected to retrieve elapsed time after calculation completed
- **Reality**: Source code sets `is_calculating=False` in `finally` block, causing `get_elapsed_calculation_time()` to return `None`
- **Test design flaw**: Assumed time would be available after calculation ended

### test_ai_strategy_flip.py (6 tests)
- **Issue**: MockPiece class used `positions` attribute
- **Reality**: Source code expects `coordinates` attribute on Piece objects
- **Test design flaw**: Mock objects didn't match the actual interface

## Solution
Fixed all 7 tests to properly validate the existing correct source code:

1. **test_ai_elapsed_time_tracking**: Used monkey-patching to track time during calculation instead of after
2. **test_ai_strategy_flip.py tests**: Changed all MockPiece classes to use `coordinates` instead of `positions`

## Result
- Before: 7 failed, 301 passed, 1 skipped
- After: 308 passed, 1 skipped (100% pass rate)
- Source code: No changes required - all logic was correct

## Files Modified
- tests/unit/test_ai_performance.py
- tests/unit/test_ai_strategy_flip.py

## Verification
All 308 unit tests now pass successfully.
