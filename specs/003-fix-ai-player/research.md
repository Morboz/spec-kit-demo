# Research: AI Player Strategy Implementation

**Date**: 2025-11-06 | **Feature**: Fix AI Player Strategy Implementation

## Research Questions

### 1. Current calculate_move Integration Analysis

**Question**: How does `ai_player.calculate_move()` currently work and what are its inputs/outputs?

**Findings**:
- **Location**: `src/models/ai_player.py:105-252`
- **Inputs**: board (List[List[int]]), pieces (List[Piece]), time_limit (int, optional)
- **Outputs**: Optional[Move] object or None
- **Current State**: Sophisticated implementation exists but is NEVER called in main game loop
- **Integration**: Method exists in AIPlayer class with comprehensive timeout handling, fallback logic, and performance metrics
- **Strategy Usage**: Each AI has a strategy (RandomStrategy, CornerStrategy, StrategicStrategy) accessible via `self.strategy`

**Decision**: Use existing `calculate_move()` method as the primary interface for AI move calculation

---

### 2. Move Object Structure Analysis

**Question**: What fields does the Move object have and does it support flip state?

**Findings**:
- **Location**: `src/services/ai_strategy.py:18-56`
- **Current Fields**:
  - `piece`: Optional[Piece]
  - `position`: Optional[Tuple[int, int]]
  - `rotation`: int (degrees: 0, 90, 180, 270)
  - `player_id`: int
  - `is_pass`: bool
- **Missing**: No flip field - only supports rotation
- **Issue**: Cannot represent flipped orientations that aren't achievable via rotation alone

**Decision**: Add `flip: bool` field to Move object to represent horizontal flip state

---

### 3. Piece Flipping Implementation Analysis

**Question**: How does piece flipping work in the current codebase and what transformations are needed?

**Findings**:
- **Rotation Support**: `src/models/piece.py` - Pieces support rotation via `rotate(90)` method
- **Flip Support**: `src/models/piece.py` - Pieces have `flip()` method for horizontal flipping
- **Placement Handler**: `src/game/placement_handler.py` has `flip_piece()` method that calls piece.flip()
- **Position Calculation**: Currently uses piece.positions (list of relative coordinates)
- **Transformation Needed**: Flipping should be applied BEFORE rotation for all combinations

**Decision**: Apply flip transformation to piece positions before rotation in strategy position calculation

---

### 4. Current _trigger_ai_move Implementation Analysis

**Question**: What does the current `_trigger_ai_move()` do and how should it be refactored?

**Findings**:
- **Location**: `main.py:425-509` (current implementation: 85 lines)
- **Current Behavior**:
  - Manually implements random selection (should use RandomStrategy)
  - Tests rotations manually (0°, 90°, 180°, 270°)
  - Uses BlokusRules.get_valid_moves() for validation
  - Does NOT use `ai_player.calculate_move()` at all
  - Bypasses strategy classes entirely

**Decision**: Replace entire method body with call to `ai_player.calculate_move()` and execute returned Move

---

### 5. AI Strategy Strategy Selection Analysis

**Question**: How are the different difficulty strategies currently selected and used?

**Findings**:
- **Creation**: `main.py:296-301` creates strategies based on difficulty
  - EASY → RandomStrategy()
  - MEDIUM → CornerStrategy()
  - HARD → StrategicStrategy()
- **Assignment**: Strategies assigned to AIPlayer in `main.py:304-312`
- **Current Issue**: Strategies exist but `calculate_move()` on them is never called
- **Available Methods**: Each strategy has `calculate_move()`, `get_available_moves()`, `evaluate_board()`

**Decision**: Ensure main game loop calls `ai_player.calculate_move()` which internally uses the assigned strategy

---

### 6. Game State Integration Analysis

**Question**: How should calculated moves be executed in the game state and placement handler?

**Findings**:
- **Board Representation**: `src/models/board.py` - 2D grid (List[List[int]])
- **Placement Handler**: `src/game/placement_handler.py` handles piece selection, rotation, flip, and placement
- **Current Flow**:
  1. Select piece via `placement_handler.select_piece(piece_name)`
  2. Apply rotations via `placement_handler.rotate_piece()` (multiple calls)
  3. Apply flip via `placement_handler.flip_piece()` if needed
  4. Place piece via `placement_handler.place_piece(row, col)`

**Decision**: After getting Move from calculate_move:
1. Select the piece in placement handler
2. Apply rotations (rotate_piece() called N times)
3. Apply flip if flip=True
4. Place at position

---

### 7. Blokus Piece Coordinate System Analysis

**Question**: How are piece positions represented and how do flip/rotate transformations work?

**Findings**:
- **Piece Representation**: Each piece has `positions` attribute - list of (row, col) tuples relative to piece origin
- **Coordinate System**: (0, 0) is top-left of piece's bounding box
- **Flip Transformation**: For horizontal flip, transform (r, c) → (r, -c)
- **Rotation Transformations**:
  - 0°: (r, c)
  - 90°: (-c, r)
  - 180°: (-r, -c)
  - 270°: (c, -r)
- **Order**: Apply flip first, then rotation (standard Blokus convention)

**Decision**: Modify strategy position calculation to apply transformations in correct order: flip → rotate

---

### 8. Existing AI Test Coverage Analysis

**Question**: What tests exist for AI player and where should new tests be added?

**Findings**:
- **Existing Tests**:
  - `tests/unit/test_ai_player.py` - Basic AI player tests
  - `tests/unit/test_ai_strategy.py` - Strategy tests
  - `tests/integration/test_single_ai.py` - Single AI gameplay
  - `tests/integration/test_three_ai.py` - Multiple AI gameplay
  - `tests/integration/test_difficulty.py` - Difficulty level tests

**Decision**: Add integration tests for:
- calculate_move() being called during gameplay
- Flip support in AI moves
- Different strategies producing different move patterns

---

## Synthesis & Recommendations

### High-Priority Implementation Tasks

1. **Add flip field to Move class** (`src/services/ai_strategy.py`)
   - Add `flip: bool` parameter to Move.__init__()
   - Update __repr__ to include flip state

2. **Update AIStrategy._get_piece_positions()** (`src/services/ai_strategy.py`)
   - Add flip parameter
   - Apply flip transformation before rotation
   - Update all strategy implementations

3. **Refactor main.py:_trigger_ai_move()** (`main.py:425-509`)
   - Replace 85 lines of manual logic with 15 lines using calculate_move()
   - Execute returned Move object properly

4. **Update piece position calculation** in strategies
   - Pass flip flag from Move to position calculation
   - Ensure transformations applied in correct order

### Test-First Development Plan

1. Write tests for Move flip field
2. Write tests for AIStrategy flip support
3. Write integration tests for calculate_move integration
4. Write tests for different strategy behaviors

### Code Complexity Justification

The existing architecture is sound - the issue is simply that sophisticated infrastructure exists but isn't being used. The fix requires:
- Minimal code addition (flip field)
- Major code removal (_trigger_ai_move manual logic)
- No architectural changes
- Clear separation of concerns maintained

## Known Unknowns (Resolved)

All research questions have been answered through codebase analysis. No NEEDS CLARIFICATION markers remain.
