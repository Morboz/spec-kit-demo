"""Unit tests for Board model."""

import pytest

from src.models.board import Board
from src.models.piece import Piece


class TestBoard:
    """Test suite for Board model."""

    def test_board_initialization(self):
        """Test creating a new 20x20 board."""
        board = Board()
        assert board.size == 20
        assert len(board.grid) == 0
        assert board.is_position_valid(0, 0)
        assert board.is_position_valid(19, 19)
        assert not board.is_position_valid(20, 20)
        assert not board.is_position_valid(-1, 0)
        assert not board.is_position_valid(0, -1)

    def test_position_validity(self):
        """Test checking if positions are valid."""
        board = Board()
        # Valid positions
        assert board.is_position_valid(0, 0)
        assert board.is_position_valid(10, 10)
        assert board.is_position_valid(19, 19)

        # Invalid positions
        assert not board.is_position_valid(20, 10)
        assert not board.is_position_valid(10, 20)
        assert not board.is_position_valid(-1, 10)
        assert not board.is_position_valid(10, -1)

    def test_position_emptiness(self):
        """Test checking if positions are empty."""
        board = Board()
        # Empty positions
        assert board.is_position_empty(0, 0)
        assert board.is_position_empty(10, 10)
        assert board.is_position_empty(19, 19)

        # Place a piece
        piece = Piece("I1")
        board.place_piece(piece, 0, 0, 1)
        assert not board.is_position_empty(0, 0)

        # Position is still empty elsewhere
        assert board.is_position_empty(1, 1)

    def test_place_single_square_piece(self):
        """Test placing a single-square piece on the board."""
        board = Board()
        piece = Piece("I1")
        positions = board.place_piece(piece, 5, 5, 1)

        assert len(positions) == 1
        assert (5, 5) in positions
        assert board.is_occupied(5, 5)
        assert board.get_occupant(5, 5) == 1
        assert board.count_player_squares(1) == 1

    def test_place_multi_square_piece(self):
        """Test placing a multi-square piece on the board."""
        board = Board()
        piece = Piece("L4")
        positions = board.place_piece(piece, 5, 5, 2)

        # L4 has 4 squares
        assert len(positions) == 4
        assert board.is_occupied(5, 5)
        assert board.is_occupied(5, 6)
        assert board.is_occupied(5, 7)
        assert board.is_occupied(6, 7)
        assert board.get_occupant(5, 5) == 2
        assert board.count_player_squares(2) == 4

    def test_cannot_place_piece_out_of_bounds(self):
        """Test that placing a piece out of bounds raises an error."""
        board = Board()
        piece = Piece("I2")
        # Try to place piece so it extends beyond bottom boundary
        with pytest.raises(ValueError, match="outside board bounds"):
            board.place_piece(piece, 19, 0, 1)

    def test_cannot_place_piece_on_occupied_position(self):
        """Test that placing a piece on an occupied position raises an error."""
        board = Board()
        piece = Piece("I1")

        # Place first piece
        board.place_piece(piece, 5, 5, 1)

        # Try to place another piece on same position
        piece2 = Piece("I1")
        with pytest.raises(ValueError, match="already occupied"):
            board.place_piece(piece2, 5, 5, 2)

    def test_get_occupied_positions(self):
        """Test retrieving all occupied positions."""
        board = Board()

        # No pieces placed
        assert len(board.get_occupied_positions()) == 0

        # Place pieces
        piece1 = Piece("I2")
        board.place_piece(piece1, 5, 5, 1)
        occupied = board.get_occupied_positions()
        assert len(occupied) == 2
        assert (5, 5) in occupied
        assert (6, 5) in occupied

        # Place another piece
        piece2 = Piece("V3")
        board.place_piece(piece2, 10, 10, 2)
        occupied = board.get_occupied_positions()
        assert len(occupied) == 5  # 2 + 3

    def test_get_player_positions(self):
        """Test retrieving positions for a specific player."""
        board = Board()

        # Place pieces for player 1
        piece1 = Piece("I2")
        board.place_piece(piece1, 5, 5, 1)

        # Place pieces for player 2
        piece2 = Piece("I1")
        board.place_piece(piece2, 10, 10, 2)

        # Check player 1 positions
        player1_positions = board.get_player_positions(1)
        assert len(player1_positions) == 2
        assert (5, 5) in player1_positions
        assert (6, 5) in player1_positions

        # Check player 2 positions
        player2_positions = board.get_player_positions(2)
        assert len(player2_positions) == 1
        assert (10, 10) in player2_positions

        # Player 3 has no positions
        player3_positions = board.get_player_positions(3)
        assert len(player3_positions) == 0

    def test_get_board_state(self):
        """Test retrieving complete board state."""
        board = Board()
        state = board.get_board_state()

        # Should be 20x20 grid
        assert len(state) == 20
        assert len(state[0]) == 20
        assert all(cell is None for row in state for cell in row)

        # Place pieces
        piece1 = Piece("I2")
        board.place_piece(piece1, 5, 5, 1)

        piece2 = Piece("L4")
        board.place_piece(piece2, 10, 10, 2)

        state = board.get_board_state()

        # Check player 1 pieces
        assert state[5][5] == 1
        assert state[6][5] == 1

        # Check player 2 pieces
        assert state[10][10] == 2
        assert state[10][11] == 2
        assert state[10][12] == 2
        assert state[11][12] == 2

        # Check empty positions
        assert state[0][0] is None
        assert state[19][19] is None

    def test_get_adjacent_positions_orthogonal(self):
        """Test retrieving orthogonal adjacent positions."""
        board = Board()
        center = (10, 10)
        adjacent = board.get_adjacent_positions(center[0], center[1])

        # Should have 4 orthogonal neighbors
        assert len(adjacent) == 4
        assert (9, 10) in adjacent  # Up
        assert (11, 10) in adjacent  # Down
        assert (10, 9) in adjacent  # Left
        assert (10, 11) in adjacent  # Right

    def test_get_adjacent_positions_with_diagonal(self):
        """Test retrieving adjacent positions including diagonal."""
        board = Board()
        center = (10, 10)
        adjacent = board.get_adjacent_positions(
            center[0], center[1], include_diagonal=True
        )

        # Should have 8 total neighbors (4 orthogonal + 4 diagonal)
        assert len(adjacent) == 8

        # Orthogonal
        assert (9, 10) in adjacent
        assert (11, 10) in adjacent
        assert (10, 9) in adjacent
        assert (10, 11) in adjacent

        # Diagonal
        assert (9, 9) in adjacent
        assert (9, 11) in adjacent
        assert (11, 9) in adjacent
        assert (11, 11) in adjacent

    def test_get_adjacent_positions_at_corner(self):
        """Test retrieving adjacent positions from corner."""
        board = Board()
        corner = (0, 0)
        adjacent = board.get_adjacent_positions(corner[0], corner[1])

        # Corner has only 2 orthogonal neighbors
        assert len(adjacent) == 2
        assert (1, 0) in adjacent  # Down
        assert (0, 1) in adjacent  # Right

    def test_count_player_squares(self):
        """Test counting squares for a player."""
        board = Board()

        # No pieces
        assert board.count_player_squares(1) == 0

        # Place some pieces for player 1
        piece1 = Piece("I2")
        board.place_piece(piece1, 5, 5, 1)
        assert board.count_player_squares(1) == 2

        piece2 = Piece("V3")
        board.place_piece(piece2, 10, 10, 1)
        assert board.count_player_squares(1) == 5

        # Player 2 has no pieces
        assert board.count_player_squares(2) == 0

    def test_board_repr(self):
        """Test string representation of board."""
        board = Board()
        assert "Board" in repr(board)
        assert "20x20" in repr(board)
        assert "occupied=0" in repr(board)

        # Place a piece
        piece = Piece("I1")
        board.place_piece(piece, 5, 5, 1)
        assert "occupied=1" in repr(board)
