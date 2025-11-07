# Research: AI Battle Mode Implementation

**Date**: 2025-11-03
**Feature**: AI Battle Mode for Blokus Game

## Research Findings

### 1. Blokus AI Strategies

#### Corner-Focused Strategy (Medium Difficulty)

**Decision**: Implement corner-priority algorithm with evaluation scoring

**Rationale**: In Blokus, corner placement is critical because:
- First piece MUST be placed in player's corner (standard rule)
- Subsequent pieces connect ONLY at corners (never edges)
- Corners provide multiple connection opportunities
- Corner control leads to better board coverage

**Implementation Approach**:
1. Generate all valid moves using existing validator
2. Score each move based on:
   - Proximity to player's existing corners (higher score for connecting to 2+ corners)
   - Distance from board edge (prefer outside positions for expansion)
   - Piece size (prefer larger pieces for corner placement to maximize coverage)
3. Select move with highest score
4. Pass if no corner connections possible

#### Strategic AI (Hard Difficulty)

**Decision**: Implement minimax-like evaluation with board control metrics

**Rationale**: Advanced Blokus AI requires:
- Multi-move lookahead for position evaluation
- Balance between expansion and blocking opponents
- Endgame optimization when pieces are limited

**Implementation Approach**:
1. Evaluate board state using multiple factors:
   - Area control: number of squares controlled
   - Corner connections: number of corner connections established
   - Mobility: number of valid moves available
   - Territory advantage: differential score vs opponents
2. Apply different weights based on game phase:
   - Opening: prioritize corner establishment and expansion
   - Mid-game: balance area control with opponent blocking
   - Endgame: optimize for point maximization
3. Use shallow lookahead (2-3 moves) with alpha-beta pruning
4. Implement timeout to ensure moves complete within 8 seconds

### 2. Board Representation & Move Generation

**Decision**: Use 2D array representation with efficient move validation

**Rationale**: Board games benefit from:
- Direct coordinate access for piece placement
- Fast validation for real-time AI calculations
- Simple adjacency and corner detection

**Implementation Details**:
- Board: 2D list (20x20 grid for Blokus)
- Each cell stores: None (empty) or player ID (occupied)
- Valid move check:
  1. For each available piece
  2. For each rotation (0°, 90°, 180°, 270°)
  3. For each board position where piece fits
  4. Verify corner connection rule: at least one corner touches existing piece
  5. Verify no edge adjacency: no edge touches same-color piece
- Optimization: Pre-compute valid moves at turn start for Easy/Medium strategies

### 3. Strategy Pattern Implementation

**Decision**: Use abstract base class with concrete implementations

**Rationale**: Strategy pattern provides:
- Clean separation between AI logic levels
- Easy to add new strategies later
- Consistent interface for TurnController
- Testable in isolation

**Implementation Structure**:
```python
from abc import ABC, abstractmethod

class AIStrategy(ABC):
    @abstractmethod
    def calculate_move(self, board, pieces, player_id) -> Move:
        """Calculate best move for current board state"""
        pass

    @abstractmethod
    def get_timeout_seconds(self) -> int:
        """Return maximum calculation time in seconds"""
        pass

class RandomStrategy(AIStrategy):
    """Easy: Random valid placement"""
    pass

class CornerStrategy(AIStrategy):
    """Medium: Prioritize corner connections"""
    pass

class StrategicStrategy(AIStrategy):
    """Hard: Multi-factor evaluation with lookahead"""
    pass
```

### 4. Timeout Handling

**Decision**: Implement time-based timeout with fallback to best known move

**Rationale**: Maintain game flow while allowing AI calculation time:
- Hard difficulty needs more time for strategic analysis
- Timeout ensures UI remains responsive
- Fallback prevents game from stalling

**Implementation Approach**:
1. Record start time when AI turn begins
2. Check elapsed time before expensive operations
3. If timeout reached:
   - Return best move found so far (for Hard AI)
   - Return any valid move (for Easy/Medium)
4. Use threading or async to prevent UI blocking
5. Display "AI thinking..." indicator during calculation

### 5. Event-Driven Turn Progression

**Decision**: Extend existing TurnController with AI-aware logic

**Rationale**: Avoid modifying core game engine:
- Existing TurnController handles human turns
- Add AI player check before waiting for input
- Automatically trigger AI calculation when it's an AI's turn
- Maintain existing UI update mechanisms

**Implementation Flow**:
1. TurnController checks current player type (human vs AI)
2. If AI player:
   - Disable human input
   - Call AIPlayer.calculate_move() with timeout
   - Animate piece placement
   - Update board state
   - Proceed to next turn
3. If human player:
   - Use existing flow (wait for click)

### 6. Tkinter Menu Extensions

**Decision**: Add game mode selection dialog before game start

**Rationale**: User experience enhancement:
- Clear choice between human vs AI opponents
- Difficulty selection affects all AI players
- Spectate mode provides additional value

**UI Components**:
- Radio buttons for game mode: Single AI, Three AI, Spectate AI
- Dropdown for difficulty: Easy, Medium, Hard
- Start Game button with mode configuration
- Clear visual distinction for AI players (e.g., "AI Player 2 (Medium)")

## Alternatives Considered

### Alternative 1: Neural Network-based AI
**Rejected Because**:
- Requires training data or reinforcement learning
- Too complex for initial implementation
- Difficult to debug and verify rule compliance
- Performance unpredictable

### Alternative 2: Monte Carlo Tree Search (MCTS)
**Rejected Because**:
- More suitable for deterministic turn-based games with perfect information
- Blokus has large branching factor, making MCTS expensive
- Harder to implement timeout guarantees
- Evaluation function still needed for selection

### Alternative 3: Pre-computed Opening Book
**Rejected Because**:
- Only helps with opening moves (first few turns)
- Doesn't address mid-game or endgame strategy
- Requires manual curation of opening sequences
- Limited applicability beyond opening

## Conclusion

The chosen approach provides:
- **Correctness**: Uses existing validation rules, no rule violations
- **Performance**: Efficient board representation with timeouts
- **Maintainability**: Strategy pattern enables easy testing and extension
- **User Experience**: Multiple difficulty levels and game modes
- **Incremental Development**: Each strategy can be implemented and tested independently

**Next Steps**: Proceed to Phase 1 design with these findings to create data model and contracts.
