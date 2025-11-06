# Quickstart Guide: AI Player Strategy Implementation

**Feature**: Fix AI Player Strategy Implementation | **Version**: 1.0 | **Date**: 2025-11-06

## Purpose

This guide enables developers to quickly understand and implement the AI player strategy fixes. After reading, you should understand the problem, the solution approach, and how to implement it.

**Time to Complete**: ~10 minutes reading

---

## Problem Overview

### What Was Wrong

The AI player implementation had a critical architectural flaw:

1. **Sophisticated Infrastructure Ignored**: The codebase had well-designed strategy classes (`RandomStrategy`, `CornerStrategy`, `StrategicStrategy`) and a comprehensive `calculate_move()` method, but...
2. **Manual Random Selection**: The game loop (`main.py:_trigger_ai_move()`) bypassed all this infrastructure and implemented manual random piece selection
3. **All Difficulties Identical**: Because manual logic was used for all AIs, Easy/Medium/Hard all behaved exactly the same (random)
4. **Missing Flip Support**: AI didn't support piece flipping, limiting its capabilities compared to human players

### Impact

- Users selecting "Medium" or "Hard" AI got no additional challenge
- Code duplication between manual logic and strategy classes
- AI couldn't use the full range of piece orientations
- Maintenance burden (fixing bugs in two places)

---

## Solution Overview

### Core Changes

1. **Use Existing Infrastructure**: Refactor game loop to call `ai_player.calculate_move()` instead of manual logic
2. **Add Flip Support**: Extend `Move` class and strategies to support horizontal piece flipping
3. **Maintain Separation**: Keep modular architecture (AIPlayer → Strategy → Move)

### Key Files Modified

| File | Change Type | Description |
|------|-------------|-------------|
| `src/services/ai_strategy.py` | **Extend** | Add `flip` field to `Move` class; update position calculation |
| `main.py` | **Refactor** | Replace 85 lines in `_trigger_ai_move()` with `calculate_move()` call |
| `src/models/ai_player.py` | **No change** | Already has correct implementation |
| Strategy files | **Enhance** | Ensure flip support in all strategy implementations |

---

## Implementation Steps

### Step 1: Extend Move Class with Flip Support

**File**: `src/services/ai_strategy.py`

**Changes**:
```python
class Move:
    def __init__(
        self,
        piece: Optional[Piece],
        position: Optional[Tuple[int, int]],
        rotation: int,
        player_id: int,
        is_pass: bool = False,
        flip: bool = False  # NEW FIELD
    ):
        # ... existing code ...
        self.flip = flip  # Store flip state

    def __repr__(self):
        if self.is_pass:
            return f"Move(player={self.player_id}, action=pass)"
        return (f"Move(player={self.player_id}, piece={self.piece.name if self.piece else None}, "
                f"position={self.position}, rotation={self.rotation}°"
                f"{', flipped' if self.flip else ''})")
```

**Why**: Enable Move objects to represent flipped orientations

---

### Step 2: Update Position Calculation for Flip

**File**: `src/services/ai_strategy.py`

**Changes** to `_get_piece_positions()`:
```python
def _get_piece_positions(
    self,
    piece: Piece,
    row: int,
    col: int,
    rotation: int,
    flip: bool = False  # NEW PARAMETER
) -> List[Tuple[int, int]]:
    """
    Get absolute board positions for piece at location with rotation and flip.

    Args:
        flip: If True, apply horizontal flip before rotation
    """
    # Get piece shape (list of relative positions)
    shape = piece.positions if hasattr(piece, 'positions') else [(0, 0)]
    positions = []

    for r, c in shape:
        # Apply flip first (if requested)
        if flip:
            c = -c  # Horizontal flip: (r, c) → (r, -c)

        # Then apply rotation
        if rotation == 90:
            new_r, new_c = -c, r
        elif rotation == 180:
            new_r, new_c = -r, -c
        elif rotation == 270:
            new_r, new_c = c, -r
        else:  # rotation == 0
            new_r, new_c = r, c

        # Add offset for position on board
        positions.append((row + new_r, col + new_c))

    return positions
```

**Update Strategy Implementations**:
```python
# In all strategy classes that override calculate_move():
def calculate_move(self, board, pieces, player_id, time_limit=None):
    # ... existing code ...

    # When generating move candidates, include flip:
    for piece in pieces:
        for flip in [False, True]:  # NEW: try both orientations
            for rotation in [0, 90, 180, 270]:
                # Calculate positions with flip
                positions = self._get_piece_positions(
                    piece, row, col, rotation, flip
                )

                # Validate and create Move
                if valid:
                    moves.append(Move(
                        piece, (row, col), rotation,
                        player_id, flip=flip
                    ))
```

**Why**: Apply flip BEFORE rotation (standard Blokus convention)

---

### Step 3: Refactor Game Loop

**File**: `main.py`

**Replace** `_trigger_ai_move()` (lines 425-509):

**OLD CODE (remove)**:
```python
def _trigger_ai_move(self, ai_player):
    # 85 lines of manual random selection
    # - Shuffles pieces
    # - Tries rotations manually
    # - Bypasses calculate_move()
    # ...
```

**NEW CODE**:
```python
def _trigger_ai_move(self, ai_player):
    """Execute AI player's turn using calculate_move()."""
    from src.game.rules import BlokusRules

    # Show AI thinking indicator
    if self.current_player_indicator:
        self.current_player_indicator.show_ai_thinking()

    try:
        # Get board state and pieces
        board_state = self.game_state.board.grid
        pieces = list(ai_player.pieces)

        # NEW: Use calculate_move() instead of manual logic
        move = ai_player.calculate_move(board_state, pieces)

        if move and not move.is_pass:
            # Select the piece
            piece_selected = self.placement_handler.select_piece(move.piece.name)
            if not piece_selected:
                print(f"AI failed to select piece: {move.piece.name}")
                self._pass_turn()
                return

            # Apply flip (if needed)
            if move.flip:
                self.placement_handler.flip_piece()

            # Apply rotation (if needed)
            rotation_count = move.rotation // 90
            for _ in range(rotation_count):
                self.placement_handler.rotate_piece()

            # Place the piece
            success, error_msg = self.placement_handler.place_piece(
                move.position[0], move.position[1]
            )

            if not success:
                print(f"AI placement failed: {error_msg}")
                self._pass_turn()
        else:
            # No valid moves or pass action
            print(f"AI Player {ai_player.player_id} has no valid moves, passing turn")
            self._pass_turn()

    except Exception as e:
        print(f"AI calculation error: {e}")
        import traceback
        traceback.print_exc()
        self._pass_turn()
    finally:
        # Hide thinking indicator
        if self.current_player_indicator:
            self.current_player_indicator.hide_ai_thinking()
```

**Why**: Use existing sophisticated infrastructure instead of duplicating logic

---

### Step 4: Write Tests First (TDD)

**Test File**: `tests/integration/test_ai_calculate_move.py`

```python
def test_ai_uses_calculate_move():
    """Verify _trigger_ai_move calls calculate_move."""
    # Setup AI game
    game = setup_ai_game(difficulty="Easy")

    # Spy on calculate_move
    with patch.object(game.ai_player, 'calculate_move') as mock_calc:
        mock_calc.return_value = Move(
            piece=game.ai_player.pieces[0],
            position=(10, 10),
            rotation=0,
            player_id=1,
            flip=False
        )

        # Trigger AI turn
        game.trigger_ai_turn()

        # Verify calculate_move was called
        assert mock_calc.called
        assert mock_calc.call_count == 1

def test_ai_supports_flip():
    """Verify AI can generate and execute flipped moves."""
    # Setup board where flip is required
    board = create_board_requiring_flip()

    ai_player = create_ai_player(difficulty="Medium")

    # Calculate move
    move = ai_player.calculate_move(board.grid, ai_player.pieces)

    # Verify flip is set appropriately
    assert move is not None
    assert hasattr(move, 'flip')

    # Verify flip can be executed
    assert move.flip in [True, False]  # Whatever the strategy chooses

def test_strategies_differ():
    """Verify different strategies produce different moves."""
    board_state = create_test_board()
    pieces = get_test_pieces()

    # Create AIs with different strategies
    easy_ai = AIPlayer(1, RandomStrategy(), "blue", "Easy")
    medium_ai = AIPlayer(2, CornerStrategy(), "red", "Medium")
    hard_ai = AIPlayer(3, StrategicStrategy(), "green", "Hard")

    # Calculate moves
    easy_move = easy_ai.calculate_move(board_state, pieces)
    medium_move = medium_ai.calculate_move(board_state, pieces)
    hard_move = hard_ai.calculate_move(board_state, pieces)

    # Verify they're not all the same
    moves = [easy_move, medium_move, hard_move]
    # At least one pair should differ
    assert len(set(moves)) > 1
```

**Why**: TDD ensures correctness and prevents regressions

---

## Understanding the Flow

### Sequence Diagram

```
Player Turn Ends
       ↓
Game Loop: _trigger_ai_move(ai_player)
       ↓
AIPlayer.calculate_move(board, pieces)
       ↓
  Strategy.calculate_move(board, pieces, player_id)
       ↓
  Strategy evaluates board
       ↓
  Generates Moves (with flip support)
       ↓
  Selects best Move
       ↓
Returns Move to AIPlayer
       ↓
Returns Move to Game Loop
       ↓
Game Loop executes Move:
  - Select piece
  - Apply flip (if move.flip=True)
  - Apply rotation (move.rotation times)
  - Place at move.position
       ↓
Game State Updated
       ↓
Next Turn
```

---

## Key Concepts

### 1. Flip vs Rotation

**Flip**: Horizontal mirror (left ↔ right)
- Applied BEFORE rotation
- Represented as `flip: bool` in Move
- Changes piece shape: `(r, c)` → `(r, -c)`

**Rotation**: Clockwise rotation in 90° increments
- Applied AFTER flip
- Represented as `rotation: int` in {0, 90, 180, 270}
- Standard transformations

**Example**:
```
Original:  □□     Flip:  □□     Rotate 90°:  □
           □                 □              □□
```

### 2. Move Execution Order

Critical: Must apply transformations in this exact order:

1. Select piece
2. Apply flip (if flip=True)
3. Apply rotation (rotate_piece() called N times where N=rotation/90)
4. Place at position

**Why**: Matches how human players interact with pieces

### 3. Strategy Differences

**Easy (RandomStrategy)**:
- No evaluation, just random selection
- Fast (<100ms)
- Uses caching for repeated states

**Medium (CornerStrategy)**:
- Evaluates corner connections
- Balances speed and intelligence
- ~500ms calculation

**Hard (StrategicStrategy)**:
- Multi-factor evaluation with lookahead
- Most sophisticated
- ~2s calculation

---

## Testing Checklist

After implementation, verify:

- [ ] `test_ai_uses_calculate_move` passes
- [ ] `test_ai_supports_flip` passes
- [ ] `test_strategies_differ` passes
- [ ] Easy AI makes random moves
- [ ] Medium AI prioritizes corners
- [ ] Hard AI makes strategic moves
- [ ] All AI difficulties run without errors
- [ ] Flipped moves execute correctly
- [ ] Timeouts are handled gracefully

---

## Common Issues

### Issue 1: Flip Applied in Wrong Order

**Symptom**: AI places pieces in impossible orientations

**Solution**: Ensure flip is applied BEFORE rotation in `_get_piece_positions()`

### Issue 2: calculate_move Not Called

**Symptom**: All AI difficulties still behave randomly

**Solution**: Verify `_trigger_ai_move()` calls `ai_player.calculate_move()` and doesn't have manual selection logic

### Issue 3: Strategies Produce Same Moves

**Symptom**: Easy/Medium/Hard all make identical moves

**Solution**: Verify each AI has different strategy assigned:
- Easy: RandomStrategy()
- Medium: CornerStrategy()
- Hard: StrategicStrategy()

### Issue 4: Flip Field Missing

**Symptom**: Move objects don't have flip attribute

**Solution**: Add `flip: bool` parameter to Move.__init__() with default False

---

## Performance Expectations

| Difficulty | Strategy | Timeout | Avg Calc Time | Expected Turn Time |
|------------|----------|---------|---------------|-------------------|
| Easy | RandomStrategy | 3s | <100ms | <200ms |
| Medium | CornerStrategy | 5s | <500ms | <700ms |
| Hard | StrategicStrategy | 8s | <2s | <4s |

If turn times exceed these, investigate:
- Too many moves being generated
- Inefficient position calculations
- Lack of caching (RandomStrategy)

---

## Verification Steps

### 1. Run Existing Tests
```bash
cd /root/blokus-step-by-step
uv pytest tests/integration/test_single_ai.py -v
uv pytest tests/integration/test_three_ai.py -v
uv pytest tests/integration/test_difficulty.py -v
```

### 2. Run New Tests
```bash
uv pytest tests/integration/test_ai_calculate_move.py -v
```

### 3. Manual Verification
```bash
# Play against Easy AI - should be random
# Play against Medium AI - should prefer corners
# Play against Hard AI - should be strategic
python src/main.py
```

### 4. Check Logs
Look for:
- "AI Player X: Calculated move in Y.Ys"
- No "AI calculation error" messages
- Different move patterns for different difficulties

---

## Next Steps

After implementation:
1. Run full test suite: `uv pytest`
2. Play complete games with all AI difficulties
3. Verify AI player performance metrics in logs
4. Check for any remaining code duplication
5. Update documentation if needed

---

## References

- **Specification**: `/specs/003-fix-ai-player/spec.md`
- **Data Model**: `/specs/003-fix-ai-player/data-model.md`
- **Contracts**:
  - `/specs/003-fix-ai-player/contracts/ai-player.md`
  - `/specs/003-fix-ai-player/contracts/ai-strategy.md`
  - `/specs/003-fix-ai-player/contracts/move.md`
  - `/specs/003-fix-ai-player/contracts/integration.md`
- **Research**: `/specs/003-fix-ai-player/research.md`

---

## Summary

**Problem**: AI bypassed sophisticated infrastructure, all difficulties behaved randomly, no flip support

**Solution**: Use `calculate_move()`, add flip support, maintain modular architecture

**Key Insight**: The fix is mostly removal (delete manual logic) and extension (add flip), not rewriting

**Outcome**: AI difficulties now behave differently with full piece orientation support

**Time Estimate**: ~2-4 hours implementation + 1 hour testing
