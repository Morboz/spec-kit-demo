"""Unit tests for Piece model."""

import pytest
from src.config.pieces import PIECE_DEFINITIONS
from src.models.piece import Piece


class TestPiece:
    """Test suite for Piece model."""

    def test_create_piece_with_valid_name(self):
        """Test creating a piece with a valid piece name."""
        piece = Piece("I5")
        assert piece.name == "I5"
        assert piece.size == 5
        assert not piece.is_placed
        assert piece.placed_position is None

    def test_create_piece_with_coordinates(self):
        """Test creating a piece with explicit coordinates."""
        coordinates = [(0, 0), (1, 0), (2, 0)]
        piece = Piece.from_coordinates("I3", coordinates)
        assert piece.name == "I3"
        assert piece.size == 3
        assert piece.coordinates == coordinates

    def test_piece_rotation_90_degrees(self):
        """Test rotating a piece 90 degrees clockwise."""
        piece = Piece("I3")
        rotated = piece.rotate(90)
        # I3 rotated 90° becomes vertical: [(0,0), (0,1), (0,2)]
        assert rotated.coordinates == [(0, 0), (0, 1), (0, 2)]
        assert not rotated.is_placed

    def test_piece_rotation_180_degrees(self):
        """Test rotating a piece 180 degrees."""
        piece = Piece("L4")
        rotated = piece.rotate(180)
        # L4 rotated 180°: [(0,0), (0,1), (0,2), (1,2)]
        # becomes: [(0,0), (0,-1), (0,-2), (-1,-2)]
        assert rotated.coordinates == [(0, 0), (0, -1), (0, -2), (-1, -2)]
        assert not rotated.is_placed

    def test_piece_rotation_270_degrees(self):
        """Test rotating a piece 270 degrees clockwise."""
        piece = Piece("T4")
        rotated = piece.rotate(270)
        # T4 rotated 270°: [(0,0), (1,0), (2,0), (1,-1)]
        assert rotated.coordinates == [(0, 0), (1, 0), (2, 0), (1, -1)]
        assert not rotated.is_placed

    def test_piece_flip_horizontal(self):
        """Test flipping a piece horizontally."""
        piece = Piece("L4")
        flipped = piece.flip()
        # L4 flipped: [(0,0), (0,1), (0,2), (1,2)]
        # becomes: [(0,0), (0,1), (0,2), (-1,2)]
        assert flipped.coordinates == [(0, 0), (0, 1), (0, 2), (-1, 2)]
        assert not flipped.is_placed

    def test_piece_get_absolute_positions(self):
        """Test calculating absolute positions on the board."""
        piece = Piece("I2")
        absolute = piece.get_absolute_positions(5, 5)
        # I2 at (5,5): [(5,5), (6,5)]
        assert absolute == [(5, 5), (6, 5)]

    def test_piece_place(self):
        """Test placing a piece on the board."""
        piece = Piece("I1")
        piece.place_at(5, 5)
        assert piece.is_placed
        assert piece.placed_position == (5, 5)

    def test_cannot_place_already_placed_piece(self):
        """Test that placing an already placed piece raises an error."""
        piece = Piece("I1")
        piece.place_at(5, 5)
        with pytest.raises(ValueError, match="Piece is already placed"):
            piece.place_at(6, 6)

    def test_all_21_pieces_available(self):
        """Test that all 21 standard Blokus pieces can be created."""
        for piece_name in PIECE_DEFINITIONS.keys():
            piece = Piece(piece_name)
            assert piece.name == piece_name
            assert piece.size == len(PIECE_DEFINITIONS[piece_name])
            assert not piece.is_placed

    def test_piece_size_matches_coordinate_count(self):
        """Test that piece size matches the number of coordinates."""
        for piece_name, coords in PIECE_DEFINITIONS.items():
            piece = Piece(piece_name)
            assert piece.size == len(coords)
            assert len(piece.coordinates) == len(coords)

    def test_original_piece_unchanged_after_rotation(self):
        """Test that rotation creates a new instance without modifying original."""
        original = Piece("Z4")
        original_coords = original.coordinates.copy()
        original.rotate(90)
        assert original.coordinates == original_coords
        assert not original.is_placed

    def test_original_piece_unchanged_after_flip(self):
        """Test that flip creates a new instance without modifying original."""
        original = Piece("W5")
        original_coords = original.coordinates.copy()
        original.flip()
        assert original.coordinates == original_coords

    def test_rotate_invalid_angle_raises_error(self):
        """Test that rotating by invalid angle raises ValueError."""
        piece = Piece("I2")
        with pytest.raises(ValueError, match="Rotation angle must be 90, 180, or 270"):
            piece.rotate(45)
