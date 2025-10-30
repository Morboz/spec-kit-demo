"""Contract tests for adjacency rule.

This test validates that pieces cannot have edge-to-edge contact with
own pieces (diagonal contact is allowed).
"""

import pytest
from src.models.board import Board
from src.models.player import Player
from src.models.piece import Piece
from src.models.game_state import GameState
from src.game.rules import BlokusRules


class TestAdjacencyRule:
    """Contract tests for adjacency validation."""

    def test_piece_with_diagonal_contact_is_valid(self):
        """Contract: Diagonal contact with own pieces is allowed.

        Given: Player has placed a piece
        When: New piece touches diagonally
        Then: Move is valid
        """
        # Given: Player has placed a piece
        board = Board()
        player = Player(player_id=1, name="Alice")
        game_state = GameState()
        game_state.board = board
        game_state.add_player(player)

        # Place first piece
        first_piece = player.get_piece("I2")
        board.place_piece(first_piece, 0, 0, 1)

        # When: Second piece touches diagonally
        second_piece = player.get_piece("V3")
        result = BlokusRules.validate_move(
            game_state, player.player_id, second_piece, 1, 1
        )

        # Then: Valid (diagonal contact allowed)
        assert result.is_valid is True

    def test_piece_with_edge_contact_is_invalid(self):
        """Contract: Edge-to-edge contact with own pieces is forbidden.

        Given: Player has placed a piece
        When: New piece touches edge-to-edge
        Then: Move is invalid
        """
        # Given: Player has placed a piece
        board = Board()
        player = Player(player_id=1, name="Alice")
        game_state = GameState()
        game_state.board = board
        game_state.add_player(player)

        # Place first piece at (0, 0) and (0, 1)
        first_piece = player.get_piece("I2")
        board.place_piece(first_piece, 0, 0, 1)

        # When: Second piece would touch edge-to-edge at (1, 0)
        second_piece = player.get_piece("V3")
        result = BlokusRules.validate_move(
            game_state, player.player_id, second_piece, 1, 0
        )

        # Then: Invalid (edge contact forbidden)
        assert result.is_valid is False
        assert "edge" in result.reason.lower() or "contact" in result.reason.lower()

    def test_piece_touching_left_edge_is_invalid(self):
        """Contract: Left edge contact with own piece is invalid.

        Given: Player has placed a piece
        When: New piece touches left edge of own piece
        Then: Move is invalid
        """
        # Given: Player has placed a piece
        board = Board()
        player = Player(player_id=1, name="Alice")
        game_state = GameState()
        game_state.board = board
        game_state.add_player(player)

        # Place first piece
        first_piece = player.get_piece("I2")
        board.place_piece(first_piece, 5, 5, 1)

        # When: Try to place piece to the left (edge contact)
        second_piece = player.get_piece("L4")
        result = BlokusRules.validate_move(
            game_state, player.player_id, second_piece, 5, 3
        )

        # Then: Invalid
        assert result.is_valid is False
        assert "contact" in result.reason.lower()

    def test_piece_touching_right_edge_is_invalid(self):
        """Contract: Right edge contact with own piece is invalid.

        Given: Player has placed a piece
        When: New piece touches right edge of own piece
        Then: Move is invalid
        """
        # Given: Player has placed a piece
        board = Board()
        player = Player(player_id=1, name="Alice")
        game_state = GameState()
        game_state.board = board
        game_state.add_player(player)

        # Place first piece
        first_piece = player.get_piece("I2")
        board.place_piece(first_piece, 5, 5, 1)

        # When: Try to place piece to the right (edge contact)
        second_piece = player.get_piece("L4")
        result = BlokusRules.validate_move(
            game_state, player.player_id, second_piece, 5, 6
        )

        # Then: Invalid
        assert result.is_valid is False
        assert "contact" in result.reason.lower()

    def test_piece_touching_top_edge_is_invalid(self):
        """Contract: Top edge contact with own piece is invalid.

        Given: Player has placed a piece
        When: New piece touches top edge of own piece
        Then: Move is invalid
        """
        # Given: Player has placed a piece
        board = Board()
        player = Player(player_id=1, name="Alice")
        game_state = GameState()
        game_state.board = board
        game_state.add_player(player)

        # Place first piece
        first_piece = player.get_piece("I2")
        board.place_piece(first_piece, 5, 5, 1)

        # When: Try to place piece above (edge contact)
        second_piece = player.get_piece("L4")
        result = BlokusRules.validate_move(
            game_state, player.player_id, second_piece, 3, 5
        )

        # Then: Invalid
        assert result.is_valid is False
        assert "contact" in result.reason.lower()

    def test_piece_touching_bottom_edge_is_invalid(self):
        """Contract: Bottom edge contact with own piece is invalid.

        Given: Player has placed a piece
        When: New piece touches bottom edge of own piece
        Then: Move is invalid
        """
        # Given: Player has placed a piece
        board = Board()
        player = Player(player_id=1, name="Alice")
        game_state = GameState()
        game_state.board = board
        game_state.add_player(player)

        # Place first piece
        first_piece = player.get_piece("I2")
        board.place_piece(first_piece, 5, 5, 1)

        # When: Try to place piece below (edge contact)
        second_piece = player.get_piece("L4")
        result = BlokusRules.validate_move(
            game_state, player.player_id, second_piece, 6, 5
        )

        # Then: Invalid
        assert result.is_valid is False
        assert "contact" in result.reason.lower()

    def test_contact_with_opponent_piece_is_allowed(self):
        """Contract: Edge contact with opponent pieces is allowed.

        Given: Two players with pieces on board
        When: Player touches opponent piece edge-to-edge
        Then: Move is valid
        """
        # Given: Two players
        board = Board()
        player1 = Player(player_id=1, name="Alice")
        player2 = Player(player_id=2, name="Bob")
        game_state = GameState()
        game_state.board = board
        game_state.add_player(player1)
        game_state.add_player(player2)

        # Player 1 places first piece
        p1_piece = player1.get_piece("I2")
        board.place_piece(p1_piece, 10, 10, 1)

        # Player 2 places piece touching player 1's piece
        p2_piece = player2.get_piece("L4")
        result = BlokusRules.validate_move(
            game_state, player2.player_id, p2_piece, 10, 12
        )

        # Then: Valid (contact with opponent allowed)
        assert result.is_valid is True

    def test_multiple_piece_contact_detection(self):
        """Contract: Any edge contact with own pieces is detected.

        Given: Player has multiple pieces
        When: New piece would touch any own piece edge-to-edge
        Then: Move is invalid
        """
        # Given: Player with multiple pieces
        board = Board()
        player = Player(player_id=1, name="Alice")
        game_state = GameState()
        game_state.board = board
        game_state.add_player(player)

        # Place first piece
        piece1 = player.get_piece("I2")
        board.place_piece(piece1, 5, 5, 1)

        # Place second piece
        piece2 = player.get_piece("V3")
        board.place_piece(piece2, 7, 7, 1)

        # When: Third piece would touch second piece edge-to-edge
        piece3 = player.get_piece("L4")
        result = BlokusRules.validate_move(
            game_state, player.player_id, piece3, 6, 7
        )

        # Then: Invalid
        assert result.is_valid is False
        assert "contact" in result.reason.lower()

    def test_partial_edge_contact_is_invalid(self):
        """Contract: Even one square with edge contact invalidates move.

        Given: Player has placed pieces
        When: New piece has even one square touching own piece edge-to-edge
        Then: Move is invalid
        """
        # Given: Player has placed a piece
        board = Board()
        player = Player(player_id=1, name="Alice")
        game_state = GameState()
        game_state.board = board
        game_state.add_player(player)

        # Place first piece
        first_piece = player.get_piece("X5")
        board.place_piece(first_piece, 5, 5, 1)

        # When: Second piece touches at one square
        second_piece = player.get_piece("I2")
        result = BlokusRules.validate_move(
            game_state, player.player_id, second_piece, 4, 5
        )

        # Then: Invalid (one edge contact)
        assert result.is_valid is False

    def test_adjacency_error_message_includes_position(self):
        """Contract: Error message specifies position of edge contact.

        Given: Player has placed a piece
        When: Invalid edge contact is attempted
        Then: Error message includes the contact position
        """
        # Given: Player has placed a piece
        board = Board()
        player = Player(player_id=1, name="Alice")
        game_state = GameState()
        game_state.board = board
        game_state.add_player(player)

        # Place first piece at (5, 5)
        piece1 = player.get_piece("I2")
        board.place_piece(piece1, 5, 5, 1)

        # When: Try edge contact at (6, 5)
        piece2 = player.get_piece("V3")
        result = BlokusRules.validate_move(
            game_state, player.player_id, piece2, 6, 5
        )

        # Then: Error includes position
        assert result.is_valid is False
        assert len(result.reason) > 0
        assert "5" in result.reason or "contact" in result.reason.lower()

    def test_no_contact_with_own_pieces_is_valid(self):
        """Contract: Piece with no contact to own pieces is valid.

        Given: Player has placed pieces
        When: New piece has no contact (not even diagonal) with own pieces
        Then: Move is valid
        """
        # Given: Player with placed pieces
        board = Board()
        player = Player(player_id=1, name="Alice")
        game_state = GameState()
        game_state.board = board
        game_state.add_player(player)

        # Place first piece
        piece1 = player.get_piece("I2")
        board.place_piece(piece1, 5, 5, 1)

        # When: Second piece is far away
        piece2 = player.get_piece("L4")
        result = BlokusRules.validate_move(
            game_state, player.player_id, piece2, 10, 10
        )

        # Then: Valid
        assert result.is_valid is True

    def test_corner_after_first_move_can_have_diagonal_contact(self):
        """Contract: After first move, diagonal contact is valid.

        Given: Player has made first move in corner
        When: Subsequent move has diagonal contact with first piece
        Then: Move is valid
        """
        # Given: Player with first move in corner
        board = Board()
        player = Player(player_id=1, name="Alice")
        game_state = GameState()
        game_state.board = board
        game_state.add_player(player)

        # First move in corner
        first_piece = player.get_piece("I2")
        board.place_piece(first_piece, 0, 0, 1)

        # When: Second move with diagonal contact
        second_piece = player.get_piece("V3")
        result = BlokusRules.validate_move(
            game_state, player.player_id, second_piece, 1, 1
        )

        # Then: Valid
        assert result.is_valid is True
