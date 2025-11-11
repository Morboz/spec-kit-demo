# Remove Unused Game Files

## Summary

Remove three unused game files that are only referenced by tests but not used in the main application flow:
- `game_loop.py` - GameLoop class not used by main application
- `ai_game_initializer.py` - AIGameInitializer class not used by main application
- `score_history.py` - ScoreHistory class not used by main application

## Why

The codebase contains three files in `src/blokus_game/game/` that are only referenced by test files but have no actual usage in the main application flow. These files represent dead code that adds maintenance burden and technical debt.

### Current Issues
1. **game_loop.py**: Contains GameLoop class that manages game loops, but main.py implements its own game loop logic
2. **ai_game_initializer.py**: Contains AIGameInitializer class for AI game setup, but main.py handles AI initialization directly
3. **score_history.py**: Contains ScoreHistory class for tracking score changes, but main application doesn't use score history features

### Business Impact
- **Maintenance Cost**: Dead code requires unnecessary maintenance
- **Code Quality**: Unused files confuse developers about actual architecture
- **Testing Complexity**: Tests depend on code that isn't used in production
- **Build Time**: Unused files slightly increase module loading time

## Out of Scope

- Refactoring main.py to use these classes instead of direct implementation
- Creating replacement functionality
- Modifying the game logic or architecture
- Adding new features that might use these classes

## What Changes

1. Three unused files are deleted from `src/blokus_game/game/`
2. All tests that depend on these files are updated or removed
3. Application functionality remains unchanged
4. All tests pass after deletion
5. Codebase builds successfully with no import errors

## Success Criteria

- Three unused files are deleted from `src/blokus_game/game/`
- All tests that depend on these files are updated or removed
- Application functionality remains unchanged
- All tests pass after deletion
- Codebase builds successfully with no import errors
