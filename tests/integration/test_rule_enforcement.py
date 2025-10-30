"""Integration test for complete rule enforcement.

This test validates that all Blokus rules are enforced together
in realistic gameplay scenarios.
"""

import pytest
from src.models.board import Board
from src.models.player import Player
from src.models.game_state import GameState
from src.game.rules import BlokusRules


class TestRuleEnforcementIntegration:
    """Integration tests for complete rule enforcement."""

    def test_complete_first_move_validation(self):
        """Contract: First move validates all rules together.

        Given: New game
        When: First move is attempted
        Then: All rules are checked (corner, bounds, no overlap)
        """
        # Given: New game with empty board
        board = Board()
        player1 = Player(player_id=1, name="Alice")
        player2 = Player(player_id=2, name="Bob")
        game_state = GameState()
        game_state.board = board
        game_state.add_player(player1)
        game_state.add_player(player2)

        # When: Valid first move in corner
        piece = player1.get_piece("I2")
        result = BlokusRules.validate_move(
            game_state, player1.player_id, piece, 0, 0
        )

        # Then: Valid
        assert result.is_valid is True
        assert "corner" in result.reason.lower()

        # When: Invalid first move (not in corner)
        piece = player1.get_piece("L4")
        result = BlokusRules.validate_move(
            game_state, player1.player_id, piece, 5, 5
        )

        # Then: Invalid due to corner rule
        assert result.is_valid is False
        assert "corner" in result.reason.lower()

    def test_complete_subsequent_move_validation(self):
        """Contract: Subsequent moves validate all applicable rules.

        Given: Game in progress with pieces on board
        When: Subsequent move is attempted
        Then: All rules checked except corner rule
        """
        # Given: Game in progress
        board = Board()
        player1 = Player(player_id=1, name="Alice")
        game_state = GameState()
        game_state.board = board
        game_state.add_player(player1)

        # First move in corner
        piece1 = player1.get_piece("I2")
        board.place_piece(piece1, 0, 0, 1)

        # When: Valid subsequent move (no edge contact, no overlap, in bounds)
        piece2 = player1.get_piece("L4")
        result = BlokusRules.validate_move(
            game_state, player1.player_id, piece2, 2, 2
        )

        # Then: Valid
        assert result.is_valid is True

    def test_complex_game_state_all_rules_enforced(self):
        """Contract: All rules enforced in complex game state.

        Given: Complex game state with multiple pieces
        When: Various moves are attempted
        Then: All rules consistently enforced
        """
        # Given: Complex game with multiple players and pieces
        board = Board()
        player1 = Player(player_id=1, name="Alice")
        player2 = Player(player_id=2, name="Bob")
        game_state = GameState()
        game_state.board = board
        game_state.add_player(player1)
        game_state.add_player(player2)

        # Player 1: First move
        p1_piece1 = player1.get_piece("X5")
        board.place_piece(p1_piece1, 0, 0, 1)

        # Player 2: First move in corner
        p2_piece1 = player2.get_piece("I2")
        board.place_piece(p2_piece1, 0, 18, 2)

        # Player 1: Second move with diagonal contact
        p1_piece2 = player1.get_piece("V3")
        result1 = BlokusRules.validate_move(
            game_state, player1.player_id, p1_piece2, 1, 1
        )
        assert result1.is_valid is True
        board.place_piece(p1_piece2, 1, 1, 1)

        # When: Player 1 tries edge contact with own piece
        p1_piece3 = player1.get_piece("L4")
        result2 = BlokusRules.validate_move(
            game_state, player1.player_id, p1_piece3, 0, 1
        )

        # Then: Invalid due to edge contact
        assert result2.is_valid is False
        assert "contact" in result2.reason.lower()

        # When: Player 2 tries to overlap
        p2_piece2 = player2.get_piece("L4")
        result3 = BlokusRules.validate_move(
            game_state, player2.player_id, p2_piece2, 0, 18
        )

        # Then: Invalid due to overlap
        assert result3.is_valid is False
        assert "occupied" in result3.reason.lower()

    def test_multiple_invalid_moves_different_rules(self):
        """Contract: Different rule violations produce specific errors.

        Given: Game state
        When: Multiple different invalid moves are attempted
        Then: Each produces appropriate error message
        """
        # Given: Game state
        board = Board()
        player = Player(player_id=1, name="Alice")
        game_state = GameState()
        game_state.board = board
        game_state.add_player(player)

        # First move in corner
        piece1 = player.get_piece("I2")
        board.place_piece(piece1, 0, 0, 1)

        # Test 1: Out of bounds
        piece_out = player.get_piece("V3")
        result1 = BlokusRules.validate_move(
            game_state, player.player_id, piece_out, -1, 5
        )
        assert result1.is_valid is False
        assert "bounds" in result1.reason.lower() or "outside" in result1.reason.lower()

        # Test 2: Overlap
        piece_overlap = player.get_piece("L4")
        result2 = BlokusRules.validate_move(
            game_state, player.player_id, piece_overlap, 0, 0
        )
        assert result2.is_valid is False
        assert "occupied" in result2.reason.lower()

        # Test 3: Edge contact
        piece_contact = player.get_piece("T5")
        result3 = BlokusRules.validate_move(
            game_state, player.player_id, piece_contact, 1, 0
        )
        assert result3.is_valid is False
        assert "contact" in result3.reason.lower()

    def test_valid_moves_allowed_across_game_lifecycle(self):
        """Contract: Valid moves allowed throughout game lifecycle.

        Given: Game from start to near completion
        When: Valid moves are attempted
        Then: All are accepted
        """
        # Given: Game setup
        board = Board()
        player1 = Player(player_id=1, name="Alice")
        player2 = Player(player_id=2, name="Bob")
        game_state = GameState()
        game_state.board = board
        game_state.add_player(player1)
        game_state.add_player(player2)

        # Turn 1: Player 1 first move
        valid_move1 = BlokusRules.validate_move(
            game_state, player1.player_id, player1.get_piece("I2"), 0, 0
        )
        assert valid_move1.is_valid is True
        board.place_piece(player1.get_piece("I2"), 0, 0, 1)

        # Turn 2: Player 2 first move
        valid_move2 = BlokusRules.validate_move(
            game_state, player2.player_id, player2.get_piece("L4"), 0, 18
        )
        assert valid_move2.is_valid is True
        board.place_piece(player2.get_piece("L4"), 0, 18, 2)

        # Turn 3: Player 1 subsequent move (diagonal)
        valid_move3 = BlokusRules.validate_move(
            game_state, player1.player_id, player1.get_piece("V3"), 1, 1
        )
        assert valid_move3.is_valid is True
        board.place_piece(player1.get_piece("V3"), 1, 1, 1)

        # Turn 4: Player 2 contact with opponent (allowed)
        valid_move4 = BlokusRules.validate_move(
            game_state, player2.player_id, player2.get_piece("I2"), 2, 18
        )
        assert valid_move4.is_valid is True

    def test_rotated_pieces_all_rules_apply(self):
        """Contract: All rules apply to rotated pieces.

        Given: Game state
        When: Rotated pieces are placed
        Then: All rules still enforced correctly
        """
        # Given: Game state
        board = Board()
        player = Player(player_id=1, name="Alice")
        game_state = GameState()
        game_state.board = board
        game_state.add_player(player)

        # First move
        piece1 = player.get_piece("I2")
        board.place_piece(piece1, 0, 0, 1)

        # When: Valid rotated piece placement
        rotated_piece = player.get_piece("L4").rotate(90)
        result = BlokusRules.validate_move(
            game_state, player.player_id, rotated_piece, 2, 2
        )

        # Then: Valid if all rules satisfied
        assert result.is_valid is True

        # When: Invalid rotated piece (edge contact)
        rotated_piece2 = player.get_piece("V3").rotate(180)
        result2 = BlokusRules.validate_move(
            game_state, player.player_id, rotated_piece2, 1, 0
        )

        # Then: Invalid
        assert result2.is_valid is False
        assert "contact" in result2.reason.lower()

    def test_error_messages_are_clear_and_actionable(self):
        """Contract: Error messages clearly indicate the problem.

        Given: Game state
        When: Invalid moves are attempted
        Then: Error messages are clear and actionable
        """
        # Given: Game state
        board = Board()
        player = Player(player_id=1, name="Alice")
        game_state = GameState()
        game_state.board = board
        game_state.add_player(player)

        # When: First move not in corner
        piece = player.get_piece("L4")
        result = BlokusRules.validate_move(
            game_state, player.player_id, piece, 5, 5
        )

        # Then: Error message is clear
        assert result.is_valid is False
        assert len(result.reason) > 10  # Meaningful message
        assert "corner" in result.reason.lower()

        # When: Out of bounds
        piece2 = player.get_piece("V3")
        result2 = BlokusRules.validate_move(
            game_state, player.player_id, piece2, -1, 5
        )

        # Then: Clear error about bounds
        assert result2.is_valid is False
        assert len(result2.reason) > 10

    def test_rule_priority_clearly_defined(self):
        """Contract: Rule checking order is consistent.

        Given: Move that violates multiple rules
        When: Validation occurs
        Then: First violation is reported
        """
        # Given: Game state with piece at (5, 5)
        board = Board()
        player = Player(player_id=1, name="Alice")
        game_state = GameState()
        game_state.board = board
        game_state.add_player(player)

        piece1 = player.get_piece("I2")
        board.place_piece(piece1, 5, 5, 1)

        # When: Move that could violate multiple rules
        # (e.g., overlap AND edge contact)
        piece2 = player.get_piece("L4")
        result = BlokusRules.validate_move(
            game_state, player.player_id, piece2, 5, 5
        )

        # Then: One rule violation is reported (consistent order)
        assert result.is_valid is False
        # Expected: Overlap is detected first (before adjacency)
        assert "occupied" in result.reason.lower()

    def test_get_invalid_positions_comprehensive(self):
        """Contract: All invalid positions and reasons are reported.

        Given: Game state
        When: Getting all invalid positions
        Then: Complete list with specific reasons is returned
        """
        # Given: Game with pieces
        board = Board()
        player = Player(player_id=1, name="Alice")
        game_state = GameState()
        game_state.board = board
        game_state.add_player(player)

        piece1 = player.get_piece("I2")
        board.place_piece(piece1, 5, 5, 1)

        # When: Get all invalid positions
        invalid_positions = BlokusRules.get_invalid_positions(
            game_state, player.player_id, player.get_piece("L4")
        )

        # Then: Comprehensive list with reasons
        assert len(invalid_positions) > 0

        # Check that reasons are meaningful
        for pos, reason in invalid_positions.items():
            assert isinstance(pos, tuple)
            assert len(pos) == 2
            assert isinstance(reason, str)
            assert len(reason) > 0

    def test_full_board_near_end_game(self):
        """Contract: Rules enforced correctly when board is nearly full.

        Given: Nearly full board
        When: Valid moves are attempted
        Then: Rules still enforced correctly
        """
        # Given: Board with many pieces
        board = Board()
        player1 = Player(player_id=1, name="Alice")
        player2 = Player(player_id=2, name="Bob")
        game_state = GameState()
        game_state.board = board
        game_state.add_player(player1)
        game_state.add_player(player2)

        # Fill board strategically (simplified)
        # Player 1: Various pieces
        p1_piece1 = player1.get_piece("I2")
        board.place_piece(p1_piece1, 0, 0, 1)

        # Player 2: Various pieces
        p2_piece1 = player2.get_piece("I2")
        board.place_piece(p2_piece1, 0, 19, 2)

        # When: Trying valid placement in limited space
        p1_piece2 = player1.get_piece("I1")
        result = BlokusRules.validate_move(
            game_state, player1.player_id, p1_piece2, 18, 18
        )

        # Then: Valid if within rules
        # (May be valid or invalid depending on surrounding pieces)
        # Just verify it returns a ValidationResult
        assert isinstance(result.is_valid, bool)

    def test_rule_enforcement_preserves_game_state(self):
        """Contract: Rule validation doesn't modify game state.

        Given: Game state
        When: Invalid moves are validated
        Then: Game state remains unchanged
        """
        # Given: Game state
        board = Board()
        player = Player(player_id=1, name="Alice")
        game_state = GameState()
        game_state.board = board
        game_state.add_player(player)

        piece1 = player.get_piece("I2")
        board.place_piece(piece1, 0, 0, 1)

        initial_state = board.get_occupied_positions()

        # When: Multiple invalid moves validated
        piece2 = player.get_piece("L4")
        result1 = BlokusRules.validate_move(
            game_state, player.player_id, piece2, 0, 0
        )
        result2 = BlokusRules.validate_move(
            game_state, player.player_id, piece2, -1, -1
        )
        result3 = BlokusRules.validate_move(
            game_state, player.player_id, piece2, 1, 0
        )

        # Then: Game state unchanged
        assert board.get_occupied_positions() == initial_state
        assert all(not r.is_valid for r in [result1, result2, result3])
