# Contract: AI Integration Flow

**Components**: AIPlayer, AIStrategy, Move, Game Loop
**Version**: 1.0
**Updated**: 2025-11-06

## Purpose

Defines the integration contract between AI components and the main game loop, ensuring calculate_move() is properly called and executed.

## High-Level Flow

```
Game Loop → _trigger_ai_move() → AIPlayer.calculate_move()
                                    ↓
                           Strategy.calculate_move()
                                    ↓
                              Returns Move object
                                    ↓
Game Loop executes Move via PlacementHandler
```

---

## Integration Point 1: Game Loop to AIPlayer

### Entry Point: `_trigger_ai_move(ai_player)`

**Location**: `main.py:425-509` (to be refactored)

**Current Problem**: Bypasses `calculate_move()`, implements manual logic

**New Contract**:

```python
def _trigger_ai_move(ai_player: AIPlayer):
    """
    Execute AI player's turn by calling calculate_move and executing result.

    Args:
        ai_player: AIPlayer instance whose turn it is
    """
    # OLD CODE (85 lines): Remove all manual random selection logic

    # NEW CODE:
    # 1. Get board state
    board_state = self.game_state.board.grid

    # 2. Get player's pieces
    pieces = ai_player.get_unplaced_pieces()

    # 3. Call calculate_move (THIS IS THE FIX)
    move = ai_player.calculate_move(board_state, pieces)

    # 4. Execute returned move
    if move and not move.is_pass:
        _execute_move(move)
    elif move and move.is_pass:
        _pass_turn()
    else:
        # No valid moves
        _pass_turn()
```

**Integration Requirements**:
- MUST call `ai_player.calculate_move()` instead of manual logic
- MUST use returned Move object for execution
- MUST handle None return (pass turn)
- MUST handle is_pass=True (pass turn)

---

## Integration Point 2: AIPlayer to Strategy

### Method: `AIPlayer.calculate_move()`

**Contract**:

```python
def calculate_move(
    self,
    board: List[List[int]],
    pieces: List[Piece],
    time_limit: Optional[int] = None
) -> Optional[Move]:
    """
    Calculate best move using assigned strategy.

    Returns:
        Move object with piece, position, rotation, flip, player_id
        OR None if no valid moves exist
    """
    # Delegate to strategy
    move = self.strategy.calculate_move(
        board, pieces, self.player_id, time_limit
    )

    # Validate returned move
    if move and not move.is_pass:
        assert move.player_id == self.player_id
        assert move.piece in pieces

    return move
```

**Integration Requirements**:
- MUST delegate to `self.strategy.calculate_move()`
- MUST pass correct parameters (board, pieces, player_id, time_limit)
- MUST validate returned Move (player_id matches, piece in pieces)
- MUST respect timeout handling
- MUST return Move or None

---

## Integration Point 3: Strategy to Move Generation

### Method: `Strategy.calculate_move()`

**Contract**:

```python
def calculate_move(
    self,
    board: List[List[int]],
    pieces: List[Piece],
    player_id: int,
    time_limit: Optional[int] = None
) -> Optional[Move]:
    """
    Generate moves including flipped orientations.

    Returns:
        Move object with flip=True/False as appropriate
        None if no valid moves
    """
    # 1. Generate all available moves (MUST include flip)
    all_moves = self._generate_moves_with_flip(board, pieces, player_id)

    # 2. Evaluate moves based on strategy
    if self.difficulty_name == "Easy":
        return random.choice(all_moves) if all_moves else None
    elif self.difficulty_name == "Medium":
        return self._score_and_select(all_moves)
    else:  # Hard
        return self._evaluate_with_lookahead(all_moves, time_limit)
```

**New Requirements for All Strategies**:
- MUST generate moves with flip=True when beneficial
- MUST include both flipped and non-flipped orientations
- MUST correctly calculate positions for flipped pieces
- MUST return Move objects with flip field set correctly

---

## Integration Point 4: Move Execution in Game Loop

### Function: `_execute_move(move)`

**Contract**:

```python
def _execute_move(move: Move):
    """
    Execute a Move object via placement handler.

    Args:
        move: Move object with piece, position, rotation, flip
    """
    # 1. Select piece in placement handler
    success = self.placement_handler.select_piece(move.piece.name)
    if not success:
        raise RuntimeError(f"Failed to select piece: {move.piece.name}")

    # 2. Apply flip (if needed)
    if move.flip:
        self.placement_handler.flip_piece()

    # 3. Apply rotation (if needed)
    rotation_count = move.rotation // 90
    for _ in range(rotation_count):
        self.placement_handler.rotate_piece()

    # 4. Place piece
    row, col = move.position
    success, error = self.placement_handler.place_piece(row, col)

    if not success:
        raise RuntimeError(f"Failed to place piece: {error}")

    # 5. Update game state
    self._on_piece_placed(move.piece.name)
```

**Integration Requirements**:
- MUST apply transformations in correct order: flip then rotation
- MUST call rotate_piece() N times for N*90° rotation
- MUST call flip_piece() if move.flip=True
- MUST call place_piece() with move.position
- MUST handle placement errors gracefully

---

## Error Handling Integration

### On Strategy Timeout

**Flow**:
```
Strategy.calculate_move() exceeds time_limit
    ↓
Returns best move found so far OR first valid move
    ↓
Game loop executes returned move
    ↓
Logs timeout event
    ↓
Game continues normally
```

**Contract**:
- Strategy MUST return a valid move on timeout (not None)
- Game loop MUST execute returned move even if timeout
- Timeout event MUST be logged
- Game MUST NOT pause or crash on timeout

---

### On Invalid Move

**Flow**:
```
Strategy returns move that fails validation
    ↓
Game loop detects invalid (via BlokusRules or placement error)
    ↓
Fallback: try to get any valid move from strategy
    ↓
If fallback fails, pass turn
    ↓
Log error for debugging
```

**Contract**:
- Returned Move MUST be validated before execution
- Invalid moves trigger fallback logic
- Fallback: call `get_available_moves()` and use first
- Ultimate fallback: pass turn
- Errors MUST be logged for debugging

---

### On Calculation Exception

**Flow**:
```
Strategy.calculate_move() raises exception
    ↓
AIPlayer.calculate_move() catches exception
    ↓
Logs exception with traceback
    ↓
Returns None (pass turn)
    ↓
Game continues normally
```

**Contract**:
- AIPlayer.calculate_move() MUST catch all exceptions
- Exceptions MUST be logged with full traceback
- MUST return None on error (pass turn)
- Game MUST continue even on calculation errors

---

## Data Flow Examples

### Example 1: Normal Move Execution

```python
# Game state: board with some pieces, AI player's turn
ai_player = self.game_state.get_current_player()  # Returns AIPlayer

# _trigger_ai_move called
move = ai_player.calculate_move(board_state, pieces)
# Returns: Move(piece=I1, position=(10,10), rotation=90, flip=True, player_id=1)

# Execute move
placement_handler.select_piece("I1")  # Returns True
placement_handler.flip_piece()  # Flip piece horizontally
placement_handler.rotate_piece()  # Rotate 90° (called once)
placement_handler.place_piece(10, 10)  # Returns (True, None)

# Success!
```

### Example 2: No Valid Moves (Pass)

```python
# Game state: AI has pieces but no valid placements
move = ai_player.calculate_move(board_state, pieces)
# Returns: None

# Execute pass
ai_player.pass_turn()
self.game_state.next_turn()

# Turn passes to next player
```

### Example 3: Timeout with Fallback

```python
# Hard AI calculating (approaching 8s timeout)
move = ai_player.calculate_move(board_state, pieces, time_limit=8)
# Strategy detects timeout, returns first valid move
# Returns: Move(piece=I2, position=(5,5), rotation=0, flip=False, player_id=1)

# Execute move normally (despite timeout)
# Logs: "AI Player 1: Calculation exceeded time limit (8.1s)"
# Game continues normally
```

---

## Performance Integration

### Expected Performance

**Easy AI (RandomStrategy)**:
- calculate_move() avg: < 100ms
- Move generation: ~50ms with caching
- Total turn time: < 200ms

**Medium AI (CornerStrategy)**:
- calculate_move() avg: < 500ms
- Move evaluation: ~200-400ms
- Total turn time: < 700ms

**Hard AI (StrategicStrategy)**:
- calculate_move() avg: < 2s
- Lookahead evaluation: ~1-3s
- Total turn time: < 4s

**Contract**: All AI turns MUST complete within their timeout (3s, 5s, 8s)

---

## Testing Integration

### Integration Test 1: calculate_move is Called

**Test**:
```python
def test_ai_uses_calculate_move():
    """Verify that _trigger_ai_move calls calculate_move."""
    # Setup AI game
    # Spy on AIPlayer.calculate_move()

    # Trigger AI turn
    _trigger_ai_move(ai_player)

    # Verify calculate_move was called
    assert ai_player.calculate_move.called
    assert ai_player.calculate_move.call_count == 1
```

### Integration Test 2: Flip Support

**Test**:
```python
def test_ai_supports_flip():
    """Verify AI can generate and execute flipped moves."""
    # Setup board where only flipped orientation fits
    move = ai_player.calculate_move(board_state, pieces)

    # Verify flip field is set
    assert move is not None
    assert hasattr(move, 'flip')

    # Verify flip is applied during execution
    _execute_move(move)
    # Check that piece was placed successfully
```

### Integration Test 3: Strategy Differences

**Test**:
```python
def test_strategies_differ():
    """Verify different strategies produce different moves."""
    board_state = create_test_board()
    pieces = get_test_pieces()

    easy_move = easy_ai.calculate_move(board_state, pieces)
    medium_move = medium_ai.calculate_move(board_state, pieces)
    hard_move = hard_ai.calculate_move(board_state, pieces)

    # At least one should differ
    moves = [easy_move, medium_move, hard_move]
    assert len(set(moves)) > 1, "All strategies produced identical moves"
```

---

## Backward Compatibility

**Existing Test Games**:
- Old tests that mock _trigger_ai_move will need updates
- Tests checking for manual random selection are obsolete
- New tests should verify calculate_move integration

**Migration Path**:
1. Refactor _trigger_ai_move to use calculate_move
2. Update existing tests to match new flow
3. Add new tests for flip support
4. Verify all AI games still work

**Breaking Changes**:
- None - this is a refactor, not API change
- Internal implementation changes only
- External behavior preserved (AI still makes moves)
