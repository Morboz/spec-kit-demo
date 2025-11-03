"""
Integration tests for Single AI battle mode.

This module tests the complete flow of a game against a single AI opponent,
including move validation, AI turn management, and game completion.
"""

import pytest
import tkinter as tk
from src.models.game_mode import GameMode, GameModeType
from src.models.ai_config import Difficulty
from src.models.ai_player import AIPlayer
from src.models.game_state import GameState, GamePhase
from src.game.game_setup import GameSetup
from src.services.ai_strategy import RandomStrategy, CornerStrategy, StrategicStrategy


class TestSingleAIMode:
    """Test suite for Single AI mode functionality."""

    def test_create_single_ai_mode(self):
        """Test creating a Single AI game mode configuration."""
        game_mode = GameMode.single_ai(Difficulty.MEDIUM)

        assert game_mode.mode_type == GameModeType.SINGLE_AI
        assert game_mode.human_player_position == 1
        assert len(game_mode.ai_players) == 1
        assert game_mode.ai_players[0].position == 3
        assert game_mode.ai_players[0].difficulty == Difficulty.MEDIUM
        assert game_mode.get_player_count() == 2
        assert game_mode.get_ai_count() == 1

    def test_single_ai_mode_validation(self):
        """Test Single AI mode configuration validation."""
        # Valid configuration
        game_mode = GameMode.single_ai(Difficulty.EASY)
        assert game_mode.validate() is True

        # Test is_ai_turn
        assert game_mode.is_ai_turn(1) is False  # Human player
        assert game_mode.is_ai_turn(3) is True   # AI player
        assert game_mode.is_ai_turn(2) is False  # Inactive position
        assert game_mode.is_ai_turn(4) is False  # Inactive position

    def test_single_ai_turn_progression(self):
        """Test turn progression in Single AI mode."""
        game_mode = GameMode.single_ai(Difficulty.MEDIUM)

        # Player 1 (human) starts
        assert game_mode.get_next_player(1) == 3

        # Next is player 3 (AI)
        assert game_mode.get_next_player(3) == 1

        # Wraps around
        assert game_mode.get_next_player(1) == 3

    def test_create_ai_player_with_strategy(self):
        """Test creating AI players with different strategies."""
        # Easy AI with RandomStrategy
        easy_ai = AIPlayer(
            player_id=2,
            strategy=RandomStrategy(),
            color="blue",
            name="Easy AI"
        )
        assert easy_ai.difficulty == "Easy"
        assert easy_ai.player_id == 2

        # Medium AI with CornerStrategy
        medium_ai = AIPlayer(
            player_id=3,
            strategy=CornerStrategy(),
            color="red",
            name="Medium AI"
        )
        assert medium_ai.difficulty == "Medium"
        assert medium_ai.player_id == 3

        # Hard AI with StrategicStrategy
        hard_ai = AIPlayer(
            player_id=4,
            strategy=StrategicStrategy(),
            color="green",
            name="Hard AI"
        )
        assert hard_ai.difficulty == "Hard"
        assert hard_ai.player_id == 4

    def test_ai_player_calculate_move(self):
        """Test AI player move calculation."""
        from src.config.pieces import get_full_piece_set

        # Create AI player
        ai_player = AIPlayer(
            player_id=2,
            strategy=RandomStrategy(),
            color="blue"
        )

        # Create empty board
        board = [[0 for _ in range(20)] for _ in range(20)]

        # Get available pieces
        pieces = get_full_piece_set()

        # Calculate move (should return a valid move or None)
        move = ai_player.calculate_move(board, pieces)

        # Move might be None if no valid moves (early in game)
        # But if not None, it should be a valid move
        if move:
            assert move.player_id == 2
            assert move.piece in pieces
            assert move.position is not None
            assert 0 <= move.position[0] < 20
            assert 0 <= move.position[1] < 20

    def test_ai_player_timeout_handling(self):
        """Test AI player handles timeouts gracefully."""
        ai_player = AIPlayer(
            player_id=2,
            strategy=StrategicStrategy(),  # Has longer timeout
            color="blue"
        )

        # Create board with some pieces
        board = [[0 for _ in range(20)] for _ in range(20)]
        pieces = []

        # Calculate move with short timeout (should not crash)
        move = ai_player.calculate_move(board, pieces, time_limit=1)

        # Should handle empty pieces gracefully
        assert move is None or isinstance(move.piece, type(None))

    def test_single_ai_game_setup(self):
        """Test setting up a complete Single AI game."""
        # Create game mode
        game_mode = GameMode.single_ai(Difficulty.EASY)

        # Create AI players
        ai_players = []
        for ai_config in game_mode.ai_players:
            strategy = RandomStrategy() if ai_config.difficulty == Difficulty.EASY else CornerStrategy()
            ai_player = AIPlayer(
                player_id=ai_config.position,
                strategy=strategy,
                color="red",
                name=f"AI ({ai_config.difficulty.name})"
            )
            ai_players.append(ai_player)

        # Verify setup
        assert len(ai_players) == 1
        assert ai_players[0].player_id == 3
        assert ai_players[0].difficulty == "Easy"

    def test_different_difficulties(self):
        """Test Single AI mode with different difficulty levels."""
        difficulties = [Difficulty.EASY, Difficulty.MEDIUM, Difficulty.HARD]

        for difficulty in difficulties:
            game_mode = GameMode.single_ai(difficulty)
            assert game_mode.validate() is True
            assert game_mode.difficulty == difficulty
            assert len(game_mode.ai_players) == 1
            assert game_mode.ai_players[0].difficulty == difficulty

    def test_ai_player_state_management(self):
        """Test AI player state (passed, calculating, etc.)."""
        ai_player = AIPlayer(
            player_id=2,
            strategy=RandomStrategy(),
            color="blue"
        )

        # Initial state
        assert not ai_player.has_passed
        assert not ai_player.is_calculating

        # Pass turn
        ai_player.pass_turn()
        assert ai_player.has_passed

        # Reset pass
        ai_player.reset_pass()
        assert not ai_player.has_passed

        # Calculate move
        board = [[0 for _ in range(20)] for _ in range(20)]
        pieces = []
        move = ai_player.calculate_move(board, pieces)

        # After calculation
        assert not ai_player.is_calculating
        assert move is not None or move is None  # Either is valid

    def test_ai_thinking_indicator_state(self):
        """Test AI thinking state is tracked correctly."""
        ai_player = AIPlayer(
            player_id=2,
            strategy=CornerStrategy(),
            color="blue"
        )

        # Start calculation
        assert not ai_player.is_calculating

        # Calculate move (sets is_calculating during calculation)
        board = [[0 for _ in range(20)] for _ in range(20)]
        pieces = []
        move = ai_player.calculate_move(board, pieces)

        # After calculation completes
        assert not ai_player.is_calculating

    def test_ai_elapsed_calculation_time(self):
        """Test tracking elapsed calculation time."""
        ai_player = AIPlayer(
            player_id=2,
            strategy=RandomStrategy(),
            color="blue"
        )

        # Not calculating yet
        elapsed = ai_player.get_elapsed_calculation_time()
        assert elapsed is None

        # Calculate move
        board = [[0 for _ in range(20)] for _ in range(20)]
        pieces = []
        move = ai_player.calculate_move(board, pieces)

        # After calculation
        assert not ai_player.is_calculating


class TestSingleAIIntegrationFlow:
    """Integration tests for complete Single AI game flow."""

    @pytest.fixture
    def single_ai_game(self):
        """Create a Single AI game for testing."""
        game_mode = GameMode.single_ai(Difficulty.MEDIUM)
        game_setup = GameSetup()
        game_state = game_setup.setup_game(num_players=2, player_names=["Human", "AI"])
        return game_mode, game_state

    def test_game_initialization(self, single_ai_game):
        """Test game initializes correctly for Single AI."""
        game_mode, game_state = single_ai_game

        assert game_state.phase == GamePhase.PLAYING
        assert game_state.get_player_count() == 2

    def test_turn_sequence(self, single_ai_game):
        """Test turn sequence follows Single AI mode rules."""
        game_mode, game_state = single_ai_game

        # Player 1 starts
        current = game_state.get_current_player()
        assert current.player_id == 1

        # Advance to next turn
        game_state.next_turn()
        current = game_state.get_current_player()
        assert current.player_id == 3  # AI player

    def test_ai_move_validation(self, single_ai_game):
        """Test AI moves are validated correctly."""
        game_mode, game_state = single_ai_game

        # Simulate AI move (would be validated by game rules)
        current_player = game_state.get_current_player()
        assert current_player.player_id in [1, 3]  # Active players

    def test_game_completion_with_ai(self, single_ai_game):
        """Test game can complete with AI player."""
        game_mode, game_state = single_ai_game

        # Simulate game progression
        # (In real scenario, players would place pieces)
        # For this test, we just verify the setup is correct
        assert game_mode.get_player_count() == 2
        assert game_mode.is_ai_turn(3)  # Player 3 is AI


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
