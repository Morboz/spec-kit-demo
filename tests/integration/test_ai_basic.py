"""Integration tests for basic AI functionality."""

from blokus_game.models.ai_config import AIConfig
from blokus_game.models.ai_player import AIPlayer
from blokus_game.models.game_mode import Difficulty, GameMode, GameModeType
from blokus_game.services.ai_strategy import (
    CornerStrategy,
    RandomStrategy,
    StrategicStrategy,
)
from blokus_game.ui.game_mode_selector import GameModeSelector


class TestAIGameModeIntegration:
    """Integration tests for AI game mode configuration."""

    def test_create_single_ai_mode(self):
        """Test creating and configuring single AI mode."""
        game_mode = GameMode.single_ai(Difficulty.MEDIUM)

        assert game_mode.mode_type == GameModeType.SINGLE_AI
        assert game_mode.difficulty == Difficulty.MEDIUM
        assert game_mode.human_player_position == 1
        assert len(game_mode.ai_players) == 1
        assert game_mode.ai_players[0].position == 3
        assert game_mode.get_player_count() == 2
        assert game_mode.get_ai_count() == 1

    def test_create_three_ai_mode(self):
        """Test creating and configuring three AI mode."""
        game_mode = GameMode.three_ai(Difficulty.EASY)

        assert game_mode.mode_type == GameModeType.THREE_AI
        assert game_mode.difficulty == Difficulty.EASY
        assert game_mode.human_player_position == 1
        assert len(game_mode.ai_players) == 3
        assert game_mode.get_player_count() == 4
        assert game_mode.get_ai_count() == 3

    def test_create_spectate_mode(self):
        """Test creating and configuring spectator mode."""
        game_mode = GameMode.spectate_ai()

        assert game_mode.mode_type == GameModeType.SPECTATE
        assert game_mode.human_player_position is None
        assert len(game_mode.ai_players) == 4
        assert game_mode.get_player_count() == 4
        assert game_mode.get_ai_count() == 4

    def test_game_mode_selector_integration(self):
        """Test game mode selector creates valid modes."""
        # Single AI
        mode = GameModeSelector.create_game_mode("single_ai", "Hard")
        assert isinstance(mode, GameMode)
        assert mode.mode_type == GameModeType.SINGLE_AI

        # Three AI
        mode = GameModeSelector.create_game_mode("three_ai", "Easy")
        assert isinstance(mode, GameMode)
        assert mode.mode_type == GameModeType.THREE_AI

        # Spectate
        mode = GameModeSelector.create_game_mode("spectate", None)
        assert isinstance(mode, GameMode)
        assert mode.mode_type == GameModeType.SPECTATE

    def test_ai_turn_detection(self):
        """Test detecting AI turns in different modes."""
        # Single AI mode
        mode = GameMode.single_ai(Difficulty.MEDIUM)
        assert not mode.is_ai_turn(1)  # Human player
        assert mode.is_ai_turn(3)  # AI player

        # Three AI mode
        mode = GameMode.three_ai(Difficulty.MEDIUM)
        assert not mode.is_ai_turn(1)  # Human player
        assert mode.is_ai_turn(2)  # AI player
        assert mode.is_ai_turn(3)  # AI player
        assert mode.is_ai_turn(4)  # AI player

        # Spectate mode
        mode = GameMode.spectate_ai()
        assert mode.is_ai_turn(1)  # All AI
        assert mode.is_ai_turn(2)  # All AI
        assert mode.is_ai_turn(3)  # All AI
        assert mode.is_ai_turn(4)  # All AI

    def test_next_player_advancement(self):
        """Test advancing to next player in different modes."""
        # Single AI mode (only positions 1 and 3 active)
        mode = GameMode.single_ai(Difficulty.MEDIUM)
        assert mode.get_next_player(1) == 3
        assert mode.get_next_player(3) == 1

        # Three AI mode (all positions active)
        mode = GameMode.three_ai(Difficulty.MEDIUM)
        assert mode.get_next_player(1) == 2
        assert mode.get_next_player(2) == 3
        assert mode.get_next_player(3) == 4
        assert mode.get_next_player(4) == 1

        # Spectate mode (all positions active)
        mode = GameMode.spectate_ai()
        assert mode.get_next_player(1) == 2
        assert mode.get_next_player(4) == 1


class TestAIPlayerIntegration:
    """Integration tests for AI player creation and configuration."""

    def test_create_ai_player_from_config(self):
        """Test creating AI player from configuration."""
        config = AIConfig(position=2, difficulty=Difficulty.EASY)
        ai_player = config.create_player()

        assert isinstance(ai_player, AIPlayer)
        assert ai_player.player_id == 2
        assert ai_player.difficulty == "Easy"
        assert ai_player.name == "AI Player 2"
        assert ai_player.color == config.color

    def test_ai_players_with_different_strategies(self):
        """Test AI players with different strategies."""
        strategies = [
            (Difficulty.EASY, RandomStrategy),
            (Difficulty.MEDIUM, CornerStrategy),
            (Difficulty.HARD, StrategicStrategy),
        ]

        for difficulty, expected_strategy_class in strategies:
            config = AIConfig(position=1, difficulty=difficulty)
            ai_player = config.create_player()

            assert isinstance(ai_player.strategy, expected_strategy_class)
            assert ai_player.difficulty == difficulty.value

    def test_ai_player_calculation(self):
        """Test AI player move calculation."""
        strategy = RandomStrategy()
        ai_player = AIPlayer(1, strategy, "blue", "Test AI")

        # Empty board
        board = [[0] * 20 for _ in range(20)]
        pieces = [ai_player.pieces[0]]  # Use first piece

        move = ai_player.calculate_move(board, pieces)

        # Should either return a move or None
        assert move is None or (move.piece is not None and move.position is not None)

    def test_multiple_ai_players_independence(self):
        """Test that multiple AI players operate independently."""
        strategies = [
            RandomStrategy(),
            CornerStrategy(),
            StrategicStrategy(),
        ]

        ai_players = []
        for i, strategy in enumerate(strategies, 2):
            config = AIConfig(position=i, difficulty=Difficulty.MEDIUM)
            ai_player = config.create_player(strategy)
            ai_players.append(ai_player)

        # Each AI should have independent strategy
        assert ai_players[0].strategy != ai_players[1].strategy
        assert ai_players[1].strategy != ai_players[2].strategy

        # Each AI should have its own strategy's difficulty (not the config's difficulty when strategy is overridden)
        expected_difficulties = ["Easy", "Medium", "Hard"]  # Based on strategy types
        actual_difficulties = [ai.difficulty for ai in ai_players]
        assert actual_difficulties == expected_difficulties


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
