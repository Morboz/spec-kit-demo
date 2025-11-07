"""
Unit tests for game statistics tracking module.

Tests the GameStatistics and PlayerStats classes for accurate tracking
of AI game statistics and performance metrics.
"""

import os
import tempfile

import pytest

from src.models.game_stats import (
    GameStatistics,
    PlayerStats,
    create_game_statistics,
)


class TestPlayerStats:
    """Test suite for PlayerStats class."""

    def test_player_stats_initialization(self):
        """Test PlayerStats initializes correctly."""
        stats = PlayerStats(player_id=1)

        assert stats.player_id == 1
        assert stats.moves_made == 0
        assert stats.passes == 0
        assert stats.pieces_placed == 0
        assert stats.total_score == 0
        assert stats.ai_calculation_times == []
        assert stats.difficulties == []

    def test_add_move(self):
        """Test recording a move."""
        stats = PlayerStats(player_id=2)

        stats.add_move(ai_time=2.5, difficulty="Medium")

        assert stats.moves_made == 1
        assert stats.pieces_placed == 1
        assert stats.ai_calculation_times == [2.5]
        assert stats.difficulties == ["Medium"]

    def test_add_multiple_moves(self):
        """Test recording multiple moves."""
        stats = PlayerStats(player_id=3)

        stats.add_move(ai_time=1.0)
        stats.add_move(ai_time=2.0)
        stats.add_move(ai_time=3.0)

        assert stats.moves_made == 3
        assert stats.pieces_placed == 3
        assert len(stats.ai_calculation_times) == 3
        assert stats.ai_calculation_times == [1.0, 2.0, 3.0]

    def test_add_pass(self):
        """Test recording a pass turn."""
        stats = PlayerStats(player_id=1)

        stats.add_pass(ai_time=1.5, difficulty="Hard")

        assert stats.passes == 1
        assert stats.moves_made == 0  # Should not increase
        assert stats.ai_calculation_times == [1.5]
        assert stats.difficulties == ["Hard"]

    def test_add_pass_does_not_increment_moves(self):
        """Test that pass doesn't increment moves counter."""
        stats = PlayerStats(player_id=4)

        stats.add_move(ai_time=2.0)
        stats.add_pass(ai_time=1.0)

        assert stats.moves_made == 1
        assert stats.passes == 1

    def test_set_final_score(self):
        """Test setting final score."""
        stats = PlayerStats(player_id=1)

        stats.set_final_score(45)

        assert stats.total_score == 45

        stats.set_final_score(52)

        assert stats.total_score == 52

    def test_get_average_ai_time(self):
        """Test calculating average AI time."""
        stats = PlayerStats(player_id=2)

        # No times yet
        assert stats.get_average_ai_time() == 0.0

        # Add times
        stats.add_move(ai_time=2.0)
        stats.add_move(ai_time=4.0)
        stats.add_move(ai_time=6.0)

        assert stats.get_average_ai_time() == 4.0  # (2+4+6)/3

    def test_get_max_ai_time(self):
        """Test calculating maximum AI time."""
        stats = PlayerStats(player_id=3)

        # No times yet
        assert stats.get_max_ai_time() == 0.0

        # Add times
        stats.add_move(ai_time=2.0)
        stats.add_move(ai_time=5.0)
        stats.add_move(ai_time=3.0)

        assert stats.get_max_ai_time() == 5.0

    def test_get_average_ai_time_single_value(self):
        """Test average with single AI time."""
        stats = PlayerStats(player_id=1)

        stats.add_move(ai_time=3.5)

        assert stats.get_average_ai_time() == 3.5

    def test_get_average_ai_time_with_passes(self):
        """Test average includes pass times."""
        stats = PlayerStats(player_id=4)

        stats.add_move(ai_time=2.0)
        stats.add_pass(ai_time=1.0)
        stats.add_move(ai_time=3.0)

        # Average of [2.0, 1.0, 3.0]
        assert stats.get_average_ai_time() == 2.0

    def test_to_dict(self):
        """Test converting PlayerStats to dictionary."""
        stats = PlayerStats(player_id=1)
        stats.add_move(ai_time=2.5, difficulty="Medium")
        stats.add_move(ai_time=3.5, difficulty="Medium")
        stats.add_pass(ai_time=1.0, difficulty="Medium")
        stats.set_final_score(45)

        result = stats.to_dict()

        assert result["player_id"] == 1
        assert result["moves_made"] == 2
        assert result["passes"] == 1
        assert result["pieces_placed"] == 2
        assert result["total_score"] == 45
        assert result["average_ai_time"] == 2.333  # (2.5 + 3.5 + 1.0) / 3
        assert result["max_ai_time"] == 3.5
        assert "Medium" in result["difficulties_used"]

    def test_difficulty_tracking(self):
        """Test tracking different difficulties."""
        stats = PlayerStats(player_id=1)

        stats.add_move(ai_time=1.0, difficulty="Easy")
        stats.add_move(ai_time=2.0, difficulty="Medium")
        stats.add_move(ai_time=3.0, difficulty="Hard")

        assert len(stats.difficulties) == 3
        assert "Easy" in stats.difficulties
        assert "Medium" in stats.difficulties
        assert "Hard" in stats.difficulties

        # to_dict should deduplicate
        result = stats.to_dict()
        difficulties = set(result["difficulties_used"])
        assert difficulties == {"Easy", "Medium", "Hard"}


class TestGameStatistics:
    """Test suite for GameStatistics class."""

    def test_game_statistics_initialization(self):
        """Test GameStatistics initializes correctly."""
        stats = create_game_statistics("spectate")

        assert stats.game_mode == "spectate"
        assert stats.start_time is not None
        assert stats.end_time is None
        assert stats.total_turns == 0
        assert len(stats.player_stats) == 4
        assert stats.turn_history == []
        assert stats.events == []
        assert stats.winner_player_id is None

        # Verify all 4 players initialized
        for player_id in [1, 2, 3, 4]:
            assert player_id in stats.player_stats
            assert stats.player_stats[player_id].player_id == player_id

    def test_record_move(self):
        """Test recording a move."""
        stats = create_game_statistics("spectate")

        stats.record_move(1, ai_time=2.5, difficulty="Medium")

        assert stats.total_turns == 1
        assert stats.player_stats[1].moves_made == 1
        assert stats.player_stats[1].pieces_placed == 1
        assert 2.5 in stats.player_stats[1].ai_calculation_times

        # Verify turn history
        assert len(stats.turn_history) == 1
        turn = stats.turn_history[0]
        assert turn["type"] == "MOVE"
        assert turn["player_id"] == 1
        assert turn["turn"] == 1

        # Verify events
        assert len(stats.events) == 1

    def test_record_move_with_piece_info(self):
        """Test recording move with piece and position info."""
        stats = create_game_statistics("spectate")

        stats.record_move(
            player_id=2, piece_id="I1", position=(5, 5), ai_time=3.0, difficulty="Hard"
        )

        turn = stats.turn_history[0]
        assert turn["piece_id"] == "I1"
        assert turn["position"] == (5, 5)
        assert turn["ai_time"] == 3.0
        assert turn["difficulty"] == "Hard"

    def test_record_pass(self):
        """Test recording a pass turn."""
        stats = create_game_statistics("spectate")

        stats.record_pass(3, ai_time=1.5, difficulty="Easy")

        assert stats.total_turns == 1
        assert stats.player_stats[3].passes == 1
        assert stats.player_stats[3].moves_made == 0  # Should not increase

        turn = stats.turn_history[0]
        assert turn["type"] == "PASS"
        assert turn["player_id"] == 3

    def test_record_multiple_turns(self):
        """Test recording multiple turns."""
        stats = create_game_statistics("spectate")

        stats.record_move(1, ai_time=2.0)
        stats.record_move(2, ai_time=3.0)
        stats.record_pass(3, ai_time=1.0)
        stats.record_move(4, ai_time=2.5)

        assert stats.total_turns == 4

        # Verify each player has correct stats
        assert stats.player_stats[1].moves_made == 1
        assert stats.player_stats[2].moves_made == 1
        assert stats.player_stats[3].passes == 1
        assert stats.player_stats[4].moves_made == 1

    def test_set_final_scores(self):
        """Test setting final scores for all players."""
        stats = create_game_statistics("spectate")

        scores = {1: 45, 2: 52, 3: 38, 4: 41}
        stats.set_final_scores(scores)

        assert stats.get_player_score(1) == 45
        assert stats.get_player_score(2) == 52
        assert stats.get_player_score(3) == 38
        assert stats.get_player_score(4) == 41

        # Verify winner detection
        assert stats.winner_player_id == 2  # Player 2 has highest score
        assert stats.get_winner_score() == 52

    def test_get_scores_dict(self):
        """Test getting scores as dictionary."""
        stats = create_game_statistics("spectate")

        scores = {1: 45, 2: 52, 3: 38, 4: 41}
        stats.set_final_scores(scores)

        result = stats.get_scores_dict()
        assert result == scores

    def test_end_game(self):
        """Test ending a game."""
        stats = create_game_statistics("spectate")

        stats.record_move(1)
        stats.record_move(2)
        stats.set_final_scores({1: 45, 2: 50, 3: 38, 4: 41})

        assert stats.end_time is None

        stats.end_game()

        assert stats.end_time is not None
        assert stats.end_time > stats.start_time

        # Verify end event added
        end_events = [e for e in stats.events if e["type"] == "GAME_END"]
        assert len(end_events) == 1
        assert end_events[0]["total_turns"] == 2
        assert end_events[0]["winner"] == 2

    def test_get_game_duration(self):
        """Test getting game duration."""
        stats = create_game_statistics("spectate")

        # Before end
        duration1 = stats.get_game_duration()
        assert duration1 >= 0

        # After ending
        stats.end_game()
        duration2 = stats.get_game_duration()
        assert duration2 >= 0
        assert duration2 >= duration1

    def test_get_duration_string(self):
        """Test formatted duration string."""
        stats = create_game_statistics("spectate")

        # Before end
        duration_str = stats.get_duration_string()
        assert isinstance(duration_str, str)
        assert ":" in duration_str  # Should be MM:SS format

        # After end
        stats.end_game()
        duration_str = stats.get_duration_string()
        assert isinstance(duration_str, str)

        # Verify format: MM:SS
        parts = duration_str.split(":")
        assert len(parts) == 2
        assert all(part.isdigit() for part in parts)

    def test_get_summary(self):
        """Test getting game summary."""
        stats = create_game_statistics("spectate")

        stats.record_move(1, ai_time=2.0)
        stats.record_move(2, ai_time=3.0)
        stats.set_final_scores({1: 45, 2: 50, 3: 38, 4: 41})
        stats.end_game()

        summary = stats.get_summary()

        assert "game_mode" in summary
        assert summary["game_mode"] == "spectate"
        assert "duration" in summary
        assert "total_turns" in summary
        assert summary["total_turns"] == 2
        assert "winner" in summary
        assert summary["winner"] == 2
        assert "winner_score" in summary
        assert summary["winner_score"] == 50
        assert "scores" in summary
        assert summary["scores"] == {1: 45, 2: 50, 3: 38, 4: 41}
        assert "total_ai_turns" in summary
        assert "average_turn_time" in summary

    def test_to_dict(self):
        """Test serializing to dictionary."""
        stats = create_game_statistics("spectate")

        stats.record_move(1, ai_time=2.5, difficulty="Medium")
        stats.record_pass(2, ai_time=1.0, difficulty="Hard")
        stats.set_final_scores({1: 45, 2: 50, 3: 38, 4: 41})
        stats.end_game()

        data = stats.to_dict()

        # Verify structure
        assert "game_mode" in data
        assert "start_time" in data
        assert "end_time" in data
        assert "total_turns" in data
        assert "winner_player_id" in data
        assert "player_stats" in data
        assert "turn_history" in data
        assert "events" in data

        # Verify content
        assert data["game_mode"] == "spectate"
        assert data["total_turns"] == 2
        assert data["winner_player_id"] == 2

        # Verify player stats
        assert 1 in data["player_stats"]
        assert data["player_stats"][1]["moves_made"] == 1
        assert 2 in data["player_stats"]
        assert data["player_stats"][2]["passes"] == 1

    def test_save_to_file(self):
        """Test saving statistics to file."""
        stats = create_game_statistics("spectate")

        stats.record_move(1, ai_time=2.5)
        stats.set_final_scores({1: 45, 2: 50, 3: 38, 4: 41})
        stats.end_game()

        # Save to temporary file
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
            filename = f.name

        try:
            stats.save_to_file(filename)

            # Verify file exists and has content
            assert os.path.exists(filename)
            with open(filename) as f:
                content = f.read()
                assert len(content) > 0
                assert '"game_mode"' in content
        finally:
            # Clean up
            if os.path.exists(filename):
                os.unlink(filename)

    def test_load_from_file(self):
        """Test loading statistics from file."""
        stats1 = create_game_statistics("spectate")

        stats1.record_move(1, ai_time=2.5, difficulty="Medium")
        stats1.record_pass(2, ai_time=1.0, difficulty="Hard")
        stats1.set_final_scores({1: 45, 2: 50, 3: 38, 4: 41})
        stats1.end_game()

        # Save to temporary file
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
            filename = f.name

        try:
            # Save
            stats1.save_to_file(filename)

            # Load
            stats2 = GameStatistics.load_from_file(filename)

            # Verify all data loaded correctly
            assert stats2.game_mode == "spectate"
            assert stats2.total_turns == 2
            assert stats2.winner_player_id == 2
            assert stats2.get_player_score(1) == 45
            assert stats2.get_player_score(2) == 50

            # Verify player stats
            assert stats2.player_stats[1].moves_made == 1
            assert stats2.player_stats[2].passes == 1

            # Verify turn history
            assert len(stats2.turn_history) == 2

            # Verify events
            assert len(stats2.events) == 3  # 2 moves + 1 end
        finally:
            # Clean up
            if os.path.exists(filename):
                os.unlink(filename)

    def test_turn_history_order(self):
        """Test that turn history maintains order."""
        stats = create_game_statistics("spectate")

        stats.record_move(3)
        stats.record_move(1)
        stats.record_move(4)
        stats.record_move(2)

        # Verify order
        assert stats.turn_history[0]["turn"] == 1
        assert stats.turn_history[0]["player_id"] == 3

        assert stats.turn_history[1]["turn"] == 2
        assert stats.turn_history[1]["player_id"] == 1

        assert stats.turn_history[2]["turn"] == 3
        assert stats.turn_history[2]["player_id"] == 4

        assert stats.turn_history[3]["turn"] == 4
        assert stats.turn_history[3]["player_id"] == 2

    def test_multiple_games_independent(self):
        """Test that multiple statistics trackers are independent."""
        stats1 = create_game_statistics("spectate")
        stats2 = create_game_statistics("three_ai")

        # Add different data
        stats1.record_move(1)
        stats1.record_move(2)

        stats2.record_move(1)
        stats2.record_move(2)
        stats2.record_move(3)

        stats1.set_final_scores({1: 45, 2: 50, 3: 38, 4: 41})
        stats2.set_final_scores({1: 55, 2: 42, 3: 39, 4: 44})

        # Verify independence
        assert stats1.total_turns == 2
        assert stats2.total_turns == 3
        assert stats1.winner_player_id == 2
        assert stats2.winner_player_id == 1
        assert stats1.get_player_score(1) == 45
        assert stats2.get_player_score(1) == 55

    def test_ai_time_tracking_accuracy(self):
        """Test accurate AI time tracking."""
        stats = create_game_statistics("spectate")

        # Record moves with different times
        stats.record_move(1, ai_time=1.5)
        stats.record_move(2, ai_time=2.5)
        stats.record_move(3, ai_time=3.5)

        # Verify each player's times
        assert stats.player_stats[1].get_average_ai_time() == 1.5
        assert stats.player_stats[2].get_average_ai_time() == 2.5
        assert stats.player_stats[3].get_average_ai_time() == 3.5

        # Overall average
        all_times = []
        for player_id in [1, 2, 3]:
            all_times.extend(stats.player_stats[player_id].ai_calculation_times)
        assert all_times == [1.5, 2.5, 3.5]

    def test_empty_game_statistics(self):
        """Test statistics with no moves recorded."""
        stats = create_game_statistics("spectate")

        # No moves recorded
        assert stats.total_turns == 0
        assert stats.get_game_duration() >= 0
        assert stats.get_duration_string() is not None

        # Can still set scores and end game
        stats.set_final_scores({1: 0, 2: 0, 3: 0, 4: 0})
        assert stats.winner_player_id is not None  # First with highest score

        stats.end_game()
        assert stats.end_time is not None

        # Summary should work
        summary = stats.get_summary()
        assert summary["total_turns"] == 0

    def test_piece_tracking(self):
        """Test tracking piece placements."""
        stats = create_game_statistics("spectate")

        stats.record_move(1, piece_id="I1")
        stats.record_move(1, piece_id="V3")
        stats.record_move(2, piece_id="L5")

        assert stats.player_stats[1].pieces_placed == 2
        assert stats.player_stats[2].pieces_placed == 1

    def test_position_tracking(self):
        """Test tracking piece positions."""
        stats = create_game_statistics("spectate")

        stats.record_move(1, position=(5, 5))
        stats.record_move(2, position=(10, 10))
        stats.record_move(3, position=(15, 15))

        # Verify positions in turn history
        assert stats.turn_history[0]["position"] == (5, 5)
        assert stats.turn_history[1]["position"] == (10, 10)
        assert stats.turn_history[2]["position"] == (15, 15)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
