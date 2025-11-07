"""
Unit tests for Move class flip field functionality.
"""

from src.services.ai_strategy import Move


def test_move_has_flip_field():
    """Test that Move class has flip field."""

    # Create a mock piece object
    class MockPiece:
        name = "I1"
        positions = [(0, 0), (0, 1), (1, 1)]

    piece = MockPiece()

    # Test Move without flip (default)
    move_no_flip = Move(
        piece=piece, position=(10, 10), rotation=0, player_id=1, flip=False
    )

    assert hasattr(move_no_flip, "flip"), "Move should have flip attribute"
    assert move_no_flip.flip == False, "Default flip should be False"

    # Test Move with flip=True
    move_with_flip = Move(
        piece=piece, position=(10, 10), rotation=0, player_id=1, flip=True
    )

    assert move_with_flip.flip == True, "Flip should be True when specified"


def test_move_flip_default():
    """Test that flip defaults to False if not specified."""

    class MockPiece:
        name = "I1"
        positions = [(0, 0), (0, 1), (1, 1)]

    piece = MockPiece()

    # Create move without specifying flip
    move = Move(piece=piece, position=(10, 10), rotation=0, player_id=1)

    assert move.flip == False, "Flip should default to False"


def test_move_repr_includes_flip():
    """Test that __repr__ includes flip state."""

    class MockPiece:
        name = "I1"
        positions = [(0, 0), (0, 1), (1, 1)]

    piece = MockPiece()

    # Test without flip
    move_no_flip = Move(
        piece=piece, position=(10, 10), rotation=0, player_id=1, flip=False
    )

    repr_str = repr(move_no_flip)
    assert (
        "flipped" not in repr_str
    ), "Repr should not include 'flipped' when flip=False"
    assert "rotation=0°" in repr_str, "Repr should include rotation"

    # Test with flip
    move_with_flip = Move(
        piece=piece, position=(10, 10), rotation=90, player_id=1, flip=True
    )

    repr_str = repr(move_with_flip)
    assert "flipped" in repr_str, "Repr should include 'flipped' when flip=True"
    assert "rotation=90°" in repr_str, "Repr should include rotation"


def test_move_pass_with_flip():
    """Test that pass moves don't need flip specified."""
    # Pass move should work with any flip value
    pass_move_no_flip = Move(
        piece=None, position=None, rotation=0, player_id=1, is_pass=True, flip=False
    )

    assert pass_move_no_flip.is_pass == True
    assert pass_move_no_flip.flip == False

    pass_move_with_flip = Move(
        piece=None, position=None, rotation=0, player_id=1, is_pass=True, flip=True
    )

    assert pass_move_with_flip.is_pass == True
    assert pass_move_with_flip.flip == True


def test_move_flip_with_rotation():
    """Test that flip and rotation work together."""

    class MockPiece:
        name = "I1"
        # L-shaped piece
        positions = [(0, 0), (1, 0), (1, 1)]

    piece = MockPiece()

    # Create moves with different flip/rotation combinations
    move_cases = [
        {"flip": False, "rotation": 0},
        {"flip": False, "rotation": 90},
        {"flip": True, "rotation": 0},
        {"flip": True, "rotation": 90},
        {"flip": True, "rotation": 180},
        {"flip": True, "rotation": 270},
    ]

    for case in move_cases:
        move = Move(
            piece=piece,
            position=(10, 10),
            player_id=1,
            flip=case["flip"],
            rotation=case["rotation"],
        )

        assert move.flip == case["flip"], f"Flip should be {case['flip']}"
        assert (
            move.rotation == case["rotation"]
        ), f"Rotation should be {case['rotation']}"


if __name__ == "__main__":
    # Run tests
    test_move_has_flip_field()
    test_move_flip_default()
    test_move_repr_includes_flip()
    test_move_pass_with_flip()
    test_move_flip_with_rotation()
    print("All Move flip tests passed!")
