"""
Unit tests for TurnController multi-AI turn management.

This module tests the TurnController's ability to manage turns for multiple AI players,
including skipping inactive positions and tracking turn state.
"""

import pytest

from blokus_game.models.ai_config import Difficulty
from blokus_game.models.game_mode import GameMode
from blokus_game.models.turn_controller import TurnController, TurnState


class TestTurnControllerMultiAI:
    """Test suite for TurnController with multiple AI players."""

    def test_turn_controller_initialization(self):
        """Test TurnController initializes correctly."""
        game_mode = GameMode.single_ai(Difficulty.MEDIUM)
        controller = TurnController(game_mode, initial_player=1)

        assert controller.game_mode == game_mode
        assert controller.current_player == 1
        assert controller.current_state == TurnState.HUMAN_TURN

    def test_is_ai_turn_single_ai(self):
        """Test is_ai_turn for Single AI mode."""
        game_mode = GameMode.single_ai(Difficulty.MEDIUM)
        controller = TurnController(game_mode, initial_player=1)

        # Player 1 is human
        assert controller.is_ai_turn is False

        # Switch to AI player (position 3 in Single AI mode)
        controller.current_player = 3
        assert controller.is_ai_turn is True

    def test_is_ai_turn_three_ai(self):
        """Test is_ai_turn for Three AI mode."""
        game_mode = GameMode.three_ai(Difficulty.MEDIUM)
        controller = TurnController(game_mode, initial_player=1)

        # Player 1 is human
        assert controller.is_ai_turn is False

        # Players 2, 3, 4 are AI
        for player_id in [2, 3, 4]:
            controller.current_player = player_id
            assert controller.is_ai_turn is True

    def test_get_next_player_single_ai(self):
        """Test get_next_player for Single AI mode."""
        game_mode = GameMode.single_ai(Difficulty.MEDIUM)
        controller = TurnController(game_mode, initial_player=1)

        # Should only cycle between positions 1 and 3
        assert controller.get_next_player(1) == 3
        assert controller.get_next_player(3) == 1

    def test_get_next_player_three_ai(self):
        """Test get_next_player for Three AI mode."""
        game_mode = GameMode.three_ai(Difficulty.MEDIUM)
        controller = TurnController(game_mode, initial_player=1)

        # Should cycle through all 4 positions
        assert controller.get_next_player(1) == 2
        assert controller.get_next_player(2) == 3
        assert controller.get_next_player(3) == 4
        assert controller.get_next_player(4) == 1

    def test_get_next_player_spectate(self):
        """Test get_next_player for Spectate mode."""
        game_mode = GameMode.spectate_ai()
        controller = TurnController(game_mode, initial_player=1)

        # Should cycle through all 4 positions (all AI)
        assert controller.get_next_player(1) == 2
        assert controller.get_next_player(2) == 3
        assert controller.get_next_player(3) == 4
        assert controller.get_next_player(4) == 1

    def test_start_turn_human(self):
        """Test starting a human turn."""
        game_mode = GameMode.three_ai(Difficulty.EASY)
        controller = TurnController(game_mode, initial_player=1)

        controller.start_turn()

        # Should be human turn
        assert controller.current_state == TurnState.HUMAN_TURN
        assert controller.is_ai_turn is False

    def test_start_turn_ai(self):
        """Test starting an AI turn."""
        game_mode = GameMode.three_ai(Difficulty.EASY)
        controller = TurnController(game_mode, initial_player=2)

        # Player 2 is AI
        assert controller.is_ai_turn is True

        controller.start_turn()

        # Should transition to AI calculating state
        assert controller.current_state == TurnState.AI_CALCULATING

    def test_turn_state_progression(self):
        """Test turn state progression through game."""
        game_mode = GameMode.three_ai(Difficulty.EASY)
        controller = TurnController(game_mode, initial_player=1)

        # Start human turn
        controller.start_turn()
        assert controller.current_state == TurnState.HUMAN_TURN

        # Advance to AI turn
        controller.current_player = 2
        controller.start_turn()
        assert controller.current_state == TurnState.AI_CALCULATING

    def test_turn_event_history(self):
        """Test that turn events are recorded in history."""
        game_mode = GameMode.single_ai(Difficulty.EASY)
        controller = TurnController(game_mode, initial_player=1)

        # Add a listener to capture events
        events = []
        controller.add_turn_listener(lambda event: events.append(event))

        # Start a turn
        controller.start_turn()

        # Should have at least one event
        assert len(events) > 0
        assert events[0].event_type == "TURN_STARTED"

    def test_elapsed_ai_time(self):
        """Test tracking elapsed AI calculation time."""
        game_mode = GameMode.single_ai(Difficulty.EASY)
        controller = TurnController(game_mode, initial_player=3)

        # Before AI calculation
        assert controller.elapsed_ai_time == 0.0

        # Start AI turn
        controller.start_turn()

        # AI is calculating
        assert controller.current_state == TurnState.AI_CALCULATING

    def test_skip_inactive_positions(self):
        """Test that inactive positions are skipped."""
        game_mode = GameMode.single_ai(Difficulty.MEDIUM)
        controller = TurnController(game_mode, initial_player=1)

        # In Single AI mode, only positions 1 and 3 are active
        # get_next_player should skip positions 2 and 4

        # From position 1, should go to 3 (skip 2)
        assert controller.get_next_player(1) == 3

        # From position 3, should go to 1 (skip 4)
        assert controller.get_next_player(3) == 1

    def test_concurrent_ai_turns(self):
        """Test handling multiple AI turns in sequence."""
        game_mode = GameMode.three_ai(Difficulty.MEDIUM)
        controller = TurnController(game_mode, initial_player=1)

        # Simulate turns for all AI players
        ai_players = [2, 3, 4]

        for player_id in ai_players:
            controller.current_player = player_id
            controller.start_turn()

            # Each AI turn should start correctly
            assert controller.is_ai_turn is True
            assert controller.current_state == TurnState.AI_CALCULATING

        # Should end up back at human player
        controller.current_player = 1
        assert controller.is_ai_turn is False

    def test_turn_controller_with_different_modes(self):
        """Test TurnController works with different game modes."""
        modes = [
            GameMode.single_ai(Difficulty.EASY),
            GameMode.three_ai(Difficulty.MEDIUM),
            GameMode.spectate_ai(),
        ]

        for game_mode in modes:
            controller = TurnController(game_mode, initial_player=1)

            # Should initialize correctly
            assert controller.game_mode == game_mode
            assert controller.current_player == 1

            # Should handle get_next_player
            next_player = controller.get_next_player(1)
            assert 1 <= next_player <= 4

    def test_turn_state_enum(self):
        """Test TurnState enum values."""
        assert TurnState.HUMAN_TURN.value == "human_turn"
        assert TurnState.AI_CALCULATING.value == "ai_calculating"
        assert TurnState.AI_MAKING_MOVE.value == "ai_making_move"
        assert TurnState.TRANSITION_AUTO.value == "transition_auto"
        assert TurnState.GAME_OVER.value == "game_over"

    def test_listener_management(self):
        """Test adding and removing turn listeners."""
        game_mode = GameMode.single_ai(Difficulty.EASY)
        controller = TurnController(game_mode, initial_player=1)

        # Define a test listener
        def test_listener(event):
            pass

        # Add listener
        controller.add_turn_listener(test_listener)

        # Should be able to remove listener
        controller.remove_turn_listener(test_listener)

    def test_get_turn_history(self):
        """Test retrieving turn history."""
        game_mode = GameMode.single_ai(Difficulty.EASY)
        controller = TurnController(game_mode, initial_player=1)

        # Get initial history
        history = controller.get_turn_history()
        assert isinstance(history, list)


class TestTurnControllerTurnProgression:
    """Test turn progression logic."""

    def test_full_turn_cycle_single_ai(self):
        """Test full turn cycle in Single AI mode."""
        game_mode = GameMode.single_ai(Difficulty.MEDIUM)
        controller = TurnController(game_mode, initial_player=1)

        # Human turn
        controller.current_player = 1
        assert not controller.is_ai_turn

        # AI turn
        controller.current_player = 3
        assert controller.is_ai_turn

        # Back to human
        next_player = controller.get_next_player(3)
        assert next_player == 1

    def test_full_turn_cycle_three_ai(self):
        """Test full turn cycle in Three AI mode."""
        game_mode = GameMode.three_ai(Difficulty.MEDIUM)
        controller = TurnController(game_mode, initial_player=1)

        # Expected sequence: 1 (human) -> 2 (AI) -> 3 (AI) -> 4 (AI) -> 1
        expected_sequence = [1, 2, 3, 4, 1]
        current = 1

        for i, expected in enumerate(expected_sequence):
            assert current == expected

            # Don't advance on the last iteration
            if i < len(expected_sequence) - 1:
                current = controller.get_next_player(current)

    def test_turn_with_default_parameter(self):
        """Test get_next_player with default current_player."""
        game_mode = GameMode.three_ai(Difficulty.EASY)
        controller = TurnController(game_mode, initial_player=2)

        # Should use current_player if parameter not provided
        assert controller.get_next_player() == 3


class TestSpectatorModeAutomatedFlow:
    """Test automated game flow in spectator mode."""

    def test_spectate_mode_all_ai_turns(self):
        """Test that all turns are AI-controlled in spectator mode."""
        game_mode = GameMode.spectate_ai()
        controller = TurnController(game_mode, initial_player=1)

        # All players should be AI-controlled
        for player_id in [1, 2, 3, 4]:
            controller.current_player = player_id
            assert controller.is_ai_turn is True

    def test_spectate_mode_start_turn_ai(self):
        """Test starting turns in spectator mode always triggers AI."""
        game_mode = GameMode.spectate_ai()
        controller = TurnController(game_mode, initial_player=1)

        # Start turn for player 1 (AI)
        controller.start_turn()

        # Should transition to AI calculating state
        assert controller.current_state == TurnState.AI_CALCULATING
        assert controller.is_ai_turn is True

    def test_spectate_mode_turn_progression(self):
        """Test turn progression in spectator mode."""
        game_mode = GameMode.spectate_ai()
        controller = TurnController(game_mode, initial_player=1)

        # All turns should follow AI sequence
        # 1 -> 2 -> 3 -> 4 -> 1
        expected_sequence = [1, 2, 3, 4, 1]
        current = 1

        for i, expected in enumerate(expected_sequence):
            assert current == expected

            # Don't advance on the last iteration
            if i < len(expected_sequence) - 1:
                current = controller.get_next_player(current)

    @pytest.mark.parametrize("starting_player", [1, 2, 3, 4])
    def test_spectate_mode_from_different_starting_players(self, starting_player):
        """Test spectator mode works from any starting player."""
        game_mode = GameMode.spectate_ai()
        controller = TurnController(game_mode, initial_player=starting_player)

        # Should always detect AI turn
        assert controller.is_ai_turn is True

        # Should be able to get next player
        next_player = controller.get_next_player(starting_player)
        assert 1 <= next_player <= 4
        assert next_player != starting_player  # Should move to different player

    def test_spectate_mode_no_human_input(self):
        """Test that spectator mode has no human input states."""
        game_mode = GameMode.spectate_ai()
        controller = TurnController(game_mode, initial_player=1)

        # Start a turn
        controller.start_turn()

        # Should never be in human turn state for any player
        for player_id in [1, 2, 3, 4]:
            controller.current_player = player_id
            controller.start_turn()
            assert controller.current_state != TurnState.HUMAN_TURN

    def test_spectate_mode_automated_end_turn(self):
        """Test that end_turn advances automatically in spectator mode."""
        game_mode = GameMode.spectate_ai()
        controller = TurnController(game_mode, initial_player=1)

        # Mock the scheduler method to simulate automatic progression
        progression_calls = []

        def mock_scheduler(delay, callback):
            progression_calls.append((delay, callback))
            # Don't actually schedule, just record

        controller._scheduler = mock_scheduler

        # Set up for end_turn
        controller.current_state = TurnState.TRANSITION_AUTO
        controller.current_player = 1

        # Call end_turn
        controller.end_turn()

        # Should have scheduled next turn
        assert len(progression_calls) == 1
        delay, callback = progression_calls[0]
        assert delay == 500  # 500ms delay
        assert callable(callback)

    def test_spectate_mode_state_transitions(self):
        """Test proper state transitions in spectator mode."""
        game_mode = GameMode.spectate_ai()
        controller = TurnController(game_mode, initial_player=1)

        # Mock scheduler to prevent auto-execution
        controller._scheduler = lambda delay, callback: None

        # Capture events
        events = []
        controller.add_turn_listener(lambda e: events.append(e))

        # Start turn - should trigger AI calculation
        controller.start_turn()
        assert controller.current_state == TurnState.AI_CALCULATING

        # Simulate move handling - this will call end_turn() which transitions to TRANSITION_AUTO
        controller.handle_ai_move(None)  # Simulating a pass/move

        # After handle_ai_move, end_turn is called, so state should be TRANSITION_AUTO
        assert controller.current_state == TurnState.TRANSITION_AUTO

    def test_spectate_mode_turn_history_events(self):
        """Test that spectator mode generates correct event history."""
        game_mode = GameMode.spectate_ai()
        controller = TurnController(game_mode, initial_player=1)

        # Track events
        events = []
        controller.add_turn_listener(lambda e: events.append(e))

        # Start first turn
        controller.start_turn()

        # Should have TURN_STARTED event
        turn_events = [e for e in events if e.event_type == "TURN_STARTED"]
        assert len(turn_events) >= 1

        # Should have AI_CALCULATION_STARTED event
        ai_events = [e for e in events if e.event_type == "AI_CALCULATION_STARTED"]
        assert len(ai_events) >= 1

    def test_spectate_mode_consecutive_turns(self):
        """Test consecutive automated turns in spectator mode."""
        game_mode = GameMode.spectate_ai()
        controller = TurnController(game_mode, initial_player=1)

        # Track player progression
        players_seen = []
        original_get_next = controller.get_next_player

        def track_next_player(current):
            result = original_get_next(current)
            players_seen.append((current, result))
            return result

        controller.get_next_player = track_next_player

        # Mock scheduler to prevent actual scheduling
        controller._scheduler = lambda delay, callback: None

        # Simulate a few turns
        for _ in range(4):
            controller.start_turn(auto_execute_ai=True)
            controller.end_turn()

        # Should have seen proper progression (2 calls per turn: start_turn and end_turn)
        assert len(players_seen) == 8

        # Verify progression pattern (each turn advances to next player)
        for current, next_player in players_seen:
            assert next_player == ((current % 4) + 1)

    def test_spectate_mode_different_from_human_modes(self):
        """Test that spectator mode behaves differently from human modes."""
        # Create controllers for different modes
        single_ai = GameMode.single_ai(Difficulty.MEDIUM)
        spectate = GameMode.spectate_ai()

        controller_single = TurnController(single_ai, initial_player=1)
        controller_spectate = TurnController(spectate, initial_player=1)

        # In Single AI mode, player 1 is human
        assert controller_single.is_ai_turn is False

        # In Spectate mode, player 1 is AI
        assert controller_spectate.is_ai_turn is True

        # Both should be able to get next player
        assert controller_single.get_next_player(1) == 3  # Skips to AI player
        assert controller_spectate.get_next_player(1) == 2  # Goes to next player

    def test_spectate_mode_turn_state_consistency(self):
        """Test that turn states remain consistent in spectator mode."""
        game_mode = GameMode.spectate_ai()
        controller = TurnController(game_mode, initial_player=1)

        # Mock scheduler to prevent auto-execution
        controller._scheduler = lambda delay, callback: None

        # Initial state
        assert controller.current_state == TurnState.HUMAN_TURN
        assert controller.is_ai_turn is True

        # After starting turn
        controller.start_turn()
        assert controller.current_state == TurnState.AI_CALCULATING

        # After handling move - handle_ai_move calls end_turn internally
        controller.handle_ai_move(None)

        # After handle_ai_move completes, state should be TRANSITION_AUTO (from end_turn)
        assert controller.current_state == TurnState.TRANSITION_AUTO


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
