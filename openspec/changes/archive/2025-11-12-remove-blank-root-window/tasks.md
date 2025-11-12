# Remove Blank Root Window - Tasks

## Task List

### 1. Implement Code Changes
**Status**: Pending
**Type**: Implementation
**Files**: src/blokus_game/main.py
**Description**: Add `self.root.withdraw()` call in `_show_game_ui()` method to hide the blank root window

**Details**:
- Location: src/blokus_game/main.py, line ~133-140 (in `_show_game_ui()` method)
- Action: Add `self.root.withdraw()` after UI components are created
- Verification: Ensure window is hidden after game UI appears

**Acceptance Criteria**:
- [ ] Code compiled without errors
- [ ] Only one window visible after game mode selection
- [ ] Game functionality works normally

### 2. Test Manual Scenarios
**Status**: Pending
**Type**: Testing
**Description**: Manually test game launch and mode selection

**Test Cases**:
- [ ] Test single AI mode launch
- [ ] Test three AI mode launch
- [ ] Test PvP local mode launch
- [ ] Test spectate mode launch
- [ ] Verify quit dialog works correctly
- [ ] Verify help dialog works correctly

### 3. Run Automated Tests
**Status**: Pending
**Type**: Testing
**Description**: Run existing test suite to ensure no regressions

**Commands**:
```bash
uv run pytest tests/ -v
```

**Acceptance Criteria**:
- [ ] All tests pass
- [ ] No new test failures
- [ ] No regression in existing functionality

### 4. Code Quality Checks
**Status**: Pending
**Type**: Quality
**Description**: Run code quality tools

**Commands**:
```bash
uv run ruff check .
uv run black .
uv run mypy .
pre-commit run --all-files
```

**Acceptance Criteria**:
- [ ] Ruff linting passes
- [ ] Code formatted with Black
- [ ] Mypy type checking passes
- [ ] All pre-commit hooks pass

## Completion Criteria

All tasks must be completed with acceptance criteria met before change is considered complete.

## Dependencies

None - tasks can be executed in order listed.
