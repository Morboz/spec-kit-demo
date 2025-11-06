# Contract: AIStrategy Interface

**Module**: `src/services/ai_strategy.py`
**Version**: 1.0
**Updated**: 2025-11-06

## Purpose

Defines the abstract base class contract for AI strategy implementations.

## Abstract Interface

### Abstract Method: `calculate_move(board, pieces, player_id, time_limit=None)`

**Signature**:
```python
@abstractmethod
def calculate_move(
    self,
    board: List[List[int]],
    pieces: List[Piece],
    player_id: int,
    time_limit: Optional[int] = None
) -> Optional[Move]:
```

**Purpose**: Calculate best move for current game state.

**Parameters**:
- `board`: 2D array (20x20) representing game board
- `pieces`: List of unplaced Piece objects
- `player_id`: ID of player making the move (1-4)
- `time_limit`: Maximum calculation time in seconds (optional)

**Returns**:
- `Move` object with piece, position, rotation, and flip
- `None` if no valid moves exist

**Preconditions**:
- `board` must be valid 20x20 grid
- `pieces` must not be empty (unless no valid moves)
- `player_id` must be 1-4

**Postconditions**:
- Returned Move has player_id matching input
- Returned Move piece is in provided pieces list
- If flip=True, piece must be flippable
- If rotation is specified, must be one of {0, 90, 180, 270}

---

### Abstract Property: `difficulty_name`

**Signature**:
```python
@property
@abstractmethod
def difficulty_name(self) -> str:
```

**Returns**: Strategy difficulty level ("Easy", "Medium", or "Hard")

---

### Abstract Property: `timeout_seconds`

**Signature**:
```python
@property
@abstractmethod
def timeout_seconds(self) -> int:
```

**Returns**: Maximum calculation time in seconds.

---

## Concrete Methods

### Method: `get_available_moves(board, pieces, player_id)`

**Signature**:
```python
def get_available_moves(
    self,
    board: List[List[int]],
    pieces: List[Piece],
    player_id: int
) -> List[Move]:
```

**Purpose**: Generate all valid moves for current state.

**Default Implementation**:
- Iterates through all pieces
- For each rotation (0°, 90°, 180°, 270°)
- For each board position (row 0-19, col 0-19)
- Tests if placement is valid
- Returns list of valid Move objects

**Performance**:
- Base implementation is O(pieces × rotations × 400 positions)
- Subclasses may optimize

**Return Value**:
- List of Move objects
- Empty list if no valid moves

**Flip Support**:
- Base implementation does NOT generate flipped orientations
- Subclasses must override to support flip

---

### Method: `evaluate_board(board, player_id)`

**Signature**:
```python
def evaluate_board(
    self,
    board: List[List[int]],
    player_id: int
) -> float:
```

**Purpose**: Evaluate board position from player's perspective.

**Default Implementation**:
```python
score = sum(1 for row in board for cell in row if cell == player_id)
return score
```

**Returns**: Numeric score (higher = better for player)

**Subclass Override**:
- May implement more sophisticated evaluation
- Should consider: corner control, mobility, area coverage

---

### Method: `_get_piece_positions(piece, row, col, rotation)`

**Signature**:
```python
def _get_piece_positions(
    self,
    piece: Piece,
    row: int,
    col: int,
    rotation: int
) -> List[Tuple[int, int]]:
```

**Purpose**: Get absolute board positions for piece at location with rotation.

**Parameters**:
- `piece`: Piece to place
- `row`: Top-left row position on board
- `col`: Top-left column position on board
- `rotation`: Rotation in degrees (0, 90, 180, 270)

**Returns**: List of (row, col) tuples for piece squares

**Algorithm**:
1. Get piece's relative positions from `piece.positions`
2. Apply rotation transformation:
   - 0°: (r, c)
   - 90°: (-c, r)
   - 180°: (-r, -c)
   - 270°: (c, -r)
3. Add board offset (row, col) to each position
4. Return list of absolute positions

**Important**: Does NOT support flip in base implementation

**Subclass Responsibility**:
- Override to add flip support
- Apply flip transformation BEFORE rotation

---

## Strategy Implementations

### RandomStrategy (Easy)

**Properties**:
- `difficulty_name`: "Easy"
- `timeout_seconds`: 3

**Strategy**:
- Randomly selects from valid moves
- Uses caching for performance
- No move evaluation

**Key Methods**:
- Overrides `calculate_move()` with caching logic
- Provides `_get_available_moves_fast()` optimization

---

### CornerStrategy (Medium)

**Properties**:
- `difficulty_name`: "Medium"
- `timeout_seconds`: 5

**Strategy**:
- Evaluates corner connections
- Scores moves based on corner adjacency
- Prefers larger pieces early

**Key Methods**:
- Overrides `calculate_move()` with scoring
- Implements `_score_move()` for corner evaluation

---

### StrategicStrategy (Hard)

**Properties**:
- `difficulty_name`: "Hard"
- `timeout_seconds`: 8

**Strategy**:
- Multi-factor evaluation
- Lookahead simulation
- Mobility assessment

**Key Methods**:
- Overrides `calculate_move()` with lookahead
- Implements `_evaluate_with_lookahead()`

---

## Contract Requirements

### For All Strategy Implementations

1. **Must Support Flip**: All strategies MUST consider flipped orientations
   - Update `_get_piece_positions()` to accept flip parameter
   - Apply flip transformation before rotation

2. **Time Limit Compliance**: All calculations MUST respect time_limit
   - Check elapsed time during evaluation
   - Return best move found so far on timeout

3. **Valid Move Generation**: All generated moves MUST be valid
   - Must not overlap existing pieces
   - Must be within board bounds
   - Must satisfy Blokus adjacency rules

4. **Performance**: Must complete within timeout_seconds
   - Easy: avg < 100ms
   - Medium: avg < 500ms
   - Hard: avg < 2s

### Flip Transformation Specification

When flip=True:
1. Take piece's relative positions
2. Transform each (r, c) to (r, -c) for horizontal flip
3. Then apply rotation transformation
4. Add board offset

Example:
```
Original positions: [(0, 0), (0, 1), (1, 1)]
After flip (0, 0): [(0, 0), (0, -1), (1, -1)]
After flip + 90° rotation: [(0, 0), (1, 0), (1, -1)]
```

---

## Error Handling

### Invalid Input
- Raise `ValueError` if board is wrong size
- Raise `ValueError` if player_id is invalid
- Raise `ValueError` if pieces is empty but moves exist

### Timeout
- Return best move found so far
- Log timeout event
- Do not raise exception

### No Valid Moves
- Return empty list from `get_available_moves()`
- Return None from `calculate_move()`

---

## Testing Requirements

### Unit Tests Required
1. Each strategy produces different move patterns
2. Flip transformations are mathematically correct
3. Timeout handling works for all strategies
4. Move validation passes game rules

### Integration Tests Required
1. Strategies integrate correctly with AIPlayer
2. Returned moves execute successfully in game
3. Performance meets timeout requirements
4. Caching works correctly (RandomStrategy)

---

## Backward Compatibility

**Breaking Changes Not Allowed**:
- Cannot remove or rename public methods
- Cannot change return types of public methods
- Cannot change difficulty_name values

**Compatible Changes**:
- Adding new methods (with different names)
- Adding optional parameters with defaults
- Enhancing internal implementations
- Adding caching or optimizations

---

## Examples

### Basic Strategy Usage
```python
strategy = RandomStrategy()
move = strategy.calculate_move(board, pieces, player_id=1)

if move:
    print(f"Place {move.piece.name} at {move.position}")
    print(f"Flip: {move.flip}, Rotation: {move.rotation}°")
```

### Custom Timeout
```python
move = strategy.calculate_move(board, pieces, player_id=1, time_limit=5)
```

### Flip Support
```python
# Strategy should generate moves with flip=True when beneficial
moves = strategy.get_available_moves(board, pieces, player_id=1)
flipped_moves = [m for m in moves if m.flip]
```
