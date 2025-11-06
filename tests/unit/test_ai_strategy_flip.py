"""
Unit tests for AIStrategy _get_piece_positions with flip support.
"""

from src.services.ai_strategy import AIStrategy


def test_get_piece_positions_without_flip():
    """Test _get_piece_positions works without flip (backward compatibility)."""
    class MockStrategy(AIStrategy):
        @property
        def difficulty_name(self):
            return "Test"
        
        @property
        def timeout_seconds(self):
            return 3
        
        def calculate_move(self, board, pieces, player_id, time_limit=None):
            return None
    
    strategy = MockStrategy()
    
    class MockPiece:
        name = "I1"
        positions = [(0, 0), (0, 1), (0, 2)]  # I-piece shape
    
    piece = MockPiece()
    
    # Test without flip (backward compatibility)
    positions = strategy._get_piece_positions(
        piece=piece,
        row=10,
        col=10,
        rotation=0
    )
    
    # Expected positions with no flip, no rotation
    assert len(positions) == 3
    assert (10, 10) in positions
    assert (10, 11) in positions
    assert (10, 12) in positions


def test_get_piece_positions_with_flip_false():
    """Test _get_piece_positions with flip=False."""
    class MockStrategy(AIStrategy):
        @property
        def difficulty_name(self):
            return "Test"
        
        @property
        def timeout_seconds(self):
            return 3
        
        def calculate_move(self, board, pieces, player_id, time_limit=None):
            return None
    
    strategy = MockStrategy()
    
    class MockPiece:
        name = "L1"
        positions = [(0, 0), (1, 0), (1, 1)]  # L-shaped piece
    
    piece = MockPiece()
    
    # Test with flip=False explicitly
    positions = strategy._get_piece_positions(
        piece=piece,
        row=10,
        col=10,
        rotation=0,
        flip=False
    )
    
    # Should be same as no flip
    assert len(positions) == 3
    assert (10, 10) in positions  # (0, 0) -> (10, 10)
    assert (11, 10) in positions  # (1, 0) -> (11, 10)
    assert (11, 11) in positions  # (1, 1) -> (11, 11)


def test_get_piece_positions_with_flip_true():
    """Test _get_piece_positions with flip=True."""
    class MockStrategy(AIStrategy):
        @property
        def difficulty_name(self):
            return "Test"
        
        @property
        def timeout_seconds(self):
            return 3
        
        def calculate_move(self, board, pieces, player_id, time_limit=None):
            return None
    
    strategy = MockStrategy()
    
    class MockPiece:
        name = "L1"
        # Original L-shape: (0,0), (1,0), (1,1)
        # After flip: (0,0), (1,0), (1,-1)
        positions = [(0, 0), (1, 0), (1, 1)]
    
    piece = MockPiece()
    
    # Test with flip=True
    positions = strategy._get_piece_positions(
        piece=piece,
        row=10,
        col=10,
        rotation=0,
        flip=True
    )
    
    # After flip, positions should be:
    # (0,0) -> (10,10)
    # (1,0) -> (11,10)
    # (1,-1) -> (11,9)  <-- Note the column is negated
    assert len(positions) == 3
    assert (10, 10) in positions
    assert (11, 10) in positions
    assert (11, 9) in positions  # Flipped position


def test_get_piece_positions_flip_then_rotate():
    """Test that flip is applied before rotation."""
    class MockStrategy(AIStrategy):
        @property
        def difficulty_name(self):
            return "Test"
        
        @property
        def timeout_seconds(self):
            return 3
        
        def calculate_move(self, board, pieces, player_id, time_limit=None):
            return None
    
    strategy = MockStrategy()
    
    class MockPiece:
        name = "L1"
        positions = [(0, 0), (1, 0), (1, 1)]
    
    piece = MockPiece()
    
    # Test flip + 90 degree rotation
    positions = strategy._get_piece_positions(
        piece=piece,
        row=10,
        col=10,
        rotation=90,
        flip=True
    )

    # Calculation:
    # Original: (0,0), (1,0), (1,1)
    # After flip: (0,0), (1,0), (1,-1)
    # After 90° rotation:
    #   (0,0) -> (0,0) -> (10,10)
    #   (1,0) -> (0,1) -> (10,11)
    #   (1,-1) -> (1,1) -> (11,11)
    assert len(positions) == 3
    assert (10, 10) in positions  # (0,0) after flip+rot
    assert (10, 11) in positions  # (1,0) after flip+rot
    assert (11, 11) in positions   # (1,-1) after flip+rot


def test_get_piece_positions_flip_all_rotations():
    """Test flip with all rotation angles."""
    class MockStrategy(AIStrategy):
        @property
        def difficulty_name(self):
            return "Test"
        
        @property
        def timeout_seconds(self):
            return 3
        
        def calculate_move(self, board, pieces, player_id, time_limit=None):
            return None
    
    strategy = MockStrategy()
    
    class MockPiece:
        name = "Square"
        positions = [(0, 0), (0, 1), (1, 0), (1, 1)]
    
    piece = MockPiece()
    
    # Test with flip and all rotations
    for rotation in [0, 90, 180, 270]:
        positions = strategy._get_piece_positions(
            piece=piece,
            row=10,
            col=10,
            rotation=rotation,
            flip=True
        )
        
        # Should always return 4 positions for square piece
        assert len(positions) == 4, f"Should have 4 positions for rotation {rotation}"
        
        # All positions should be valid (within reasonable bounds)
        for r, c in positions:
            assert isinstance(r, int)
            assert isinstance(c, int)


def test_get_piece_positions_flip_with_simple_piece():
    """Test flip with a simple 2-square piece."""
    class MockStrategy(AIStrategy):
        @property
        def difficulty_name(self):
            return "Test"
        
        @property
        def timeout_seconds(self):
            return 3
        
        def calculate_move(self, board, pieces, player_id, time_limit=None):
            return None
    
    strategy = MockStrategy()
    
    class MockPiece:
        name = "I2"
        positions = [(0, 0), (0, 1)]
    
    piece = MockPiece()
    
    # Without flip
    positions_no_flip = strategy._get_piece_positions(
        piece=piece,
        row=5,
        col=5,
        rotation=0,
        flip=False
    )
    
    # With flip
    positions_with_flip = strategy._get_piece_positions(
        piece=piece,
        row=5,
        col=5,
        rotation=0,
        flip=True
    )
    
    # Both should have 2 positions
    assert len(positions_no_flip) == 2
    assert len(positions_with_flip) == 2
    
    # With flip, the second position should be different
    # No flip: (0,0), (0,1) -> (5,5), (5,6)
    # With flip: (0,0), (0,-1) -> (5,5), (5,4)
    assert positions_no_flip[1] == (5, 6)
    assert positions_with_flip[1] == (5, 4)


if __name__ == "__main__":
    # Run tests
    test_get_piece_positions_without_flip()
    test_get_piece_positions_with_flip_false()
    test_get_piece_positions_with_flip_true()
    test_get_piece_positions_flip_then_rotate()
    test_get_piece_positions_flip_all_rotations()
    test_get_piece_positions_flip_with_simple_piece()
    print("All AI strategy flip tests passed!")
