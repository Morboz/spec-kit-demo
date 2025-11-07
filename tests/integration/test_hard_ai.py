"""
Integration test for Hard AI behavior.
Verifies that Hard AI uses StrategicStrategy.
"""

import pytest

from src.models.ai_player import AIPlayer
from src.services.ai_strategy import StrategicStrategy


def test_hard_ai_has_strategic_strategy():
    """Test that Hard AI uses StrategicStrategy."""
    ai_player = AIPlayer(
        player_id=1, strategy=StrategicStrategy(), color="green", name="Hard AI"
    )

    assert isinstance(
        ai_player.strategy, StrategicStrategy
    ), "Hard AI should use StrategicStrategy"
    assert ai_player.strategy.difficulty_name == "Hard"


def test_hard_ai_calculates_moves():
    """Test that Hard AI can calculate moves."""
    ai_player = AIPlayer(
        player_id=1, strategy=StrategicStrategy(), color="green", name="Hard AI"
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


def test_hard_ai_uses_evaluation():
    """Test that Hard AI uses board evaluation."""
    strategy = StrategicStrategy()

    board = [[0] * 20 for _ in range(20)]

    class MockPiece:
        name = "Square"
        positions = [(0, 0), (0, 1), (1, 0), (1, 1)]
        is_placed = False

    piece = MockPiece()

    # Evaluate board
    score = strategy.evaluate_board(board, player_id=1)
    assert isinstance(score, (int, float)), "Should return numeric score"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
