# Contract: AIPlayer Interface

**Module**: `src/models/ai_player.py`
**Version**: 1.0
**Updated**: 2025-11-06

## Purpose

Defines the contract for AIPlayer class representing AI-controlled players in Blokus.

## Public Interface

### Method: `calculate_move(board, pieces, time_limit=None)`

**Signature**:
```python
def calculate_move(
    self,
    board: List[List[int]],
    pieces: List[Piece],
    time_limit: Optional[int] = None
) -> Optional[Move]:
```

**Purpose**: Calculate the best move for the current game state using the assigned strategy.

**Parameters**:
- `board`: 2D array (20x20) representing current game board state
  - Each cell contains 0 (empty) or player_id (1-4)
- `pieces`: List of unplaced Piece objects available to player
- `time_limit`: Maximum calculation time in seconds (optional, uses strategy default)

**Returns**:
- `Move` object representing the chosen move
- `None` if no valid moves exist (player should pass)

**Preconditions**:
- `self.strategy` must be non-None
- `board` must be 20x20 2D array
- `pieces` must contain only unplaced pieces
- `time_limit` must be positive if provided

**Postconditions**:
- If returns Move, the Move.piece is in the provided `pieces` list
- If returns Move, the Move.player_id matches `self.player_id`
- If returns None, no valid moves are available
- Calculation completes within `time_limit` or strategy timeout

**Exceptions**:
- May raise `ValueError` if strategy is invalid
- May raise `TimeoutError` if calculation exceeds time_limit

**Performance**:
- Must complete within strategy.timeout_seconds (3s, 5s, or 8s)
- Average case: < 100ms for Easy, < 500ms for Medium, < 2s for Hard

**Concurrency**:
- Not thread-safe for concurrent calls
- Sets `is_calculating` flag during execution

---

### Method: `get_available_moves(board, pieces)`

**Signature**:
```python
def get_available_moves(
    self,
    board: List[List[int]],
    pieces: List[Piece]
) -> List[Move]:
```

**Purpose**: Generate all valid moves for current state (delegates to strategy).

**Returns**: List of Move objects representing all legal placements.

---

### Property: `difficulty`

**Signature**:
```python
@property
def difficulty(self) -> str:
```

**Returns**: Difficulty name from assigned strategy ("Easy", "Medium", or "Hard")

---

### Property: `timeout_seconds`

**Signature**:
```python
@property
def timeout_seconds(self) -> int:
```

**Returns**: Timeout limit from assigned strategy in seconds.

---

### Method: `is_ai_turn()`

**Signature**:
```python
def is_ai_turn(self) -> bool:
```

**Returns**: Always `True` for AIPlayer instances.

---

### Method: `pass_turn()`

**Signature**:
```python
def pass_turn(self):
```

**Purpose**: Mark that player has no valid moves and passes turn.

**Postconditions**:
- Sets `has_passed = True`
- Does not modify board or pieces

---

## Properties

### Required Properties
- `player_id: int` - Unique player identifier (1-4)
- `strategy: AIStrategy` - Strategy for move calculation
- `color: str` - Display color for pieces
- `name: str` - Player display name
- `pieces: List[Piece]` - Unplaced pieces
- `score: int` - Current game score
- `is_calculating: bool` - Whether currently calculating

### Read-Only Properties
- `difficulty: str` - Strategy difficulty name
- `timeout_seconds: int` - Strategy timeout

---

## Integration Points

### With Game State
- Receives board state as input to calculate_move
- Returns Move objects for execution by game loop
- Must respect game rules via validation

### With Placement Handler
- Move objects executed by placement_handler.place_piece()
- Requires piece selection and transformation before placement

### With Strategy
- Delegates all move calculation to self.strategy
- Strategy encapsulates difficulty-specific logic

---

## Validation Rules

1. Player ID must be unique across all players in game
2. Strategy must be one of: RandomStrategy, CornerStrategy, StrategicStrategy
3. Cannot calculate move without assigned strategy
4. Cannot calculate move with empty strategy implementation
5. Returned Move must be validated before execution

---

## Error Handling

### Timeouts
- If calculation exceeds time_limit, return fallback move or None
- Log timeout events for debugging
- Continue game even on timeout (fallback to pass or simple move)

### Invalid State
- If no pieces remain, return None (pass)
- If board is invalid, raise ValueError
- If strategy is None, raise RuntimeError

### Exceptions
- All exceptions logged via ai_logger
- Game continues on calculation errors (fallback to pass)
- Performance metrics recorded even on errors

---

## Examples

### Basic Usage
```python
# Create AI player with RandomStrategy
ai = AIPlayer(
    player_id=1,
    strategy=RandomStrategy(),
    color="blue",
    name="Easy AI"
)

# Calculate move
board = [[0] * 20 for _ in range(20)]
pieces = ai.get_unplaced_pieces()
move = ai.calculate_move(board, pieces)

if move:
    print(f"Selected {move.piece.name} at {move.position}")
else:
    print("No valid moves, passing")
```

### With Custom Timeout
```python
move = ai.calculate_move(board, pieces, time_limit=5)
```

### Strategy Switching
```python
ai.switch_to_difficulty("Hard")
difficulty = ai.difficulty  # Returns "Hard"
```
