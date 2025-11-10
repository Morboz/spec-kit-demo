# Design: Remove Unused Model Files

## Architectural Context

The current `src/blokus_game/models/` directory contains 10 Python files, but analysis shows that 2 of them (`game_stats.py` and `turn_controller.py`) are only used in test files and have no production usage. This creates unnecessary complexity and potential maintenance overhead.

## Current State Analysis

### game_stats.py
- **Purpose**: Provides game statistics functionality
- **Production Usage**: None found
- **Test Usage**:
  - `tests/integration/test_spectate.py` - imports `create_game_statistics`
  - `tests/unit/test_game_stats.py` - dedicated test file for this module
- **Dependencies**: Minimal, standalone module

### turn_controller.py
- **Purpose**: Turn management and control logic
- **Production Usage**: None found
- **Test Usage**:
  - `tests/unit/test_turn_controller.py` - dedicated test file
  - `tests/unit/test_ai_edge_cases.py` - imports `TurnController, TurnState`
  - `tests/integration/test_ai_basic.py` - imports `TurnController, TurnState`
  - `tests/integration/test_spectate.py` - imports `TurnController, TurnState`
- **Dependencies**: Imports from other models but not imported by any production code

## Decision Rationale

### Why Remove These Files?
1. **Dead Code Elimination**: No production code imports these modules, indicating they are not part of the active application
2. **Simplified Mental Model**: Reduces the cognitive load when understanding the codebase architecture
3. **Maintenance Reduction**: Eliminates the need to maintain code that provides no runtime value
4. **Test Accuracy**: Prevents testing of implementation details that aren't actually used

### Alternative Considered and Rejected
- **Keep for Future Use**: Rejected because there's no clear roadmap or requirement indicating these will be needed
- **Move to tests directory**: Rejected because this would still maintain unused code and create confusion about what's being tested
- **Mark as deprecated**: Rejected because deprecation still leaves dead code in the codebase

## Implementation Strategy

### Phase 1: Analysis and Documentation
- Confirm usage patterns across the entire codebase
- Document all dependencies and imports
- Identify all test files that will need updates

### Phase 2: Test File Updates
- Remove or update tests that specifically test the unused modules
- Update integration tests that import functionality from these modules
- Ensure test coverage remains adequate for core functionality

### Phase 3: File Removal
- Remove the unused model files
- Update any documentation references
- Verify no broken imports remain

## Risk Mitigation

### Low Risk Assessment
- **Production Impact**: None - no production code imports these modules
- **Test Coverage**: Minimal - only affects tests of the unused functionality itself
- **Rollback Strategy**: Files can be restored from git if needed

### Validation Steps
1. Verify no production imports exist using `rg` and `grep`
2. Run full test suite before and after changes
3. Ensure build, linting, and type checking pass
4. Manual smoke test of main application functionality

## Success Criteria
- All tests pass after updates
- No broken imports in the codebase
- Application functionality unchanged
- Reduced complexity in models directory
- Documentation updated to reflect simplified structure
