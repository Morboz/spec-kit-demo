# Implementation Plan: Fix AI Player Strategy Implementation

**Branch**: `003-fix-ai-player` | **Date**: 2025-11-06 | **Spec**: /specs/003-fix-ai-player/spec.md
**Input**: Feature specification from `/specs/003-fix-ai-player/spec.md`

## Summary

**Primary Requirement**: Refactor AI player implementation to use existing `calculate_move()` infrastructure and strategy classes (RandomStrategy, CornerStrategy, StrategicStrategy) instead of manual random selection. Add support for piece flipping to ensure AI capabilities match human players.

**Technical Approach**:
- Refactor `main.py:_trigger_ai_move()` to call `ai_player.calculate_move()` instead of implementing manual random selection
- Extend `AIStrategy` and implementations to support both rotation and horizontal flipping
- Ensure Move objects properly represent flipped orientations
- Maintain timeout handling and fallback mechanisms in calculate_move()

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: tkinter (standard library), pytest (testing)
**Storage**: In-memory game state (no persistence required)
**Testing**: pytest with unit, integration, and contract test structure
**Target Platform**: Desktop (tkinter-based GUI application)
**Project Type**: Single desktop application
**Performance Goals**: AI calculations complete within timeout (Easy: 3s, Medium: 5s, Hard: 8s)
**Constraints**: Must maintain existing code structure and modular architecture
**Scale/Scope**: Single-player AI opponent against 1-3 human players

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] Principle I: Incremental Development - Implementation broken into small, verifiable steps
  - Step 1: Refactor _trigger_ai_move to call calculate_move()
  - Step 2: Extend Move to support flip state
  - Step 3: Add flip support to AIStrategy implementations
  - Step 4: Update piece position calculation for flipped orientations
- [x] Principle II: Test-First Development - TDD approach planned for all game logic
  - Write tests for calculate_move integration
  - Write tests for flip support in strategies
  - Write tests for Move object flip state
- [x] Principle III: Modular Architecture - Clear separation of board, pieces, players, rules
  - Maintains existing separation: AIPlayer (models/), AIStrategy (services/), Move (services/)
  - No new modules introduced, only extends existing interfaces
- [x] Principle IV: Rules Compliance - Plan to implement exact Blokus rules with validation
  - AI will use existing BlokusRules for move validation
  - Flipping adheres to standard Blokus piece orientation rules
- [x] Principle V: Clear Documentation - Documentation approach defined for all interfaces
  - Update AI player docstrings to reflect calculate_move usage
  - Document flip parameter in Move class
  - Quickstart guide updates for AI strategy differences

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)
<!--
  ACTION REQUIRED: Replace the placeholder tree below with the concrete layout
  for this feature. Delete unused options and expand the chosen structure with
  real paths (e.g., apps/admin, packages/something). The delivered plan must
  not include Option labels.
-->

```text
# [REMOVE IF UNUSED] Option 1: Single project (DEFAULT)
src/
├── models/
├── services/
├── cli/
└── lib/

tests/
├── contract/
├── integration/
└── unit/

# [REMOVE IF UNUSED] Option 2: Web application (when "frontend" + "backend" detected)
backend/
├── src/
│   ├── models/
│   ├── services/
│   └── api/
└── tests/

frontend/
├── src/
│   ├── components/
│   ├── pages/
│   └── services/
└── tests/

# [REMOVE IF UNUSED] Option 3: Mobile + API (when "iOS/Android" detected)
api/
└── [same as backend above]

ios/ or android/
└── [platform-specific structure: feature modules, UI flows, platform tests]
```

**Structure Decision**: Single desktop application - uses existing structure:
- `src/models/` - Contains AIPlayer
- `src/services/` - Contains AIStrategy and Move
- `src/game/` - Contains game loop (_trigger_ai_move)
- `tests/` - Unit, integration, and contract tests

## Complexity Tracking

No violations. All design decisions align with Constitution principles.

### Why No Complexity Tracking Table Needed

All requirements satisfied through simple, maintainable changes:
1. **No new modules added** - only extends existing interfaces
2. **No new architectural patterns** - maintains separation of concerns
3. **No performance optimizations** - existing infrastructure already optimized
4. **No new dependencies** - uses existing framework and libraries

The fix is primarily a refactor (removing manual logic) rather than adding complexity.

## Re-Evaluation: Constitution Check (Post-Design)

*GATE: Must pass after Phase 1 design.*

- [x] Principle I: Incremental Development - Confirmed: 4-step implementation plan
  - Step 1: Add flip field to Move (isolated change)
  - Step 2: Update position calculation (isolated change)
  - Step 3: Refactor game loop (single method refactor)
  - Step 4: Write tests (independent verification)
- [x] Principle II: Test-First Development - Confirmed: TDD plan documented in contracts
  - Tests written for calculate_move integration
  - Tests for flip support in strategies
  - Integration tests for move execution
- [x] Principle III: Modular Architecture - Confirmed: No architectural changes
  - AIPlayer (models/) → Strategy (services/) → Move (services/) flow maintained
  - Clear interfaces defined in contracts/
  - No circular dependencies introduced
- [x] Principle IV: Rules Compliance - Confirmed: Uses existing validation
  - BlokusRules.get_valid_moves() for move validation
  - Placement handler for execution
  - Flip adheres to standard Blokus rules
- [x] Principle V: Clear Documentation - Confirmed: Comprehensive docs created
  - quickstart.md for implementation guidance
  - contracts/ for interface definitions
  - research.md for technical decisions
  - data-model.md for entity relationships

**Result**: ✅ ALL GATES PASS - Design complies with Constitution
