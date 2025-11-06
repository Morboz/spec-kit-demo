"""
Integration test for Easy AI behavior.
Verifies that Easy AI uses RandomStrategy and makes random moves.
"""

import pytest
from src.models.ai_player import AIPlayer
from src.services.ai_strategy import RandomStrategy


def test_easy_ai_has_random_strategy():
    """Test that Easy AI uses RandomStrategy."""
    ai_player = AIPlayer(
        player_id=1,
        strategy=RandomStrategy(),
        color="blue",
        name="Easy AI"
    )
    
    assert isinstance(ai_player.strategy, RandomStrategy), "Easy AI should use RandomStrategy"
    assert ai_player.strategy.difficulty_name == "Easy"


def test_easy_ai_calculates_moves():
    """Test that Easy AI can calculate moves."""
    ai_player = AIPlayer(
        player_id=1,
        strategy=RandomStrategy(),
        color="blue",
        name="Easy AI"
    )
    
    # Create a simple board state
    board = [[0] * 20 for _ in range(20)]
    
    # Create a simple piece
    class MockPiece:
        name = "I1"
        positions = [(0, 0), (0, 1), (0, 2)]
        is_placed = False
    
    piece = MockPiece()
    
    # Calculate move
    move = ai_player.calculate_move(board, [piece])
    
    # Should return a valid move or None (if no valid placements)
    if move is not None:
        assert move.player_id == 1
        assert hasattr(move, 'flip')
        assert move.flip in [True, False]


def test_easy_ai_generates_different_moves():
    """Test that Easy AI can generate different moves (randomness)."""
    ai_player = AIPlayer(
        player_id=1,
        strategy=RandomStrategy(),
        color="blue",
        name="Easy AI"
    )
    
    board = [[0] * 20 for _ in range(20)]
    
    class MockPiece:
        name = "L1"
        positions = [(0, 0), (1, 0), (1, 1)]
        is_placed = False
    
    piece = MockPiece()
    
    # Generate multiple moves - should be able to generate different ones
    moves = ai_player.strategy.get_available_moves(board, [piece], player_id=1)
    
    assert len(moves) > 0, "Should generate some moves"
    assert any(not m.flip for m in moves), "Should generate non-flipped moves"
    assert any(m.flip for m in moves), "Should generate flipped moves"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
