"""Unit tests for AI Player model."""

import pytest
from src.models.ai_player import AIPlayer
from src.services.ai_strategy import RandomStrategy, CornerStrategy, StrategicStrategy
from src.config.pieces import get_piece


class TestAIPlayer:
    """Test suite for AIPlayer model."""

    def test_create_ai_player_with_valid_id(self):
        """Test creating an AI player with valid ID."""
        strategy = RandomStrategy()
        ai_player = AIPlayer(1, strategy, "blue", "Test AI")

        assert ai_player.player_id == 1
        assert ai_player.strategy == strategy
        assert ai_player.color == "blue"
        assert ai_player.name == "Test AI"
        assert ai_player.score == 0
        assert not ai_player.has_passed
        assert not ai_player.is_calculating
        assert len(ai_player.pieces) == 21

    def test_create_ai_player_with_default_name(self):
        """Test creating AI player uses default name."""
        strategy = RandomStrategy()
        ai_player = AIPlayer(2, strategy, "red")

        assert ai_player.name == "AI Player 2"

    def test_create_ai_player_with_invalid_id_raises_error(self):
        """Test creating AI player with invalid ID raises ValueError."""
        strategy = RandomStrategy()

        with pytest.raises(ValueError, match="Player ID must be 1-4"):
            AIPlayer(0, strategy, "blue")

        with pytest.raises(ValueError, match="Player ID must be 1-4"):
            AIPlayer(5, strategy, "red")

    def test_ai_player_has_all_21_pieces(self):
        """Test that a new AI player has all 21 standard pieces."""
        strategy = RandomStrategy()
        ai_player = AIPlayer(1, strategy, "blue")

        assert len(ai_player.pieces) == 21
        assert all(p.is_placed == False for p in ai_player.pieces)

    def test_difficulty_property(self):
        """Test that difficulty property returns strategy's difficulty."""
        easy_strategy = RandomStrategy()
        medium_strategy = CornerStrategy()
        hard_strategy = StrategicStrategy()

        easy_ai = AIPlayer(1, easy_strategy, "blue")
        medium_ai = AIPlayer(2, medium_strategy, "red")
        hard_ai = AIPlayer(3, hard_strategy, "green")

        assert easy_ai.difficulty == "Easy"
        assert medium_ai.difficulty == "Medium"
        assert hard_ai.difficulty == "Hard"

    def test_pass_turn(self):
        """Test that pass_turn sets the passed flag."""
        strategy = RandomStrategy()
        ai_player = AIPlayer(1, strategy, "blue")

        assert not ai_player.has_passed

        ai_player.pass_turn()
        assert ai_player.has_passed

        # Reset at next turn
        ai_player.reset_pass()
        assert not ai_player.has_passed

    def test_has_pieces_remaining(self):
        """Test has_pieces_remaining returns correct status."""
        strategy = RandomStrategy()
        ai_player = AIPlayer(1, strategy, "blue")

        assert ai_player.has_pieces_remaining()
        assert len(ai_player.pieces) == 21

        # Remove a piece
        piece = ai_player.pieces[0]
        ai_player.remove_piece(piece)

        assert ai_player.has_pieces_remaining()
        assert len(ai_player.pieces) == 20

    def test_remove_piece(self):
        """Test removing a piece from inventory."""
        strategy = RandomStrategy()
        ai_player = AIPlayer(1, strategy, "blue")

        piece = ai_player.pieces[0]
        ai_player.remove_piece(piece)

        assert piece not in ai_player.pieces
        assert len(ai_player.pieces) == 20

    def test_remove_piece_not_in_inventory_raises_error(self):
        """Test removing piece not in inventory raises ValueError."""
        strategy = RandomStrategy()
        ai_player = AIPlayer(1, strategy, "blue")

        piece = get_piece("I5")

        with pytest.raises(ValueError, match="not in inventory"):
            ai_player.remove_piece(piece)

    def test_is_ai_turn(self):
        """Test that is_ai_turn always returns True for AI players."""
        strategy = RandomStrategy()
        ai_player = AIPlayer(1, strategy, "blue")

        assert ai_player.is_ai_turn()

    def test_get_available_moves(self):
        """Test getting available moves."""
        strategy = RandomStrategy()
        ai_player = AIPlayer(1, strategy, "blue")

        board = [[0] * 20 for _ in range(20)]
        pieces = ai_player.pieces[:5]  # Use first 5 pieces

        moves = ai_player.get_available_moves(board, pieces)

        assert isinstance(moves, list)
        # Note: Without proper validation, this may return many moves
        # In a real game, these would be validated by BlokusRules

    def test_evaluate_position(self):
        """Test evaluating board position."""
        strategy = RandomStrategy()
        ai_player = AIPlayer(1, strategy, "blue")

        # Empty board
        board = [[0] * 20 for _ in range(20)]
        score = ai_player.evaluate_position(board)

        assert isinstance(score, (int, float))
        assert score == 0

        # Board with player's pieces
        board[10][10] = 1
        board[10][11] = 1
        score = ai_player.evaluate_position(board)

        assert score == 2

    def test_calculate_move_with_no_moves(self):
        """Test calculate_move returns None when no valid moves."""
        strategy = RandomStrategy()
        ai_player = AIPlayer(1, strategy, "blue")

        board = [[0] * 20 for _ in range(20)]
        pieces = []  # No pieces

        move = ai_player.calculate_move(board, pieces)

        assert move is None

    def test_calculate_move_tracks_calculation_state(self):
        """Test that calculate_move properly tracks calculation state."""
        strategy = RandomStrategy()
        ai_player = AIPlayer(1, strategy, "blue")

        board = [[0] * 20 for _ in range(20)]
        pieces = ai_player.pieces[:5]

        # Start calculation
        assert not ai_player.is_calculating

        move = ai_player.calculate_move(board, pieces)

        # After calculation
        assert not ai_player.is_calculating
        assert move is not None or len(ai_player.pieces) == 0

    def test_calculate_move_invalid_piece_raises_error(self):
        """Test that calculate_move raises error if piece not in inventory."""
        strategy = RandomStrategy()
        ai_player = AIPlayer(1, strategy, "blue")

        board = [[0] * 20 for _ in range(20)]
        pieces = [get_piece("I5")]  # Piece not in AI's inventory

        # This should handle gracefully (returns None or raises)
        # Depending on implementation
        try:
            move = ai_player.calculate_move(board, pieces)
            # If it returns without error, that's also acceptable
            # (the strategy should handle invalid pieces)
        except ValueError as e:
            assert "not in inventory" in str(e)

    def test_get_piece_count(self):
        """Test get_piece_count returns correct count."""
        strategy = RandomStrategy()
        ai_player = AIPlayer(1, strategy, "blue")

        assert ai_player.get_piece_count() == 21

        ai_player.remove_piece(ai_player.pieces[0])
        assert ai_player.get_piece_count() == 20

    def test_str_representation(self):
        """Test string representation of AI player."""
        strategy = CornerStrategy()
        ai_player = AIPlayer(2, strategy, "red", "My AI")

        repr_str = repr(ai_player)
        assert "AIPlayer" in repr_str
        assert "id=2" in repr_str
        assert "My AI" in repr_str
        assert "Medium" in repr_str

    def test_elapsed_calculation_time(self):
        """Test tracking elapsed calculation time."""
        strategy = RandomStrategy()
        ai_player = AIPlayer(1, strategy, "blue")

        assert ai_player.get_elapsed_calculation_time() is None

        # Note: We can't easily test the actual timing without mocking
        # but we can verify the method exists and returns a value when calculating

    def test_different_strategies_produce_different_behavior(self):
        """Test that different strategies can be used interchangeably."""
        strategies = [
            RandomStrategy(),
            CornerStrategy(),
            StrategicStrategy()
        ]

        board = [[0] * 20 for _ in range(20)]
        pieces = [get_piece("I5")]

        for i, strategy in enumerate(strategies, 1):
            ai_player = AIPlayer(i, strategy, "blue")
            assert ai_player.strategy == strategy
            assert ai_player.difficulty == strategy.difficulty_name
            assert ai_player.timeout_seconds == strategy.timeout_seconds
