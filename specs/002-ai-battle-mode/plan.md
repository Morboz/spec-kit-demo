# Implementation Plan: AI Battle Mode

**Branch**: `002-ai-battle-mode` | **Date**: 2025-11-03 | **Spec**: [link](spec.md)
**Input**: Feature specification from `/specs/002-ai-battle-mode/spec.md`

## Summary

**Primary Requirement**: Add AI-powered gameplay modes to the Blokus game, supporting Single AI, Three AI, and Spectate AI modes. AI players must follow all Blokus rules and operate autonomously with configurable difficulty levels.

**Technical Approach**: Extend existing Python/tkinter game with AI player entities that implement three strategy levels (Easy: random, Medium: corner-focused, Hard: strategic). Game mode selection UI added to allow users to choose AI opponents. Turn controller enhanced to manage automatic AI moves without human intervention.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: tkinter (standard library)
**Storage**: N/A (in-memory game state, no persistence required)
**Testing**: pytest (testing framework)
**Target Platform**: Desktop GUI application
**Project Type**: Single desktop application
**Performance Goals**: AI move calculation within 3-8 seconds (difficulty dependent)
**Constraints**: Must maintain real-time game flow; AI cannot block UI; all Blokus rules must be followed
**Scale/Scope**: 4-player game support (human + up to 3 AI); 3 AI strategy implementations

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] Principle I: Incremental Development - Implementation broken into small, verifiable steps
  - Phase 1: UI for game mode selection
  - Phase 2: AI player entity and basic random strategy
  - Phase 3: Corner-focused strategy (Medium)
  - Phase 4: Strategic AI (Hard)
  - Phase 5: Three AI mode and Spectate mode
  - Phase 6: Integration testing and refinement

- [x] Principle II: Test-First Development - TDD approach planned for all game logic
  - Tests for AI move generation (all three strategies)
  - Tests for AI rule compliance
  - Tests for game mode selection
  - Tests for automatic turn progression
  - Tests for difficulty setting persistence

- [x] Principle III: Modular Architecture - Clear separation of board, pieces, players, rules
  - AIPlayer as distinct module from HumanPlayer
  - AIStrategy as pluggable interface
  - TurnController extended but not modified in core logic
  - GameMode configuration isolated from game engine

- [x] Principle IV: Rules Compliance - Plan to implement exact Blokus rules with validation
  - AI must validate moves against existing rule engine
  - No special cases - AI uses same validation as human players
  - Pass turn when no valid moves available
  - Corner connection and adjacency rules enforced

- [x] Principle V: Clear Documentation - Documentation approach defined for all interfaces
  - AIPlayer API documented with examples
  - AIStrategy interface with implementation guide
  - Game mode selection flow documented
  - Quickstart guide for running AI battles

**Post-Design Re-evaluation**: All principles remain satisfied. Design artifacts (data-model.md, contracts/, quickstart.md) provide clear implementation guidance without implementation details.

## Project Structure

### Documentation (this feature)

```text
specs/002-ai-battle-mode/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
│   ├── ai-player.contract
│   ├── ai-strategy.contract
│   ├── game-mode.contract
│   └── turn-controller.contract
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
src/
├── models/
│   ├── game_state.py    # Existing: game state management
│   ├── player.py        # Existing: Player class
│   └── ai_player.py     # New: AIPlayer entity with strategy
├── services/
│   ├── game_engine.py   # Existing: core game logic
│   ├── move_validator.py # Existing: Blokus rules validation
│   └── ai_strategy.py   # New: Strategy interface and implementations
├── ui/
│   ├── main_menu.py     # Existing: game menu
│   └── game_mode_selector.py # New: UI for selecting AI modes
└── game.py              # Existing: main game orchestrator

tests/
├── unit/
│   ├── test_ai_player.py        # New: AI player tests
│   ├── test_ai_strategies.py    # New: strategy behavior tests
│   └── test_game_mode_selector.py # New: UI tests
└── integration/
    └── test_ai_battle_modes.py  # New: end-to-end AI mode tests
```

**Structure Decision**: Single project structure with clear separation between AI logic (ai_player.py, ai_strategy.py) and existing game components. New files isolated to allow independent testing and development.

## Phase 0: Research Tasks ✅ COMPLETED

### AI Strategy Research ✅
- ✅ Research optimal Blokus opening strategies for corner-focused AI (Medium difficulty)
- ✅ Research evaluation functions for strategic AI (Hard difficulty)
- ✅ Research board representation techniques for efficient move generation
- ✅ Research timeout handling for AI calculations to maintain game flow

### Implementation Patterns ✅
- ✅ Research strategy pattern implementation in Python for AI difficulty levels
- ✅ Research event-driven architecture for automatic turn progression
- ✅ Research Tkinter menu extensions for game mode selection

**Research Output**: [research.md](research.md) contains comprehensive findings on AI strategies, implementation patterns, and design decisions.

## Phase 1: Design & Contracts ✅ COMPLETED

### Design Artifacts Created:

1. **data-model.md**: Entity definitions and relationships
   - AIPlayer entity with strategy and state management
   - AIStrategy interface with three implementations
   - GameMode configuration for different battle types
   - Extended TurnController for AI-aware turn progression
   - Complete validation rules and error handling

2. **contracts/**: Interface specifications
   - ai-player.contract: AIPlayer class interface
   - ai-strategy.contract: Strategy pattern implementation
   - game-mode.contract: Game mode configuration
   - turn-controller.contract: Extended turn management
   - All contracts include usage examples and compliance requirements

3. **quickstart.md**: Developer implementation guide
   - Step-by-step implementation instructions
   - Test-first development approach
   - Performance testing guidelines
   - Debugging tips and common issues
   - Integration examples with existing game

### Agent Context Updated ✅
- Updated CLAUDE.md with Python 3.11+ and tkinter dependencies
- Added feature-specific technology stack information
- Maintained manual additions section intact

**Design Outcome**: Complete implementation blueprint ready for Phase 2 task generation.

## Phase 2: Task Generation (Next)

**To be completed by**: `/speckit.tasks` command

**Output**: tasks.md with implementation tasks organized by user story priority:
- P1: Single AI mode with basic strategy
- P2: Three AI mode extension
- P3: Difficulty settings
- P4: Spectate mode
- Integration testing and validation

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations at this time. All principles can be followed with the proposed incremental approach.

**Post-Design Status**: No changes to complexity assessment. All design decisions align with Constitution principles:
- Incremental development supported by phased approach
- Test-first development detailed in quickstart guide
- Modular architecture clearly defined in contracts
- Rules compliance enforced through existing validators
- Clear documentation provided in quickstart and contracts

## Next Steps

1. Run `/speckit.tasks` to generate implementation tasks
2. Begin Phase 3: Implementation following TDD approach
3. Validate each task independently before proceeding
4. Update tests and documentation as implementation progresses

## References

- **Feature Specification**: [spec.md](spec.md)
- **Research Findings**: [research.md](research.md)
- **Data Model**: [data-model.md](data-model.md)
- **Quickstart Guide**: [quickstart.md](quickstart.md)
- **Contracts**: [contracts/](contracts/)
- **Agent Context**: /root/blokus-step-by-step/CLAUDE.md
