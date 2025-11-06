# Data Model: AI Player Strategy Implementation

**Date**: 2025-11-06 | **Feature**: Fix AI Player Strategy Implementation

## Entity Overview

The data model centers on the interaction between AIPlayer, AIStrategy, and Move objects, with piece flipping added as a new dimension.

---

## Entity: Move

**Purpose**: Represents a piece placement action with all necessary orientation information

**Fields**:
- `piece`: Optional[Piece]
  - Description: Piece object to be placed (None if passing)
  - Type: Piece from `src/models/piece.py`
  - Required: Yes (unless is_pass=True)
- `position`: Optional[Tuple[int, int]]
  - Description: Board coordinates (row, col) where piece's top-left should be placed
  - Type: Tuple[int, int] where 0 ≤ row, col < 20
  - Required: Yes (unless is_pass=True)
- `rotation`: int
  - Description: Rotation in degrees
  - Type: Integer from {0, 90, 180, 270}
  - Required: Yes
  - Default: 0
- `flip`: bool
  - Description: Whether piece should be horizontally flipped before rotation
  - Type: Boolean
  - Required: Yes
  - Default: False
- `player_id`: int
  - Description: ID of player making the move (1-4)
  - Type: Integer from {1, 2, 3, 4}
  - Required: Yes
- `is_pass`: bool
  - Description: Special marker for pass action (no piece placed)
  - Type: Boolean
  - Required: Yes
  - Default: False

**Relationships**:
- Associated with AIStrategy via strategy.calculate_move() return
- Passed to game execution in main.py:_trigger_ai_move()
- Validated by BlokusRules before placement

**State Transitions**:
- Created by AIStrategy.calculate_move()
- Validated by game rules (BlokusRules)
- Executed by placement handler
- Cannot be modified after creation (immutable)

**Validation Rules**:
- If is_pass=True, then piece and position must be None
- If is_pass=False, then piece and position must not be None
- rotation must be one of {0, 90, 180, 270}
- player_id must be 1-4

---

## Entity: AIPlayer

**Purpose**: Represents an AI-controlled player with strategy-based decision making

**Fields**:
- `player_id`: int
  - Description: Unique identifier for player
  - Type: Integer from {1, 2, 3, 4}
- `strategy`: AIStrategy
  - Description: Strategy instance for move calculation
  - Type: RandomStrategy, CornerStrategy, or StrategicStrategy
- `color`: str
  - Description: Display color for pieces
  - Type: String (hex or named color)
- `name`: str
  - Description: Player display name
  - Type: String
- `pieces`: List[Piece]
  - Description: Unplaced pieces available to player
  - Type: List[Piece]
- `score`: int
  - Description: Current game score
  - Type: Integer (starts at 0)
- `is_calculating`: bool
  - Description: Whether player is currently calculating a move
  - Type: Boolean
  - Default: False

**Key Methods**:
- `calculate_move(board, pieces, time_limit) -> Optional[Move]`
  - Purpose: Calculate best move using assigned strategy
  - Returns: Move object or None (for pass/no moves)
  - Timeout: Respects strategy's timeout_seconds

**Relationships**:
- Has-one strategy (RandomStrategy, CornerStrategy, or StrategicStrategy)
- Composed of pieces from piece inventory
- Interacts with game state for move validation
- Connected to placement handler for move execution

**Validation Rules**:
- player_id must be unique across all players
- strategy must be non-None
- pieces list must not contain placed pieces

---

## Entity: AIStrategy (Abstract Base)

**Purpose**: Defines interface for AI move calculation strategies

**Subclasses**:
- **RandomStrategy**: Easy difficulty - random valid moves
- **CornerStrategy**: Medium difficulty - corner-focused placement
- **StrategicStrategy**: Hard difficulty - multi-factor evaluation

**Interface Methods**:
- `calculate_move(board, pieces, player_id, time_limit) -> Optional[Move]`
  - Purpose: Calculate best move for current game state
  - Inputs: board state, available pieces, player ID, optional time limit
  - Returns: Move object or None
- `get_available_moves(board, pieces, player_id) -> List[Move]`
  - Purpose: Generate all valid moves for current state
  - Returns: List of Move objects
- `evaluate_board(board, player_id) -> float`
  - Purpose: Evaluate board position from player's perspective
  - Returns: Numeric score (higher = better)

**Properties**:
- `difficulty_name`: str
  - Returns: "Easy", "Medium", or "Hard"
- `timeout_seconds`: int
  - Returns: Maximum calculation time (Easy: 3s, Medium: 5s, Hard: 8s)

**Relationships**:
- Instantiated and assigned to AIPlayer
- Used exclusively by AIPlayer.calculate_move()
- Returns Move objects to game loop

---

## Entity: RandomStrategy (Easy AI)

**Purpose**: Easy difficulty AI that selects random valid moves

**Key Characteristics**:
- Prioritizes speed over strategy
- Uses caching for performance
- Selects completely random from valid moves
- Timeout: 3 seconds

**Strategy Specifics**:
- No evaluation of move quality
- Uses LRU cache for repeated board states
- Good for beginners and casual play

---

## Entity: CornerStrategy (Medium AI)

**Purpose**: Medium difficulty AI that prioritizes corner connections

**Key Characteristics**:
- Evaluates corner adjacency
- Considers piece size and placement location
- Balances speed and intelligence
- Timeout: 5 seconds

**Strategy Specifics**:
- Scores moves based on corner connections
- Prefers larger pieces early in game
- Considers board edges for expansion

---

## Entity: StrategicStrategy (Hard AI)

**Purpose**: Hard difficulty AI with lookahead and multi-factor evaluation

**Key Characteristics**:
- Most sophisticated strategy
- Uses lookahead simulation
- Evaluates multiple factors
- Timeout: 8 seconds

**Strategy Specifics**:
- Simulates move consequences
- Evaluates mobility and area control
- Optimizes for end-game position

---

## Relationships Diagram

```
┌──────────────┐
│   AIPlayer   │
│              │
│ - player_id  │
│ - strategy ────┐
│ - pieces     │ │
│ - score      │ │
└──────────────┘ │
       │         │
       │ has-one │
       │         │
       ▼         │
┌─────────────┐  │
│ AIStrategy  │  │
│ (abstract)  │  │
└─────────────┘  │
       │         │
       ├─────────┴────────────┐
       ▼                      ▼
┌─────────────┐         ┌─────────────┐
│ Random/     │         │    Move     │
│ Corner/     │         │             │
│ Strategic   │         │ - piece     │
└─────────────┘         │ - position  │
                        │ - rotation  │
                        │ - flip      │
                        │ - player_id │
                        └─────────────┘
                              │
                              │ executed_by
                              ▼
                    ┌──────────────────┐
                    │ PlacementHandler │
                    └──────────────────┘
```

---

## Data Flow

1. **Turn begins**: main.py calls `_trigger_ai_move(ai_player)`
2. **Calculate move**: `ai_player.calculate_move(board, pieces, time_limit)`
   - Delegates to `strategy.calculate_move()`
   - Strategy evaluates board and selects Move
3. **Validate move**: Game validates Move against Blokus rules
4. **Execute move**: PlacementHandler places piece according to Move
5. **Update state**: Game state updated, turn advances

---

## Validation & Constraints

### Board State Validation
- Move position must be within board bounds (0-19 for both row/col)
- Move must not overlap existing pieces
- Move must satisfy Blokus adjacency rules (corners ok, edges not ok)

### Piece State Validation
- Move piece must be in player's unplaced pieces
- Flip and rotation must be valid for piece shape
- Cannot place already-placed piece

### Player State Validation
- Player must be active (not eliminated)
- Player must have pieces remaining (unless passing)
- calculate_move must complete within timeout

---

## Extensibility Points

1. **New Strategies**: Add new AIStrategy subclasses for different difficulty levels
2. **Custom Scoring**: Extend evaluation methods for different strategic approaches
3. **Move Types**: Add additional move types beyond placement and pass
4. **Parallel Calculation**: Could extend to multi-threaded move evaluation for Hard AI
