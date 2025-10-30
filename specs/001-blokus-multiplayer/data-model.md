# Data Model: Blokus Game

**Feature**: Blokus Local Multiplayer Game
**Phase**: 1 - Design and Contracts
**Date**: 2025-10-30

## Entities

### 1. Game Board

**Purpose**: Represents the 20x20 grid where pieces are placed during gameplay.

**Fields**:
- `size`: integer (always 20) - Board dimension
- `grid`: 2D array [20][20] of PlayerID or None - Occupancy state
  - None: Empty square
  - PlayerID: Square occupied by specific player
- `starting_corners`: dict - Mapping of PlayerID to (row, col) corner positions
  - Player 1: (0, 0)
  - Player 2: (0, 19)
  - Player 3: (19, 19)
  - Player 4: (19, 0)

**Validation Rules**:
- Grid must initialize as 20x20 with all None values
- Starting corners must be at board edges (0,0), (0,19), (19,19), (19,0)

**State Transitions**:
- `initialize()`: Sets up empty board with starting corners
- `place_piece(player_id, piece, position)`: Marks grid positions as occupied by player
- `is_occupied(row, col)`: Returns True if square has a piece
- `is_within_bounds(row, col)`: Returns True if position is on board

---

### 2. Blokus Piece

**Purpose**: Represents a geometric piece that players place on the board.

**Fields**:
- `name`: string - Unique identifier (e.g., "I1", "L4", "X5")
- `coordinates`: list of (row, col) tuples - Shape definition relative to origin (0,0)
- `size`: integer - Number of squares in piece
- `color`: string - Player-specific color for rendering
- `is_placed`: boolean - Whether piece has been placed on board
- `placed_position`: (row, col) or None - Where piece was placed if is_placed is True

**Derived Properties**:
- `rotated(angle)`: Returns new Piece instance with coordinates rotated
- `flipped()`: Returns new Piece instance with coordinates mirrored horizontally
- `get_absolute_positions(anchor_row, anchor_col)`: Returns actual board positions

**Validation Rules**:
- Coordinates must define connected shape (no gaps)
- Size must match number of coordinate pairs
- Each piece has exactly one of 21 predefined shapes

**Standard Pieces** (21 total):
```
I1: [(0,0)]
I2: [(0,0), (1,0)]
I3: [(0,0), (1,0), (2,0)]
I4: [(0,0), (1,0), (2,0), (3,0)]
I5: [(0,0), (1,0), (2,0), (3,0), (4,0)]
L4: [(0,0), (0,1), (0,2), (1,2)]
L5: [(0,0), (0,1), (0,2), (0,3), (1,3)]
T4: [(0,0), (0,1), (0,2), (1,1)]
Z4: [(0,0), (0,1), (1,1), (1,2)]
Z5: [(0,0), (0,1), (1,1), (1,2), (2,2)]
V3: [(0,0), (1,0), (1,1)]
V4: [(0,0), (1,0), (2,0), (2,1)]
V5: [(0,0), (1,0), (2,0), (3,0), (3,1)]
U5: [(0,0), (0,1), (1,0), (1,2), (0,2)]
T5: [(0,0), (0,1), (0,2), (1,1), (2,1)]
W5: [(0,0), (1,0), (1,1), (2,1), (2,2)]
X5: [(1,0), (0,1), (1,1), (2,1), (1,2)]
Y5: [(0,0), (1,0), (2,0), (3,0), (2,1)]
F5: [(1,0), (2,0), (0,1), (1,1), (1,2)]
P5: [(0,0), (1,0), (0,1), (1,1), (0,2)]
W4: [(0,0), (1,0), (1,1), (2,1)]
```

---

### 3. Player

**Purpose**: Represents a game participant with their pieces and game state.

**Fields**:
- `player_id`: integer (1-4) - Unique identifier
- `name`: string - Player's display name
- `color`: string - Hex color code for UI (#FF0000, #00FF00, etc.)
- `score`: integer (default: 0) - Current game score
- `pieces`: list of Piece objects - All 21 pieces, initially unplaced
- `starting_corner`: (row, col) - Board corner where first piece must be placed
- `has_made_first_move`: boolean (default: False) - Tracks if first turn completed

**Validation Rules**:
- player_id must be unique within game
- name cannot be empty
- color must be valid hex code
- Player starts with exactly 21 pieces
- Each piece assigned to exactly one player

**State Transitions**:
- `place_piece(piece, position)`: Marks piece as placed, updates score
- `get_available_pieces()`: Returns list of unplaced pieces
- `get_score()`: Calculates current score based on placed pieces

**Calculated Properties**:
- `placed_squares`: Total squares from placed pieces
- `unplaced_pieces_count`: Number of pieces remaining
- `can_make_move(board)`: Checks if any valid moves exist

---

### 4. Game State

**Purpose**: Contains the complete state of the game including board, players, and turn information.

**Fields**:
- `board`: Board object - The game board instance
- `players`: list of Player objects - All players in order
- `current_player_index`: integer - Index of player whose turn it is (0-based)
- `game_phase`: enum - "setup", "playing", or "ended"
- `game_history`: list of Move objects - Chronological record of all moves
- `skipped_turns_count`: integer - Consecutive turns skipped
- `winner`: Player or None - Winner when game ends

**Validation Rules**:
- Must have 2-4 players
- Game phase determines valid actions
- current_player_index must be within players list
- Game ends when end conditions are met (see Rules section)

**State Transitions**:
- `start_game()`: Changes from "setup" to "playing"
- `next_turn()`: Advances to next player
- `skip_turn()`: Called when player has no valid moves
- `end_game()`: Changes to "ended" state, calculates winner
- `make_move(player, piece, position)`: Validates and records move

**End Game Conditions** (any of):
1. All players have skipped their turn consecutively
2. All players have placed all pieces
3. All players have no valid moves AND no pieces remaining

---

### 5. Turn

**Purpose**: Represents a single turn in the game when a player places one piece.

**Fields**:
- `turn_number`: integer - Sequential turn number
- `player_id`: integer - Player making the move
- `piece`: Piece object - Piece being placed
- `position`: (row, col) - Board position where piece was placed
- `is_valid`: boolean - Whether move passed validation
- `error_message`: string or None - Error if move was invalid
- `timestamp`: datetime - When turn was completed

**Validation Rules**:
- Only one piece can be placed per turn
- Player must be current player
- Position must be valid for piece
- All game rules must be satisfied

**Immutable Record**: Once created, a Turn record does not change (audit trail)

---

## Relationships

```
Game State
├── Board (1:1)
│   └── Grid (20x20 occupancy)
├── Players (1:N)
│   └── Each Player has many Pieces (21 each)
└── Game History (1:N of Turn records)

Player
├── Player ID (unique)
├── Name
├── Color
├── Score (calculated)
└── Pieces (21 Piece objects)

Board
├── Size (20)
├── Grid (2D array)
└── Starting Corners (mapped to Players)

Piece
├── Coordinates (relative positions)
├── Owner (Player)
├── Placed Status
└── Placed Position (if placed)
```

## Data Flow

1. **Game Initialization**:
   - Create Board with empty grid
   - Create 2-4 Players with unique IDs, names, colors
   - Assign 21 Pieces to each Player
   - Set game_phase to "setup"

2. **Turn Cycle**:
   - Current player selects available Piece
   - Player rotates/flips piece (creates transformation)
   - Player selects position on Board
   - Validation checks all rules
   - If valid: Update Board, update Piece, record Turn, advance to next player
   - If invalid: Return error message, same player tries again

3. **Game End**:
   - Check end conditions after each turn
   - Calculate final scores for all players
   - Determine winner (highest score, or tie)
   - Set game_phase to "ended"
   - Record winner in game_state
