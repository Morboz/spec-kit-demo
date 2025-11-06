## MODIFIED Requirements

### Requirement: Fix GameState initialization in all integration tests
Integration tests MUST use the correct GameState initialization pattern instead of non-existent `initialize()` method.

#### Scenario: GameState initialization with players
**Given:** A test needs to set up a GameState with players
**When:** The test creates GameState and adds players properly
**Then:** GameState is correctly initialized with players
**Expected:** No AttributeError for 'initialize' method
**Changes:**
- Replace `game_state.initialize(n_players)` with proper player setup
- Use `game_state = GameState()`
- Add players using `game_state.add_player(player)`
- Call `game_state.start_game()` after adding all players

#### Scenario: Single AI mode test setup
**Given:** A test for Single AI game mode
**When:** The test sets up GameState for 2 players (1 human, 1 AI)
**Then:** GameState contains correct player configuration
**Expected:** GameState has Player(1) and AIPlayer(3)
**Changes:**
- Create Player(1, "Human") and add to GameState
- Create AIPlayer(3) and add to GameState
- Call `game_state.start_game()` after adding players

#### Scenario: Three AI mode test setup
**Given:** A test for Three AI game mode
**When:** The test sets up GameState for 4 players (1 human, 3 AI)
**Then:** GameState contains correct player configuration
**Expected:** GameState has Player(1) and three AIPlayers
**Changes:**
- Create Player(1, "Human") and add to GameState
- Create AIPlayer(2), AIPlayer(3), AIPlayer(4) and add to GameState
- Call `game_state.start_game()` after adding all players

### Requirement: Fix turn advancement method calls
Integration tests MUST use `next_turn()` method instead of non-existent `advance_turn()`.

#### Scenario: Single turn advancement
**Given:** A GameState with active players
**When:** The test advances to the next turn
**Then:** `game_state.next_turn()` is called
**Expected:** Turn advances correctly, no AttributeError
**Changes:**
- Replace ALL instances of `game_state.advance_turn()`
- Use `game_state.next_turn()` instead

#### Scenario: Multiple consecutive turns
**Given:** A game loop in a test
**When:** The test processes multiple turns
**Then:** Each iteration calls `game_state.next_turn()`
**Expected:** All turns processed without errors
**Changes:**
- In all test loops, change `game_state.advance_turn()` to `game_state.next_turn()`
- Verify turn order matches game mode configuration

### Requirement: Fix variable scope errors in test code
Test code MUST properly handle variable scope in nested functions and closures.

#### Scenario: Variable scope in ThreadPoolExecutor
**Given:** A test using ThreadPoolExecutor
**When:** A nested function modifies a counter variable
**Then:** Variable is properly declared for closure
**Expected:** No UnboundLocalError
**Changes:**
- Fix `games_completed` variable in `test_system_stability_under_prolonged_load`
- Use `nonlocal games_completed` in nested function
- Or use dictionary for closure: `games_completed = {'count': 0}`

#### Scenario: Variable scope in while loop
**Given:** A test with a while loop containing nested functions
**When:** The nested function updates a loop variable
**Then:** Variable is properly declared for closure
**Expected:** No UnboundLocalError
**Changes:**
- Apply same fix pattern as ThreadPoolExecutor scenario
- Ensure all variables modified in nested functions are properly scoped

### Requirement: All integration tests pass after fixes
All integration tests that were failing MUST pass successfully after corrections are applied.

#### Scenario: test_ai_stress.py tests pass
**Given:** All 7 tests in test_ai_stress.py
**When:** Tests are executed
**Then:** All tests pass successfully
**Expected:** 100% pass rate for AI stress tests
**Changes:**
- test_multiple_singletai_games_concurrent: Fix initialization and turn methods
- test_mixed_difficulty_concurrent_games: Fix initialization and turn methods
- test_max_concurrent_load: Fix initialization and turn methods
- test_rapid_game_creation_and_destruction: Fix initialization and turn methods
- test_memory_isolation_between_concurrent_games: Fix initialization and turn methods
- test_concurrent_ai_calculation_isolation: Fix initialization and turn methods
- test_system_stability_under_prolonged_load: Fix initialization, turn methods, and variable scope

#### Scenario: test_all_modes.py tests pass
**Given:** All affected tests in test_all_modes.py
**When:** Tests are executed
**Then:** All tests pass successfully
**Expected:** 100% pass rate for game mode tests
**Changes:**
- test_game_state_isolation_between_modes: Fix initialization and turn methods
- test_complete_single_ai_game_flow: Fix initialization and turn methods
- test_complete_three_ai_game_flow: Fix initialization and turn methods
- test_spectate_mode_fully_autonomous: Fix initialization and turn methods

#### Scenario: Other integration tests pass
**Given:** All tests in integration test suite
**When:** Full integration test suite is executed
**Then:** All tests pass
**Expected:** 100% pass rate across all integration tests
**Changes:**
- Check and fix test_game_performance.py
- Check and fix test_complete_game_flow.py
- Fix any other files using incorrect GameState API
