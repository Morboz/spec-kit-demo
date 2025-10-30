"""Integration test for complete piece placement workflow with UI and game logic.

This test validates that the entire piece placement process works correctly,
including piece selection, rotation, flip, validation, and placement.
"""

import pytest
from src.models.board import Board
from src.models.player import Player
from src.models.game_state import GameState
from src.game.placement_handler import PlacementHandler


class TestCompletePlacementFlow:
    """Integration tests for complete placement workflow."""

    def test_complete_piece_placement_flow(self):
        """Integration: Full piece placement from selection to board.

        Given: Game with player, board, and game state
        When: Player selects piece, rotates it, and places it
        Then: Piece is successfully placed and game state is updated
        """
        # Given: Game setup
        board = Board()
        game_state = GameState()
        player = Player(player_id=1, name="Alice")
        dummy_player = Player(player_id=2, name="Bob")  # Dummy for 2-player minimum

        game_state.board = board
        game_state.add_player(player)
        game_state.add_player(dummy_player)
        game_state.start_game()

        # Given: Placement handler
        handler = PlacementHandler(board, game_state, player)

        # When: Select a piece
        success = handler.select_piece("I2")
        assert success, "Should be able to select I2 piece"

        # Then: Piece is selected
        selected_piece = handler.get_selected_piece()
        assert selected_piece is not None
        assert selected_piece.name == "I2"

        # When: Rotate the piece
        handler.rotate_piece()
        assert handler.get_rotation_count() == 1

        # When: Place the piece in corner (valid for first move)
        success, error = handler.place_piece(0, 0)
        assert success, f"Should successfully place piece, got error: {error}"

        # Then: Piece is placed on board
        assert board.is_occupied(0, 0)
        assert board.get_occupant(0, 0) == 1
        assert board.count_player_squares(1) == 2  # I2 has 2 squares

        # Then: Player's piece inventory is updated
        assert player.get_remaining_piece_count() == 20
        assert not selected_piece.is_placed  # The reference piece, but...

        # Note: The actual piece in player's inventory should be marked as placed
        placed_pieces = player.get_placed_pieces()
        assert len(placed_pieces) == 1
        assert placed_pieces[0].name == "I2"

        # Then: Game state is updated
        assert len(game_state.get_move_history()) == 1
        move = game_state.get_move_history()[0]
        assert move["player_id"] == 1
        assert move["piece_name"] == "I2"
        assert move["row"] == 0
        assert move["col"] == 0
        assert move["rotation"] == 90

        # Then: Current player advances
        assert game_state.current_player_index == 1  # Should be on player 2

    def test_piece_placement_with_flip(self):
        """Integration: Piece placement with flip transformation.

        Given: Game setup
        When: Player selects piece, flips it, and places it
        Then: Flipped piece is placed correctly
        """
        # Given: Game setup
        board = Board()
        game_state = GameState()
        player = Player(player_id=1, name="Alice")
        dummy_player = Player(player_id=2, name="Bob")

        game_state.board = board
        game_state.add_player(player)
        game_state.add_player(dummy_player)
        game_state.start_game()

        # Given: Placement handler
        handler = PlacementHandler(board, game_state, player)

        # When: Select and flip a piece
        handler.select_piece("L4")
        handler.flip_piece()
        assert handler.is_piece_flipped()

        # When: Place the piece
        success, error = handler.place_piece(0, 0)
        assert success, f"Should successfully place flipped piece: {error}"

        # Then: Flipped piece is placed
        assert board.count_player_squares(1) == 4  # L4 has 4 squares

    def test_piece_placement_with_multiple_rotations(self):
        """Integration: Multiple rotations compose correctly.

        Given: Game setup
        When: Player rotates piece multiple times and places it
        Then: Final rotation is correct
        """
        # Given: Game setup
        board = Board()
        game_state = GameState()
        player = Player(player_id=1, name="Alice")
        dummy_player = Player(player_id=2, name="Bob")

        game_state.board = board
        game_state.add_player(player)
        game_state.add_player(dummy_player)
        game_state.start_game()

        # Given: Placement handler
        handler = PlacementHandler(board, game_state, player)

        # When: Select and rotate multiple times
        handler.select_piece("I1")
        handler.rotate_piece()  # 90 degrees
        handler.rotate_piece()  # 180 degrees
        handler.rotate_piece()  # 270 degrees

        assert handler.get_rotation_count() == 3

        # When: Place the piece
        success, error = handler.place_piece(0, 0)
        assert success, f"Should successfully place rotated piece: {error}"

        # Then: Move records correct rotation
        move = game_state.get_move_history()[0]
        assert move["rotation"] == 270  # 3 * 90

    def test_invalid_piece_placement_is_rejected(self):
        """Integration: Invalid placement is properly rejected.

        Given: Game with a piece already placed
        When: Player attempts invalid placement
        Then: Placement is rejected with appropriate error
        """
        # Given: Game with piece already placed
        board = Board()
        game_state = GameState()
        player = Player(player_id=1, name="Alice")
        dummy_player = Player(player_id=2, name="Bob")

        game_state.board = board
        game_state.add_player(player)
        game_state.add_player(dummy_player)
        game_state.start_game()

        # Place first piece
        piece1 = player.get_piece("I1")
        board.place_piece(piece1, 0, 0, 1)
        player.place_piece("I1", 0, 0)

        # Given: Placement handler
        handler = PlacementHandler(board, game_state, player)

        # When: Attempt overlapping placement
        handler.select_piece("I1")
        success, error = handler.place_piece(0, 0)

        # Then: Placement is rejected
        assert not success, "Overlapping placement should be rejected"
        assert error is not None, "Should provide error message"

    def test_second_player_can_place_after_first(self):
        """Integration: Second player can place after first player.

        Given: Game where first player has placed a piece
        When: Second player places their piece
        Then: Both players' pieces are on board correctly
        """
        # Given: Game setup
        board = Board()
        game_state = GameState()
        player1 = Player(player_id=1, name="Alice")
        player2 = Player(player_id=2, name="Bob")

        game_state.board = board
        game_state.add_player(player1)
        game_state.add_player(player2)
        game_state.start_game()

        # When: Player 1 places piece
        handler1 = PlacementHandler(board, game_state, player1)
        handler1.select_piece("I2")
        success, error = handler1.place_piece(0, 0)
        assert success, f"Player 1 should place successfully: {error}"

        # When: Update handler for player 2
        handler2 = PlacementHandler(board, game_state, player2)

        # When: Player 2 places piece in their corner
        handler2.select_piece("I2")
        success, error = handler2.place_piece(0, 19)
        assert success, f"Player 2 should place successfully: {error}"

        # Then: Both pieces are on board
        assert board.count_player_squares(1) == 2
        assert board.count_player_squares(2) == 2
        assert board.get_occupant(0, 0) == 1
        assert board.get_occupant(0, 19) == 2

        # Then: Game state shows two moves
        assert len(game_state.get_move_history()) == 2
        assert game_state.move_history[0]["player_id"] == 1
        assert game_state.move_history[1]["player_id"] == 2

    def test_placement_handler_callbacks_work(self):
        """Integration: Placement handler callbacks are called correctly.

        Given: Placement handler with callbacks
        When: Piece is placed successfully
        Then: on_piece_placed callback is called
        """
        # Given: Game setup
        board = Board()
        game_state = GameState()
        player = Player(player_id=1, name="Alice")
        dummy_player = Player(player_id=2, name="Bob")

        game_state.board = board
        game_state.add_player(player)
        game_state.add_player(dummy_player)
        game_state.start_game()

        # Given: Handler with callback tracking
        handler = PlacementHandler(board, game_state, player)
        callback_called = []

        def on_piece_placed(piece_name: str):
            callback_called.append(("placed", piece_name))

        def on_placement_error(error_msg: str):
            callback_called.append(("error", error_msg))

        handler.set_callbacks(on_piece_placed, on_placement_error)

        # When: Place piece successfully
        handler.select_piece("I1")
        success, error = handler.place_piece(0, 0)
        assert success

        # Then: Success callback was called
        assert len(callback_called) == 1
        assert callback_called[0][0] == "placed"
        assert callback_called[0][1] == "I1"

    def test_placement_handler_error_callback(self):
        """Integration: Error callback is called on invalid placement.

        Given: Placement handler with callbacks
        When: Invalid placement is attempted
        Then: on_placement_error callback is called
        """
        # Given: Game setup
        board = Board()
        game_state = GameState()
        player = Player(player_id=1, name="Alice")
        dummy_player = Player(player_id=2, name="Bob")

        game_state.board = board
        game_state.add_player(player)
        game_state.add_player(dummy_player)
        game_state.start_game()

        # Given: Handler with callback tracking
        handler = PlacementHandler(board, game_state, player)
        callback_called = []

        def on_piece_placed(piece_name: str):
            callback_called.append(("placed", piece_name))

        def on_placement_error(error_msg: str):
            callback_called.append(("error", error_msg))

        handler.set_callbacks(on_piece_placed, on_placement_error)

        # When: Attempt invalid placement (no piece selected)
        success, error = handler.place_piece(0, 0)
        assert not success

        # Then: Error callback was called
        assert len(callback_called) == 1
        assert callback_called[0][0] == "error"
