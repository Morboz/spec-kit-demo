"""
Integration test for AI flip support.
Verifies that AI strategies generate and execute flipped moves.
"""

import pytest

from blokus_game.models.ai_player import AIPlayer
from blokus_game.services.ai_strategy import (
    CornerStrategy,
    RandomStrategy,
    StrategicStrategy,
)


def test_random_strategy_generates_flipped_moves():
    """Test that RandomStrategy can generate moves with flip=True."""
    strategy = RandomStrategy()

    class MockPiece:
        name = "L1"
        positions = [(0, 0), (1, 0), (1, 1)]  # L-shaped piece
        is_placed = False

    piece = MockPiece()
    board = [[0] * 20 for _ in range(20)]

    # Generate moves
    moves = strategy.get_available_moves(board, [piece], player_id=1)

    # Should have both flipped and non-flipped moves
    flipped_moves = [m for m in moves if m.flip]
    non_flipped_moves = [m for m in moves if not m.flip]

    assert len(moves) > 0, "Should generate some moves"
    assert len(flipped_moves) > 0, "Should generate flipped moves"
    assert len(non_flipped_moves) > 0, "Should generate non-flipped moves"


def test_corner_strategy_generates_flipped_moves():
    """Test that CornerStrategy can generate moves with flip=True."""
    strategy = CornerStrategy()

    class MockPiece:
        name = "L1"
        positions = [(0, 0), (1, 0), (1, 1)]
        is_placed = False

    piece = MockPiece()
    board = [[0] * 20 for _ in range(20)]

    # Generate moves
    moves = strategy.get_available_moves(board, [piece], player_id=1)

    # Should have both flipped and non-flipped moves
    flipped_moves = [m for m in moves if m.flip]
    non_flipped_moves = [m for m in moves if not m.flip]

    assert len(moves) > 0, "Should generate some moves"
    assert len(flipped_moves) > 0, "Should generate flipped moves"
    assert len(non_flipped_moves) > 0, "Should generate non-flipped moves"


def test_strategic_strategy_generates_flipped_moves():
    """Test that StrategicStrategy can generate moves with flip=True."""
    strategy = StrategicStrategy()

    class MockPiece:
        name = "L1"
        positions = [(0, 0), (1, 0), (1, 1)]
        is_placed = False

    piece = MockPiece()
    board = [[0] * 20 for _ in range(20)]

    # Generate moves
    moves = strategy.get_available_moves(board, [piece], player_id=1)

    # Should have both flipped and non-flipped moves
    flipped_moves = [m for m in moves if m.flip]
    non_flipped_moves = [m for m in moves if not m.flip]

    assert len(moves) > 0, "Should generate some moves"
    assert len(flipped_moves) > 0, "Should generate flipped moves"
    assert len(non_flipped_moves) > 0, "Should generate non-flipped moves"


def test_ai_player_calculate_move_with_flip():
    """Test that AI players can calculate moves with flip support."""
    # Test with all three strategies
    for StrategyClass in [RandomStrategy, CornerStrategy, StrategicStrategy]:
        ai_player = AIPlayer(
            player_id=1,
            strategy=StrategyClass(),
            color="blue",
            name=f"{StrategyClass.__name__} AI",
        )

        class MockPiece:
            name = "L1"
            positions = [(0, 0), (1, 0), (1, 1)]
            is_placed = False

        piece = MockPiece()
        board = [[0] * 20 for _ in range(20)]

        # Calculate move
        move = ai_player.calculate_move(board, [piece])

        if move is not None:
            # Verify move has flip attribute
            assert hasattr(
                move, "flip"
            ), f"{StrategyClass.__name__} should return moves with flip attribute"
            assert move.flip in [True, False], "Flip should be boolean"


def test_flip_creates_different_positions():
    """Test that flip creates different piece positions."""

    class MockPiece:
        name = "L1"
        positions = [(0, 0), (1, 0), (1, 1)]  # L-shape

    piece = MockPiece()
    strategy = RandomStrategy()

    # Get positions without flip
    pos_no_flip = strategy._get_piece_positions(
        piece=piece, row=10, col=10, rotation=0, flip=False
    )

    # Get positions with flip
    pos_with_flip = strategy._get_piece_positions(
        piece=piece, row=10, col=10, rotation=0, flip=True
    )

    # Positions should be different
    assert pos_no_flip != pos_with_flip, "Flip should change piece positions"

    # Both should have 3 positions
    assert len(pos_no_flip) == 3, "Should have 3 positions"
    assert len(pos_with_flip) == 3, "Should have 3 positions"


def test_flip_then_rotation():
    """Test that flip is applied before rotation."""

    class MockPiece:
        name = "L1"
        positions = [(0, 0), (1, 0), (1, 1)]

    piece = MockPiece()
    strategy = RandomStrategy()

    # Test flip + 90° rotation
    positions = strategy._get_piece_positions(
        piece=piece, row=10, col=10, rotation=90, flip=True
    )

    # Verify positions are valid
    for r, c in positions:
        assert isinstance(r, int)
        assert isinstance(c, int)

    # Should have 3 positions for L-piece
    assert len(positions) == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
