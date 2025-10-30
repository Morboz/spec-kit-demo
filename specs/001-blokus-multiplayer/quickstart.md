# Quickstart Guide: Blokus Game

**Feature**: Blokus Local Multiplayer Game
**Phase**: 1 - Design and Contracts
**Date**: 2025-10-30

## Overview

This guide will help you understand and run the Blokus local multiplayer game within 10 minutes. The Blokus game is a strategy board game for 2-4 players where you place geometric pieces on a 20x20 board, trying to claim territory while following specific placement rules.

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
├── main.py                 # Application entry point
├── config/
│   └── pieces.py          # All 21 piece definitions
├── models/
│   ├── board.py           # Board state and grid management
│   ├── piece.py           # Piece class with transformations
│   └── player.py          # Player state and score tracking
├── game/
│   ├── game_state.py      # Overall game state machine
│   ├── rules.py           # Move validation and rule checking
│   └── scoring.py         # Score calculation
└── ui/
    ├── game_window.py     # Main game interface
    ├── board_display.py   # Board rendering
    └── piece_selector.py  # Piece selection UI

tests/
├── unit/                   # Component tests
│   ├── test_board.py
│   ├── test_piece.py
│   ├── test_rules.py
│   └── test_scoring.py
├── integration/            # Game flow tests
│   └── test_game_flow.py
└── fixtures/              # Test data
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
- tkinter (usually included with Python)

### Installation
```bash
# Clone repository
git clone <repository-url>
cd blokus-step-by-step

# Install dependencies (if any)
pip install -r requirements.txt  # Usually none needed
```

### Launch Game
```bash
python src/main.py
```

### Game Controls

**Setup Phase**:
1. Select number of players (2-4)
2. Enter player names
3. Click "Start Game"

**Playing Phase**:
1. Click on your piece to select it
2. Use rotation buttons or keyboard shortcuts:
   - `R`: Rotate 90° clockwise
   - `F`: Flip horizontally
   - `ESC`: Clear selection
3. Click board position to place piece
4. Or click "Skip Turn" if no valid moves

**During Game**:
- Current player highlighted
- Available pieces shown in panel
- Scores updated after each move
- Game ends automatically when complete

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

## Performance Expectations

- **UI Responsiveness**: <100ms per interaction
- **Board Rendering**: 60 FPS during gameplay
- **Move Validation**: <1ms per move
- **Game Setup**: <5 seconds for 4 players

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
