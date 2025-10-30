# Quickstart Guide: Blokus Game

**Feature**: Blokus Local Multiplayer Game
**Phase**: 10 - Polish & Cross-Cutting Concerns (Complete)
**Date**: 2025-10-30

## Overview

This guide will help you understand and run the Blokus local multiplayer game within 10 minutes. The Blokus game is a strategy board game for 2-4 players where you place geometric pieces on a 20x20 board, trying to claim territory while following specific placement rules.

**Phase 10 Features**: Complete game with configuration presets, keyboard shortcuts, restart functionality, optimized rendering, and comprehensive error handling.

## What is Blokus?

Blokus is a turn-based strategy board game featuring:
- **2-4 players** on a single device
- **21 unique pieces** per player (geometric shapes made of 1-5 squares)
- **20x20 board** where pieces are placed
- **Core rule**: Your pieces can only touch your own pieces at corners (diagonally), never at edges
- **First move rule**: Each player's first piece must touch their corner
- **Scoring**: +1 per placed square, -5 per unplaced piece, +15 bonus for placing all pieces

## Project Structure

```
src/
├── main.py                      # Application entry point (Phase 10)
├── config/
│   ├── pieces.py               # All 21 piece definitions
│   └── game_config.py          # Game configuration options (Phase 10)
├── models/
│   ├── board.py                # Board state and grid management
│   ├── piece.py                # Piece class with transformations
│   └── player.py               # Player state and score tracking
├── game/
│   ├── game_state.py           # Overall game state machine
│   ├── rules.py                # Move validation and rule checking
│   ├── scoring.py              # Score calculation
│   ├── score_history.py        # Score tracking history (Phase 9)
│   ├── game_loop.py            # Game loop management (Phase 9)
│   ├── turn_manager.py         # Turn-based gameplay (Phase 7)
│   ├── end_game_detector.py    # Game end detection (Phase 6)
│   ├── winner_determiner.py    # Winner determination (Phase 6)
│   └── error_handler.py        # Error handling & recovery (Phase 10)
└── ui/
    ├── game_window.py          # Main game interface
    ├── board_display.py        # Board rendering
    ├── piece_selector.py       # Piece selection UI
    ├── current_player_indicator.py  # Turn indicator (Phase 3)
    ├── scoreboard.py           # Score display (Phase 3)
    ├── piece_inventory.py      # Piece inventory (Phase 3)
    ├── game_results.py         # End game results (Phase 4)
    ├── state_sync.py           # UI state synchronization (Phase 3)
    ├── keyboard_shortcuts.py   # Keyboard controls (Phase 10)
    ├── restart_button.py       # Game restart (Phase 10)
    ├── board_renderer.py       # Optimized board rendering (Phase 10)
    ├── error_display.py        # Error display (Phase 8)
    ├── placement_preview.py    # Placement validation (Phase 8)
    └── score_breakdown.py      # Score breakdown (Phase 9)

tests/
├── unit/                           # Component tests
│   ├── test_board.py
│   ├── test_piece.py
│   ├── test_player.py
│   ├── test_rules.py
│   ├── test_scoring.py
│   └── test_game_state.py
├── contract/                        # API contract tests
│   ├── test_board_init.py          # Board initialization
│   ├── test_piece_rotation.py      # Piece rotations
│   ├── test_piece_flip.py          # Piece flips
│   ├── test_move_validation.py     # Move validation
│   ├── test_turn_sequence.py       # Turn sequence (Phase 7)
│   ├── test_skip_turn.py           # Skip turn logic (Phase 7)
│   ├── test_game_end.py            # Game end detection (Phase 6)
│   ├── test_final_scoring.py       # Final scoring (Phase 6)
│   ├── test_state_display.py       # UI state display (Phase 5)
│   └── test_score_calculation.py   # Score calculations (Phase 9)
├── integration/                     # Game flow tests
│   ├── test_game_setup.py          # Game setup (Phase 3)
│   ├── test_piece_placement.py     # Piece placement (Phase 4)
│   ├── test_complete_game_flow.py  # Complete flow (Phase 10)
│   ├── test_end_game_flow.py       # End game flow (Phase 6)
│   ├── test_turn_flow.py           # Turn flow (Phase 7)
│   ├── test_rule_enforcement.py    # Rule enforcement (Phase 8)
│   ├── test_score_updates.py       # Score updates (Phase 9)
│   └── test_ui_updates.py          # UI updates (Phase 5)
└── fixtures/                       # Test data
```

## Architecture Overview

### Core Components

1. **Board** (`models/board.py`)
   - Manages 20x20 grid
   - Tracks piece occupancy
   - Validates board boundaries

2. **Piece** (`models/piece.py`)
   - Defines 21 Blokus shapes
   - Handles rotations (90°, 180°, 270°) and flips
   - Calculates absolute positions

3. **Player** (`models/player.py`)
   - Tracks score and piece inventory
   - Manages placement state

4. **Game State** (`game/game_state.py`)
   - Orchestrates turn order
   - Manages game flow (setup → playing → ended)
   - Records move history

5. **Rules Validator** (`game/rules.py`)
   - Enforces Blokus rules
   - Validates all moves
   - Checks game end conditions

6. **UI** (`ui/`)
   - Renders board and pieces
   - Handles user interactions
   - Displays scores and turn info

### Data Flow

```
[User Input] → [UI] → [Game State] → [Rules Validator]
                                            ↓
[Board Update] ← [Piece Placement] ← [Validation Result]
                                            ↓
                                [Score Calculation]
```

## Key Blokus Rules (Implementation)

### Rule 1: First Move Must Touch Corner
```
Player 1: Start at (0, 0) - top-left
Player 2: Start at (0, 19) - top-right
Player 3: Start at (19, 19) - bottom-right
Player 4: Start at (19, 0) - bottom-left
```
Your first piece must include your starting corner position.

### Rule 2: No Edge-to-Edge Contact (Own Pieces Only)
```
✓ CORRECT: Diagonal touch (corner-to-corner)
✗ INCORRECT: Edge touch
```
Your pieces can only touch your own pieces at corners, never at edges.

### Rule 3: No Piece Overlap
Each board position can only hold one piece square.

### Rule 4: Stay on Board
All piece squares must be within the 20x20 grid (rows 0-19, cols 0-19).

## Running the Game

### Prerequisites
- Python 3.11 or higher
- uv package manager (recommended) or tkinter (usually included with Python)

### Installation
```bash
# Clone repository
git clone <repository-url>
cd blokus-step-by-step

# Using uv (recommended - fast, modern Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh
uv sync

# Or using pip
pip install -r requirements.txt  # Usually none needed
```

### Launch Game
```bash
# Using uv (recommended)
uv run python src/main.py

# Or directly with Python
python src/main.py
```

### Game Configuration Presets (Phase 10)

The game offers three configuration presets:

1. **Casual** - Relaxed game with animations and visual aids
2. **Tournament** - Fast-paced game without animations
3. **High Contrast** - High contrast colors for accessibility

Or create **Custom Configuration**:
- Custom player names and colors
- Board size (10-30)
- Color scheme selection
- Grid visibility options
- Animation speed control

### Game Controls

**Setup Phase**:
1. Choose preset or custom configuration
2. Enter player names (2-4 players)
3. Click "Start Game"

**Playing Phase - Mouse Controls**:
1. Click on your piece to select it
2. Use rotation/flip buttons
3. Click board position to place piece
4. Click "Skip Turn" if no valid moves
5. Click "New Game" to restart

**Playing Phase - Keyboard Shortcuts (Phase 10)**:
- `R` or `r`: Rotate piece clockwise
- `Shift+R`: Rotate piece counterclockwise
- `F` or `f`: Flip piece
- `1-9` or `0`: Select piece by number
- `Space`: Skip turn
- `Enter`: Place piece
- `Esc`: Cancel current action
- `Ctrl+N`: New game
- `Ctrl+Q`: Quit game
- `H` or `?`: Show help with all shortcuts

**During Game**:
- Current player highlighted in UI
- Available pieces shown in panel with counts
- Real-time score updates after each move
- Score breakdown visible in detailed view
- Game ends automatically when complete
- Optimized board rendering for smooth performance
- Comprehensive error handling with recovery

## Testing

### Run All Tests
```bash
# From project root
pytest tests/ -v
```

### Run Specific Test
```bash
# Unit tests only
pytest tests/unit/ -v

# Integration tests
pytest tests/integration/ -v

# Specific test file
pytest tests/unit/test_piece.py -v
```

### Test Coverage
```bash
pytest tests/ --cov=src --cov-report=html
# Open htmlcov/index.html to view coverage report
```

## Development Workflow

### Following the Constitution

**Principle I: Incremental Development**
- Each feature implemented in small steps
- Each increment independently testable
- Document reasoning before implementation

**Principle II: Test-First Development**
- Write tests BEFORE implementation
- TDD cycle: Test → Fail → Implement → Pass → Refactor
- All game logic has test coverage

**Principle III: Modular Architecture**
- Clear separation: models, game logic, UI
- Dependencies flow toward game_state
- Each module has single responsibility

**Principle IV: Rules Compliance**
- All 21 Blokus pieces implemented exactly
- Validation comprehensive and correct
- Error messages explain rule violations

**Principle V: Clear Documentation**
- All public methods documented
- User scenarios reflected in tests
- This guide enables 10-minute setup

### Implementation Order

1. **Foundational** (must complete first):
   - Piece model and transformations
   - Board model and grid management
   - Rules validator core logic

2. **Core Gameplay**:
   - Game state machine
   - Player management
   - Turn sequencing

3. **UI Layer**:
   - Board display
   - Piece selection
   - Game controls

4. **Polish**:
   - Score tracking
   - End game detection
   - UI polish and error handling

## Common Development Tasks

### Adding a New Piece
1. Add coordinates to `config/pieces.py`
2. Add test in `tests/unit/test_piece.py`
3. Verify in `tests/unit/test_board.py` placement validation

### Modifying Rules
1. Update validation in `game/rules.py`
2. Update tests to reflect new behavior
3. Run full test suite to verify no regressions

### Debugging Invalid Moves
```python
# Enable debug mode
game_state.set_debug_mode(True)

# Check validation details
result = rules.validate_move(game_state, player_id, piece, position)
print(result.validation_details)
```

### Inspecting Game State
```python
# Pretty-print current game state
from pprint import pprint
pprint(game_state.to_dict())
```

## Troubleshooting

### "tkinter not found" Error
**Solution**: Install tkinter
```bash
# Ubuntu/Debian
sudo apt-get install python3-tk

# macOS (with Homebrew)
brew install python-tk

# Windows: Usually included with Python
```

### Piece Placement Rejected
- Check: Is it your first move? Must touch your corner.
- Check: Does piece stay within 20x20 board?
- Check: Does piece overlap existing pieces?
- Check: Does piece touch your pieces edge-to-edge?

### Game Won't End
- Game should end when all players skip consecutively OR all pieces placed
- Check: Are players correctly skipping when no moves available?
- Check: End game detection in `game/rules.py`

## Performance Expectations (Phase 10 Optimizations)

- **UI Responsiveness**: <50ms per interaction (optimized from <100ms)
- **Board Rendering**: 60+ FPS with optimized renderer (double-buffering, region updates)
- **Move Validation**: <1ms per move
- **Game Setup**: <3 seconds for 4 players (down from <5 seconds)
- **Memory Usage**: Optimized with caching and efficient data structures
- **Error Recovery**: <100ms automatic recovery for most errors
- **Keyboard Responsiveness**: <10ms for all shortcuts

**Phase 10 Performance Features**:
- Optimized Board Renderer with double buffering
- Region-based updates (only redraw changed areas)
- Caching for piece shapes and grid lines
- Configurable rendering quality
- Performance metrics tracking (debug mode)

## Next Steps

After understanding the basics:
1. Review `spec.md` for full feature requirements
2. Review `data-model.md` for entity relationships
3. Review `contracts/*.yaml` for component interfaces
4. Run test suite to verify understanding
5. Start with foundational components (Piece, Board, Rules)

## Getting Help

- **Architecture Questions**: Review `data-model.md` and contracts
- **Rules Questions**: Review `spec.md` Blokus rules section
- **Implementation Questions**: Review `research.md` technical decisions
- **Testing Questions**: Check existing tests in `tests/unit/`

## Resources

- [Official Blokus Rules](http://www.blokus.com/)
- Python tkinter documentation: https://docs.python.org/3/library/tkinter.html
- pytest documentation: https://docs.pytest.org/
- Project constitution: `.specify/memory/constitution.md`
