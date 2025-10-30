# Research: Blokus Game Implementation

**Date**: 2025-10-30
**Feature**: Blokus Local Multiplayer Game
**Phase**: 0 - Research and Technical Decisions

## Research Findings

### Decision 1: GUI Framework Selection

**Question**: Which Python GUI framework should be used for the Blokus game?

**Options Evaluated**:

| Framework | Pros | Cons | Suitability |
|-----------|------|------|-------------|
| **tkinter** (standard library) | • No external dependencies<br>• Ships with Python<br>• Cross-platform<br>• Simple for 2D games | • Looks dated<br>• Limited advanced graphics<br>• Basic animation support | Good - Simple 2D board game fits well |
| **Pygame** | • Game-focused library<br>• Excellent 2D graphics<br>• Sprite and animation support<br>• Active gaming community | • External dependency<br>• Additional learning curve<br>• More complex than needed | Good - Strong for game logic |
| **PyQt/PySide** | • Modern, polished UI<br>• Rich widget set<br>• Good documentation<br>• Professional appearance | • Licensing complexity (GPL/commercial)<br>• Heavier dependency<br>• Overkill for this scope | Fair - More features than needed |

**Decision**: tkinter

**Rationale**: The Blokus game requires a simple 2D grid-based interface with piece selection and placement. tkinter's capabilities are well-suited for this, and being part of the standard library eliminates external dependencies. The "dated" appearance is acceptable for a strategy board game where functionality matters more than visual polish. This aligns with Constitution Principle I (Incremental Development) by reducing complexity.

**Alternative Rejected**: Pygame - While excellent for games, it introduces unnecessary complexity for a turn-based board game. The additional dependency and learning curve don't justify the benefits for this specific use case.

### Decision 2: Piece Representation

**Question**: How should Blokus pieces be represented and managed?

**Approach**: Each piece defined as a set of coordinates relative to origin (0,0).

**Examples**:
- I1: [(0,0)]
- I2: [(0,0), (1,0)]
- L4: [(0,0), (0,1), (0,2), (1,2)]

**Transformations**:
- Rotation: 90°, 180°, 270° clockwise
- Flip: Horizontal mirror across vertical axis

**Storage**: Pre-defined in config/pieces.py as data structures with metadata (name, size, color)

**Rationale**: Coordinate-based representation is memory-efficient, supports all transformations mathematically, and enables easy collision detection and validation.

### Decision 3: Rule Validation Strategy

**Validation Order** (for move validation):
1. Bounds check - piece fits within 20x20 board
2. Occupancy check - no overlap with existing pieces
3. First-move rule - for new player, piece touches their starting corner
4. Adjacency rule - piece touches own pieces only at corners (not edges)

**Implementation**: Dedicated validator module in game/rules.py with composable validation functions.

**Rationale**: Checking in this order catches most errors early and provides clear error messages by validation stage.

### Decision 4: Testing Strategy

**Test Organization**:
- Unit tests: Each model and game logic component
- Integration tests: Complete game scenarios (full game, turn sequences)
- Property-based tests: Piece transformations (rotation/flip consistency)

**Coverage Goals**: >90% code coverage for game logic modules

**Rationale**: Constitution Principle II (Test-First Development) requires comprehensive testing. Game rules have many edge cases that benefit from automated testing.

## Summary of Technical Decisions

1. **GUI**: tkinter for simplicity and zero dependencies
2. **Architecture**: Modular separation (models, game logic, UI, config)
3. **Piece System**: Coordinate-based representation with mathematical transformations
4. **Validation**: Ordered rule checking with clear error messages
5. **Testing**: pytest with unit and integration tests

## Assumptions Validated

- Offline-only gameplay (no network needed) ✓
- Desktop platform suitable (not web/mobile) ✓
- 2-4 player support needed ✓
- Visual polish less important than functionality ✓

## Open Questions Resolved

Q: Should we support save/load game state?
A: Not in MVP scope. Can be added later as enhancement.

Q: Should pieces have animated movement?
A: Not required. Instant placement is acceptable for turn-based gameplay.
