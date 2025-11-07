"""Contract tests for first move corner rule.

This test validates that the first move must be placed in the player's
starting corner as per official Blokus rules.
"""

from src.game.rules import BlokusRules
from src.models.board import Board
from src.models.game_state import GameState
from src.models.player import Player


class TestFirstMoveCornerRule:
    """Contract tests for first move corner validation."""

    def test_first_move_in_corner_is_valid(self):
        """Contract: First move placed in starting corner is valid.

        Given: Empty board and player making first move
        When: Piece is placed in player's starting corner
        Then: Move is valid
        """
        # Given: Empty board and player
        board = Board()
        player = Player(player_id=1, name="Alice")
        game_state = GameState()
        game_state.board = board
        game_state.add_player(player)

        # Player's starting corner is (0, 0)
        piece = player.get_piece("I2")

        # When: Piece is placed with one square in corner
        result = BlokusRules.validate_move(game_state, player.player_id, piece, 0, 0)

        # Then: Move is valid (I2 at (0,0) covers (0,0) and (1,0))
        assert result.is_valid is True

    def test_first_move_not_in_corner_is_invalid(self):
        """Contract: First move not in starting corner is invalid.

        Given: Empty board and player making first move
        When: Piece is placed NOT in player's starting corner
        Then: Move is invalid with specific error message
        """
        # Given: Empty board and player
        board = Board()
        player = Player(player_id=1, name="Alice")
        game_state = GameState()
        game_state.board = board
        game_state.add_player(player)

        # When: Piece is placed away from corner
        piece = player.get_piece("I2")
        result = BlokusRules.validate_move(game_state, player.player_id, piece, 5, 5)

        # Then: Move is invalid
        assert result.is_valid is False
        assert "corner" in result.reason.lower()
        assert "0, 0" in result.reason or "(0, 0)" in result.reason

    def test_player_1_first_move_in_top_left_corner(self):
        """Contract: Player 1's first move must be in top-left corner.

        Given: Player 1 (top-left corner)
        When: First move is made
        Then: Must include position (0, 0)
        """
        # Given: Player 1
        board = Board()
        player = Player(player_id=1, name="Alice")
        game_state = GameState()
        game_state.board = board
        game_state.add_player(player)

        # When: Trying to place at (0, 0)
        piece = player.get_piece("V3")
        result = BlokusRules.validate_move(game_state, player.player_id, piece, 0, 0)

        # Then: Valid
        assert result.is_valid is True

    def test_player_2_first_move_in_top_right_corner(self):
        """Contract: Player 2's first move must be in top-right corner.

        Given: Player 2 (top-right corner at (0, 19))
        When: First move is made
        Then: Must include position (0, 19)
        """
        # Given: Player 2 with top-right corner
        board = Board()
        player = Player(player_id=2, name="Bob")
        game_state = GameState()
        game_state.board = board
        game_state.add_player(player)

        # When: Trying to place at (0, 19) with I1 at corner
        piece = player.get_piece("I1")
        result = BlokusRules.validate_move(game_state, player.player_id, piece, 0, 19)

        # Then: Valid (I1 at (0, 19) covers the corner)
        assert result.is_valid is True

    def test_player_3_first_move_in_bottom_left_corner(self):
        """Contract: Player 3's first move must be in bottom-right corner.

        Given: Player 3 (bottom-right corner at (19, 19))
        When: First move is made
        Then: Must include position (19, 19)
        """
        # Given: Player 3 with bottom-left corner
        board = Board()
        player = Player(player_id=3, name="Charlie")
        game_state = GameState()
        game_state.board = board
        game_state.add_player(player)

        # When: Trying to place at (19, 19) with I1 at corner
        piece = player.get_piece("I1")
        result = BlokusRules.validate_move(game_state, player.player_id, piece, 19, 19)

        # Then: Valid (I1 at (19, 19) covers the corner)
        assert result.is_valid is True

    def test_player_4_first_move_in_bottom_right_corner(self):
        """Contract: Player 4's first move must be in bottom-left corner.

        Given: Player 4 (bottom-left corner at (19, 0))
        When: First move is made
        Then: Must include position (19, 0)
        """
        # Given: Player 4 with bottom-right corner
        board = Board()
        player = Player(player_id=4, name="Diana")
        game_state = GameState()
        game_state.board = board
        game_state.add_player(player)

        # When: Trying to place at (19, 0) with I1 at corner
        piece = player.get_piece("I1")
        result = BlokusRules.validate_move(game_state, player.player_id, piece, 19, 0)

        # Then: Valid (I1 at (19, 0) covers the corner)
        assert result.is_valid is True

    def test_second_move_not_required_in_corner(self):
        """Contract: Second move does not need to be in corner.

        Given: Player who has already placed one piece
        When: Second move is made with diagonal contact to first piece
        Then: Corner rule does not apply, but corner-to-corner contact is required
        """
        # Given: Player who has placed a piece
        board = Board()
        player = Player(player_id=1, name="Alice")
        game_state = GameState()
        game_state.board = board
        game_state.add_player(player)

        # First, place a piece in the corner
        first_piece = player.get_piece("I2")
        board.place_piece(first_piece, 0, 0, 1)
        first_piece.place_at(0, 0)

        # When: Second piece is placed with diagonal contact to first piece
        # I2 at (0,0) covers (0,0) and (1,0)
        # L4 at (2,1) will have diagonal contact at (1,1)
        second_piece = player.get_piece("L4")
        result = BlokusRules.validate_move(
            game_state, player.player_id, second_piece, 2, 1
        )

        # Then: Valid (corner rule doesn't apply, diagonal contact is valid)
        assert result.is_valid is True

    def test_piece_extending_from_corner_is_valid(self):
        """Contract: Piece can extend from corner square.

        Given: Empty board
        When: First move places piece with one square in corner
        Then: Valid even if piece extends away from corner
        """
        # Given: Empty board
        board = Board()
        player = Player(player_id=1, name="Alice")
        game_state = GameState()
        game_state.board = board
        game_state.add_player(player)

        # When: L4 piece placed with corner at (0, 0)
        piece = player.get_piece("L4")
        result = BlokusRules.validate_move(game_state, player.player_id, piece, 0, 0)

        # Then: Valid
        assert result.is_valid is True

    def test_error_message_specifies_correct_corner(self):
        """Contract: Error message includes the correct corner coordinates.

        Given: Player with known starting corner
        When: First move is invalid (not in corner)
        Then: Error message includes expected corner coordinates
        """
        # Given: Player 2 with corner at (0, 19)
        board = Board()
        player = Player(player_id=2, name="Bob")
        game_state = GameState()
        game_state.board = board
        game_state.add_player(player)

        # When: Invalid first move
        piece = player.get_piece("I2")
        result = BlokusRules.validate_move(game_state, player.player_id, piece, 10, 10)

        # Then: Error message includes correct corner
        assert result.is_valid is False
        assert "0" in result.reason and "19" in result.reason
        assert "corner" in result.reason.lower()

    def test_corner_rule_with_large_piece(self):
        """Contract: Large piece must still touch corner on first move.

        Given: Empty board
        When: Large piece (e.g., X5) is first move
        Then: At least one square must be in corner
        """
        # Given: Empty board
        board = Board()
        player = Player(player_id=1, name="Alice")
        game_state = GameState()
        game_state.board = board
        game_state.add_player(player)

        # When: L4 piece placed with corner at (0, 0)
        piece = player.get_piece("L4")
        result = BlokusRules.validate_move(game_state, player.player_id, piece, 0, 0)

        # Then: Valid (L4 at (0,0) covers (0,0))
        assert result.is_valid is True

    def test_corner_rule_prevents_missed_corner(self):
        """Contract: First move that doesn't touch corner is rejected.

        Given: Empty board and player
        When: First move is attempted without touching corner
        Then: Move is rejected with clear error
        """
        # Given: Empty board
        board = Board()
        player = Player(player_id=1, name="Alice")
        game_state = GameState()
        game_state.board = board
        game_state.add_player(player)

        # When: First move at position far from corner
        piece = player.get_piece("I2")
        result = BlokusRules.validate_move(game_state, player.player_id, piece, 3, 3)

        # Then: Invalid with descriptive error
        assert result.is_valid is False
        assert len(result.reason) > 0
        assert "corner" in result.reason.lower()
