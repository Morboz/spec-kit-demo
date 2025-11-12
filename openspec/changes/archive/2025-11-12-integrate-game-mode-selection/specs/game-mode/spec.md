# Game Mode Capability - Delta Specification

## Overview
This delta extends the game mode capability to support PvP local multiplayer mode alongside existing AI battle modes.

## ADDED Requirements

### Requirement: PvP Local Multiplayer Mode
The GameMode system SHALL support local PvP multiplayer configuration with 2-4 players.

**Type:** ADDED
**Rationale:** Users want to play traditional multiplayer Blokus without AI opponents in the unified mode selector.

#### Scenario: Creating 2-Player PvP Mode
- **Given** the game mode system
- **When** creating a PvP mode with 2 players
- **Then** the configuration should have:
  - human_player_position set to None (all players are human)
  - ai_players list empty
  - total player count of 2

#### Scenario: Creating 4-Player PvP Mode
- **Given** the game mode system
- **When** creating a PvP mode with 4 players
- **Then** the configuration should have:
  - human_player_position set to None
  - ai_players list empty
  - total player count of 4

### Requirement: PvP Mode Factory Method
The GameMode class SHALL provide a factory method for creating PvP local configurations.

**Type:** ADDED
**Signature:**
```python
@classmethod
def pvp_local(cls, player_count: int = 2) -> "GameMode"
```

#### Scenario: Creating PvP Mode via Factory Method
- **Given** GameMode class
- **When** calling GameMode.pvp_local(3)
- **Then** it returns a GameMode instance with:
  - mode_type = GameModeType.PVP_LOCAL
  - human_player_position = None
  - ai_players = []
  - player count = 3

### Requirement: PvP Mode Validation
The GameMode validation SHALL enforce PvP-specific constraints.

**Type:** ADDED
**Constraints:**
- Player count MUST be between 2 and 4 inclusive
- No AI players allowed (ai_players MUST be empty)
- human_player_position MUST be None

#### Scenario: Validating PvP Mode with 3 Players
- **Given** a GameMode with PVP_LOCAL and 3 players
- **When** calling validate()
- **Then** it returns True

#### Scenario: Invalidating PvP Mode with 1 Player
- **Given** a GameMode with PVP_LOCAL and 1 player
- **When** calling validate()
- **Then** it returns False with validation error

#### Scenario: Invalidating PvP Mode with AI Players
- **Given** a GameMode with PVP_LOCAL and AI players configured
- **When** calling validate()
- **Then** it returns False with validation error

## MODIFIED Requirements

### Requirement: GameModeType Enum Extension
The GameModeType enum SHALL include PVP_LOCAL mode alongside existing AI modes.

**Type:** MODIFIED
**Added Value:**
```python
PVP_LOCAL = "pvp_local"
```

**Rationale:** PvP mode is a distinct mode type that requires different handling than AI modes.

#### Scenario: PvP Mode Type Exists
- **Given** GameModeType enum
- **When** accessing GameModeType.PVP_LOCAL
- **Then** it returns the value "pvp_local"

### Requirement: GameMode.is_ai_turn() for PvP Mode
The is_ai_turn() method SHALL return False for all players in PvP mode.

**Type:** MODIFIED
**Current Behavior:** Returns False if current player matches human_player_position
**New Behavior:** In PvP mode, all players are human, so ALWAYS return False

**Rationale:** PvP mode has no AI players, so no turn should ever be AI-controlled.

#### Scenario: PvP Mode Never Has AI Turn
- **Given** a PvP mode game state
- **When** checking is_ai_turn() for any player (1-4)
- **Then** it returns False

## REMOVED Requirements

None.

## Technical Details

### Data Model Changes
- Add GameModeType.PVP_LOCAL enum value
- Add GameMode.pvp_local() class method
- Update GameMode.validate() to handle PvP validation rules
- Update GameMode.is_ai_turn() to handle PvP mode (return False)

### Backward Compatibility
- Existing AI modes (SINGLE_AI, THREE_AI, SPECTATE) remain unchanged
- Existing factory methods (single_ai, three_ai, spectate_ai) remain functional
- Existing validation logic for AI modes preserved
- PvP mode is an additive extension only

### Player Configuration for PvP Mode
```python
# PvP mode configuration
mode_type = GameModeType.PVP_LOCAL
human_player_position = None  # All players are human
ai_players = []  # No AI players
player_names = ["Player 1", "Player 2", ...]  # Set by user
```

## References
- Base specification: GameMode class in `src/blokus_game/models/game_mode.py`
- Related: UnifiedGameModeSelector component specification
