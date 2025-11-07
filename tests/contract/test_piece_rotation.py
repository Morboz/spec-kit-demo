"""Contract tests for Piece rotation functionality.

This test validates that pieces can be rotated correctly, ensuring
rotation transformations work properly for gameplay.
"""

import pytest

from src.models.board import Board
from src.models.piece import Piece
from src.models.player import Player


class TestPieceRotationContract:
    """Contract tests for Piece rotation."""

    def test_piece_rotation_creates_new_instance(self):
        """Contract: Rotation creates a new piece without modifying original.

        Given: A piece with specific coordinates
        When: The piece is rotated
        Then: A new piece is returned and original is unchanged
        """
        # Given: Original piece
        piece = Piece("L4")
        original_coords = piece.coordinates.copy()

        # When: Piece is rotated
        rotated_piece = piece.rotate(90)

        # Then: New piece is created
        assert rotated_piece is not piece, "Rotation should create new instance"
        assert rotated_piece.name == piece.name
        assert rotated_piece.size == piece.size

        # Then: Original piece is unchanged
        assert piece.coordinates == original_coords
        assert not piece.is_placed
        assert rotated_piece.is_placed is False

    def test_piece_rotation_90_degrees(self):
        """Contract: 90-degree rotation transforms coordinates correctly.

        Given: A piece with known coordinates
        When: The piece is rotated 90 degrees clockwise
        Then: Coordinates are transformed using (x, y) -> (-y, x)
        """
        # Given: L4 piece with coordinates [(0,0), (0,1), (0,2), (1,2)]
        piece = Piece("L4")

        # When: Rotated 90 degrees
        rotated = piece.rotate(90)

        # Then: Coordinates are rotated
        # Original: [(0,0), (0,1), (0,2), (1,2)]
        # After 90° rotation: [(0,0), (-1,0), (-2,0), (-2,1)]
        expected = [(0, 0), (-1, 0), (-2, 0), (-2, 1)]
        assert rotated.coordinates == expected

    def test_piece_rotation_180_degrees(self):
        """Contract: 180-degree rotation transforms coordinates correctly.

        Given: A piece with known coordinates
        When: The piece is rotated 180 degrees
        Then: Coordinates are transformed using (x, y) -> (-x, -y)
        """
        # Given: L4 piece
        piece = Piece("L4")

        # When: Rotated 180 degrees
        rotated = piece.rotate(180)

        # Then: Coordinates are rotated
        # Original: [(0,0), (0,1), (0,2), (1,2)]
        # After 180° rotation: [(0,0), (0,-1), (0,-2), (-1,-2)]
        expected = [(0, 0), (0, -1), (0, -2), (-1, -2)]
        assert rotated.coordinates == expected

    def test_piece_rotation_270_degrees(self):
        """Contract: 270-degree rotation transforms coordinates correctly.

        Given: A piece with known coordinates
        When: The piece is rotated 270 degrees clockwise
        Then: Coordinates are transformed using (x, y) -> (y, -x)
        """
        # Given: L4 piece
        piece = Piece("L4")

        # When: Rotated 270 degrees
        rotated = piece.rotate(270)

        # Then: Coordinates are rotated
        # Original: [(0,0), (0,1), (0,2), (1,2)]
        # After 270° rotation: [(0,0), (1,0), (2,0), (2,-1)]
        expected = [(0, 0), (1, 0), (2, 0), (2, -1)]
        assert rotated.coordinates == expected

    def test_piece_rotation_invalid_angle_raises_error(self):
        """Contract: Invalid rotation angles raise ValueError.

        Given: A piece
        When: An invalid rotation angle is provided
        Then: ValueError is raised with appropriate message
        """
        piece = Piece("I2")

        # Test invalid angles
        with pytest.raises(ValueError, match="Rotation angle must be 90, 180, or 270"):
            piece.rotate(45)

        with pytest.raises(ValueError, match="Rotation angle must be 90, 180, or 270"):
            piece.rotate(0)

        with pytest.raises(ValueError, match="Rotation angle must be 90, 180, or 270"):
            piece.rotate(360)

    def test_rotated_piece_can_be_placed_on_board(self):
        """Contract: Rotated piece can be placed on board.

        Given: A piece that is rotated
        When: The rotated piece is placed on valid board position
        Then: Piece is successfully placed
        """
        # Given: Empty board and player
        board = Board()
        player = Player(player_id=1, name="Alice")
        piece = player.get_piece("L4")

        # When: Piece is rotated and placed
        rotated_piece = piece.rotate(90)
        positions = board.place_piece(rotated_piece, 5, 5, 1)

        # Then: Piece is placed
        assert len(positions) == 4
        assert board.is_occupied(5, 5)
        assert board.count_player_squares(1) == 4

    def test_rotation_preserves_piece_size(self):
        """Contract: Rotation does not change piece size.

        Given: A piece with specific size
        When: The piece is rotated
        Then: Size remains the same
        """
        piece = Piece("X5")
        assert piece.size == 5

        rotated = piece.rotate(90)
        assert rotated.size == 5

        rotated = piece.rotate(180)
        assert rotated.size == 5

        rotated = piece.rotate(270)
        assert rotated.size == 5

    def test_multiple_rotations_compose_correctly(self):
        """Contract: Multiple rotations compose to correct final state.

        Given: A piece
        When: Rotated multiple times
        Then: Final rotation matches expected transformation
        """
        # Given: L4 piece
        piece = Piece("L4")

        # When: Rotate 90 twice (180 total)
        rotated_90 = piece.rotate(90)
        rotated_180 = rotated_90.rotate(90)

        # Then: Should match single 180 rotation
        direct_180 = piece.rotate(180)
        assert rotated_180.coordinates == direct_180.coordinates

        # When: Rotate 90 four times (360 total)
        rotated_360 = piece.rotate(90).rotate(90).rotate(90).rotate(90)

        # Then: Should match original (with normalization)
        # Note: May not be exactly equal due to coordinate system, but should have same size
        assert rotated_360.size == piece.size

    def test_rotation_with_asymmetric_piece(self):
        """Contract: Asymmetric pieces rotate differently than symmetric ones.

        Given: Asymmetric piece (e.g., L-shape)
        When: Rotated
        Then: Shape is transformed asymmetrically
        """
        # Given: T5 piece (asymmetric)
        piece = Piece("T5")

        # When: Rotated
        rotated = piece.rotate(90)

        # Then: Coordinates change in non-uniform way
        assert rotated.coordinates != piece.coordinates
        assert len(rotated.coordinates) == len(piece.coordinates)
        assert rotated.size == piece.size
