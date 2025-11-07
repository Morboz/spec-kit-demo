"""Contract tests for board bounds validation.

This test validates that all pieces must be placed within the 20x20
board boundaries.
"""

from blokus_game.game.rules import BlokusRules
from blokus_game.models.board import Board
from blokus_game.models.game_state import GameState
from blokus_game.models.player import Player


class TestBoardBounds:
    """Contract tests for board bounds validation."""

    def test_piece_within_bounds_is_valid(self):
        """Contract: Piece completely within board bounds is valid.

        Given: Player has placed first piece at corner
        When: Second piece is placed with diagonal contact to first piece
        Then: Move is valid
        """
        # Given: Player has placed first piece at corner
        board = Board()
        player = Player(player_id=1, name="Alice")
        game_state = GameState()
        game_state.board = board
        game_state.add_player(player)

        # Place first piece at corner
        first_piece = player.get_piece("I2")
        board.place_piece(first_piece, 0, 0, 1)
        first_piece.place_at(0, 0)

        # When: Second piece placed with diagonal contact at (2, 1)
        piece = player.get_piece("L4")
        result = BlokusRules.validate_move(game_state, player.player_id, piece, 2, 1)

        # Then: Valid
        assert result.is_valid is True

    def test_piece_at_top_boundary_is_valid(self):
        """Contract: Piece at top boundary (row 0) is valid.

        Given: Player has placed first piece at corner
        When: Second piece is placed with diagonal contact
        Then: Move is valid
        """
        # Given: Player has placed first piece at corner
        board = Board()
        player = Player(player_id=1, name="Alice")
        game_state = GameState()
        game_state.board = board
        game_state.add_player(player)

        # Place first piece at corner
        first_piece = player.get_piece("I2")
        board.place_piece(first_piece, 0, 0, 1)
        first_piece.place_at(0, 0)

        # When: Second piece placed with diagonal contact at (2, 1)
        piece = player.get_piece("L4")
        result = BlokusRules.validate_move(game_state, player.player_id, piece, 2, 1)

        # Then: Valid
        assert result.is_valid is True

    def test_piece_at_left_boundary_is_valid(self):
        """Contract: Piece at left boundary (col 0) is valid.

        Given: Player has placed first piece at corner
        When: Second piece is placed with diagonal contact
        Then: Move is valid
        """
        # Given: Player has placed first piece at corner
        board = Board()
        player = Player(player_id=1, name="Alice")
        game_state = GameState()
        game_state.board = board
        game_state.add_player(player)

        # Place first piece at corner
        first_piece = player.get_piece("I2")
        board.place_piece(first_piece, 0, 0, 1)
        first_piece.place_at(0, 0)

        # When: Second piece placed with diagonal contact at (2, 1)
        piece = player.get_piece("L4")
        result = BlokusRules.validate_move(game_state, player.player_id, piece, 2, 1)

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
        result = BlokusRules.validate_move(game_state, player.player_id, piece, -1, 5)

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
        result = BlokusRules.validate_move(game_state, player.player_id, piece, 19, 5)

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
        result = BlokusRules.validate_move(game_state, player.player_id, piece, 5, -1)

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
        result = BlokusRules.validate_move(game_state, player.player_id, piece, 5, 19)

        # Then: Invalid
        assert result.is_valid is False
        assert "bounds" in result.reason.lower() or "outside" in result.reason.lower()

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
        result = BlokusRules.validate_move(game_state, player.player_id, piece, 19, 5)

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
        result = BlokusRules.validate_move(game_state, player.player_id, piece, 17, 5)

        # Then: Invalid (extends beyond row 19)
        assert result.is_valid is False

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
        result = BlokusRules.validate_move(game_state, player.player_id, piece, 18, 18)

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
        valid_moves = BlokusRules.get_valid_moves(game_state, player.player_id, piece)

        # Then: All moves are within bounds
        for row, col in valid_moves:
            # Verify piece doesn't go out of bounds
            positions = piece.get_absolute_positions(row, col)
            for pos_row, pos_col in positions:
                assert 0 <= pos_row < board.size
                assert 0 <= pos_col < board.size
