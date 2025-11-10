"""
Integration tests for Spectate mode.

Tests the spectator mode configuration and setup functionality.
"""

import pytest

from blokus_game.models.game_mode import Difficulty, GameMode, GameModeType


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
            assert config.difficulty in [
                Difficulty.EASY,
                Difficulty.MEDIUM,
                Difficulty.HARD,
            ]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
