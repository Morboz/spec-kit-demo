"""
Unit tests for TurnController multi-AI turn management.

This module tests the TurnController's ability to manage turns for multiple AI players,
including skipping inactive positions and tracking turn state.
"""

import pytest
import time
from src.models.turn_controller import TurnController, TurnState
from src.models.game_mode import GameMode, GameModeType
from src.models.ai_config import Difficulty


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

        for expected in expected_sequence:
            assert current == expected

            if expected != 4:
                current = controller.get_next_player(current)

    def test_turn_with_default_parameter(self):
        """Test get_next_player with default current_player."""
        game_mode = GameMode.three_ai(Difficulty.EASY)
        controller = TurnController(game_mode, initial_player=2)

        # Should use current_player if parameter not provided
        assert controller.get_next_player() == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
