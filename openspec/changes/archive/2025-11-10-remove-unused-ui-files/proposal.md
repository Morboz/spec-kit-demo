# Change: Remove unused UI files from blokus_game/ui directory

## Why
Remove dead code to improve maintainability, reduce confusion, and simplify the codebase by eliminating unused UI components that are no longer referenced or needed.

## What Changes
- Remove `board_click_handler.py` - Unused board click handling logic
- Remove `spectator_mode_indicator.py` - Unused spectator mode UI components
- Remove `game_results.py` - Unused game results display window
- Remove `test_keyboard_shortcuts.py` - Test-only file that should be in tests/
- Update any remaining references or documentation

## Impact
- Affected specs: None (these are unused files)
- Affected code: UI module structure reduced by 4 files
- Dependencies: No active dependencies on these files
- Risk: Low - files are confirmed unused
