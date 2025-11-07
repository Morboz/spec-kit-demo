"""Integration test for Phase 8 - Complete Rule Enforcement

This test verifies that all Phase 8 rule enforcement components work together:
- Rules validator with comprehensive error messages
- Error display UI component
- Placement preview with real-time validation
- Complete integration in game flow

This test validates the complete Phase 8 implementation.
"""

from unittest.mock import Mock

from src.game.rules import BlokusRules, ValidationResult
from src.models.board import Board
from src.models.game_state import GameState
from src.models.player import Player
from src.ui.error_display import ErrorDisplay
from src.ui.placement_preview import PlacementPreview


class TestPhase8CompleteRuleEnforcement:
    """Integration tests for complete Phase 8 rule enforcement."""

    def test_error_display_shows_validation_errors(self):
        """Contract: ErrorDisplay shows validation errors with proper formatting.

        Given: ErrorDisplay component
        When: Validation error is shown
        Then: Error is displayed with appropriate formatting
        """
        # Given: Mock parent and ErrorDisplay
        mock_parent = Mock()
        error_display = ErrorDisplay(mock_parent)

        # When: Show validation error
        error_display.show_validation_error(
            "First move must include corner position (0, 0)", "corner"
        )

        # Then: Error is displayed
        assert "Invalid move" in error_display.error_message_var.get()
        assert "corner" in error_display.error_message_var.get()

    def test_placement_preview_validates_in_real_time(self):
        """Contract: PlacementPreview validates moves in real-time.

        Given: Game state with board and player
        When: Preview is activated and mouse moves over invalid position
        Then: Preview shows invalid placement
        """
        # Given: Game setup
        board = Board()
        player = Player(player_id=1, name="Alice")
        game_state = GameState()
        game_state.board = board
        game_state.add_player(player)

        # First move in corner
        first_piece = player.get_piece("I2")
        board.place_piece(first_piece, 0, 0, 1)
        first_piece.place_at(0, 0)

        # Mock canvas
        mock_canvas = Mock()
        mock_canvas.create_rectangle = Mock(return_value=123)
        mock_canvas.delete = Mock()

        # Create PlacementPreview
        preview = PlacementPreview(mock_canvas, game_state)

        # When: Activate preview for second move
        second_piece = player.get_piece("L4")
        preview.activate(second_piece, 1)

        # Simulate mouse move over valid position
        # Board coordinates: (5, 5) should be valid (no overlap, no edge contact)
        result = preview.get_validation_result(5, 5)

        # Then: Result is ValidationResult
        assert isinstance(result, ValidationResult)
        assert result.is_valid is True

    def test_placement_preview_rejects_invalid_moves(self):
        """Contract: PlacementPreview rejects invalid moves.

        Given: Game state with placed pieces
        When: Preview shows invalid placement
        Then: Preview indicates invalid move
        """
        # Given: Game with placed pieces
        board = Board()
        player = Player(player_id=1, name="Alice")
        game_state = GameState()
        game_state.board = board
        game_state.add_player(player)

        # First piece at (0, 0)
        first_piece = player.get_piece("I2")
        board.place_piece(first_piece, 0, 0, 1)
        first_piece.place_at(0, 0)

        # Mock canvas
        mock_canvas = Mock()
        mock_canvas.create_rectangle = Mock(return_value=456)
        mock_canvas.delete = Mock()

        preview = PlacementPreview(mock_canvas, game_state)
        preview.activate(player.get_piece("V3"), 1)

        # When: Check invalid position (overlap at 0, 0)
        result = preview.get_validation_result(0, 0)

        # Then: Invalid due to overlap
        assert isinstance(result, ValidationResult)
        assert result.is_valid is False
        assert "occupied" in result.reason.lower()

    def test_rules_validator_provides_comprehensive_error_messages(self):
        """Contract: Rules validator provides comprehensive, actionable error messages.

        Given: Various invalid move scenarios
        When: Each move is validated
        Then: Each returns specific, actionable error message
        """
        # Given: Game state
        board = Board()
        player = Player(player_id=1, name="Alice")
        game_state = GameState()
        game_state.board = board
        game_state.add_player(player)

        # Test 1: Corner rule violation
        piece1 = player.get_piece("I2")
        result1 = BlokusRules.validate_move(game_state, 1, piece1, 5, 5)
        assert not result1.is_valid
        assert "corner" in result1.reason.lower()
        assert "0, 0" in result1.reason

        # Test 2: Bounds violation
        result2 = BlokusRules.validate_move(game_state, 1, piece1, -1, 5)
        assert not result2.is_valid
        assert "bounds" in result2.reason.lower() or "outside" in result2.reason.lower()

        # Test 3: Overlap violation (after first move)
        board.place_piece(piece1, 0, 0, 1)
        piece1.place_at(0, 0)

        piece2 = player.get_piece("L4")
        result3 = BlokusRules.validate_move(game_state, 1, piece2, 0, 0)
        assert not result3.is_valid
        assert "occupied" in result3.reason.lower()

        # Test 4: Adjacency violation
        result4 = BlokusRules.validate_move(game_state, 1, piece2, 1, 0)
        assert not result4.is_valid
        assert "contact" in result4.reason.lower()

    def test_get_invalid_positions_comprehensive(self):
        """Contract: get_invalid_positions returns all invalid positions with reasons.

        Given: Game state with pieces
        When: Getting all invalid positions
        Then: Returns comprehensive list with specific reasons
        """
        # Given: Game with pieces
        board = Board()
        player = Player(player_id=1, name="Alice")
        game_state = GameState()
        game_state.board = board
        game_state.add_player(player)

        # Place first piece
        piece1 = player.get_piece("I2")
        board.place_piece(piece1, 0, 0, 1)
        piece1.place_at(0, 0)

        # When: Get invalid positions for new piece
        piece2 = player.get_piece("L4")
        invalid_positions = BlokusRules.get_invalid_positions(game_state, 1, piece2)

        # Then: Contains multiple invalid positions with reasons
        assert len(invalid_positions) > 0

        # Verify reasons are meaningful
        for pos, reason in invalid_positions.items():
            assert isinstance(pos, tuple)
            assert len(pos) == 2
            assert isinstance(reason, str)
            assert len(reason) > 0

            # Verify reason describes the violation
            reason_lower = reason.lower()
            assert (
                "corner" in reason_lower
                or "bounds" in reason_lower
                or "outside" in reason_lower
                or "occupied" in reason_lower
                or "contact" in reason_lower
            )

    def test_rule_enforcement_in_multiplayer_game(self):
        """Contract: Rule enforcement works correctly in multiplayer scenarios.

        Given: Game with multiple players
        When: Players take turns making moves
        Then: All rules enforced correctly for each player
        """
        # Given: Two players
        board = Board()
        player1 = Player(player_id=1, name="Alice")
        player2 = Player(player_id=2, name="Bob")
        game_state = GameState()
        game_state.board = board
        game_state.add_player(player1)
        game_state.add_player(player2)

        # Player 1: First move in corner
        p1_piece1 = player1.get_piece("I2")
        result1 = BlokusRules.validate_move(game_state, 1, p1_piece1, 0, 0)
        assert result1.is_valid
        board.place_piece(p1_piece1, 0, 0, 1)
        p1_piece1.place_at(0, 0)

        # Player 2: First move in their corner
        p2_piece1 = player2.get_piece("I2")
        result2 = BlokusRules.validate_move(game_state, 2, p2_piece1, 0, 19)
        assert result2.is_valid
        board.place_piece(p2_piece1, 0, 19, 2)
        p2_piece1.place_at(0, 19)

        # Player 1: Second move (valid diagonal)
        p1_piece2 = player1.get_piece("V3")
        result3 = BlokusRules.validate_move(game_state, 1, p1_piece2, 1, 1)
        assert result3.is_valid

        # Player 2: Can touch Player 1's piece (opponent contact allowed)
        p2_piece2 = player2.get_piece("L4")
        result4 = BlokusRules.validate_move(game_state, 2, p2_piece2, 1, 18)
        assert result4.is_valid

    def test_placement_preview_distinguishes_rule_types(self):
        """Contract: PlacementPreview correctly identifies rule types from messages.

        Given: Various validation results
        When: Getting rule type
        Then: Correctly identifies corner, bounds, overlap, adjacency
        """
        # Given: Preview with mock setup
        mock_canvas = Mock()
        game_state = GameState()
        preview = PlacementPreview(mock_canvas, game_state)

        # Test rule type detection
        assert preview._get_rule_type("First move must include corner") == "corner"
        assert preview._get_rule_type("Position is outside bounds") == "bounds"
        assert preview._get_rule_type("Position is occupied") == "overlap"
        assert preview._get_rule_type("Edge-to-edge contact") == "adjacency"

    def test_error_display_supports_multiple_message_types(self):
        """Contract: ErrorDisplay supports error, warning, and info messages.

        Given: ErrorDisplay component
        When: Showing different message types
        Then: Messages displayed with appropriate styling
        """
        # Given: Mock parent
        mock_parent = Mock()
        error_display = ErrorDisplay(mock_parent)

        # Test error message
        error_display.show("Error message")
        assert "Error message" == error_display.error_message_var.get()

        # Test warning message
        error_display.show_warning("Warning message")
        assert "Warning message" == error_display.message_var.get()

        # Test info message
        error_display.show_info("Info message")
        assert "Info message" == error_display.error_message_var.get()

    def test_complete_game_flow_with_rule_enforcement(self):
        """Contract: Complete game flow enforces all rules correctly.

        Given: New game
        When: Playing through multiple turns with various moves
        Then: All rules enforced, errors clearly shown
        """
        # Given: New game
        board = Board()
        player1 = Player(player_id=1, name="Alice")
        player2 = Player(player_id=2, name="Bob")
        game_state = GameState()
        game_state.board = board
        game_state.add_player(player1)
        game_state.add_player(player2)

        # Turn 1: Player 1 - Valid first move
        piece = player1.get_piece("I2")
        result = BlokusRules.validate_move(game_state, 1, piece, 0, 0)
        assert result.is_valid
        assert "corner" not in result.reason.lower() or "valid" in result.reason.lower()

        board.place_piece(piece, 0, 0, 1)
        piece.place_at(0, 0)

        # Turn 2: Player 2 - Valid first move
        piece = player2.get_piece("I2")
        result = BlokusRules.validate_move(game_state, 2, piece, 0, 19)
        assert result.is_valid

        board.place_piece(piece, 0, 19, 2)
        piece.place_at(0, 19)

        # Turn 3: Player 1 - Valid second move (diagonal)
        piece = player1.get_piece("L4")
        result = BlokusRules.validate_move(game_state, 1, piece, 1, 1)
        assert result.is_valid

        # Turn 4: Player 1 tries invalid move (edge contact) - should fail
        piece = player1.get_piece("V3")
        result = BlokusRules.validate_move(game_state, 1, piece, 0, 1)
        assert not result.is_valid
        assert "contact" in result.reason.lower()

        # Turn 5: Player 1 tries overlap - should fail
        piece = player1.get_piece("T5")
        result = BlokusRules.validate_move(game_state, 1, piece, 0, 0)
        assert not result.is_valid
        assert "occupied" in result.reason.lower()

    def test_validation_preserves_game_state(self):
        """Contract: Validation does not modify game state.

        Given: Game state
        When: Validating multiple invalid moves
        Then: Game state remains unchanged
        """
        # Given: Game state
        board = Board()
        player = Player(player_id=1, name="Alice")
        game_state = GameState()
        game_state.board = board
        game_state.add_player(player)

        # Place one piece
        piece1 = player.get_piece("I2")
        board.place_piece(piece1, 0, 0, 1)
        piece1.place_at(0, 0)

        initial_board_state = board.get_board_state()

        # When: Validate multiple invalid moves
        piece2 = player.get_piece("L4")

        result1 = BlokusRules.validate_move(game_state, 1, piece2, 0, 0)  # Overlap
        result2 = BlokusRules.validate_move(game_state, 1, piece2, -1, 0)  # Bounds
        result3 = BlokusRules.validate_move(game_state, 1, piece2, 1, 0)  # Edge contact

        # Then: All invalid
        assert not result1.is_valid
        assert not result2.is_valid
        assert not result3.is_valid

        # Then: Board state unchanged
        assert board.get_board_state() == initial_board_state
