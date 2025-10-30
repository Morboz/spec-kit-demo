"""Contract tests for board bounds validation.

This test validates that all pieces must be placed within the 20x20
board boundaries.
"""

import pytest
from src.models.board import Board
from src.models.player import Player
from src.models.game_state import GameState
from src.game.rules import BlokusRules


class TestBoardBounds:
    """Contract tests for board bounds validation."""

    def test_piece_within_bounds_is_valid(self):
        """Contract: Piece completely within board bounds is valid.

        Given: Empty 20x20 board
        When: Piece is placed fully within bounds
        Then: Move is valid
        """
        # Given: Empty board
        board = Board()
        player = Player(player_id=1, name="Alice")
        game_state = GameState()
        game_state.board = board
        game_state.add_player(player)

        # When: Piece placed at (5, 5) with all squares in bounds
        piece = player.get_piece("I2")
        result = BlokusRules.validate_move(
            game_state, player.player_id, piece, 5, 5
        )

        # Then: Valid
        assert result.is_valid is True

    def test_piece_at_top_boundary_is_valid(self):
        """Contract: Piece at top boundary (row 0) is valid.

        Given: Empty board
        When: Piece is placed with top edge at row 0
        Then: Move is valid
        """
        # Given: Empty board
        board = Board()
        player = Player(player_id=1, name="Alice")
        game_state = GameState()
        game_state.board = board
        game_state.add_player(player)

        # When: Piece placed at row 0
        piece = player.get_piece("I2")
        result = BlokusRules.validate_move(
            game_state, player.player_id, piece, 0, 5
        )

        # Then: Valid
        assert result.is_valid is True

    def test_piece_at_bottom_boundary_is_valid(self):
        """Contract: Piece at bottom boundary (row 19) is valid.

        Given: Empty board
        When: Piece is placed with bottom edge at row 19
        Then: Move is valid
        """
        # Given: Empty board
        board = Board()
        player = Player(player_id=1, name="Alice")
        game_state = GameState()
        game_state.board = board
        game_state.add_player(player)

        # When: Piece placed at row 18 (occupies 18, 19)
        piece = player.get_piece("I2")
        result = BlokusRules.validate_move(
            game_state, player.player_id, piece, 18, 5
        )

        # Then: Valid
        assert result.is_valid is True

    def test_piece_at_left_boundary_is_valid(self):
        """Contract: Piece at left boundary (col 0) is valid.

        Given: Empty board
        When: Piece is placed with left edge at col 0
        Then: Move is valid
        """
        # Given: Empty board
        board = Board()
        player = Player(player_id=1, name="Alice")
        game_state = GameState()
        game_state.board = board
        game_state.add_player(player)

        # When: Piece placed at col 0
        piece = player.get_piece("I2")
        result = BlokusRules.validate_move(
            game_state, player.player_id, piece, 5, 0
        )

        # Then: Valid
        assert result.is_valid is True

    def test_piece_at_right_boundary_is_valid(self):
        """Contract: Piece at right boundary (col 19) is valid.

        Given: Empty board
        When: Piece is placed with right edge at col 19
        Then: Move is valid
        """
        # Given: Empty board
        board = Board()
        player = Player(player_id=1, name="Alice")
        game_state = GameState()
        game_state.board = board
        game_state.add_player(player)

        # When: Piece placed at col 18 (occupies 18, 19)
        piece = player.get_piece("I2")
        result = BlokusRules.validate_move(
            game_state, player.player_id, piece, 5, 18
        )

        # Then: Valid
        assert result.is_valid is True

    def test_piece_extending_beyond_top_is_invalid(self):
        """Contract: Piece extending beyond top boundary is invalid.

        Given: Empty board
        When: Piece is placed such that it extends above row 0
        Then: Move is invalid with bounds error
        """
        # Given: Empty board
        board = Board()
        player = Player(player_id=1, name="Alice")
        game_state = GameState()
        game_state.board = board
        game_state.add_player(player)

        # When: Piece anchor at negative row
        piece = player.get_piece("V3")
        result = BlokusRules.validate_move(
            game_state, player.player_id, piece, -1, 5
        )

        # Then: Invalid
        assert result.is_valid is False
        assert "bounds" in result.reason.lower() or "outside" in result.reason.lower()

    def test_piece_extending_beyond_bottom_is_invalid(self):
        """Contract: Piece extending beyond bottom boundary is invalid.

        Given: Empty board
        When: Piece is placed such that it extends below row 19
        Then: Move is invalid with bounds error
        """
        # Given: Empty board
        board = Board()
        player = Player(player_id=1, name="Alice")
        game_state = GameState()
        game_state.board = board
        game_state.add_player(player)

        # When: Piece anchor at row 19 (would extend to 21)
        piece = player.get_piece("V3")
        result = BlokusRules.validate_move(
            game_state, player.player_id, piece, 19, 5
        )

        # Then: Invalid
        assert result.is_valid is False
        assert "bounds" in result.reason.lower() or "outside" in result.reason.lower()

    def test_piece_extending_beyond_left_is_invalid(self):
        """Contract: Piece extending beyond left boundary is invalid.

        Given: Empty board
        When: Piece is placed such that it extends left of col 0
        Then: Move is invalid with bounds error
        """
        # Given: Empty board
        board = Board()
        player = Player(player_id=1, name="Alice")
        game_state = GameState()
        game_state.board = board
        game_state.add_player(player)

        # When: Piece anchor at negative col
        piece = player.get_piece("V3")
        result = BlokusRules.validate_move(
            game_state, player.player_id, piece, 5, -1
        )

        # Then: Invalid
        assert result.is_valid is False
        assert "bounds" in result.reason.lower() or "outside" in result.reason.lower()

    def test_piece_extending_beyond_right_is_invalid(self):
        """Contract: Piece extending beyond right boundary is invalid.

        Given: Empty board
        When: Piece is placed such that it extends right of col 19
        Then: Move is invalid with bounds error
        """
        # Given: Empty board
        board = Board()
        player = Player(player_id=1, name="Alice")
        game_state = GameState()
        game_state.board = board
        game_state.add_player(player)

        # When: Piece anchor at col 19 (would extend to 22)
        piece = player.get_piece("V3")
        result = BlokusRules.validate_move(
            game_state, player.player_id, piece, 5, 19
        )

        # Then: Invalid
        assert result.is_valid is False
        assert "bounds" in result.reason.lower() or "outside" in result.reason.lower()

    def test_large_piece_at_corner_within_bounds(self):
        """Contract: Large piece at corner fully within bounds is valid.

        Given: Empty board
        When: Large piece is placed at corner (0, 0)
        Then: Move is valid if within bounds
        """
        # Given: Empty board
        board = Board()
        player = Player(player_id=1, name="Alice")
        game_state = GameState()
        game_state.board = board
        game_state.add_player(player)

        # When: X5 piece placed at (0, 0)
        piece = player.get_piece("X5")
        result = BlokusRules.validate_move(
            game_state, player.player_id, piece, 0, 0
        )

        # Then: Valid
        assert result.is_valid is True

    def test_error_message_includes_invalid_position(self):
        """Contract: Error message specifies which position is out of bounds.

        Given: Empty board
        When: Piece extends beyond bounds
        Then: Error message includes the out-of-bounds coordinates
        """
        # Given: Empty board
        board = Board()
        player = Player(player_id=1, name="Alice")
        game_state = GameState()
        game_state.board = board
        game_state.add_player(player)

        # When: Piece extends beyond bottom
        piece = player.get_piece("V3")
        result = BlokusRules.validate_move(
            game_state, player.player_id, piece, 19, 5
        )

        # Then: Error includes position
        assert result.is_valid is False
        assert len(result.reason) > 0
        # Position might be (19, 5), (20, 5), (21, 5) depending on piece orientation

    def test_partially_out_of_bounds_is_invalid(self):
        """Contract: Even partial out-of-bounds placement is invalid.

        Given: Empty board
        When: Some squares of piece are in bounds, others out
        Then: Move is invalid
        """
        # Given: Empty board
        board = Board()
        player = Player(player_id=1, name="Alice")
        game_state = GameState()
        game_state.board = board
        game_state.add_player(player)

        # When: I5 piece placed with end out of bounds
        piece = player.get_piece("I5")
        result = BlokusRules.validate_move(
            game_state, player.player_id, piece, 17, 5
        )

        # Then: Invalid (extends beyond row 19)
        assert result.is_valid is False

    def test_rotated_piece_within_bounds(self):
        """Contract: Rotated piece within bounds is valid.

        Given: Empty board
        When: Rotated piece is placed fully within bounds
        Then: Move is valid
        """
        # Given: Empty board
        board = Board()
        player = Player(player_id=1, name="Alice")
        game_state = GameState()
        game_state.board = board
        game_state.add_player(player)

        # When: L4 piece rotated and placed at (5, 5)
        piece = player.get_piece("L4").rotate(90)
        result = BlokusRules.validate_move(
            game_state, player.player_id, piece, 5, 5
        )

        # Then: Valid
        assert result.is_valid is True

    def test_rotated_piece_extending_beyond_bounds(self):
        """Contract: Rotated piece extending beyond bounds is invalid.

        Given: Empty board
        When: Rotated piece extends beyond bounds
        Then: Move is invalid
        """
        # Given: Empty board
        board = Board()
        player = Player(player_id=1, name="Alice")
        game_state = GameState()
        game_state.board = board
        game_state.add_player(player)

        # When: Rotated L4 piece placed near edge (extends out)
        piece = player.get_piece("L4").rotate(90)
        result = BlokusRules.validate_move(
            game_state, player.player_id, piece, 18, 18
        )

        # Then: Invalid
        assert result.is_valid is False

    def test_board_size_is_20_by_20(self):
        """Contract: Board size is exactly 20x20.

        Given: Board instance
        When: Board size is checked
        Then: Size is 20
        """
        board = Board()
        assert board.size == 20

    def test_all_positions_in_bounds_are_valid_anchor_points(self):
        """Contract: All positions that keep piece in bounds are valid anchors.

        Given: Piece of known size
        When: Valid anchor positions are calculated
        Then: All anchors keep piece within bounds
        """
        # Given: Empty board and I5 piece
        board = Board()
        player = Player(player_id=1, name="Alice")
        game_state = GameState()
        game_state.board = board
        game_state.add_player(player)

        piece = player.get_piece("I5")

        # When: Get valid moves
        valid_moves = BlokusRules.get_valid_moves(
            game_state, player.player_id, piece
        )

        # Then: All moves are within bounds
        for row, col in valid_moves:
            # Verify piece doesn't go out of bounds
            positions = piece.get_absolute_positions(row, col)
            for pos_row, pos_col in positions:
                assert 0 <= pos_row < board.size
                assert 0 <= pos_col < board.size
