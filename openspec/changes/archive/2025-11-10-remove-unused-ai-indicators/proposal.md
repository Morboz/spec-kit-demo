# Remove Unused AI Indicator Components

## Summary

Remove two unused AI indicator UI components that are not imported or used anywhere in the main application code.

## Why

These AI indicator components were developed but never integrated into the main application. They represent dead code that:

1. **Adds maintenance overhead** - Files must be maintained even though unused
2. **Creates confusion** - Developers might waste time investigating unused components
3. **Violates clean code principles** - Dead code should be removed rather than left in place
4. **Current functionality is sufficient** - AI thinking feedback is already handled by `current_player_indicator.py`

The current implementation provides adequate AI feedback through the existing `show_ai_thinking()` and `hide_ai_thinking()` methods, making these components redundant.

## What Changes

This change removes two unused UI components and updates documentation references:

1. **File Removals**:
   - Delete `src/blokus_game/ui/ai_thinking_indicator.py` (487 lines)
   - Delete `src/blokus_game/ui/ai_difficulty_indicator.py` (432 lines)

2. **Documentation Updates**:
   - Remove references from `openspec/project.md` UI structure
   - Clean up `docs/constitution_validation.md` component listings
   - Update `specs/002-ai-battle-mode/tasks.md` file structure

3. **No Code Changes Required**:
   - No import statements to remove (files were never imported)
   - No functionality to replace (current implementation handles AI feedback)
   - No breaking changes to existing code

## Files to Remove

- `src/blokus_game/ui/ai_thinking_indicator.py` - Enhanced visual feedback for AI thinking state
- `src/blokus_game/ui/ai_difficulty_indicator.py` - UI components for displaying AI difficulty levels

## Analysis

**Usage Check Results:**
- `ai_thinking_indicator.py`: Only referenced in documentation files, not imported by any application code
- `ai_difficulty_indicator.py`: Only referenced in documentation files, not imported by any application code
- `main.py`: Does not import or use either component
- Current AI thinking feedback is handled by `current_player_indicator.py` with `show_ai_thinking()` and `hide_ai_thinking()` methods

**Rationale:**
- These components are legacy code that was never integrated
- They add maintenance overhead without providing value
- Current AI feedback is already implemented elsewhere
- Removing unused code improves codebase cleanliness

## Impact

- **No functional impact** - components are not used
- **Reduced maintenance** - fewer files to maintain
- **Cleaner codebase** - removes dead code

## Alternatives Considered

- **Keep the files**: No benefit, adds maintenance overhead
- **Integrate the files**: Would require significant refactoring; current implementation is already working
- **Mark as deprecated**: Still leaves unused code in codebase

## Recommendation

Remove both files as they provide no value and are not used by the application.
