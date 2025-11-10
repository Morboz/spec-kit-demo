# Remove Unused Model Files

## Why
Remove unused model files that have no production dependencies to simplify the codebase architecture and eliminate maintenance overhead for dead code. This improves code maintainability and reduces confusion for developers working with the codebase.

## What Changes
- Remove two unused model files from `src/blokus_game/models/`
- Update all test files that import from these modules
- Update project documentation to reflect the simplified structure

## Summary
Remove two unused model files from `src/blokus_game/models/` that are only referenced in test files and have no production usage:

- `game_stats.py` - Only used in test files, provides game statistics functionality not utilized by the main application
- `turn_controller.py` - Only used in test files, appears to be legacy turn management code superseded by other components

## Rationale
- **Code Cleanup**: Remove dead code to improve maintainability and reduce confusion
- **Simplified Architecture**: Streamline the models directory to only include actively used components
- **Test Isolation**: Eliminate the risk of testing implementation details that aren't part of the production codebase
- **Build Efficiency**: Reduce unnecessary imports and compilation overhead

## Impact Analysis
- **No Breaking Changes**: These files have no production imports, so removal will not affect the main application
- **Test Updates**: Will require updates to test files that import these modules
- **Documentation**: Project documentation may need minor updates to reflect the simplified model structure

## Files to be Removed
1. `src/blokus_game/models/game_stats.py`
2. `src/blokus_game/models/turn_controller.py`

## Test Files Requiring Updates
- `tests/integration/test_spectate.py`
- `tests/unit/test_game_stats.py`
- `tests/unit/test_turn_controller.py`
- `tests/unit/test_ai_edge_cases.py`
- `tests/integration/test_ai_basic.py`

## Validation Criteria
- All existing production functionality remains intact
- Test suite updated to reflect removal of unused components
- Build and linting pass without errors
- No remaining imports reference the removed files
