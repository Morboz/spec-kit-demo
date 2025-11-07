"""
Integration tests for Spectate mode.

Tests the complete spectator mode functionality including:
- Spectator mode configuration
- Automated game flow
- AI vs AI gameplay
- Statistics tracking
- Game completion
"""

import pytest
import time
from unittest.mock import Mock, MagicMock, patch
from src.models.game_mode import GameMode, GameModeType, Difficulty
from src.models.game_stats import GameStatistics, create_game_statistics
from src.models.turn_controller import TurnController, TurnState
from src.services.ai_strategy import Move


class TestSpectateMode:
    """Test suite for spectator mode."""

    def test_spectate_mode_configuration(self):
        """Test that spectator mode is configured correctly."""
        game_mode = GameMode.spectate_ai()

        # Verify configuration
        assert game_mode.mode_type == GameModeType.SPECTATE
        assert game_mode.human_player_position is None
        assert len(game_mode.ai_players) == 4
        assert game_mode.get_player_count() == 4
        assert game_mode.get_ai_count() == 4

        # Verify all 4 positions are AI
        ai_positions = {config.position for config in game_mode.ai_players}
        assert ai_positions == {1, 2, 3, 4}

        # Verify no human player
        assert game_mode.is_ai_turn(1)
        assert game_mode.is_ai_turn(2)
        assert game_mode.is_ai_turn(3)
        assert game_mode.is_ai_turn(4)

        # Verify validation passes
        assert game_mode.validate()

    def test_spectate_mode_difficulty_distribution(self):
        """Test that spectator mode has mixed difficulty levels."""
        game_mode = GameMode.spectate_ai()

        # Verify different difficulties are assigned
        difficulties = {config.difficulty for config in game_mode.ai_players}
        assert len(difficulties) >= 2  # Should have at least 2 different difficulties

        # Verify all difficulties are valid
        for config in game_mode.ai_players:
            assert config.difficulty in [Difficulty.EASY, Difficulty.MEDIUM, Difficulty.HARD]

    def test_turn_controller_spectate_mode_initialization(self):
        """Test turn controller initialization for spectate mode."""
        game_mode = GameMode.spectate_ai()
        controller = TurnController(game_mode, initial_player=1)

        # Verify configuration
        assert controller.game_mode == game_mode
        assert controller.current_player == 1
        assert controller.current_state == TurnState.HUMAN_TURN

        # In spectate mode, player 1 is AI
        assert controller.is_ai_turn

    def test_spectate_mode_all_ai_turns(self):
        """Test that all turns are AI-controlled in spectate mode."""
        game_mode = GameMode.spectate_ai()
        controller = TurnController(game_mode, initial_player=1)

        # All players should be AI-controlled
        for player_id in [1, 2, 3, 4]:
            assert game_mode.is_ai_turn(player_id)

        # Controller should detect AI turns
        assert controller.is_ai_turn

    @patch('src.models.turn_controller.time.sleep')
    def test_spectate_mode_automated_turn_progression(self, mock_sleep):
        """Test that spectate mode automatically progresses turns."""
        game_mode = GameMode.spectate_ai()
        controller = TurnController(game_mode, initial_player=1)

        # Track turn events
        events = []
        controller.add_turn_listener(lambda e: events.append(e))

        # Start a turn
        controller.start_turn()

        # Verify AI calculation started
        ai_started_events = [e for e in events if e.event_type == "AI_CALCULATION_STARTED"]
        assert len(ai_started_events) > 0

        # Verify state changed to AI_CALCULATING
        assert controller.current_state == TurnState.AI_CALCULATING

    def test_spectate_mode_turn_sequence(self):
        """Test that spectate mode follows correct turn sequence."""
        game_mode = GameMode.spectate_ai()
        controller = TurnController(game_mode, initial_player=1)

        # Test next player progression through all 4 players
        current = 1
        for expected_next in [2, 3, 4, 1]:
            next_player = controller.get_next_player(current)
            assert next_player == expected_next
            current = next_player

    def test_spectate_mode_game_statistics_creation(self):
        """Test that game statistics are created correctly for spectate mode."""
        stats = create_game_statistics("spectate")

        # Verify initial state
        assert stats.game_mode == "spectate"
        assert stats.total_turns == 0
        assert stats.winner_player_id is None
        assert len(stats.player_stats) == 4

        # Verify all players initialized
        for player_id in [1, 2, 3, 4]:
            assert player_id in stats.player_stats
            assert stats.player_stats[player_id].player_id == player_id
            assert stats.player_stats[player_id].moves_made == 0
            assert stats.player_stats[player_id].passes == 0

    def test_spectate_mode_statistics_recording(self):
        """Test that game statistics are recorded correctly."""
        stats = create_game_statistics("spectate")

        # Record moves for different players
        stats.record_move(1, ai_time=2.5, difficulty="Medium")
        stats.record_move(2, ai_time=3.1, difficulty="Hard")
        stats.record_move(3, ai_time=1.8, difficulty="Easy")

        # Verify turn count
        assert stats.total_turns == 3

        # Verify player stats
        assert stats.player_stats[1].moves_made == 1
        assert stats.player_stats[1].pieces_placed == 1
        assert stats.player_stats[1].ai_calculation_times == [2.5]
        assert "Medium" in stats.player_stats[1].difficulties

        assert stats.player_stats[2].moves_made == 1
        assert stats.player_stats[2].ai_calculation_times == [3.1]

        assert stats.player_stats[3].moves_made == 1
        assert stats.player_stats[3].ai_calculation_times == [1.8]

    def test_spectate_mode_statistics_pass_recording(self):
        """Test that pass turns are recorded correctly."""
        stats = create_game_statistics("spectate")

        # Record passes
        stats.record_pass(1, ai_time=1.0, difficulty="Medium")
        stats.record_pass(2, ai_time=1.5, difficulty="Hard")

        # Verify pass tracking
        assert stats.total_turns == 2
        assert stats.player_stats[1].passes == 1
        assert stats.player_stats[2].passes == 1

        # Verify move count unchanged
        assert stats.player_stats[1].moves_made == 0
        assert stats.player_stats[2].moves_made == 0

    def test_spectate_mode_final_scores(self):
        """Test that final scores are tracked correctly."""
        stats = create_game_statistics("spectate")

        # Set final scores
        scores = {1: 45, 2: 52, 3: 38, 4: 41}
        stats.set_final_scores(scores)

        # Verify scores
        assert stats.get_player_score(1) == 45
        assert stats.get_player_score(2) == 52
        assert stats.get_player_score(3) == 38
        assert stats.get_player_score(4) == 41

        # Verify winner detection
        assert stats.winner_player_id == 2  # Player 2 has highest score
        assert stats.get_winner_score() == 52

    def test_spectate_mode_game_duration(self):
        """Test that game duration is calculated correctly."""
        stats = create_game_statistics("spectate")

        # Should have non-zero start time
        assert stats.start_time is not None

        # Get duration before end
        duration1 = stats.get_game_duration()
        assert duration1 >= 0

        # Wait a bit
        time.sleep(0.1)

        # Duration should increase
        duration2 = stats.get_game_duration()
        assert duration2 > duration1

        # End game and check duration string
        stats.end_game()
        assert stats.end_time is not None
        duration_str = stats.get_duration_string()
        assert isinstance(duration_str, str)
        assert ":" in duration_str  # Format should be MM:SS

    def test_spectate_mode_statistics_summary(self):
        """Test that game summary is generated correctly."""
        stats = create_game_statistics("spectate")

        # Record some moves
        stats.record_move(1, ai_time=2.0)
        stats.record_move(2, ai_time=3.0)

        # Set final scores
        stats.set_final_scores({1: 40, 2: 50, 3: 30, 4: 35})

        # End game
        stats.end_game()

        # Get summary
        summary = stats.get_summary()

        # Verify summary contents
        assert summary["game_mode"] == "spectate"
        assert summary["total_turns"] == 2
        assert summary["winner"] == 2
        assert summary["winner_score"] == 50
        assert "scores" in summary
        assert summary["scores"][1] == 40
        assert summary["scores"][2] == 50
        assert "duration" in summary
        assert "total_ai_turns" in summary

    def test_spectate_mode_statistics_serialization(self):
        """Test that statistics can be serialized and deserialized."""
        stats = create_game_statistics("spectate")

        # Record some data
        stats.record_move(1, ai_time=2.5, difficulty="Medium")
        stats.record_pass(2, ai_time=1.0, difficulty="Hard")
        stats.set_final_scores({1: 45, 2: 50, 3: 35, 4: 40})
        stats.end_game()

        # Convert to dict
        data = stats.to_dict()

        # Verify structure
        assert "game_mode" in data
        assert "start_time" in data
        assert "end_time" in data
        assert "total_turns" in data
        assert "player_stats" in data
        assert "turn_history" in data
        assert "events" in data

        # Verify player stats
        assert "1" in data["player_stats"]
        assert data["player_stats"]["1"]["moves_made"] == 1
        assert "2" in data["player_stats"]
        assert data["player_stats"]["2"]["passes"] == 1

    def test_spectate_mode_complete_game_flow(self):
        """Test complete spectate mode game flow from start to finish."""
        # Create game mode and statistics
        game_mode = GameMode.spectate_ai()
        stats = create_game_statistics("spectate")

        # Create turn controller
        controller = TurnController(game_mode, initial_player=1)

        # Track events
        events = []
        controller.add_turn_listener(lambda e: events.append(e))

        # Simulate a few turns
        for turn in range(10):
            current_player = controller.current_player

            # Record in statistics
            stats.record_move(current_player, ai_time=2.0)

            # In real game, would call controller.start_turn()
            # For testing, we'll just verify the flow works

            # Advance to next player
            next_player = controller.get_next_player(current_player)
            controller.current_player = next_player

        # Verify game progression
        assert stats.total_turns == 10
        assert controller.current_player != 1  # Should have progressed

    def test_spectate_mode_event_logging(self):
        """Test that game events are logged correctly."""
        stats = create_game_statistics("spectate")

        # Record various events
        stats.record_move(1, piece_id="I1", position=(5, 5), ai_time=2.5, difficulty="Medium")
        stats.record_pass(2, ai_time=1.0, difficulty="Hard")
        stats.record_move(3, piece_id="V3", position=(10, 10), ai_time=3.2, difficulty="Easy")

        # Verify turn history
        assert len(stats.turn_history) == 3

        # Verify first event
        move_event = stats.turn_history[0]
        assert move_event["type"] == "MOVE"
        assert move_event["player_id"] == 1
        assert move_event["turn"] == 1
        assert move_event["piece_id"] == "I1"
        assert move_event["position"] == (5, 5)
        assert move_event["ai_time"] == 2.5
        assert move_event["difficulty"] == "Medium"

        # Verify pass event
        pass_event = stats.turn_history[1]
        assert pass_event["type"] == "PASS"
        assert pass_event["player_id"] == 2
        assert pass_event["turn"] == 2
        assert pass_event["ai_time"] == 1.0

        # Verify end event not yet added
        end_events = [e for e in stats.events if e["type"] == "GAME_END"]
        assert len(end_events) == 0

        # End game and verify
        stats.end_game()
        end_events = [e for e in stats.events if e["type"] == "GAME_END"]
        assert len(end_events) == 1
        assert end_events[0]["total_turns"] == 3

    def test_spectate_mode_multiple_games(self):
        """Test that multiple spectator games can be tracked independently."""
        # Create two separate statistics trackers
        stats1 = create_game_statistics("spectate")
        stats2 = create_game_statistics("spectate")

        # Record different data in each
        stats1.record_move(1, ai_time=2.0)
        stats1.set_final_scores({1: 45, 2: 50, 3: 38, 4: 41})
        stats1.end_game()

        stats2.record_move(1, ai_time=3.0)
        stats2.record_move(2, ai_time=4.0)
        stats2.set_final_scores({1: 55, 2: 42, 3: 39, 4: 44})
        stats2.end_game()

        # Verify independence
        assert stats1.total_turns == 1
        assert stats2.total_turns == 2
        assert stats1.winner_player_id == 2
        assert stats2.winner_player_id == 1
        assert stats1.get_player_score(1) == 45
        assert stats2.get_player_score(1) == 55

    def test_spectate_mode_statistics_average_calculations(self):
        """Test that AI time averages are calculated correctly."""
        stats = create_game_statistics("spectate")

        # Record multiple moves for same player
        stats.record_move(1, ai_time=2.0, difficulty="Medium")
        stats.record_move(1, ai_time=4.0, difficulty="Medium")
        stats.record_move(1, ai_time=6.0, difficulty="Medium")

        # Calculate averages
        p1_stats = stats.player_stats[1]
        assert p1_stats.get_average_ai_time() == 4.0  # (2+4+6)/3
        assert p1_stats.get_max_ai_time() == 6.0

        # Add a pass with AI time
        stats.record_pass(2, ai_time=1.0, difficulty="Hard")

        # Verify pass time counted
        p2_stats = stats.player_stats[2]
        assert p2_stats.get_average_ai_time() == 1.0

    def test_spectate_mode_ui_integration(self):
        """Test integration with spectator mode indicator UI."""
        from src.ui.spectator_mode_indicator import SpectatorModeIndicator

        # Create mock parent
        root = Mock()
        root.after = Mock()

        # Create game mode and indicator
        game_mode = GameMode.spectate_ai()

        # Note: We can't fully test the UI without tkinter,
        # but we can verify the class exists and has expected methods
        assert SpectatorModeIndicator is not None
        assert hasattr(SpectatorModeIndicator, 'update_current_player')
        assert hasattr(SpectatorModeIndicator, 'update_turn_count')
        assert hasattr(SpectatorModeIndicator, 'set_thinking_state')
        assert hasattr(SpectatorModeIndicator, 'set_game_over')


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
