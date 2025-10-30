# Feature Specification: Blokus Local Multiplayer Game

**Feature Branch**: `001-blokus-multiplayer`
**Created**: 2025-10-30
**Status**: Draft
**Input**: User description: "开发一个可以本地多人游玩的Blokus游戏"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Game Setup (Priority: P1)

Players set up a new Blokus game by selecting the number of players (2-4), entering player names, and choosing their colors. The game board initializes with all pieces available.

**Why this priority**: No game can be played without proper initialization. This is the foundation for all other features.

**Independent Test**: Can be fully tested by starting a new game, verifying the board appears empty, all player pieces are available, and the system clearly identifies whose turn it is.

**Acceptance Scenarios**:

1. **Given** the game launcher, **When** 2-4 players start a new game and enter names, **Then** the game board displays correctly with each player assigned a color and starting position.

2. **Given** players have set up the game, **When** the game begins, **Then** Player 1's turn is clearly indicated and all 21 pieces are available for that player.

---

### User Story 2 - Placing a Piece (Priority: P1)

On a player's turn, they select one of their available pieces, rotate/flip it as needed, position it on the board following Blokus rules, and confirm the placement. The system validates the move and updates the game state.

**Why this priority**: This is the core gameplay mechanic. Without the ability to place pieces, the game cannot exist.

**Independent Test**: Can be fully tested by having a single player attempt various piece placements, verifying valid placements are accepted and invalid placements are rejected with clear messages.

**Acceptance Scenarios**:

1. **Given** it's a player's turn, **When** they select a piece, rotate/flip it, place it on a valid position on the board, and confirm, **Then** the piece appears on the board, is removed from their available pieces, and the turn passes to the next player.

2. **Given** it's a player's turn, **When** they attempt to place a piece that violates Blokus rules (wrong starting position for first move, overlapping existing pieces, or touching own pieces corner-to-corner only), **Then** the system rejects the placement and displays a clear error message explaining which rule was violated.

---

### User Story 3 - Game State Visibility (Priority: P1)

At any time during the game, players can clearly see the current game state: whose turn it is, what pieces each player has remaining, the current score, and the board layout.

**Why this priority**: Players must understand the current state to make informed decisions. This is essential for fair gameplay and game flow.

**Independent Test**: Can be fully tested by checking that all game information is visible and clearly organized, showing active player, piece inventory, and board state.

**Acceptance Scenarios**:

1. **Given** a game in progress, **When** any player views the board, **Then** they can clearly see whose turn it is, which pieces each player has remaining, and the current score for all players.

2. **Given** a game in progress, **When** a player examines their available pieces, **Then** they can easily identify which pieces they've already placed and which are still available.

---

### User Story 4 - Game End and Winner Determination (Priority: P1)

The game automatically detects when it should end (all players have no valid moves or no pieces remaining), calculates final scores based on placed pieces and remaining pieces, and declares the winner.

**Why this priority**: Every game must have a clear conclusion with accurate scoring. Without this, players cannot determine who won.

**Independent Test**: Can be fully tested by playing through to game end and verifying the winner is correctly identified based on Blokus scoring rules.

**Acceptance Scenarios**:

1. **Given** the end-game conditions are met, **When** the game completes, **Then** final scores are calculated correctly and the winner (or tie) is announced clearly to all players.

2. **Given** the final scores are displayed, **When** players review the results, **Then** they can see a breakdown of how scores were calculated (points for placed squares, deductions for unplaced pieces).

---

### User Story 5 - Turn-Based Gameplay Flow (Priority: P2)

Players take turns in sequence (Player 1 → Player 2 → etc.). After each successful piece placement, the turn automatically passes to the next player. If a player has no valid moves, they skip their turn.

**Why this priority**: This ensures fair, orderly gameplay and prevents confusion about whose turn it is.

**Independent Test**: Can be fully tested by observing multiple full turns, verifying turns pass correctly and players are only active on their turn.

**Acceptance Scenarios**:

1. **Given** Player 1 has just placed a piece, **When** the move is confirmed, **Then** the turn passes to Player 2, and Player 1 cannot make additional moves until their next turn.

2. **Given** it's a player's turn and they have no valid moves available, **When** they skip their turn, **Then** the turn passes to the next player, and this is clearly indicated in the game log.

---

### User Story 6 - Rule Enforcement (Priority: P2)

The game strictly enforces all official Blokus rules: first move must be in a player's starting corner, pieces can only touch other pieces at corners (not edges), and pieces cannot overlap or go outside the board.

**Why this priority**: Correct rule enforcement is what makes the game authentic and enjoyable. Invalid moves ruin the game experience.

**Independent Test**: Can be fully tested by attempting various invalid moves and verifying they are all rejected with appropriate error messages.

**Acceptance Scenarios**:

1. **Given** it's a player's first turn, **When** they attempt to place a piece anywhere except their starting corner, **Then** the system rejects the move and displays a message explaining the first-move rule.

2. **Given** a player attempts to place a piece, **When** the piece would touch one of their existing pieces edge-to-edge, **Then** the system rejects the placement and explains the corner-only rule.

---

### User Story 7 - Score Tracking and Display (Priority: P3)

Throughout the game, running scores are displayed and updated after each move. Players can see how their score changes based on their placements and can compare scores with other players.

**Why this priority**: While not essential for basic gameplay, score tracking adds competitive element and helps players understand their performance.

**Independent Test**: Can be fully tested by placing various pieces and verifying the score changes match the expected Blokus scoring rules.

**Acceptance Scenarios**:

1. **Given** a player places a piece, **When** the placement is confirmed, **Then** their score updates correctly based on the number of squares placed, and all players can see the updated scoreboard.

2. **Given** the game displays scores, **When** players compare scores, **Then** they can understand how each player's score was calculated (squares placed minus penalties for remaining pieces).

---

### Edge Cases

- What happens when multiple players have no valid moves but still have pieces remaining?
- How does the game handle the last piece placement when a player places their final piece?
- What if a player attempts to undo a move after confirmation?
- How are ties handled when multiple players have the same final score?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST support 2-4 players in a single game session on one device
- **FR-002**: System MUST provide a 20x20 game board for piece placement
- **FR-003**: System MUST include all 21 Blokus pieces for each player (I1, I2, I3, I4, I5, L4, L5, T4, Z4, Z5, V3, V4, V5, U5, T5, W5, X5, Y5, F5, P5, W4)
- **FR-004**: System MUST enforce turn-based gameplay with clear indication of current player
- **FR-005**: System MUST allow players to rotate and flip pieces before placement
- **FR-006**: System MUST validate all moves against official Blokus rules
- **FR-007**: System MUST reject invalid moves with clear, actionable error messages
- **FR-008**: System MUST automatically skip players who have no valid moves
- **FR-009**: System MUST calculate scores according to Blokus rules (1 point per placed square, -5 points per unplaced piece)
- **FR-010**: System MUST detect game end conditions (all players skip turn OR all players have no pieces OR all pieces placed)
- **FR-011**: System MUST display current game state including board, scores, available pieces, and current player
- **FR-012**: System MUST prevent players from taking actions during other players' turns

### Key Entities

- **Game Board**: A 20x20 grid where pieces are placed, with tracking of occupied squares by player
- **Blokus Piece**: A geometric shape defined by coordinates, with properties for rotation, flip, and color
- **Player**: A game participant with name, color, score, starting corner position, and collection of pieces
- **Game State**: The current status including turn order, scores, board occupancy, and game phase (setup/playing/ended)
- **Turn**: A game phase where one player selects, positions, and places one piece on the board

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Four players can complete a full game from start to finish in under 45 minutes, including setup and gameplay
- **SC-002**: 100% of invalid moves are detected and rejected with error messages explaining the specific rule violation
- **SC-003**: Game state is always accurate, with all players able to see correct board, scores, and piece availability
- **SC-004**: First move rule is correctly enforced: every player's first piece must be placed in their assigned corner and touching that corner
- **SC-005**: Piece adjacency rule is correctly enforced: a player's pieces may only touch their own pieces at corners, never at edges
- **SC-006**: Final scores are calculated correctly for all players based on standard Blokus scoring
- **SC-007**: Players can identify whose turn it is and what actions are available to them within 2 seconds of any game state