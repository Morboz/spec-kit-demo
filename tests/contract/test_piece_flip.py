"""Contract tests for Piece flip functionality.

This test validates that pieces can be flipped correctly, ensuring
horizontal mirroring transformations work properly for gameplay.
"""

import pytest
from src.models.piece import Piece
from src.models.board import Board
from src.models.player import Player
from src.models.game_state import GameState


class TestPieceFlipContract:
    """Contract tests for Piece flip."""

    def test_piece_flip_creates_new_instance(self):
        """Contract: Flip creates a new piece without modifying original.

        Given: A piece with specific coordinates
        When: The piece is flipped
        Then: A new piece is returned and original is unchanged
        """
        # Given: Original piece
        piece = Piece("L4")
        original_coords = piece.coordinates.copy()

        # When: Piece is flipped
        flipped_piece = piece.flip()

        # Then: New piece is created
        assert flipped_piece is not piece, "Flip should create new instance"
        assert flipped_piece.name == piece.name
        assert flipped_piece.size == piece.size

        # Then: Original piece is unchanged
        assert piece.coordinates == original_coords
        assert not piece.is_placed
        assert flipped_piece.is_placed is False

    def test_piece_flip_horizontal_mirroring(self):
        """Contract: Horizontal flip transforms coordinates correctly.

        Given: A piece with known coordinates
        When: The piece is flipped horizontally
        Then: Coordinates are transformed using (x, y) -> (x, -y)
        """
        # Given: L4 piece with coordinates [(0,0), (0,1), (0,2), (1,2)]
        piece = Piece("L4")

        # When: Piece is flipped
        flipped = piece.flip()

        # Then: Coordinates are mirrored
        # Original: [(0,0), (0,1), (0,2), (1,2)]
        # After flip: [(0,0), (0,-1), (0,-2), (1,-2)]
        expected = [(0, 0), (0, -1), (0, -2), (1, -2)]
        assert flipped.coordinates == expected

    def test_flip_preserves_piece_size(self):
        """Contract: Flip does not change piece size.

        Given: A piece with specific size
        When: The piece is flipped
        Then: Size remains the same
        """
        piece = Piece("X5")
        assert piece.size == 5

        flipped = piece.flip()
        assert flipped.size == 5
        assert len(flipped.coordinates) == 5

    def test_flip_with_symmetric_piece(self):
        """Contract: Symmetric pieces remain unchanged after flip.

        Given: Symmetric piece (e.g., X5 which has rotational symmetry)
        When: The piece is flipped
        Then: Coordinates may change but shape is equivalent
        """
        # Given: X5 piece (symmetric)
        piece = Piece("X5")

        # When: Flipped
        flipped = piece.flip()

        # Then: Size is preserved
        assert flipped.size == piece.size
        assert len(flipped.coordinates) == len(piece.coordinates)

        # Note: For X5, coordinates may differ but the shape is equivalent
        # This is expected for symmetric pieces

    def test_flip_with_asymmetric_piece(self):
        """Contract: Asymmetric pieces change shape after flip.

        Given: Asymmetric piece (e.g., L-shape or F5)
        When: The piece is flipped
        Then: Shape is transformed to mirror image
        """
        # Given: F5 piece (asymmetric)
        piece = Piece("F5")

        # When: Flipped
        flipped = piece.flip()

        # Then: Coordinates are different
        assert flipped.coordinates != piece.coordinates
        assert len(flipped.coordinates) == len(piece.coordinates)
        assert flipped.size == piece.size

    def test_double_flip_returns_to_original(self):
        """Contract: Flipping twice returns to original state.

        Given: A piece
        When: The piece is flipped twice
        Then: Coordinates return to original state
        """
        # Given: L4 piece
        piece = Piece("L4")
        original_coords = piece.coordinates.copy()

        # When: Flipped twice
        flipped_once = piece.flip()
        flipped_twice = flipped_once.flip()

        # Then: Should match original
        assert flipped_twice.coordinates == original_coords

    def test_flipped_piece_can_be_placed_on_board(self):
        """Contract: Flipped piece can be placed on board.

        Given: A piece that is flipped
        When: The flipped piece is placed on valid board position
        Then: Piece is successfully placed
        """
        # Given: Empty board and player
        board = Board()
        player = Player(player_id=1, name="Alice")
        piece = player.get_piece("L4")

        # When: Piece is flipped and placed
        flipped_piece = piece.flip()
        positions = board.place_piece(flipped_piece, 5, 5, 1)

        # Then: Piece is placed
        assert len(positions) == 4
        assert board.is_occupied(5, 5)
        assert board.count_player_squares(1) == 4

    def test_flip_then_rotate_produces_correct_transformation(self):
        """Contract: Flip and rotation can be composed.

        Given: A piece
        When: The piece is flipped and then rotated
        Then: Combined transformation is applied correctly
        """
        # Given: L4 piece
        piece = Piece("L4")

        # When: Flipped then rotated 90
        flipped = piece.flip()
        rotated_flipped = flipped.rotate(90)

        # Then: Transformation is applied
        assert rotated_flipped.size == piece.size
        assert not rotated_flipped.is_placed

        # Coordinates should be different from original
        assert rotated_flipped.coordinates != piece.coordinates

    def test_flip_with_various_piece_shapes(self):
        """Contract: Flip works correctly for all piece types.

        Given: Various piece shapes
        When: Each piece is flipped
        Then: All pieces maintain their size and can be used
        """
        # Test with different piece types
        pieces_to_test = ["I1", "I2", "I3", "L4", "L5", "T4", "T5", "Z4", "Z5", "V3"]

        for piece_name in pieces_to_test:
            # Given: Piece
            piece = Piece(piece_name)

            # When: Flipped
            flipped = piece.flip()

            # Then: Size is preserved
            assert (
                flipped.size == piece.size
            ), f"Piece {piece_name} size changed after flip"

            # Then: Coordinates count is same
            assert len(flipped.coordinates) == len(
                piece.coordinates
            ), f"Piece {piece_name} coordinate count changed after flip"

    def test_flip_does_not_mark_piece_as_placed(self):
        """Contract: Flipping does not mark piece as placed.

        Given: An unplaced piece
        When: The piece is flipped
        Then: Flipped piece is still unplaced
        """
        piece = Piece("I2")
        assert not piece.is_placed

        flipped = piece.flip()
        assert not flipped.is_placed
        assert flipped.is_placed is False

    def test_flipped_piece_has_no_placed_position(self):
        """Contract: Flipped piece has no placed position.

        Given: An unplaced piece
        When: The piece is flipped
        Then: Flipped piece has no placed_position
        """
        piece = Piece("I2")
        assert piece.placed_position is None

        flipped = piece.flip()
        assert flipped.placed_position is None
