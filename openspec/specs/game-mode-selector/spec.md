# Game Mode Selector Capability - Specification

## Overview
This specification defines the UnifiedGameModeSelector component that provides a single dialog for selecting all game modes (AI and PvP) with their respective configurations.

## Requirements

### Requirement: Unified Mode Selection Dialog
The system SHALL provide a single unified dialog that allows users to select any game mode (AI or PvP) and configure its settings in one interface.

**Type:** ADDED
**Rationale:** Eliminates the need for multiple sequential dialogs and improves user experience by showing all options at once.

#### Scenario: Single Dialog Shows All Modes
- **Given** the game mode selector is invoked
- **When** the dialog appears
- **Then** it displays options for:
  - Single AI (human vs AI)
  - Three AI (human vs 3 AI)
  - Spectate (AI vs AI)
  - PvP Local (2-4 human players)

### Requirement: Dynamic Configuration UI
The selector SHALL dynamically show configuration options based on the selected mode.

**Type:** ADDED
**Behavior:**
- **AI Modes (Single AI, Three AI):** Show difficulty selector
- **Spectate Mode:** Show info text (no configuration needed)
- **PvP Mode:** Show player count and player name inputs
- **All Modes:** Show common settings (board size, color scheme)

#### Scenario: AI Mode Shows Difficulty
- **Given** the selector dialog
- **When** user selects "Single AI" mode
- **Then** the dialog shows:
  - Difficulty selection (Easy, Medium, Hard)
  - Common settings (board size, color scheme)

#### Scenario: PvP Mode Shows Player Configuration
- **Given** the selector dialog
- **When** user selects "PvP Local" mode
- **Then** the dialog shows:
  - Player count selector (2-4 players)
  - Player name inputs (based on count)
  - Common settings (board size, color scheme)

#### Scenario: Spectate Mode Shows Minimal UI
- **Given** the selector dialog
- **When** user selects "Spectate" mode
- **Then** the dialog shows:
  - Informational text about spectate mode
  - Common settings (board size, color scheme)
  - No difficulty selector

### Requirement: Mode-Specific Option Visibility
The selector SHALL conditionally display relevant options and hide irrelevant ones based on selected mode.

**Type:** ADDED
**UI States:**
| Mode | Difficulty | Player Count | Player Names | Common Settings |
|------|------------|--------------|--------------|-----------------|
| Single AI | ✓ | ✗ | ✗ | ✓ |
| Three AI | ✓ | ✗ | ✗ | ✓ |
| Spectate | ✗ | ✗ | ✗ | ✓ |
| PvP Local | ✗ | ✓ | ✓ | ✓ |

#### Scenario: Difficulty Hidden for PvP
- **Given** PvP Local mode is selected
- **When** the dialog renders
- **Then** the difficulty selector is not visible

#### Scenario: Player Configuration Hidden for AI
- **Given** Single AI mode is selected
- **When** the dialog renders
- **Then** player count and name inputs are not visible

### Requirement: Form Validation
The selector SHALL validate user inputs before allowing game start.

**Type:** ADDED
**Validation Rules:**
- PvP mode: All player names must be non-empty
- All modes: Board size must be valid (10-30)
- All modes: Color scheme must be selected

#### Scenario: Validation Prevents Empty Player Names
- **Given** PvP mode with 3 players
- **When** player name for Player 2 is empty
- **Then** the "Start Game" button is disabled or shows error

#### Scenario: Validation Allows Valid Configuration
- **Given** Single AI mode with Medium difficulty
- **When** all fields are properly filled
- **Then** the "Start Game" button is enabled

### Requirement: Result Configuration Object
The selector SHALL return a structured configuration object that can be used to initialize the game.

**Type:** ADDED
**Result Schema:**
```python
{
    "mode_type": str,           # "single_ai", "three_ai", "spectate", "pvp_local"
    "difficulty": str | None,   # "Easy", "Medium", "Hard" (for AI modes)
    "player_count": int | None, # 2-4 (for PvP mode)
    "player_names": list[str] | None,  # (for PvP mode)
    "board_size": int,          # 10-30
    "color_scheme": str,        # "default", "pastel", "vibrant", "high_contrast"
    "show_grid": bool,
    "show_coordinates": bool
}
```

#### Scenario: Single AI Configuration Returned
- **Given** Single AI mode with Hard difficulty selected
- **When** user clicks "Start Game"
- **Then** the returned object contains:
  ```python
  {
      "mode_type": "single_ai",
      "difficulty": "Hard",
      "player_count": None,
      "player_names": None,
      "board_size": 20,
      ...
  }
  ```

#### Scenario: PvP Configuration Returned
- **Given** PvP Local mode with 3 players and custom names
- **When** user clicks "Start Game"
- **Then** the returned object contains:
  ```python
  {
      "mode_type": "pvp_local",
      "difficulty": None,
      "player_count": 3,
      "player_names": ["Alice", "Bob", "Charlie"],
      "board_size": 20,
      ...
  }
  ```

### Requirement: UnifiedGameModeSelector Class
The system SHALL provide a UnifiedGameModeSelector class with the following interface.

**Type:** ADDED
**Class:** `UnifiedGameModeSelector`
**Location:** `src/blokus_game/ui/unified_game_mode_selector.py`

**Methods:**
- `__init__(parent: tk.Widget | None, callback: Callable | None)`
- `show() -> dict | None` - Display dialog and return configuration
- `create_dialog() -> None` - Build the UI (private)
- `on_mode_changed() -> None` - Handle mode selection change
- `on_start_clicked() -> None` - Handle start button click
- `on_cancel_clicked() -> None` - Handle cancel button click

#### Scenario: Selector Created with Parent
- **Given** a tkinter root window
- **When** creating UnifiedGameModeSelector(root, callback)
- **Then** it initializes with parent window and callback function

#### Scenario: Selector Shows Dialog
- **Given** a UnifiedGameModeSelector instance
- **When** calling show()
- **Then** it displays the dialog and blocks until user responds

### Requirement: Convenience Function
The system SHALL provide a convenience function for showing the unified selector.

**Type:** ADDED
**Function:**
```python
def show_unified_game_mode_selector(
    parent: tk.Widget | None = None,
    callback: Callable | None = None
) -> dict | None
```

**Location:** `src/blokus_game/ui/unified_game_mode_selector.py`

**Rationale:** Provides simple API for launching the selector without needing to instantiate the class directly.

#### Scenario: Convenience Function Displays Dialog
- **Given** a tkinter root window
- **When** calling show_unified_game_mode_selector(root, callback)
- **Then** it creates a selector instance, shows the dialog, and returns the result

## MODIFIED Requirements

None.

## REMOVED Requirements

None.

## Technical Implementation Details

### UI Layout
The dialog should have a logical flow:
1. **Header:** "Select Game Mode"
2. **Mode Selection:** Radio buttons for 4 modes
3. **Configuration Area:** Dynamically shown based on mode
4. **Common Settings:** Board size, color scheme, options
5. **Action Buttons:** Start Game, Cancel

### State Management
- Track selected mode in StringVar
- Track configuration values in respective variables
- Update UI visibility based on mode selection
- Validate inputs before enabling start button

### Callback Integration
- Support optional callback function
- Callback receives (mode_type, config_dict) on successful selection
- Support cancellation (returns None)

### Tkinter Components Required
- Radiobutton widgets for mode selection
- LabelFrame containers for organized sections
- StringVar/IntVar for form state
- Spinbox for numeric inputs (board size, player count)
- Entry widgets for player names
- Combobox for color scheme
- Checkbutton for boolean options
- Button widgets for actions

## Backward Compatibility
- Existing GameModeSelector remains available (for backward compatibility)
- New selector is additive - doesn't remove existing functionality
- Command-line --spectate flag continues to work
- Existing game setup flow preserved for non-UI usage

## Testing Strategy
- Unit tests for UnifiedGameModeSelector class
- Integration tests with GameSetupManager
- Validation tests for all mode configurations
- UI tests to verify dynamic behavior (if possible)

## References
- Base: Existing GameModeSelector in `src/blokus_game/ui/game_mode_selector.py`
- Integration: GameSetupManager in `src/blokus_game/managers/game_setup_manager.py`
- Model: GameMode specification (delta)
