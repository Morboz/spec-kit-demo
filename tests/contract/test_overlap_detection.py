"""Contract tests for piece overlap detection.

This test validates that pieces cannot overlap with any existing
pieces on the board, regardless of player.
"""

from blokus_game.game.rules import BlokusRules
from blokus_game.models.board import Board
from blokus_game.models.game_state import GameState
from blokus_game.models.player import Player


class TestOverlapDetection:
    """Contract tests for overlap validation."""

    def test_piece_without_overlap_is_valid(self):
        """Contract: Piece that doesn't overlap is valid.

        Given: Board with existing pieces
        When: New piece is placed in empty space
        Then: Move is valid
        """
        # Given: Board with pieces
        board = Board()
        player = Player(player_id=1, name="Alice")
        game_state = GameState()
        game_state.board = board
        game_state.add_player(player)

        # Place first piece
        piece1 = player.get_piece("I2")
        board.place_piece(piece1, 5, 5, 1)
        piece1.place_at(5, 5)

        # When: Second piece placed with diagonal contact at (7, 6)
        # L4 piece: [(0, 0), (0, 1), (0, 2), (1, 2)]
        # At (7, 6): positions are (7, 6), (7, 7), (7, 8), (8, 8)
        # Diagonal contact with I2 at (5, 5): (8, 8) touches (7, 7) diagonally ✓
        piece2 = player.get_piece("L4")
        result = BlokusRules.validate_move(game_state, player.player_id, piece2, 7, 6)

        # Then: Valid
        assert result.is_valid is True

    def test_overlap_with_own_piece_is_invalid(self):
        """Contract: Overlap with own piece is invalid.

        Given: Player has placed a piece
        When: New piece overlaps own piece
        Then: Move is invalid
        """
        # Given: Player with placed piece
        board = Board()
        player = Player(player_id=1, name="Alice")
        game_state = GameState()
        game_state.board = board
        game_state.add_player(player)

        # Place first piece at (5, 5) and (5, 6)
        piece1 = player.get_piece("I2")
        board.place_piece(piece1, 5, 5, 1)

        # When: Second piece tries to overlap at (5, 5)
        piece2 = player.get_piece("V3")
        result = BlokusRules.validate_move(game_state, player.player_id, piece2, 5, 5)

        # Then: Invalid
        assert result.is_valid is False
        assert "occupied" in result.reason.lower()

    def test_overlap_with_opponent_piece_is_invalid(self):
        """Contract: Overlap with opponent piece is invalid.

        Given: Two players with pieces on board
        When: Player tries to overlap opponent's piece
        Then: Move is invalid
        """
        # Given: Two players
        board = Board()
        player1 = Player(player_id=1, name="Alice")
        player2 = Player(player_id=2, name="Bob")
        game_state = GameState()
        game_state.board = board
        game_state.add_player(player1)
        game_state.add_player(player2)

        # Player 1 places piece
        piece1 = player1.get_piece("I2")
        board.place_piece(piece1, 10, 10, 1)
        piece1.place_at(10, 10)

        # When: Player 2 tries to overlap
        piece2 = player2.get_piece("L4")
        result = BlokusRules.validate_move(
            game_state, player2.player_id, piece2, 10, 10
        )

        # Then: Invalid
        assert result.is_valid is False
        assert "occupied" in result.reason.lower()

    def test_partial_overlap_is_invalid(self):
        """Contract: Even partial overlap is invalid.

        Given: Board with a piece
        When: New piece overlaps at even one square
        Then: Move is invalid
        """
        # Given: Board with piece
        board = Board()
        player = Player(player_id=1, name="Alice")
        game_state = GameState()
        game_state.board = board
        game_state.add_player(player)

        # Place X5 piece at (5, 5)
        piece1 = player.get_piece("X5")
        board.place_piece(piece1, 5, 5, 1)
        piece1.place_at(5, 5)

        # When: I2 piece tries to overlap at one square
        piece2 = player.get_piece("I2")
        result = BlokusRules.validate_move(game_state, player.player_id, piece2, 5, 5)

        # Then: Invalid
        assert result.is_valid is False

    def test_adjacent_without_overlap_is_valid(self):
        """Contract: Pieces adjacent without overlapping are valid.

        Given: Board with a piece
        When: New piece is placed adjacent (not overlapping)
        Then: Move is valid
        """
        # Given: Board with piece
        board = Board()
        player = Player(player_id=1, name="Alice")
        game_state = GameState()
        game_state.board = board
        game_state.add_player(player)

        # Place first piece at (5, 5)
        piece1 = player.get_piece("I2")
        board.place_piece(piece1, 5, 5, 1)
        piece1.place_at(5, 5)

        # When: Second piece placed with diagonal contact at (7, 6)
        # V3 piece: [(0, 0), (1, 0), (1, 1)]
        # At (7, 6): positions are (7, 6), (8, 6), (8, 7)
        # Diagonal contact with I2 at (5, 5): (8, 7) touches (7, 6) diagonally ✓
        piece2 = player.get_piece("V3")
        result = BlokusRules.validate_move(game_state, player.player_id, piece2, 7, 6)

        # Then: Valid (adjacent but not overlapping)
        assert result.is_valid is True

    def test_diagonal_without_overlap_is_valid(self):
        """Contract: Pieces diagonally adjacent without overlapping are valid.

        Given: Board with a piece
        When: New piece is placed diagonally adjacent
        Then: Move is valid
        """
        # Given: Board with piece
        board = Board()
        player = Player(player_id=1, name="Alice")
        game_state = GameState()
        game_state.board = board
        game_state.add_player(player)

        # Place first piece at (5, 5)
        piece1 = player.get_piece("I2")
        board.place_piece(piece1, 5, 5, 1)
        piece1.place_at(5, 5)

        # When: Second piece with diagonal contact at (7, 6)
        # L4 piece: [(0, 0), (0, 1), (0, 2), (1, 2)]
        # At (7, 6): positions are (7, 6), (7, 7), (7, 8), (8, 8)
        # Diagonal contact with I2 at (5, 5): (8, 8) touches (7, 7) diagonally ✓
        piece2 = player.get_piece("L4")
        result = BlokusRules.validate_move(game_state, player.player_id, piece2, 7, 6)

        # Then: Valid (diagonal, not overlapping)
        assert result.is_valid is True

    def test_overlap_error_message_includes_position(self):
        """Contract: Overlap error message specifies the position.

        Given: Board with a piece at known position
        When: Overlap is attempted
        Then: Error message includes the overlapping position
        """
        # Given: Board with piece at (10, 10)
        board = Board()
        player = Player(player_id=1, name="Alice")
        game_state = GameState()
        game_state.board = board
        game_state.add_player(player)

        piece1 = player.get_piece("I2")
        board.place_piece(piece1, 10, 10, 1)
        piece1.place_at(10, 10)

        # When: Overlap at (10, 10)
        piece2 = player.get_piece("V3")
        result = BlokusRules.validate_move(game_state, player.player_id, piece2, 10, 10)

        # Then: Error includes position
        assert result.is_valid is False
        assert "10" in result.reason and "occupied" in result.reason.lower()

    def test_multiple_overlapping_positions_detected(self):
        """Contract: Multiple overlaps are detected (first one reported).

        Given: Board with multiple occupied positions
        When: Piece overlaps multiple positions
        Then: Overlap is detected (may report first or all)
        """
        # Given: Board with L-shaped piece
        board = Board()
        player = Player(player_id=1, name="Alice")
        game_state = GameState()
        game_state.board = board
        game_state.add_player(player)

        # Place L4 piece
        piece1 = player.get_piece("L4")
        board.place_piece(piece1, 10, 10, 1)
        piece1.place_at(10, 10)

        # When: New L4 piece overlaps at multiple points
        piece2 = player.get_piece("L4")
        result = BlokusRules.validate_move(game_state, player.player_id, piece2, 10, 10)

        # Then: Overlap detected
        assert result.is_valid is False

    def test_touching_corner_is_not_overlap(self):
        """Contract: Pieces touching at corners are not overlapping.

        Given: Board with a piece
        When: New piece touches at corner only
        Then: Move is valid (not overlap)
        """
        # Given: Board with piece
        board = Board()
        player = Player(player_id=1, name="Alice")
        game_state = GameState()
        game_state.board = board
        game_state.add_player(player)

        # Place first piece
        piece1 = player.get_piece("I2")
        board.place_piece(piece1, 5, 5, 1)
        piece1.place_at(5, 5)

        # When: Second piece touches at corner with diagonal contact (7, 6)
        # V3 piece: [(0, 0), (1, 0), (1, 1)]
        # At (7, 6): positions are (7, 6), (8, 6), (8, 7)
        # Diagonal contact with I2 at (5, 5): (8, 7) touches (7, 6) diagonally ✓
        piece2 = player.get_piece("V3")
        result = BlokusRules.validate_move(game_state, player.player_id, piece2, 7, 6)

        # Then: Valid (corner touch, not overlap)
        assert result.is_valid is True

    def test_complex_shape_overlap_detection(self):
        """Contract: Complex shapes detect overlap correctly.

        Given: Board with complex piece
        When: New complex piece overlaps
        Then: Overlap is detected
        """
        # Given: Board with X5 piece
        board = Board()
        player = Player(player_id=1, name="Alice")
        game_state = GameState()
        game_state.board = board
        game_state.add_player(player)

        # Place X5
        piece1 = player.get_piece("X5")
        board.place_piece(piece1, 10, 10, 1)
        piece1.place_at(10, 10)

        # When: L4 piece tries to overlap
        piece2 = player.get_piece("L4")
        result = BlokusRules.validate_move(game_state, player.player_id, piece2, 10, 10)

        # Then: Overlap detected
        assert result.is_valid is False

    def test_all_occupied_positions_tracked(self):
        """Contract: Board correctly tracks all occupied positions.

        Given: Board with multiple pieces from multiple players
        When: Checking occupied positions
        Then: All occupied positions are tracked
        """
        # Given: Multiple players with pieces
        board = Board()
        player1 = Player(player_id=1, name="Alice")
        player2 = Player(player_id=2, name="Bob")
        game_state = GameState()
        game_state.board = board
        game_state.add_player(player1)
        game_state.add_player(player2)

        # Place pieces with diagonal contact
        p1_piece = player1.get_piece("I2")
        board.place_piece(p1_piece, 5, 5, 1)
        p1_piece.place_at(5, 5)

        # Player 2 piece with diagonal contact to player 1
        p2_piece = player2.get_piece("V3")
        board.place_piece(p2_piece, 7, 6, 2)
        p2_piece.place_at(7, 6)

        # When: Check occupied positions
        occupied = board.get_occupied_positions()

        # Then: All positions are occupied
        assert (5, 5) in occupied  # I2 first square
        assert (6, 5) in occupied  # I2 second square (vertical)
        assert (7, 6) in occupied  # V3 first square
        assert (8, 6) in occupied  # V3 second square
        assert (8, 7) in occupied  # V3 third square

    def test_overlap_prevents_piece_placement(self):
        """Contract: Overlap prevents piece from being placed.

        Given: Board with pieces
        When: Overlapping placement is attempted
        Then: No squares are placed
        """
        # Given: Board with piece
        board = Board()
        player = Player(player_id=1, name="Alice")
        game_state = GameState()
        game_state.board = board
        game_state.add_player(player)

        # Place first piece
        piece1 = player.get_piece("I2")
        board.place_piece(piece1, 5, 5, 1)
        piece1.place_at(5, 5)

        initial_occupied = len(board.get_occupied_positions())

        # When: Try overlapping placement
        piece2 = player.get_piece("L4")
        result = BlokusRules.validate_move(game_state, player.player_id, piece2, 5, 5)

        # Then: Placement prevented, no new squares added
        assert result.is_valid is False
        assert len(board.get_occupied_positions()) == initial_occupied

    def test_different_sized_pieces_overlap(self):
        """Contract: Overlap detection works for any size piece.

        Given: Board with pieces of various sizes
        When: Overlap occurs with different sized pieces
        Then: Overlap is always detected
        """
        # Given: Board with different sized pieces
        board = Board()
        player = Player(player_id=1, name="Alice")
        game_state = GameState()
        game_state.board = board
        game_state.add_player(player)

        # Place I5 piece
        piece1 = player.get_piece("I5")
        board.place_piece(piece1, 5, 5, 1)
        piece1.place_at(5, 5)

        # When: Small piece tries to overlap
        piece2 = player.get_piece("I1")
        result = BlokusRules.validate_move(game_state, player.player_id, piece2, 7, 5)

        # Then: Overlap detected
        assert result.is_valid is False

    def test_rotated_piece_overlap(self):
        """Contract: Overlap detection works for rotated pieces.

        Given: Board with pieces
        When: Rotated piece overlaps
        Then: Overlap is detected
        """
        # Given: Board with piece
        board = Board()
        player = Player(player_id=1, name="Alice")
        game_state = GameState()
        game_state.board = board
        game_state.add_player(player)

        # Place piece
        piece1 = player.get_piece("I2")
        board.place_piece(piece1, 5, 5, 1)
        piece1.place_at(5, 5)

        # When: Rotated piece overlaps
        piece2 = player.get_piece("L4").rotate(90)
        result = BlokusRules.validate_move(game_state, player.player_id, piece2, 5, 5)

        # Then: Overlap detected
        assert result.is_valid is False
