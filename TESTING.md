# Testing with uv

## Running Tests

### Install uv (if not already installed)
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Setup Project
```bash
# Initialize the project (already done)
uv init

# Install dev dependencies
uv sync --dev
```

### Run Tests

#### Run All Tests
```bash
uv run pytest tests/ -v
```

#### Run Specific Test Files
```bash
# Run Phase 5 tests
uv run pytest tests/unit/test_game_mode_selector.py -v
uv run pytest tests/unit/test_ai_player.py -v
uv run pytest tests/integration/test_difficulty.py -v

# Run validation script
uv run python tests/integration/validate_phase5.py
```

#### Run with Coverage
```bash
uv run pytest tests/ --cov=src --cov-report=html
```

#### Run Specific Test Class
```bash
uv run pytest tests/unit/test_ai_player.py::TestAIPlayer::test_switch_strategy -v
```

## Test Structure

### Unit Tests
- `tests/unit/test_ai_player.py` - AI player functionality
- `tests/unit/test_ai_strategy.py` - AI strategies
- `tests/unit/test_game_mode.py` - Game mode configuration
- `tests/unit/test_game_mode_selector.py` - UI mode selector
- `tests/unit/test_turn_controller.py` - Turn management

### Integration Tests
- `tests/integration/test_difficulty.py` - Difficulty settings validation
- `tests/integration/test_single_ai.py` - Single AI mode
- `tests/integration/test_three_ai.py` - Three AI mode
- `tests/integration/validate_phase5.py` - Phase 5 comprehensive validation

## Phase 5 Features to Test

1. **Difficulty Selection UI**
   - Change difficulty and verify it's saved
   - Restart game mode selector and verify saved difficulty is loaded

2. **Strategy Switching**
   ```bash
   uv run pytest tests/unit/test_ai_player.py::TestAIPlayer::test_switch_strategy -v
   uv run pytest tests/unit/test_ai_player.py::TestAIPlayer::test_switch_to_difficulty -v
   ```

3. **Performance Optimization**
   ```bash
   uv run pytest tests/integration/test_difficulty.py::TestAIDifficultyBehavior::test_easy_ai_caching_performance -v
   ```

4. **Validation**
   ```bash
   uv run python tests/integration/validate_phase5.py
   ```

## Expected Test Results

Phase 5 should pass:
- T049-T050: Difficulty Configuration UI
- T051-T052: Strategy Switching
- T053-T054: Performance Optimization
- T055-T057: Testing
- T058-T060: Validation

Total: 60/94 tasks (63.8%) complete
