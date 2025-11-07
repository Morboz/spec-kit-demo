"""Unit tests for Game Mode configuration."""

import pytest

from src.models.ai_config import AIConfig, Difficulty
from src.models.game_mode import GameMode, GameModeType


class TestGameMode:
    """Test suite for GameMode configuration."""

    def test_create_single_ai_mode(self):
        """Test creating single AI mode."""
        mode = GameMode.single_ai(Difficulty.MEDIUM)

        assert mode.mode_type == GameModeType.SINGLE_AI
        assert mode.difficulty == Difficulty.MEDIUM
        assert mode.human_player_position == 1
        assert len(mode.ai_players) == 1
        assert mode.ai_players[0].position == 3
        assert mode.get_player_count() == 2
        assert mode.get_ai_count() == 1

    def test_create_three_ai_mode(self):
        """Test creating three AI mode."""
        mode = GameMode.three_ai(Difficulty.EASY)

        assert mode.mode_type == GameModeType.THREE_AI
        assert mode.difficulty == Difficulty.EASY
        assert mode.human_player_position == 1
        assert len(mode.ai_players) == 3
        assert mode.get_player_count() == 4
        assert mode.get_ai_count() == 3

    def test_create_spectate_mode(self):
        """Test creating spectator mode."""
        mode = GameMode.spectate_ai()

        assert mode.mode_type == GameModeType.SPECTATE
        assert mode.human_player_position is None
        assert len(mode.ai_players) == 4
        assert mode.get_player_count() == 4
        assert mode.get_ai_count() == 4

    def test_is_ai_turn(self):
        """Test checking if current player is AI."""
        mode = GameMode.single_ai(Difficulty.MEDIUM)

        # Player 1 is human
        assert not mode.is_ai_turn(1)

        # Player 3 is AI
        assert mode.is_ai_turn(3)

        # Player 2 is not in game
        assert not mode.is_ai_turn(2)
        assert not mode.is_ai_turn(4)

    def test_is_ai_turn_three_ai(self):
        """Test is_ai_turn for three AI mode."""
        mode = GameMode.three_ai(Difficulty.MEDIUM)

        assert not mode.is_ai_turn(1)  # Human
        assert mode.is_ai_turn(2)  # AI
        assert mode.is_ai_turn(3)  # AI
        assert mode.is_ai_turn(4)  # AI

    def test_is_ai_turn_spectate(self):
        """Test is_ai_turn for spectator mode."""
        mode = GameMode.spectate_ai()

        # All players are AI
        assert mode.is_ai_turn(1)
        assert mode.is_ai_turn(2)
        assert mode.is_ai_turn(3)
        assert mode.is_ai_turn(4)

    def test_get_next_player_single_ai(self):
        """Test getting next player in single AI mode."""
        mode = GameMode.single_ai(Difficulty.MEDIUM)

        # Player 1 -> Player 3
        assert mode.get_next_player(1) == 3

        # Player 3 -> Player 1 (wrap around)
        assert mode.get_next_player(3) == 1

    def test_get_next_player_three_ai(self):
        """Test getting next player in three AI mode."""
        mode = GameMode.three_ai(Difficulty.MEDIUM)

        assert mode.get_next_player(1) == 2
        assert mode.get_next_player(2) == 3
        assert mode.get_next_player(3) == 4
        assert mode.get_next_player(4) == 1

    def test_get_next_player_spectate(self):
        """Test getting next player in spectator mode."""
        mode = GameMode.spectate_ai()

        assert mode.get_next_player(1) == 2
        assert mode.get_next_player(2) == 3
        assert mode.get_next_player(3) == 4
        assert mode.get_next_player(4) == 1

    def test_validate_single_ai(self):
        """Test validating single AI mode configuration."""
        mode = GameMode.single_ai(Difficulty.MEDIUM)
        assert mode.validate()

    def test_validate_three_ai(self):
        """Test validating three AI mode configuration."""
        mode = GameMode.three_ai(Difficulty.EASY)
        assert mode.validate()

    def test_validate_spectate(self):
        """Test validating spectator mode configuration."""
        mode = GameMode.spectate_ai()
        assert mode.validate()

    def test_custom_ai_configs(self):
        """Test creating mode with custom AI configurations."""
        custom_ais = [
            AIConfig(position=2, difficulty=Difficulty.EASY),
            AIConfig(position=3, difficulty=Difficulty.MEDIUM),
            AIConfig(position=4, difficulty=Difficulty.HARD),
        ]

        mode = GameMode(GameModeType.THREE_AI, Difficulty.MEDIUM, custom_ais)

        assert len(mode.ai_players) == 3
        assert mode.ai_players[0].difficulty == Difficulty.EASY
        assert mode.ai_players[1].difficulty == Difficulty.MEDIUM
        assert mode.ai_players[2].difficulty == Difficulty.HARD

    def test_get_player_count(self):
        """Test getting total player count."""
        single_mode = GameMode.single_ai(Difficulty.MEDIUM)
        assert single_mode.get_player_count() == 2

        three_mode = GameMode.three_ai(Difficulty.MEDIUM)
        assert three_mode.get_player_count() == 4

        spectate_mode = GameMode.spectate_ai()
        assert spectate_mode.get_player_count() == 4

    def test_get_ai_count(self):
        """Test getting AI player count."""
        single_mode = GameMode.single_ai(Difficulty.MEDIUM)
        assert single_mode.get_ai_count() == 1

        three_mode = GameMode.three_ai(Difficulty.MEDIUM)
        assert three_mode.get_ai_count() == 3

        spectate_mode = GameMode.spectate_ai()
        assert spectate_mode.get_ai_count() == 4

    def test_str_representation(self):
        """Test string representation of game mode."""
        mode = GameMode.single_ai(Difficulty.MEDIUM)
        repr_str = repr(mode)

        assert "single_ai" in repr_str
        assert "players=2" in repr_str
        assert "ai=1" in repr_str

    def test_invalid_configuration_raises_error(self):
        """Test that invalid configuration raises ValueError."""
        # Try to create AIConfig with invalid position - should raise immediately
        with pytest.raises(ValueError, match="Position must be 1-4"):
            AIConfig(position=5, difficulty=Difficulty.MEDIUM)  # Invalid position

    def test_duplicate_positions_raises_error(self):
        """Test that duplicate positions raise ValueError."""
        custom_ais = [
            AIConfig(position=2, difficulty=Difficulty.MEDIUM),
            AIConfig(position=2, difficulty=Difficulty.HARD),  # Duplicate!
        ]

        # This should fail validation and raise ValueError
        with pytest.raises(ValueError, match="Invalid game mode configuration"):
            GameMode(GameModeType.THREE_AI, Difficulty.MEDIUM, custom_ais)

    def test_difficulty_property(self):
        """Test difficulty property."""
        mode = GameMode.single_ai(Difficulty.HARD)
        assert mode.difficulty == Difficulty.HARD

    def test_mode_type_property(self):
        """Test mode type property."""
        mode = GameMode.single_ai(Difficulty.MEDIUM)
        assert mode.mode_type == GameModeType.SINGLE_AI

    def test_human_player_position_property(self):
        """Test human player position property."""
        single_mode = GameMode.single_ai(Difficulty.MEDIUM)
        assert single_mode.human_player_position == 1

        spectate_mode = GameMode.spectate_ai()
        assert spectate_mode.human_player_position is None

    def test_ai_players_property(self):
        """Test AI players property."""
        mode = GameMode.three_ai(Difficulty.EASY)
        assert len(mode.ai_players) == 3
        assert all(isinstance(config, AIConfig) for config in mode.ai_players)

    def test_default_spectate_difficulty_mix(self):
        """Test that spectator mode has mixed difficulties."""
        mode = GameMode.spectate_ai()

        # Should have different difficulties for interesting games
        difficulties = [config.difficulty for config in mode.ai_players]
        assert Difficulty.HARD in difficulties
        assert Difficulty.MEDIUM in difficulties
        assert Difficulty.EASY in difficulties

    def test_custom_difficulty_applies_to_all_ai(self):
        """Test that custom difficulty applies to all AI players."""
        mode = GameMode.three_ai(Difficulty.HARD)

        # All AI players should have HARD difficulty
        for config in mode.ai_players:
            assert config.difficulty == Difficulty.HARD

    def test_invalid_mode_type_raises_error(self):
        """Test that invalid mode type raises error."""
        # Create a mode instance bypassing __init__ to test validation directly
        mode = GameMode.__new__(GameMode)
        mode.mode_type = "invalid"  # Not a GameModeType
        mode.difficulty = Difficulty.MEDIUM
        mode.human_player_position = 1
        mode.ai_players = []

        # validate() should return False for invalid mode_type
        assert not mode.validate()
