# Implementation Tasks: Fix AI Player Strategy Implementation

**Feature**: Fix AI Player Strategy Implementation
**Branch**: `003-fix-ai-player`
**Created**: 2025-11-06
**Source Plan**: `/specs/003-fix-ai-player/plan.md`

## Overview

This document provides actionable, executable tasks for implementing AI player strategy fixes. Tasks are organized by user story for independent implementation and testing. Total tasks: 27

### User Story Priorities
- **P1 (Critical)**: US1 (Easy AI), US2 (Medium AI), US3 (Hard AI), US5 (calculate_move refactor)
- **P2 (Important)**: US4 (Flip Support)

### Implementation Strategy

**MVP First**: Start with User Story 5 (calculate_move refactor) as it enables all other stories. Then implement User Story 4 (Flip Support) followed by individual difficulty stories (US1, US2, US3).

**Incremental Delivery**:
- Phase 1-2: Foundation (can be done in parallel with any story)
- Phase 3: User Story 5 (Core Refactor - enable all others)
- Phase 4: User Story 4 (Flip Support - enhances all strategies)
- Phase 5: User Story 1 (Easy AI)
- Phase 6: User Story 2 (Medium AI)
- Phase 7: User Story 3 (Hard AI)
- Phase 8: Polish & Validation

---

## Phase 1: Setup & Analysis

*Goal*: Understand current implementation and prepare for changes

- [x] T001 Read current AI player implementation in src/models/ai_player.py
- [x] T002 Read current strategy implementations in src/services/ai_strategy.py
- [x] T003 Read current game loop implementation in main.py (lines 425-509)
- [x] T004 Read existing test files for AI in tests/integration/test_single_ai.py, test_three_ai.py, test_difficulty.py
- [x] T005 Review piece model to understand flip/rotate capabilities in src/models/piece.py

**Independent Test**: Can verify understanding by explaining current implementation flow

---

## Phase 2: Foundational Infrastructure

*Goal*: Core changes needed before user stories (can run in parallel with Phase 3+)

- [x] T006 [P] Add flip field to Move class in src/services/ai_strategy.py
- [x] T007 [P] Update __repr__ in Move class to include flip state in src/services/ai_strategy.py
- [x] T008 [P] Update _get_piece_positions() to support flip parameter in src/services/ai_strategy.py
- [x] T009 [P] Test Move class flip field in tests/unit/test_move_flip.py (create new file)
- [x] T010 [P] Test _get_piece_positions with flip in tests/unit/test_ai_strategy_flip.py (create new file)

**Independent Test**: All tests pass; Move objects correctly store and represent flip state

---

## Phase 3: User Story 5 - AI Uses calculate_move Method (P1)

*Goal*: Refactor game loop to use existing calculate_move() infrastructure

**Story Goal**: AI player uses calculate_move() method instead of manual random selection

**Independent Test**: Verify that `ai_player.calculate_move()` is called during AI turns and returns Move objects that are properly executed

### Implementation

- [x] T011 [US5] Create integration test for calculate_move being called in tests/integration/test_ai_calculate_move_integration.py
- [x] T012 [US5] Refactor main.py:_trigger_ai_move() to call ai_player.calculate_move() instead of manual logic
- [x] T013 [US5] Execute returned Move object with proper piece selection, flip, rotation, and placement
- [x] T014 [US5] Handle None return from calculate_move (pass turn)
- [x] T015 [US5] Run integration test to verify calculate_move is called

**Independent Test Criteria**:
- ✅ `_trigger_ai_move()` calls `ai_player.calculate_move()`
- ✅ Returned Move objects execute successfully
- ✅ None return results in turn pass
- ✅ Integration test passes

---

## Phase 4: User Story 4 - AI Supports Piece Flipping (P2)

*Goal*: AI can flip pieces horizontally in addition to rotating

**Story Goal**: AI players utilize flip transformation to match human player capabilities

**Independent Test**: Verify AI can place pieces in orientations requiring flip (not achievable by rotation alone)

### Implementation

- [x] T016 [US4] Update RandomStrategy to generate flipped move candidates in src/services/ai_strategy.py
- [x] T017 [US4] Update CornerStrategy to generate flipped move candidates in src/services/ai_strategy.py
- [x] T018 [US4] Update StrategicStrategy to generate flipped move candidates in src/services/ai_strategy.py
- [x] T019 [US4] Test AI generates moves with flip=True when beneficial in tests/integration/test_ai_flip_support.py

**Independent Test Criteria**:
- ✅ AI strategies generate moves with flip=True
- ✅ Flipped moves execute successfully via placement handler
- ✅ Flipped + rotated moves work correctly
- ✅ Test passes in board state requiring flip

---

## Phase 5: User Story 1 - Easy AI Uses Random Strategy (P1)

*Goal*: Easy AI makes random valid moves from all available options

**Story Goal**: Easy AI (RandomStrategy) selects random valid moves, completing in under 100ms

**Independent Test**: Can be verified by playing Easy AI and confirming random but valid move selection

### Implementation

- [x] T020 [US1] Verify RandomStrategy is properly assigned to Easy AI in main.py (line 297)
- [x] T021 [US1] Create test verifying Easy AI makes random moves in tests/integration/test_easy_ai.py
- [x] T022 [US1] Run test to confirm Easy AI produces different random moves across multiple turns

**Independent Test Criteria**:
- ✅ Easy AI assigned RandomStrategy
- ✅ Moves are random but valid
- ✅ Average calculation time < 100ms
- ✅ Test suite passes

---

## Phase 6: User Story 2 - Medium AI Uses Corner Strategy (P1)

*Goal*: Medium AI prioritizes corner placement and connections

**Story Goal**: Medium AI (CornerStrategy) consistently prefers corner-adjacent placements over non-corner positions

**Independent Test**: Can be verified by comparing Medium AI move selection against random baseline

### Implementation

- [x] T023 [US2] Verify CornerStrategy is properly assigned to Medium AI in main.py (line 299)
- [x] T024 [US2] Create test verifying Medium AI prioritizes corners in tests/integration/test_medium_ai.py
- [x] T025 [US2] Run test to confirm Medium AI prefers corner connections 80%+ of the time

**Independent Test Criteria**:
- ✅ Medium AI assigned CornerStrategy
- ✅ 80%+ of moves prefer corner connections when available
- ✅ Average calculation time < 500ms
- ✅ Test suite passes

---

## Phase 7: User Story 3 - Hard AI Uses Strategic Strategy (P1)

*Goal*: Hard AI uses lookahead and multi-factor evaluation

**Story Goal**: Hard AI (StrategicStrategy) makes demonstrably superior strategic decisions with lookahead evaluation

**Independent Test**: Can be verified by comparing Hard AI decisions against Medium/Easy in same board states

### Implementation

- [x] T026 [US3] Verify StrategicStrategy is properly assigned to Hard AI in main.py (line 301)
- [x] T027 [US3] Create test verifying Hard AI makes strategic decisions in tests/integration/test_hard_ai.py
- [x] T028 [US3] Run test to confirm Hard AI produces superior decisions to Medium AI

**Independent Test Criteria**:
- ✅ Hard AI assigned StrategicStrategy
- ✅ Uses multi-factor evaluation (corner, mobility, area)
- ✅ Average calculation time < 2s
- ✅ Test suite passes

---

## Phase 8: Polish & Validation

*Goal*: Comprehensive testing and validation across all user stories

### Final Tests & Verification

- [x] T029 Run full AI test suite: uv pytest tests/integration/test_*.py -v
- [x] T030 Run unit tests for flip support: uv pytest tests/unit/test_*flip*.py -v
- [x] T031 Play complete game against Easy AI and verify behavior
- [x] T032 Play complete game against Medium AI and verify behavior
- [x] T033 Play complete game against Hard AI and verify behavior
- [x] T034 Verify all three difficulties demonstrate different win patterns
- [x] T035 Check logs for "AI Player X: Calculated move in Y.Ys" messages
- [x] T036 Confirm no "AI calculation error" messages in logs

### Documentation Updates

- [x] T037 Update docstrings in src/models/ai_player.py to reflect calculate_move usage
- [x] T038 Add documentation for flip parameter in src/services/ai_strategy.py

### Performance Validation

- [x] T039 Verify Easy AI average < 100ms, max < 3s
- [x] T040 Verify Medium AI average < 500ms, max < 5s
- [x] T041 Verify Hard AI average < 2s, max < 8s

**Independent Test Criteria**:
- ✅ All 31 new integration and unit tests pass
- ✅ All three AI difficulties working correctly
- ✅ Flip support fully functional
- ✅ calculate_move() properly integrated
- ✅ Performance within timeout limits

---

## Dependencies & Execution Order

### Dependency Graph

```
Phase 1 (Setup) ──┐
                  ├── Phase 2 (Foundation)
Phase 2 (Foundation) ──┤
                      ├── Phase 3 (US5 - calculate_move refactor)
Phase 3 (US5) ─────────┼── Phase 4 (US4 - Flip Support)
Phase 4 (US4) ─────────┼── Phase 5 (US1 - Easy)
                      ├── Phase 6 (US2 - Medium)
                      └── Phase 7 (US3 - Hard)

Phase 5, 6, 7 ─────────┼── Phase 8 (Polish)
```

### Story Completion Order

**Recommended Sequence**:
1. Phase 1 (Setup) - Understand codebase
2. Phase 2 (Foundation) - Add flip support (can run parallel)
3. Phase 3 (US5) - calculate_move refactor (ENABLES all other stories)
4. Phase 4 (US4) - Flip support (ENHANCES all AI strategies)
5. Phase 5 (US1) - Easy AI verification
6. Phase 6 (US2) - Medium AI verification
7. Phase 7 (US3) - Hard AI verification
8. Phase 8 (Polish) - Final validation

**Critical Path**: Phase 3 (US5) must complete before Phase 5-7 can be independently validated

---

## Parallel Execution Opportunities

The following tasks can run in parallel:

1. **Phase 1 tasks** (T001-T005) - Multiple people reading different files
2. **Phase 2 tasks** (T006-T010) - Adding flip support to Move class
3. **Phase 4 tasks** (T016-T018) - Adding flip to each strategy (independent files)
4. **Phase 5-7 tasks** (T020-T028) - Testing different AI difficulties (independent)
5. **Phase 8 verification** (T029-T041) - Running tests and playing games

### Example Parallel Workflow

```
Week 1:
- Developer A: Phase 1 & Phase 2 (T001-T010)
- Developer B: Phase 3 (T011-T015) - wait for Phase 2 to complete

Week 2:
- Developer A: Phase 4 (T016-T019)
- Developer B: Phase 5 (T020-T022)
- Developer C: Phase 6 (T023-T025)

Week 3:
- Developer A: Phase 7 (T026-T028)
- All: Phase 8 (T029-T041)
```

---

## Success Criteria Summary

| User Story | Priority | Key Requirement | Test Criteria |
|------------|----------|-----------------|---------------|
| US5 | P1 | Use calculate_move() | calculate_move called, moves executed |
| US4 | P2 | Support piece flipping | Flipped moves generate and execute |
| US1 | P1 | Easy AI random moves | Random, valid, <100ms avg |
| US2 | P1 | Medium AI corner strategy | 80%+ prefer corners, <500ms avg |
| US3 | P1 | Hard AI strategic | Superior decisions, <2s avg |

---

## Implementation Notes

### Key Files Modified

| File | Change | Phase |
|------|--------|-------|
| src/services/ai_strategy.py | Add flip to Move, update position calc | Phase 2 |
| tests/unit/test_move_flip.py | Test flip field | Phase 2 |
| tests/unit/test_ai_strategy_flip.py | Test position calc | Phase 2 |
| main.py | Refactor _trigger_ai_move() | Phase 3 |
| tests/integration/test_ai_calculate_move_integration.py | Test calculate_move integration | Phase 3 |
| src/services/ai_strategy.py | Update RandomStrategy | Phase 4 |
| src/services/ai_strategy.py | Update CornerStrategy | Phase 4 |
| src/services/ai_strategy.py | Update StrategicStrategy | Phase 4 |
| tests/integration/test_ai_flip_support.py | Test flip support | Phase 4 |
| tests/integration/test_easy_ai.py | Test Easy AI | Phase 5 |
| tests/integration/test_medium_ai.py | Test Medium AI | Phase 6 |
| tests/integration/test_hard_ai.py | Test Hard AI | Phase 7 |

### Critical Implementation Details

1. **Flip Order**: Always apply flip BEFORE rotation in _get_piece_positions()
2. **calculate_move Integration**: Must pass board (List[List[int]]) and pieces (List[Piece])
3. **Move Execution**: Select piece → Apply flip → Apply rotation → Place
4. **Timeout Handling**: All strategies already have timeout logic - preserve it

### Common Pitfalls

1. ❌ Applying rotation before flip (WRONG)
2. ❌ Forgetting to pass flip parameter to _get_piece_positions()
3. ❌ Not handling None return from calculate_move()
4. ❌ Not calling rotate_piece() N times for N*90° rotation

---

## Testing Commands

```bash
# Run all AI integration tests
uv pytest tests/integration/test_ai_*.py -v

# Run specific test files
uv pytest tests/integration/test_ai_calculate_move_integration.py -v
uv pytest tests/integration/test_ai_flip_support.py -v
uv pytest tests/integration/test_easy_ai.py -v
uv pytest tests/integration/test_medium_ai.py -v
uv pytest tests/integration/test_hard_ai.py -v

# Run unit tests
uv pytest tests/unit/test_move_flip.py -v
uv pytest tests/unit/test_ai_strategy_flip.py -v

# Run existing AI tests
uv pytest tests/integration/test_single_ai.py -v
uv pytest tests/integration/test_three_ai.py -v
uv pytest tests/integration/test_difficulty.py -v

# Run all tests
uv pytest
```

---

## MVP Scope Recommendation

**Start with**: Phase 3 (User Story 5 - calculate_move refactor)

**Why**: This is the foundational change that enables all other stories. Without it, AI continues to use manual random selection regardless of difficulty.

**Minimum Viable Implementation**:
- Phase 1 (T001-T005): Understand current code
- Phase 2 (T006-T010): Add flip support foundation
- Phase 3 (T011-T015): Refactor to use calculate_move
- Basic verification (T029-T035 subset)

**Value Delivered**:
- Eliminates code duplication
- Uses existing sophisticated infrastructure
- Sets foundation for difficulty-specific behavior

**Time Estimate**: 2-3 days for MVP, 1 week for full implementation

---

## File Paths Reference

### Source Files
- `src/models/ai_player.py` - AIPlayer class and calculate_move method
- `src/services/ai_strategy.py` - Strategy classes and Move class
- `src/models/piece.py` - Piece model with rotate/flip methods
- `main.py` - Game loop with _trigger_ai_move method

### Test Files (Existing)
- `tests/integration/test_single_ai.py`
- `tests/integration/test_three_ai.py`
- `tests/integration/test_difficulty.py`
- `tests/unit/test_ai_player.py`
- `tests/unit/test_ai_strategy.py`

### Test Files (To Create)
- `tests/integration/test_ai_calculate_move_integration.py`
- `tests/integration/test_ai_flip_support.py`
- `tests/integration/test_easy_ai.py`
- `tests/integration/test_medium_ai.py`
- `tests/integration/test_hard_ai.py`
- `tests/unit/test_move_flip.py`
- `tests/unit/test_ai_strategy_flip.py`

---

## Summary

**Total Tasks**: 41
**Parallelizable Tasks**: 15
**User Story Phases**: 5 (US1, US2, US3, US4, US5)
**Estimated Duration**: 1-2 weeks
**Critical Path**: Phase 3 (calculate_move refactor)

**Success**: AI difficulties demonstrate measurably different behavior with flip support and proper calculate_move integration
