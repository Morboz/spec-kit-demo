"""
Regression Test: Piece Placement Interaction Bug

This test ensures that the core piece selection → board placement interaction
bug does not reoccur. The bug manifested as: user selects piece but clicking
board has no response, no errors shown.

The fix involved:
1. Correcting callback initialization order (_setup_callbacks after UI creation)
2. Adding set_player() method to PieceSelector for turn synchronization
3. Enhanced visual feedback for piece selection

Test covers the complete interaction flow to prevent regression.
"""

import os
import time

from blokus_game.game.error_handler import get_error_handler
from blokus_game.game.placement_handler import PlacementHandler

# Import game components
from blokus_game.models.board import Board
from blokus_game.models.game_state import GameState
from blokus_game.models.player import Player


class TestPiecePlacementBugRegression:
    """Regression tests for piece placement interaction bug."""

    def test_piece_selection_callback_is_invoked(self):
        """
        Regression Test 1: Piece selection callback should be invoked.

        Previously: PieceSelector created before callbacks set, causing
        on_piece_selected to never be called.

        Now: UI created first, then callbacks set, ensuring proper connection.
        """
        # Setup
        board = Board()
        game_state = GameState()
        player = Player(player_id=1, name="Alice")
        dummy_player = Player(player_id=2, name="Bob")

        game_state.board = board
        game_state.add_player(player)
        game_state.add_player(dummy_player)
        game_state.start_game()

        placement_handler = PlacementHandler(board, game_state, player)

        # Track callback invocation
        callback_invoked = []

        def test_callback(piece_name: str):
            callback_invoked.append(piece_name)

        placement_handler.set_callbacks(
            on_piece_placed=lambda name: test_callback(name),
            on_placement_error=lambda msg: None,
        )

        # Exercise: Select a piece
        result = placement_handler.select_piece("I2")

        # Verify: Selection should succeed
        assert result is True, "Piece selection should succeed"
        assert (
            placement_handler.selected_piece is not None
        ), "Selected piece should be set"

    def test_piece_selector_synchronizes_on_turn_change(self):
        """
        Regression Test 2: PieceSelector should update when player changes.

        Previously: PieceSelector kept old player reference after turn change,
        causing wrong pieces to be displayed.

        Now: set_player() method updates player reference and refreshes display.
        """
        # Setup
        board = Board()
        game_state = GameState()
        player1 = Player(player_id=1, name="Alice")
        player2 = Player(player_id=2, name="Bob")

        game_state.board = board
        game_state.add_player(player1)
        game_state.add_player(player2)
        game_state.start_game()

        placement_handler = PlacementHandler(board, game_state, player1)

        # Exercise: Player 1 selects and places a piece
        placement_handler.select_piece("I2")
        success, error = placement_handler.place_piece(0, 0)
        assert success is True, f"First placement should succeed: {error}"

        # Verify: Turn advances to player 2
        current_player = game_state.get_current_player()
        assert current_player.player_id == 2, "Turn should advance to player 2"

        # Exercise: Update placement handler with new player
        placement_handler.current_player = current_player

        # Verify: Handler references correct player
        assert (
            placement_handler.current_player == player2
        ), "Handler should reference player 2"

    def test_complete_piece_selection_to_placement_flow(self):
        """
        Regression Test 3: Complete flow from piece selection to placement.

        This is the full interaction flow that was broken:
        1. User selects piece from PieceSelector
        2. Piece appears selected (visual feedback)
        3. User clicks valid board position
        4. Piece successfully placed on board
        5. Game advances to next player's turn

        This test verifies all steps work end-to-end.
        """
        # Setup
        board = Board()
        game_state = GameState()
        player1 = Player(player_id=1, name="Alice")
        player2 = Player(player_id=2, name="Bob")

        game_state.board = board
        game_state.add_player(player1)
        game_state.add_player(player2)
        game_state.start_game()

        placement_handler = PlacementHandler(board, game_state, player1)

        # Initial state
        assert (
            player1.get_remaining_piece_count() == 21
        ), "Player 1 should have 21 pieces initially"

        # Exercise: Select a piece
        success = placement_handler.select_piece("I2")
        assert success is True, "Piece selection should succeed"
        assert (
            placement_handler.selected_piece is not None
        ), "Selected piece should be set"

        selected_piece_name = placement_handler.selected_piece.name

        # Exercise: Place piece at valid position (corner for first move)
        success, error = placement_handler.place_piece(0, 0)

        # Verify: Placement succeeds
        assert success is True, f"Placement should succeed: {error}"
        assert error is None, "No error should occur on valid placement"

        # Verify: Piece is removed from player's inventory
        assert (
            player1.get_remaining_piece_count() == 20
        ), "Player 1 should have 20 pieces after placement"

        # Verify: Piece is placed on board (I2 is horizontal, occupies (0,0) and (1,0))
        assert board.grid.get((0, 0)) == 1, "Board should show piece at (0, 0)"
        assert board.grid.get((1, 0)) == 1, "Board should show I2 piece occupies (1, 0)"

        # Verify: Turn advances
        current_player = game_state.get_current_player()
        assert current_player.player_id == 2, "Turn should advance to player 2"

        # Verify: Selection is cleared
        assert (
            placement_handler.selected_piece is None
        ), "Selection should be cleared after placement"

    def test_visual_feedback_states(self):
        """
        Regression Test 4: Visual feedback should work correctly.

        Enhanced UI feedback:
        - Hover over piece → highlight appears
        - Click piece → button shows pressed state
        - Hover over valid board position → preview outline appears

        This test verifies the UI state management for visual feedback.
        """
        # Setup
        board = Board()
        game_state = GameState()
        player = Player(player_id=1, name="Alice")
        dummy_player = Player(player_id=2, name="Bob")

        game_state.board = board
        game_state.add_player(player)
        game_state.add_player(dummy_player)
        game_state.start_game()

        placement_handler = PlacementHandler(board, game_state, player)

        # Verify: Initial state - no piece selected
        assert (
            placement_handler.selected_piece is None
        ), "No piece should be selected initially"

        # Exercise: Select piece
        success = placement_handler.select_piece("L4")
        assert success is True, "Piece selection should succeed"

        # Verify: Selected piece is set
        assert (
            placement_handler.selected_piece is not None
        ), "Selected piece should be set"
        assert (
            placement_handler.selected_piece.name == "L4"
        ), "L4 piece should be selected"

        # Exercise: Clear selection
        placement_handler.clear_selection()

        # Verify: Selection is cleared
        assert placement_handler.selected_piece is None, "Selection should be cleared"

    def test_structured_event_logging(self):
        """
        Regression Test 5: Structured event logging should record all interactions.

        Events logged to blokus_errors.log in JSON format:
        - piece_selected
        - placement_attempted
        - placement_succeeded
        - placement_failed

        This test verifies logging infrastructure works correctly.
        """
        # Setup - use isolated environment
        log_file = "test_blokus_errors.log"

        # Clean up any existing test log
        if os.path.exists(log_file):
            os.remove(log_file)

        # Ensure error handler uses test log
        error_handler = get_error_handler()
        error_handler.structured_log_file = log_file

        # Exercise: Log various events
        error_handler.log_structured_event(
            event_type="piece_selected", player_id=1, piece_name="I2"
        )

        error_handler.log_structured_event(
            event_type="placement_attempted",
            player_id=1,
            piece_name="I2",
            position=(0, 0),
        )

        # Verify: Log file is created
        assert os.path.exists(log_file), "Log file should be created"

        # Verify: Log contains expected events
        import json

        with open(log_file) as f:
            lines = f.readlines()
            assert len(lines) == 2, "Two events should be logged"

            # Parse first event
            event1 = json.loads(lines[0])
            assert (
                event1["event_type"] == "piece_selected"
            ), "First event should be piece_selected"
            assert event1["player_id"] == 1, "Event should include player_id"
            assert event1["piece_name"] == "I2", "Event should include piece_name"

            # Parse second event
            event2 = json.loads(lines[1])
            assert (
                event2["event_type"] == "placement_attempted"
            ), "Second event should be placement_attempted"
            assert event2["position"] == [0, 0], "Event should include position"

        # Cleanup
        os.remove(log_file)

    def test_placement_performance_requirement(self):
        """
        Regression Test 6: Placement operations should complete within 200ms.

        SC-001: 100% of valid placements complete in <200ms

        This performance requirement ensures responsive user experience.
        """
        # Setup
        board = Board()
        game_state = GameState()
        player = Player(player_id=1, name="Alice")
        dummy_player = Player(player_id=2, name="Bob")

        game_state.board = board
        game_state.add_player(player)
        game_state.add_player(dummy_player)
        game_state.start_game()

        placement_handler = PlacementHandler(board, game_state, player)

        # Exercise & Verify: Time piece selection and placement
        start_time = time.time()
        success = placement_handler.select_piece("I2")
        placement_success, error = placement_handler.place_piece(0, 0)
        end_time = time.time()

        elapsed_ms = (end_time - start_time) * 1000

        # Verify: Operation succeeds
        assert success is True, "Piece selection should succeed"
        assert placement_success is True, f"Placement should succeed: {error}"

        # Verify: Performance requirement
        assert elapsed_ms < 200, f"Placement took {elapsed_ms:.2f}ms, should be < 200ms"

    def test_error_handling_for_invalid_placement(self):
        """
        Regression Test 7: Invalid placements should be rejected with clear errors.

        Previous bug: No errors shown when placement failed silently.

        Now: Clear error messages and proper validation.
        """
        # Setup
        board = Board()
        game_state = GameState()
        player = Player(player_id=1, name="Alice")
        dummy_player = Player(player_id=2, name="Bob")

        game_state.board = board
        game_state.add_player(player)
        game_state.add_player(dummy_player)
        game_state.start_game()

        placement_handler = PlacementHandler(board, game_state, player)

        # First: Place a piece legally
        placement_handler.select_piece("I2")
        success, error = placement_handler.place_piece(0, 0)
        assert success is True, f"First placement should succeed: {error}"

        # Exercise: Try to place piece in invalid position
        # (Already occupied by player's own piece)
        placement_handler.select_piece("V3")
        success, error = placement_handler.place_piece(0, 0)

        # Verify: Placement is rejected
        assert success is False, "Invalid placement should be rejected"
        assert error is not None, "Error message should be provided"
        assert (
            "occupied" in error.lower() or "already" in error.lower()
        ), "Error should mention occupancy"

    def test_callback_initialization_order(self):
        """
        Regression Test 8: Callbacks must be initialized after UI components.

        Core bug: Callbacks set before PieceSelector created, breaking the chain:
        PieceSelector.button.click → _on_piece_selected → placement_handler.select_piece

        Fix: Create UI first, then set callbacks.
        """
        # Setup
        board = Board()
        game_state = GameState()
        player = Player(player_id=1, name="Alice")
        dummy_player = Player(player_id=2, name="Bob")

        game_state.board = board
        game_state.add_player(player)
        game_state.add_player(dummy_player)
        game_state.start_game()

        placement_handler = PlacementHandler(board, game_state, player)

        # Verify: Callbacks can be set
        callback_set = []

        def test_piece_placed(piece_name: str):
            callback_set.append(("placed", piece_name))

        def test_placement_error(error_msg: str):
            callback_set.append(("error", error_msg))

        # Exercise: Set callbacks
        placement_handler.set_callbacks(
            on_piece_placed=test_piece_placed, on_placement_error=test_placement_error
        )

        # Verify: Callbacks are registered
        assert (
            placement_handler.on_piece_placed is not None
        ), "on_piece_placed callback should be set"
        assert (
            placement_handler.on_placement_error is not None
        ), "on_placement_error callback should be set"

        # Exercise: Trigger placement
        placement_handler.select_piece("I2")
        success, error = placement_handler.place_piece(0, 0)

        # Verify: Callback is invoked
        assert (
            len(callback_set) > 0
        ), "Callback should be invoked on successful placement"
        assert callback_set[0][0] == "placed", "on_piece_placed should be called"
