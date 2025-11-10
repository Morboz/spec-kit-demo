# Design: Remove Unused Game Files

## Architecture Impact

### Current Architecture
The `src/blokus_game/game/` directory contains core game logic modules. Three of these modules are only used by tests:

1. **game_loop.py** - GameLoop class for managing game progression
2. **ai_game_initializer.py** - AIGameInitializer for AI game setup
3. **score_history.py** - ScoreHistory for tracking score changes

### Target Architecture
After removal, the `game/` directory will contain only actively used modules:
- error_handler.py
- game_setup.py
- placement_handler.py
- rules.py
- scoring.py
- turn_manager.py
- turn_validator.py
- end_game_detector.py
- winner_determiner.py
- __init__.py

### Implementation Strategy

#### File Deletion Approach
1. **Direct Deletion**: Remove the three unused files completely
2. **Test Cleanup**: Update or remove tests that depend on deleted modules
3. **Validation**: Ensure no remaining imports or references

#### Test Migration Strategy
Since these files are only used by tests, we need to handle the test dependencies:

**Option A: Remove Dependent Tests**
- Remove tests that exclusively test the unused classes
- Keep tests that verify actual application functionality

**Option B: In-line Test Logic**
- Move essential test logic directly into test files
- Replace class calls with equivalent functionality

**Chosen Approach**: **Option A** - Remove tests that exclusively verify unused classes, as they don't provide value for production code validation.

### Risk Assessment

#### Low Risk
- No production code changes
- Application functionality unchanged
- Clear scope boundaries

#### Medium Risk
- Test removal might reduce coverage temporarily
- Need to ensure no hidden dependencies

#### Mitigation Strategies
1. Comprehensive test run after deletion
2. Verify application builds and runs correctly
3. Check for any runtime import errors

## Dependencies Analysis

### External Dependencies
None of the three files have unique external dependencies that would be lost.

### Internal Dependencies
- **game_loop.py** depends on:
  - end_game_detector.py (used by other modules)
  - scoring.py (used by main.py)
  - turn_manager.py (used by main.py)
  - winner_determiner.py (used by UI components)

- **ai_game_initializer.py** depends on:
  - Models and UI components (all used elsewhere)

- **score_history.py** depends on:
  - models.game_state.py (used extensively)

### Test Dependencies
The following test files will need updates:
- test_complete_score_system.py
- test_complete_game_flow.py
- test_turn_flow.py
- test_complete_end_game_flow.py
- test_ai_basic.py

## Implementation Plan

1. **Phase 1**: Remove the three unused files
2. **Phase 2**: Update or remove dependent tests
3. **Phase 3**: Validate application functionality
4. **Phase 4**: Run full test suite

### Validation Strategy
- Application builds without import errors
- All existing functionality works
- No test failures unrelated to removed code
- Coverage metrics remain acceptable
