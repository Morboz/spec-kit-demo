# Data Model: AI Battle Mode

**Feature**: AI Battle Mode
**Date**: 2025-11-03
**Based on**: [research.md](research.md) findings

## Entities

### AIPlayer

**Purpose**: Represents an AI-controlled player in the Blokus game

**Attributes**:
- `id` (int): Unique player identifier (1-4, matching board quadrants)
- `strategy` (AIStrategy): Strategy instance determining move calculation
- `color` (str): Display color for player's pieces (e.g., "blue", "red")
- `name` (str): Display name (e.g., "AI Player 2")
- `pieces` (List[BlokusPiece]): Remaining pieces to place
- `score` (int): Current game score
- `has_passed` (bool): Whether player passed on current turn
- `difficulty` (str): Difficulty level (Easy, Medium, Hard)

**State Transitions**:
- `idle` → `calculating` (when AI turn begins)
- `calculating` → `idle` (after move is calculated)
- `idle` → `passed` (when no valid moves available)
- Any state → `game_over` (when game ends)

**Validation Rules**:
- Must follow all Blokus rules (validated by existing move validator)
- Must respect timeout constraints from strategy
- Cannot make moves that violate corner/adjacency rules
- Cannot skip calculation when valid moves exist (unless explicitly passing)

---

### AIStrategy

**Purpose**: Interface defining AI move calculation behavior

**Implementations**:
- `RandomStrategy`: Easy difficulty - random valid placement
- `CornerStrategy`: Medium difficulty - prioritizes corner connections
- `StrategicStrategy`: Hard difficulty - multi-factor evaluation with lookahead

**Interface Methods**:
- `calculate_move(board, pieces, player_id, time_limit) -> Move`:
  - Calculates best move given current board state
  - Returns Move object with piece, position, rotation
  - Must complete within time_limit seconds
  - Returns None if no valid moves available
- `get_timeout_seconds() -> int`:
  - Returns maximum calculation time (3 for Easy, 5 for Medium, 8 for Hard)
- `evaluate_board(board, player_id) -> float`:
  - Returns evaluation score for current board state (Higher = better for player)
  - Used by StrategicStrategy for lookahead

**Contract Requirements**:
- Must return valid moves only (passes existing validator)
- Must respect timeout - return best available move if time exceeded
- Must handle edge case: no valid moves → return None
- Thread-safe for concurrent calculation

---

### GameMode

**Purpose**: Configuration for different AI battle modes

**Attributes**:
- `mode_type` (str): "single_ai", "three_ai", "spectate"
- `human_player_position` (int): Position of human player (1-4), None for spectate
- `ai_players` (List[AIConfig]): List of AI player configurations
- `difficulty` (str): Default difficulty for all AI players

**Configurations**:

**Single AI Mode**:
```python
mode_type: "single_ai"
human_player_position: 1
ai_players: [AIConfig(position=3, difficulty=difficulty)]
difficulty: "Medium"  # or Easy/Hard
```

**Three AI Mode**:
```python
mode_type: "three_ai"
human_player_position: 1
ai_players: [
  AIConfig(position=2, difficulty=difficulty),
  AIConfig(position=3, difficulty=difficulty),
  AIConfig(position=4, difficulty=difficulty)
]
difficulty: "Medium"
```

**Spectate Mode**:
```python
mode_type: "spectate"
human_player_position: None
ai_players: [
  AIConfig(position=1, difficulty="Hard"),
  AIConfig(position=2, difficulty="Medium"),
  AIConfig(position=3, difficulty="Hard"),
  AIConfig(position=4, difficulty="Easy")
]
difficulty: N/A
```

**Validation Rules**:
- Exactly 2 players for single_ai (1 human + 1 AI)
- Exactly 4 players for three_ai (1 human + 3 AI)
- Exactly 4 players for spectate (0 human + 4 AI)
- AI positions must be distinct
- Human position must be unique if specified
- Difficulty must be one of: Easy, Medium, Hard

---

### TurnController (Extended)

**Purpose**: Manages turn progression including AI automatic moves

**New Responsibilities**:
- Detect when current player is AI
- Trigger AI move calculation without human input
- Handle timeout scenarios gracefully
- Update UI to show "AI thinking..." state
- Maintain game flow during AI turns

**Interface Extensions**:
- `is_ai_turn() -> bool`: Check if current player is AI
- `trigger_ai_turn() -> None`: Initiate AI move calculation
- `handle_ai_move(move) -> None`: Process AI-calculated move
- `set_game_mode(mode: GameMode) -> None`: Configure mode before game start

**State Machine**:
- `human_turn` (existing): Waiting for human input
- `ai_calculating` (new): AI is calculating move
- `ai_making_move` (new): AI is animating/placing piece
- `transition_auto` (new): Automatically moving to next turn

**Timeout Handling**:
- Start timer when entering `ai_calculating` state
- Check elapsed time before expensive operations
- Fallback to best-known move or any valid move if timeout
- Log timeout events for debugging
- Update UI to show calculation progress

---

### Move

**Purpose**: Represents a piece placement action

**Attributes**:
- `piece` (BlokusPiece): Piece being placed
- `position` (Tuple[int, int]): Top-left corner position on board
- `rotation` (int): Rotation in degrees (0, 90, 180, 270)
- `player_id` (int): Player making the move
- `is_pass` (bool): True if player is passing turn

**Validation**:
- Must be valid according to Blokus rules
- Must be within board bounds
- Must not conflict with existing pieces
- Corner connection must be satisfied (or it's the first move)
- No edge adjacency with same-color pieces

---

### AIConfig

**Purpose**: Configuration for a single AI player

**Attributes**:
- `position` (int): Board position (1-4)
- `difficulty` (str): AI difficulty level
- `name` (str, optional): Custom display name
- `color` (str, optional): Custom color (defaults to standard palette)

**Validation Rules**:
- Position must be 1-4
- Difficulty must be Easy, Medium, or Hard
- Position must be unique within game mode
- Color must be valid tkinter color

---

## Relationships

```
GameMode
├── ai_players (0-4 AIConfig)
│   └── references AIPlayer.position and AIPlayer.difficulty
└── human_player_position (optional, references player 1-4)

TurnController
├── current_player (Player or AIPlayer)
│   └── has strategy (if AIPlayer)
├── game_mode (GameMode)
└── board_state (shared reference)

AIPlayer
├── strategy (AIStrategy implementation)
│   └── calculates → Move
├── pieces (owned)
└── score (calculated)

Board
├── cell[20][20] (PlayerID or None)
├── validate_move(Move) → bool
└── apply_move(Move) → None
```

## State Validation

### Game Start Validation
- GameMode configuration is valid
- All AI players have valid strategies
- Board is initialized (empty)
- All players have full piece set
- Turn order is set (player 1 starts)

### Turn Validation
- Current player is valid (exists in game)
- If AI: strategy is configured and responsive
- If human: UI is ready for input
- Game is not over
- No players have exceeded pass limit (if applicable)

### Move Validation
- Move passes existing Blokus rule validation
- Move is within timeout constraints (for AI)
- Player has the specified piece available
- Position is on board and unoccupied
- All edge cases handled (no moves, timeout, etc.)

## Error Handling

### Invalid Move Generation
- **Error**: AI generates invalid move
- **Handling**: Reject move, log error, trigger recalculation with timeout
- **Recovery**: Use simpler strategy (Easy) if Hard strategy fails

### Strategy Timeout
- **Error**: AI calculation exceeds time limit
- **Handling**: Interrupt calculation, use best move found or random valid move
- **Recovery**: Reduce difficulty or log warning, continue game

### No Valid Moves
- **Error**: AI has no valid moves available
- **Handling**: Automatically pass turn, update player state
- **Recovery**: Wait for next turn, check again

### Multiple AI Consecutive Passes
- **Error**: All remaining players pass consecutively
- **Handling**: Detect end game condition, calculate final scores
- **Recovery**: Display game over screen with results
