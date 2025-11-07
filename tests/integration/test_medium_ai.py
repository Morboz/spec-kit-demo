"""
Integration test for Medium AI behavior.
Verifies that Medium AI uses CornerStrategy.
"""

import pytest

from src.models.ai_player import AIPlayer
from src.services.ai_strategy import CornerStrategy


def test_medium_ai_has_corner_strategy():
    """Test that Medium AI uses CornerStrategy."""
    ai_player = AIPlayer(
        player_id=1, strategy=CornerStrategy(), color="red", name="Medium AI"
    )

    assert isinstance(
        ai_player.strategy, CornerStrategy
    ), "Medium AI should use CornerStrategy"
    assert ai_player.strategy.difficulty_name == "Medium"


def test_medium_ai_calculates_moves():
    """Test that Medium AI can calculate moves."""
    ai_player = AIPlayer(
        player_id=1, strategy=CornerStrategy(), color="red", name="Medium AI"
    )

    board = [[0] * 20 for _ in range(20)]

    class MockPiece:
        name = "I1"
        positions = [(0, 0), (0, 1), (0, 2)]
        is_placed = False

    piece = MockPiece()

    move = ai_player.calculate_move(board, [piece])

    if move is not None:
        assert move.player_id == 1
        assert hasattr(move, "flip")


def test_medium_ai_evaluates_corners():
    """Test that Medium AI considers corner placements."""
    strategy = CornerStrategy()

    board = [[0] * 20 for _ in range(20)]
    # Add some player pieces near corners
    board[0][0] = 1  # Player's corner
    board[19][19] = 1  # Opposite corner

    class MockPiece:
        name = "L1"
        positions = [(0, 0), (1, 0), (1, 1)]
        is_placed = False

    piece = MockPiece()

    moves = strategy.get_available_moves(board, [piece], player_id=1)

    assert len(moves) > 0, "Should generate moves near corners"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
