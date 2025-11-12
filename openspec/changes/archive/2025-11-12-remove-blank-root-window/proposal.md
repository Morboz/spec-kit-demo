# Remove Blank Root Window

## Summary

When launching the Blokus game with `uv run python -m blokus_game.main` and selecting a game mode, two windows appear:
1. A blank, unused root window (created during app initialization)
2. The actual game window (created after mode selection)

Users expect only one window - the game window. The blank root window should be hidden or removed.

## Problem

The issue occurs because:
1. `BlokusApp.__init__()` creates a root window (`self.root = tk.Tk()`) at line 50 of main.py
2. After game mode selection, `UIManager.show_game_ui()` creates a new Toplevel window for the game at line 134 of ui_manager.py
3. The original root window remains visible and unused

## Solution

Hide the root window after the game UI is successfully created by calling `self.root.withdraw()` in the `_show_game_ui()` method.

## Benefits

- Cleaner user experience - only one window visible
- Reduced window clutter
- Faster application startup perception
- Maintains window hierarchy for proper modal dialog behavior

## Technical Approach

**Option 1: Hide root window in `_show_game_ui()`**
- Pros: Simple, maintains window hierarchy
- Cons: Root window still exists (minimal overhead)

**Option 2: Destroy root window after game UI creation**
- Pros: Completely removes unused window
- Cons: May break modal dialogs that depend on root window

**Option 3: Create game window as main window instead of Toplevel**
- Pros: Most straightforward
- Cons: Requires larger refactoring of window management

**Chosen: Option 1** - Hide the root window with `withdraw()` as it provides the best balance of simplicity and functionality while preserving window hierarchy for future modal dialogs.

## Scope

- Modify `BlokusApp._show_game_ui()` to hide root window
- No changes to game logic or other UI components
- No changes to modal dialog behavior
- Backward compatible - existing functionality preserved

## Risk Assessment

**Low Risk**: Simple one-line change with no side effects
- Window hierarchy preserved for modal dialogs
- Game functionality unchanged
- Easy to revert if needed

## Testing

1. Launch game with `uv run python -m blokus_game.main`
2. Select any game mode
3. Verify only one window appears (game window)
4. Verify game functionality works normally
5. Verify modal dialogs (help, quit confirmation) work correctly

## Dependencies

None - this change is isolated and has no dependencies on other features or changes.

## Rollback Plan

If issues arise, simply remove the `self.root.withdraw()` line from `_show_game_ui()` to restore original behavior.
