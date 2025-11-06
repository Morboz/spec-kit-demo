# Tasks: Fix Test Adjacency Rule Validation

## Task Checklist

### Phase 1: Analysis and Planning
- [x] 1.1 Identify failing tests in test_adjacency_rule.py
- [x] 1.2 Analyze root cause of test failures
- [x] 1.3 Verify rule validation logic is correct
- [x] 1.4 Document findings in proposal.md

### Phase 2: Test Fixes
- [x] 2.1 Fix test_piece_with_diagonal_contact_is_valid - adjust V3 coordinates
- [x] 2.2 Fix test_piece_with_edge_contact_is_invalid - correct placement and assertions
- [x] 2.3 Fix test_piece_touching_left_edge_is_invalid - use corner position
- [x] 2.4 Fix test_piece_touching_top_edge_is_invalid - use corner position
- [x] 2.5 Fix test_piece_touching_bottom_edge_is_invalid - use corner position
- [x] 2.6 Fix test_contact_with_opponent_piece_is_allowed - Player 2 corner placement
- [x] 2.7 Fix test_no_contact_with_own_pieces_is_valid - add piece.place_at() call
- [x] 2.8 Fix test_corner_after_first_move_can_have_diagonal_contact - add piece.place_at() call

### Phase 3: Piece State Management
- [x] 3.1 Add piece.place_at() calls for all first moves
- [x] 3.2 Add piece.place_at() calls for subsequent moves
- [x] 3.3 Verify piece.is_placed tracking works correctly

### Phase 4: Validation
- [x] 4.1 Run all 12 adjacency rule tests
- [x] 4.2 Verify all tests pass
- [x] 4.3 Confirm rule validation logic unchanged
- [x] 4.4 Document results

### Phase 5: Documentation
- [x] 5.1 Update proposal.md with detailed findings
- [x] 5.2 Document coordinate calculations for clarity
- [x] 5.3 Record root cause analysis

## Validation Commands

```bash
# Run adjacency rule tests
uv run pytest tests/contract/test_adjacency_rule.py -v

# Expected: 12 passed
```

## Acceptance Criteria

- [x] All 12 tests in test_adjacency_rule.py pass
- [x] No functional code changes (only test modifications)
- [x] Rule validation logic confirmed working correctly
- [x] Documentation complete in proposal.md

## Notes

The primary issue was that `board.place_piece()` doesn't automatically mark pieces as placed. Tests must call `piece.place_at()` to update the piece's `is_placed` flag, which is used by validation rules to enforce first move corner placement and subsequent move corner-to-corner connection requirements.
