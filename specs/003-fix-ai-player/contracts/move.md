# Contract: Move Object

**Module**: `src/services/ai_strategy.py`
**Version**: 1.0
**Updated**: 2025-11-06

## Purpose

Represents a piece placement action with complete orientation information.

## Structure

### Fields

#### `piece: Optional[Piece]`

**Type**: `Optional[Piece]` from `src/models/piece.py`

**Description**: Piece object to be placed

**Constraints**:
- Must not be None unless `is_pass=True`
- Must be in player's unplaced pieces list
- Must not be already placed

**Validation**:
```python
if not is_pass and piece is None:
    raise ValueError("Move must specify piece unless passing")
if piece is not None and piece.is_placed:
    raise ValueError("Cannot place already-placed piece")
```

---

#### `position: Optional[Tuple[int, int]]`

**Type**: `Optional[Tuple[int, int]]`

**Description**: Board coordinates where piece's top-left corner should be placed

**Constraints**:
- Format: (row, col)
- Row must be 0-19
- Col must be 0-19
- Must not be None unless `is_pass=True`

**Validation**:
```python
if not is_pass and position is None:
    raise ValueError("Move must specify position unless passing")
if position is not None:
    row, col = position
    if not (0 <= row < 20 and 0 <= col < 20):
        raise ValueError("Position out of board bounds")
```

---

#### `rotation: int`

**Type**: `int`

**Description**: Rotation in degrees applied to piece

**Constraints**:
- Must be one of: {0, 90, 180, 270}
- Applied AFTER flip (if flip=True)

**Validation**:
```python
if rotation not in {0, 90, 180, 270}:
    raise ValueError(f"Invalid rotation: {rotation}")
```

---

#### `flip: bool`

**Type**: `bool`

**Description**: Whether piece should be horizontally flipped before rotation

**Constraints**:
- True: Flip piece horizontally (mirror left-right)
- False: No flip, use piece's default orientation
- Applied BEFORE rotation

**Default**: False

**Example**:
```python
# Piece shape: [(0,0), (0,1), (1,1)]
# Without flip: Same shape
# With flip: [(0,0), (0,-1), (1,-1)] then rotated
```

---

#### `player_id: int`

**Type**: `int`

**Description**: ID of player making the move

**Constraints**:
- Must be 1-4
- Must match the AIPlayer's player_id
- Must be unique across all players

**Validation**:
```python
if player_id not in {1, 2, 3, 4}:
    raise ValueError(f"Invalid player_id: {player_id}")
```

---

#### `is_pass: bool`

**Type**: `bool`

**Description**: Special marker for pass action (no piece placement)

**Constraints**:
- True: Player passes turn, no piece placed
- False: Normal piece placement move

**Default**: False

**Interaction with other fields**:
```python
if is_pass:
    assert piece is None
    assert position is None
else:
    assert piece is not None
    assert position is not None
```

---

## Initialization

### Constructor

**Signature**:
```python
def __init__(
    self,
    piece: Optional[Piece],
    position: Optional[Tuple[int, int]],
    rotation: int,
    player_id: int,
    is_pass: bool = False,
    flip: bool = False  # NEW FIELD
):
```

**Parameters**:
- All parameters required except `is_pass` (has default) and `flip` (has default)
- Order matters for backward compatibility

**Example**:
```python
# Normal placement
move = Move(
    piece=piece,
    position=(10, 10),
    rotation=90,
    player_id=1,
    flip=True
)

# Pass action
pass_move = Move(
    piece=None,
    position=None,
    rotation=0,
    player_id=1,
    is_pass=True
)
```

---

## Methods

### `__repr__()`

**Signature**:
```python
def __repr__(self) -> str:
```

**Returns**: String representation for debugging

**Format**:
```
# For placement moves:
Move(player=1, piece=I1, position=(10, 10), rotation=90°, flip=True)

# For pass moves:
Move(player=1, action=pass)
```

**Example**:
```python
print(move)
# Output: Move(player=1, piece=I1, position=(10, 10), rotation=90°, flip=True)
```

---

## Transformation Application Order

When executing a Move, transformations MUST be applied in this order:

1. **Select Piece**: Get piece from player's inventory
2. **Apply Flip**: If `flip=True`, call `piece.flip()`
3. **Apply Rotation**: Call `piece.rotate(90)` N times where N = rotation/90
4. **Place at Position**: Call `placement_handler.place_piece(row, col)`

**Critical**: Flip must be applied BEFORE rotation

**Example Execution**:
```python
# Given move = Move(piece, (10, 10), rotation=90, player_id=1, flip=True)

# Step 1: Select piece
placement_handler.select_piece(piece.name)

# Step 2: Flip (if needed)
if move.flip:
    placement_handler.flip_piece()

# Step 3: Rotate (if needed)
rotation_count = move.rotation // 90
for _ in range(rotation_count):
    placement_handler.rotate_piece()

# Step 4: Place
placement_handler.place_piece(move.position[0], move.position[1])
```

---

## Validation

### Pre-Placement Validation

Before executing a Move, validate:

1. **Player owns piece**:
   ```python
   if not is_pass and piece not in player.pieces:
       raise ValueError("Player does not own this piece")
   ```

2. **Piece is unplaced**:
   ```python
   if not is_pass and getattr(piece, 'is_placed', False):
       raise ValueError("Piece is already placed")
   ```

3. **Position is valid**:
   ```python
   if not is_pass:
       row, col = position
       if not (0 <= row < 20 and 0 <= col < 20):
           raise ValueError("Position out of bounds")
   ```

4. **Rotation is valid**:
   ```python
   if rotation not in {0, 90, 180, 270}:
       raise ValueError("Invalid rotation")
   ```

5. **Blokus rules compliance**:
   - Use `BlokusRules.get_valid_moves()` to validate
   - Check no edge adjacency (only corner adjacency allowed)
   - Check no overlap with existing pieces
   - First move must be in starting corner

---

## Usage Examples

### Creating Moves

```python
# Simple move (no flip, no rotation)
move1 = Move(piece, (5, 5), 0, player_id=1)

# Rotated move
move2 = Move(piece, (5, 5), 90, player_id=1)

# Flipped move
move3 = Move(piece, (5, 5), 0, player_id=1, flip=True)

# Flipped and rotated move
move4 = Move(piece, (5, 5), 90, player_id=1, flip=True)

# Pass
pass_move = Move(None, None, 0, player_id=1, is_pass=True)
```

### Checking Move Properties

```python
if move.is_pass:
    print("Player passes")
else:
    print(f"Place {move.piece.name} at {move.position}")
    print(f"Flip: {move.flip}, Rotation: {move.rotation}°")

# Check if move requires flip
if move.flip:
    print("This move requires flipping the piece")
```

### Accessing Move Data

```python
# Get piece name
piece_name = move.piece.name if move.piece else "PASS"

# Get board position
row, col = move.position

# Get orientation
orientation = f"{'flipped ' if move.flip else ''}{move.rotation}°"

print(f"Move: {piece_name} at ({row}, {col}) - {orientation}")
```

---

## Integration

### With AIPlayer
- Created by `strategy.calculate_move()`
- Returned to game loop from `AIPlayer.calculate_move()`

### With Strategy
- Strategy decides flip and rotation values
- Must ensure flip+rotation combination is valid for piece

### With Game Loop
- Passed to `_trigger_ai_move()` execution
- Validated before placement
- Executed via placement_handler

### With Placement Handler
- Piece selected via `piece.name`
- Flip applied via `flip_piece()`
- Rotation applied via `rotate_piece()` (multiple calls)
- Placement via `place_piece(row, col)`

---

## Backward Compatibility

**Existing Code**:
- Old Move objects had no `flip` field
- All existing moves have `flip=False` by default

**Migration**:
- Existing code continues to work (flip defaults to False)
- New code can set `flip=True` for flipped orientations
- No breaking changes to constructor

**Serialization**:
```python
# Old format (JSON): {"piece": ..., "position": ..., "rotation": 90, ...}
# New format adds: ..., "flip": true, ...}
```

---

## Testing Requirements

### Unit Tests
1. Can create Move with flip=True and flip=False
2. __repr__ includes flip state
3. Validation rejects invalid combinations
4. Pass moves have None piece and position

### Integration Tests
1. Flipped moves execute correctly via placement handler
2. Flip+rotation combinations work correctly
3. Validation catches invalid moves before placement
4. Performance: flip transformation is fast (<1ms)

### Contract Tests
1. Move objects from different strategies have flip field
2. Flip field is accessible and set correctly
3. Flip defaults to False for backward compatibility
4. Validation in game loop accepts valid flipped moves
