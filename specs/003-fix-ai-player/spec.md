# Feature Specification: Fix AI Player Strategy Implementation

**Feature Branch**: `003-fix-ai-player`
**Created**: 2025-11-06
**Status**: Draft
**Input**: User description: "发现ai_player的严重问题： 1. main.py中，ai的三个难度都是随机的move规则。 2. ai_player.py中的calculate_move没有被调用。3. AI move的逻辑需要被正确重构。4. ai_player.py中的calculate_move是不是没有考虑flip 翻转棋子的情况"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Easy AI Uses Random Strategy (Priority: P1)

As a player playing against AI with Easy difficulty, I want the AI to make random valid moves so that the game is challenging but not overwhelming.

**Why this priority**: This is the most critical fix - without it, all AI difficulties behave identically (random), making the difficulty selection meaningless.

**Independent Test**: Can be tested by running a game with Easy AI and verifying moves are random but valid, followed by playing Medium and Hard AI to confirm they behave differently.

**Acceptance Scenarios**:

1. **Given** game state with valid moves available, **When** Easy AI (RandomStrategy) takes its turn, **Then** it selects a random valid move from all available options
2. **Given** game state with no valid moves, **When** Easy AI takes its turn, **Then** it passes the turn
3. **Given** multiple Easy AI players, **When** each takes their turn, **Then** they select different random moves

---

### User Story 2 - Medium AI Uses Corner Strategy (Priority: P1)

As a player playing against AI with Medium difficulty, I want the AI to prioritize corner placement and corner connections so that it plays more strategically than Easy AI.

**Why this priority**: This is core functionality that users expect when selecting Medium difficulty - the AI should demonstrate clear strategic behavior beyond randomness.

**Independent Test**: Can be tested by running games with Medium AI and verifying it consistently prefers corner-adjacent placements compared to random selection.

**Acceptance Scenarios**:

1. **Given** a board state with multiple valid moves, **When** Medium AI (CornerStrategy) takes its turn, **Then** it selects moves that maximize corner connections
2. **Given** a board state where corner placement is possible, **When** Medium AI takes its turn, **Then** it prefers corner-adjacent positions over non-corner positions

---

### User Story 3 - Hard AI Uses Strategic Strategy (Priority: P1)

As a player playing against AI with Hard difficulty, I want the AI to use lookahead and multi-factor evaluation so that it plays optimally and poses the greatest challenge.

**Why this priority**: This is the premium difficulty level that players expect to be genuinely challenging and intelligent.

**Independent Test**: Can be tested by comparing Hard AI moves against Medium/Easy, verifying it makes demonstrably better strategic decisions.

**Acceptance Scenarios**:

1. **Given** a board state with multiple valid moves, **When** Hard AI (StrategicStrategy) takes its turn, **Then** it evaluates moves using multi-factor scoring (corner connections, mobility, area control)
2. **Given** a board state near game end, **When** Hard AI takes its turn, **Then** it makes moves that optimize final score

---

### User Story 4 - AI Supports Piece Flipping (Priority: P2)

As an AI player, I want to be able to flip pieces horizontally in addition to rotating them so that I can utilize the full range of piece orientations available to human players.

**Why this priority**: Human players can flip pieces, and AI should have the same capabilities to ensure fair gameplay. This also increases the number of available strategic options.

**Independent Test**: Can be tested by verifying AI can place pieces in orientations that require flipping (not achievable by rotation alone).

**Acceptance Scenarios**:

1. **Given** a piece that requires flipping to fit in a valid position, **When** any AI difficulty takes its turn, **Then** it can consider the flipped orientation as a valid option
2. **Given** a board state where only flipped orientations are valid, **When** AI takes its turn, **Then** it can successfully place the piece using flip

---

### User Story 5 - AI Uses calculate_move Method (Priority: P1)

As a developer, I want the AI to use the existing `calculate_move()` infrastructure so that the code is consistent, maintainable, and leverages the sophisticated strategy implementations already built.

**Why this priority**: This fixes the architectural disconnect where sophisticated strategy classes exist but aren't being used, leading to code duplication and inconsistent AI behavior.

**Independent Test**: Can be verified by checking that `AIPlayer.calculate_move()` is called during AI turns and returns Move objects that are properly executed.

**Acceptance Scenarios**:

1. **Given** an AI player's turn, **When** the turn is processed, **Then** `ai_player.calculate_move()` is called with proper parameters
2. **Given** `calculate_move()` returns a valid Move, **When** the move is executed, **Then** the piece is placed at the specified position with correct rotation/flip
3. **Given** `calculate_move()` returns None (no moves), **When** the turn is processed, **Then** the AI passes the turn

### Edge Cases

- What happens when AI has only one piece remaining and it cannot be placed in any orientation?
- How does the system handle timeout scenarios when Hard AI calculates moves?
- What occurs when multiple AI players have no valid moves simultaneously?
- How are invalid moves from calculate_move handled (e.g., piece already placed, out of bounds)?
- What happens if flip/rotate operations fail during move execution?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: AI Player's `calculate_move()` method MUST be called during AI turns instead of manual random selection
- **FR-002**: Easy AI (RandomStrategy) MUST select random valid moves from all available options
- **FR-003**: Medium AI (CornerStrategy) MUST prioritize moves that establish corner connections
- **FR-004**: Hard AI (StrategicStrategy) MUST use multi-factor evaluation including lookahead and mobility assessment
- **FR-005**: AI strategies MUST support both rotation (0°, 90°, 180°, 270°) and horizontal flipping of pieces
- **FR-006**: AI move calculation MUST return a valid Move object or None if no valid moves exist
- **FR-007**: Returned Move objects MUST include piece, position, rotation, and flip information
- **FR-008**: main.py's `_trigger_ai_move()` method MUST be refactored to use `ai_player.calculate_move()` instead of manual logic
- **FR-009**: All AI difficulties MUST demonstrate measurably different behavior (move selection patterns)
- **FR-010**: Invalid moves from `calculate_move()` MUST be handled gracefully with fallback to pass or alternative valid move

### Key Entities

- **AIPlayer**: Represents an AI-controlled player with a strategy, capable of calculating moves
- **AIStrategy**: Abstract base class defining the interface for AI strategies
- **Move**: Represents a piece placement action with piece, position, rotation, and flip information
- **RandomStrategy**: Easy difficulty strategy that selects random valid moves
- **CornerStrategy**: Medium difficulty strategy that prioritizes corner connections
- **StrategicStrategy**: Hard difficulty strategy that uses lookahead and multi-factor evaluation

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Easy AI demonstrates random move selection with average calculation time under 100ms
- **SC-002**: Medium AI prioritizes corner connections in 80%+ of moves where corner placement is available
- **SC-003**: Hard AI makes demonstrably superior strategic decisions compared to Medium AI in 70%+ of comparable game states
- **SC-004**: AI supports piece flipping, successfully placing pieces in orientations requiring flip in 100% of test cases
- **SC-005**: AI calculates and executes moves within timeout limits (Easy: 3s, Medium: 5s, Hard: 8s)
- **SC-006**: Three difficulty levels show statistically significant different win rates when competing against each other
- **SC-007**: Code duplication is eliminated by using existing `calculate_move()` infrastructure in 100% of AI turn scenarios

## Assumptions

- Existing strategy classes (RandomStrategy, CornerStrategy, StrategicStrategy) are functionally correct
- The board representation and piece models support flip operations
- Timeout handling in `calculate_move()` is already implemented
- Move validation will continue to be handled by existing placement validation logic

## Dependencies

- Requires BlokusRules.get_valid_moves() for comprehensive move validation
- Depends on piece rotation and flip methods in piece model
- Integrates with existing game state and placement handler infrastructure
