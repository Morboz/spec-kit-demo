"""Unit tests for Player model."""

import pytest

from blokus_game.config.pieces import get_all_piece_names
from blokus_game.models.piece import Piece
from blokus_game.models.player import Player


class TestPlayer:
    """Test suite for Player model."""

    def test_create_player_with_valid_id(self):
        """Test creating a player with valid ID."""
        player = Player(1, "Alice")
        assert player.player_id == 1
        assert player.name == "Alice"
        assert player.score == 0
        assert player.is_active
        assert not player.has_passed
        assert len(player.pieces) == 21

    def test_create_player_with_invalid_id_raises_error(self):
        """Test creating player with invalid ID raises ValueError."""
        with pytest.raises(ValueError, match="Player ID must be 1-4"):
            Player(0, "Invalid")

        with pytest.raises(ValueError, match="Player ID must be 1-4"):
            Player(5, "Invalid")

    def test_player_has_all_21_pieces(self):
        """Test that a new player has all 21 standard pieces."""
        player = Player(1, "Alice")
        all_piece_names = set(get_all_piece_names())
        player_piece_names = set(player.get_piece_names())

        assert player_piece_names == all_piece_names
        assert len(player.pieces) == 21

    def test_get_piece(self):
        """Test retrieving a specific piece."""
        player = Player(1, "Alice")
        piece = player.get_piece("I5")
        assert piece is not None
        assert piece.name == "I5"
        assert piece.size == 5

        # Non-existent piece
        piece = player.get_piece("X99")
        assert piece is None

    def test_get_all_pieces(self):
        """Test retrieving all pieces."""
        player = Player(1, "Alice")
        pieces = player.get_all_pieces()
        assert len(pieces) == 21
        assert all(isinstance(p, Piece) for p in pieces)

    def test_get_unplaced_pieces(self):
        """Test retrieving unplaced pieces."""
        player = Player(1, "Alice")
        unplaced = player.get_unplaced_pieces()
        assert len(unplaced) == 21  # All pieces are unplaced initially

        # Place a piece
        player.place_piece("I1", 0, 0)
        unplaced = player.get_unplaced_pieces()
        assert len(unplaced) == 20

    def test_get_placed_pieces(self):
        """Test retrieving placed pieces."""
        player = Player(1, "Alice")
        placed = player.get_placed_pieces()
        assert len(placed) == 0

        # Place some pieces
        player.place_piece("I1", 0, 0)
        player.place_piece("I2", 5, 5)

        placed = player.get_placed_pieces()
        assert len(placed) == 2
        assert all(p.is_placed for p in placed)

    def test_remove_piece(self):
        """Test removing a piece from inventory."""
        player = Player(1, "Alice")
        assert len(player.pieces) == 21

        # Remove a piece
        removed = player.remove_piece("I5")
        assert removed is not None
        assert removed.name == "I5"
        assert len(player.pieces) == 20

        # Try to remove non-existent piece
        removed = player.remove_piece("X99")
        assert removed is None
        assert len(player.pieces) == 20

    def test_score_operations(self):
        """Test score modification."""
        player = Player(1, "Alice")
        assert player.get_score() == 0

        # Add points
        player.add_points(10)
        assert player.get_score() == 10

        player.add_points(5)
        assert player.get_score() == 15

        # Subtract points
        player.subtract_points(3)
        assert player.get_score() == 12

    def test_piece_placement(self):
        """Test placing a piece."""
        player = Player(1, "Alice")
        piece = player.get_piece("I1")
        assert not piece.is_placed

        player.place_piece("I1", 5, 5)
        assert piece.is_placed
        assert piece.placed_position == (5, 5)

    def test_cannot_place_nonexistent_piece(self):
        """Test that placing a non-existent piece raises error."""
        player = Player(1, "Alice")
        with pytest.raises(ValueError, match="Player does not have piece"):
            player.place_piece("X99", 0, 0)

    def test_cannot_place_already_placed_piece(self):
        """Test that placing an already placed piece raises error."""
        player = Player(1, "Alice")
        player.place_piece("I1", 0, 0)

        with pytest.raises(ValueError, match="already placed"):
            player.place_piece("I1", 5, 5)

    def test_remaining_piece_count(self):
        """Test counting remaining pieces."""
        player = Player(1, "Alice")
        assert player.get_remaining_piece_count() == 21

        player.place_piece("I1", 0, 0)
        assert player.get_remaining_piece_count() == 20

        player.place_piece("I2", 5, 5)
        assert player.get_remaining_piece_count() == 19

    def test_remaining_squares(self):
        """Test counting remaining squares."""
        player = Player(1, "Alice")
        # All 21 pieces total 89 squares (1+2+6+20+60 = 1*1 + 1*2 + 2*3 + 5*4 + 12*5)
        assert player.get_remaining_squares() == 89

        # Place an I1 (1 square)
        player.place_piece("I1", 0, 0)
        assert player.get_remaining_squares() == 88

    def test_has_pieces_remaining(self):
        """Test checking if player has remaining pieces."""
        player = Player(1, "Alice")
        assert player.has_pieces_remaining()

        # Place all pieces
        for piece_name in player.get_piece_names():
            player.place_piece(piece_name, 0, 0)

        assert not player.has_pieces_remaining()

    def test_player_color(self):
        """Test getting player color."""
        player1 = Player(1, "Alice")
        player2 = Player(2, "Bob")
        player3 = Player(3, "Charlie")
        player4 = Player(4, "Diana")

        assert player1.get_color() == "#FF0000"  # Red
        assert player2.get_color() == "#00FF00"  # Green
        assert player3.get_color() == "#0000FF"  # Blue
        assert player4.get_color() == "#FFFF00"  # Yellow

    def test_starting_corner(self):
        """Test getting player starting corner."""
        player1 = Player(1, "Alice")
        player2 = Player(2, "Bob")
        player3 = Player(3, "Charlie")
        player4 = Player(4, "Diana")

        assert player1.get_starting_corner() == (0, 0)
        assert player2.get_starting_corner() == (0, 19)
        assert player3.get_starting_corner() == (19, 19)
        assert player4.get_starting_corner() == (19, 0)

    def test_pass_turn(self):
        """Test player pass functionality."""
        player = Player(1, "Alice")
        assert not player.has_passed

        player.pass_turn()
        assert player.has_passed

        player.reset_pass()
        assert not player.has_passed

    def test_active_inactive_state(self):
        """Test player active/inactive state."""
        player = Player(1, "Alice")
        assert player.is_active

        player.set_inactive()
        assert not player.is_active

        player.set_active()
        assert player.is_active

    def test_player_repr(self):
        """Test string representation of player."""
        player = Player(1, "Alice")
        repr_str = repr(player)
        assert "Player" in repr_str
        assert "id=1" in repr_str
        assert "Alice" in repr_str
        assert "score=0" in repr_str
        assert "placed=0" in repr_str
        assert "unplaced=21" in repr_str

        # Place a piece
        player.place_piece("I1", 0, 0)
        repr_str = repr(player)
        assert "placed=1" in repr_str
        assert "unplaced=20" in repr_str

    def test_create_player_with_custom_pieces(self):
        """Test creating player with custom piece list."""
        custom_pieces = [
            Piece.from_coordinates("Custom1", [(0, 0)]),
            Piece.from_coordinates("Custom2", [(0, 0), (0, 1)]),
        ]
        player = Player(1, "Alice", pieces=custom_pieces)

        assert len(player.pieces) == 2
        assert player.get_piece("Custom1") is not None
        assert player.get_piece("Custom2") is not None
