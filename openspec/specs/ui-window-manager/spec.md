# ui-window-manager Specification

## Purpose
TBD - created by archiving change remove-blank-root-window. Update Purpose after archive.
## Requirements
### Requirement: Hide Root Window After Game UI Creation
The BlokusApp class SHALL hide the root window after the game UI is successfully created.

**Location:** `src/blokus_game/main.py`, method `_show_game_ui()`

**Implementation:**
```python
self.root.withdraw()
```

**Rationale:** Prevents redundant blank window from appearing alongside the game window.

#### Scenario: Single Window After Mode Selection
- **Given** the application is launched and a game mode is selected
- **When** the game UI appears
- **Then** only one window should be visible (the game window)
- **And** the root window should be hidden

#### Scenario: Modal Dialogs Still Work
- **Given** the root window is hidden
- **When** a modal dialog is opened (help, quit, etc.)
- **Then** the dialog should appear correctly
- **And** the dialog should be properly parented

### Requirement: Preserve Window Hierarchy for Dialogs
The root window SHALL remain in memory (though hidden) to support modal dialog parent hierarchy.

**Implementation:** Use `withdraw()` instead of `destroy()`

**Rationale:** Modal dialogs depend on root window for proper centering and transient behavior.

#### Scenario: Dialog Proper Centering
- **Given** the game is running with hidden root window
- **When** a modal dialog is opened
- **Then** it should center relative to the game window
- **And** maintain proper modal behavior

### Requirement: Hide Root Window After UI is Ready
The root window SHALL be hidden ONLY AFTER the game UI window is fully created.

**Location:** Last line of `_show_game_ui()` method

**Rationale:** Prevents race conditions and ensures proper window creation sequence.

#### Scenario: No Race Conditions
- **Given** game mode is selected
- **When** `_show_game_ui()` executes
- **Then** UI components are created first
- **And** root window is hidden last
- **And** no intermediate state shows both windows
