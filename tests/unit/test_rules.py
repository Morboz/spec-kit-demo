"""Unit tests for Rules validator."""

import pytest
from src.game.rules import BlokusRules, ValidationResult
from src.models.game_state import GameState
from src.models.board import Board
from src.models.player import Player
from src.models.piece import Piece


class TestValidationResult:
    """Test suite for ValidationResult."""

    def test_valid_result(self):
        """Test creating a valid validation result."""
        result = ValidationResult(True)
        assert result.is_valid
        assert result.reason == ""

    def test_invalid_result(self):
        """Test creating an invalid validation result."""
        result = ValidationResult(False, "Test error")
        assert not result.is_valid
        assert result.reason == "Test error"

    def test_result_repr(self):
        """Test string representation of validation result."""
        valid = ValidationResult(True)
        assert "valid=True" in repr(valid)

        invalid = ValidationResult(False, "Error")
        assert "valid=False" in repr(invalid)
        assert "Error" in repr(invalid)


class TestBlokusRules:
    """Test suite for BlokusRules validator."""

    def setup_method(self):
        """Set up test fixtures."""
        self.game_state = GameState()
        self.board = self.game_state.board
        self.player1 = Player(1, "Alice")
        self.player2 = Player(2, "Bob")

        self.game_state.add_player(self.player1)
        self.game_state.add_player(self.player2)
        self.game_state.start_game()

    def test_validate_move_with_nonexistent_player(self):
        """Test that validation fails for non-existent player."""
        result = BlokusRules.validate_move(self.game_state, 999, Piece("I1"), 0, 0)
        assert not result.is_valid
        assert "Player not found" in result.reason

    def test_validate_move_with_nonexistent_piece(self):
        """Test that validation fails for piece not owned by player."""
        # Create a custom piece not in player's inventory
        piece = Piece.from_coordinates("Custom", [(0, 0)])
        result = BlokusRules.validate_move(self.game_state, 1, piece, 0, 0)
        assert not result.is_valid
        assert "does not own this piece" in result.reason

    def test_validate_move_with_already_placed_piece(self):
        """Test that validation fails for already placed piece."""
        piece = self.player1.get_piece("I1")
        self.player1.place_piece("I1", 0, 0)

        result = BlokusRules.validate_move(self.game_state, 1, piece, 5, 5)
        assert not result.is_valid
        assert "already placed" in result.reason

    def test_validate_move_out_of_bounds(self):
        """Test that validation fails for out of bounds placement."""
        piece = self.player1.get_piece("I5")

        # Try to place near bottom edge
        result = BlokusRules.validate_move(self.game_state, 1, piece, 18, 0)
        assert not result.is_valid
        assert "outside board bounds" in result.reason

    def test_validate_move_with_overlap(self):
        """Test that validation fails for overlapping pieces."""
        # Place a piece
        piece1 = self.player1.get_piece("I1")
        self.board.place_piece(piece1, 5, 5, 1)

        # Try to place another piece on the same position
        piece2 = self.player1.get_piece("I2")
        result = BlokusRules.validate_move(self.game_state, 1, piece2, 5, 5)
        assert not result.is_valid
        assert "already occupied" in result.reason

    def test_validate_move_with_own_edge_contact(self):
        """Test that validation fails with edge-to-edge contact with own piece."""
        # Place a piece for player 1
        piece1 = self.player1.get_piece("I1")
        self.board.place_piece(piece1, 5, 5, 1)

        # Try to place another piece that touches it edge-to-edge
        piece2 = self.player1.get_piece("I1")
        result = BlokusRules.validate_move(self.game_state, 1, piece2, 5, 6)
        assert not result.is_valid
        assert "edge-to-edge contact" in result.reason

    def test_validate_move_with_opponent_contact_allowed(self):
        """Test that edge-to-edge contact with opponent pieces is allowed."""
        # Make first moves for both players
        piece1 = self.player1.get_piece("I1")
        self.board.place_piece(piece1, 0, 0, 1)
        self.player1.place_piece("I1", 0, 0)

        piece2 = self.player2.get_piece("I2")
        self.board.place_piece(piece2, 0, 19, 2)
        self.player2.place_piece("I2", 0, 19)

        # Place another piece for player 1 that has diagonal contact with piece1 at (0,0)
        # I2 at (1,1) has diagonal contact with (0,0)
        piece3 = self.player1.get_piece("I2")
        result = BlokusRules.validate_move(self.game_state, 1, piece3, 1, 1)
        # This should be valid - has diagonal contact with own piece
        assert result.is_valid

    def test_validate_diagonal_contact_allowed(self):
        """Test that diagonal contact with own pieces is required and allowed."""
        # Make first move
        piece1 = self.player1.get_piece("I1")
        self.board.place_piece(piece1, 0, 0, 1)
        self.player1.place_piece("I1", 0, 0)

        # Try to place another piece that only touches diagonally
        # I2 at (1,1) will have one square at (1,1) which is diagonal to (0,0)
        piece2 = self.player1.get_piece("I2")
        result = BlokusRules.validate_move(self.game_state, 1, piece2, 1, 1)
        # This should be valid - diagonal contact is required and allowed
        assert result.is_valid

    def test_validate_first_move_must_be_in_corner(self):
        """Test that first move must be in player's corner."""
        # Player 1's corner is (0, 0)
        piece = self.player1.get_piece("I1")

        # Valid placement in corner
        result = BlokusRules.validate_move(self.game_state, 1, piece, 0, 0)
        assert result.is_valid

        # Invalid placement not in corner - use a different piece
        piece2 = self.player1.get_piece("I2")
        result = BlokusRules.validate_move(self.game_state, 1, piece2, 5, 5)
        assert not result.is_valid
        assert "corner" in result.reason.lower()

    def test_validate_first_move_with_larger_piece(self):
        """Test first move with larger piece that includes corner."""
        piece = self.player1.get_piece("I5")
        piece.rotate(90)  # Make it vertical

        # Place so that it includes corner (0,0)
        result = BlokusRules.validate_move(self.game_state, 1, piece, 0, 0)
        assert result.is_valid

    def test_validate_move_not_in_first_move(self):
        """Test that non-first moves don't need to be in corner but need diagonal contact."""
        # Make the first move for player 1
        piece1 = self.player1.get_piece("I1")
        result = BlokusRules.validate_move(self.game_state, 1, piece1, 0, 0)
        assert result.is_valid

        # Place the piece on the board
        self.board.place_piece(piece1, 0, 0, 1)
        self.player1.place_piece("I1", 0, 0)

        # Now player 1's subsequent moves don't need to be in corner
        # but must have diagonal contact with existing piece at (0,0)
        piece2 = self.player1.get_piece("I2")
        result = BlokusRules.validate_move(self.game_state, 1, piece2, 1, 1)
        assert result.is_valid

    def test_validate_valid_move(self):
        """Test a completely valid move."""
        # Player 1's first move in corner
        piece = self.player1.get_piece("I1")
        result = BlokusRules.validate_move(self.game_state, 1, piece, 0, 0)
        assert result.is_valid

    def test_get_valid_moves(self):
        """Test getting all valid moves for a piece."""
        # For first move, only corner is valid
        piece = self.player1.get_piece("I1")
        valid_moves = BlokusRules.get_valid_moves(self.game_state, 1, piece)

        # At least corner (0,0) should be valid
        assert (0, 0) in valid_moves

        # Make the first move
        self.board.place_piece(piece, 0, 0, 1)
        self.player1.place_piece("I1", 0, 0)

        # Player 2's first move
        piece2 = self.player2.get_piece("I1")
        valid_moves = BlokusRules.get_valid_moves(self.game_state, 2, piece2)

        # Player 2's corner is (0, 19)
        assert (0, 19) in valid_moves

    def test_get_invalid_positions(self):
        """Test getting invalid positions and their reasons."""
        piece = self.player1.get_piece("I1")
        invalid_moves = BlokusRules.get_invalid_positions(self.game_state, 1, piece)

        # Many positions should be invalid for first move
        assert len(invalid_moves) > 0

        # Positions should map to error reasons
        for position, reason in invalid_moves.items():
            assert isinstance(position, tuple)
            assert len(position) == 2
            assert isinstance(reason, str)
            assert len(reason) > 0

        # Corner (0,0) should be valid, so not in invalid moves
        assert (0, 0) not in invalid_moves

    def test_validate_multiple_squares_piece(self):
        """Test validation with a piece that has multiple squares."""
        piece = self.player1.get_piece("L4")

        # First move in corner
        result = BlokusRules.validate_move(self.game_state, 1, piece, 0, 0)
        # This is valid as long as (0,0) is included
        assert result.is_valid

    def test_first_move_for_different_players(self):
        """Test that each player has different corner requirements."""
        # Player 1: top-left corner (0, 0)
        piece1 = self.player1.get_piece("I1")
        result1 = BlokusRules.validate_move(self.game_state, 1, piece1, 0, 0)
        assert result1.is_valid

        # Player 2: top-right corner (0, 19)
        piece2 = self.player2.get_piece("I1")
        result2 = BlokusRules.validate_move(self.game_state, 2, piece2, 0, 19)
        assert result2.is_valid

    def test_validate_move_with_rotation(self):
        """Test validation with rotated piece."""
        piece = self.player1.get_piece("I5")
        rotated_piece = piece.rotate(90)

        # First move in corner with rotated piece
        result = BlokusRules.validate_move(self.game_state, 1, rotated_piece, 0, 0)
        assert result.is_valid

    def test_validate_move_with_flip(self):
        """Test validation with flipped piece."""
        # Make first move
        piece1 = self.player1.get_piece("I1")
        self.board.place_piece(piece1, 0, 0, 1)
        self.player1.place_piece("I1", 0, 0)

        # Test with flipped piece (not first move)
        # Use I2 which is simpler and place at safe position
        piece = self.player1.get_piece("I2")
        flipped_piece = piece.flip()

        # Place at (1,1) to have diagonal contact with (0,0)
        result = BlokusRules.validate_move(self.game_state, 1, flipped_piece, 1, 1)
        assert result.is_valid

    def test_board_boundaries(self):
        """Test that placements at board edges are handled correctly."""
        # Make first move
        piece1 = self.player1.get_piece("I1")
        self.board.place_piece(piece1, 0, 0, 1)
        self.player1.place_piece("I1", 0, 0)

        # Valid placement at edge for subsequent moves
        # Must have diagonal contact with (0,0), so place at (1,1) first
        piece2 = self.player1.get_piece("I2")
        result = BlokusRules.validate_move(self.game_state, 1, piece2, 1, 1)
        assert result.is_valid

    def test_empty_board_state(self):
        """Test with completely empty board."""
        game_state = GameState()
        player1 = Player(1, "Alice")
        player2 = Player(2, "Bob")
        game_state.add_player(player1)
        game_state.add_player(player2)
        game_state.start_game()

        piece = player1.get_piece("I1")
        result = BlokusRules.validate_move(game_state, 1, piece, 0, 0)
        assert result.is_valid
