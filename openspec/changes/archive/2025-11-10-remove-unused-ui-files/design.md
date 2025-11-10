## Context
The blokus_game/ui directory contains several Python files that are no longer being used in the codebase. These files represent dead code that adds maintenance overhead and can confuse developers working on the UI system.

## Goals / Non-Goals
- Goals:
  - Remove unused UI components to simplify the codebase
  - Improve maintainability by reducing dead code
  - Make the UI module structure clearer and more focused
- Non-Goals:
  - No functional changes to the game
  - No changes to actively used UI components

## Decisions
- Decision: Remove four identified unused files from src/blokus_game/ui/
  - board_click_handler.py: No imports found, appears to be legacy click handling
  - spectator_mode_indicator.py: No imports found, spectator mode functionality not implemented
  - game_results.py: No imports found, game results handled elsewhere in main.py
  - test_keyboard_shortcuts.py: Test file incorrectly placed in src/ instead of tests/
- Alternatives considered:
  - Keep files for potential future use: Rejected due to maintenance overhead
  - Move files to archive/: Rejected as they serve no purpose
  - Refactor to make them useful: Rejected as current functionality is sufficient

## Risks / Trade-offs
- Risk: Hidden dependencies not found by grep search → Mitigation: Comprehensive testing after removal
- Risk: Files may be imported dynamically → Mitigation: Check main.py and key entry points
- Trade-off: Reduced code clarity if spectator mode is added later → Mitigation: Can re-implement if needed

## Migration Plan
1. Verify no active usage through comprehensive search
2. Remove files one by one with testing between each removal
3. Run full test suite and application verification
4. Commit changes with clear commit message explaining cleanup

## Open Questions
- Should test_keyboard_shortcuts.py be moved to tests/ or removed entirely?
- Are there any dynamic imports or runtime loading mechanisms not captured by static analysis?
