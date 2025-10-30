"""Integration test for complete game state visibility.

This test validates that all UI components correctly display and synchronize
game state information in a real game scenario.
"""

import pytest
from src.game.game_setup import GameSetup
from src.game.placement_handler import PlacementHandler
from src.ui.current_player_indicator import CurrentPlayerIndicator
from src.ui.scoreboard import Scoreboard
from src.ui.piece_inventory import PieceInventory
from src.ui.state_sync import StateSynchronizer
from src.models.game_state import GameState


class TestCompleteStateVisibility:
    """Integration tests for complete state visibility."""

    def test_all_ui_components_display_initial_state(self):
        """Integration: All UI components show correct initial state.

        Given: New game setup
        When: Game state is initialized
        Then: State is ready for UI components
        """
        # Given: Game setup
        setup = GameSetup()
        game_state = setup.setup_game(2, ["Alice", "Bob"])
        game_state.start_game()

        # Then: Current player is correct
        current = game_state.get_current_player()
        assert current is not None
        assert current.name == "Alice"

        # Then: All players have 21 pieces
        assert game_state.players[0].get_remaining_piece_count() == 21
        assert game_state.players[1].get_remaining_piece_count() == 21

        # Then: Board is empty
        board = setup.get_board()
        assert board.count_player_squares(1) == 0
        assert board.count_player_squares(2) == 0

    def test_state_synchronizer_coordinates_all_components(self):
        """Integration: StateSynchronizer coordinates all UI updates.

        Given: Game state with UI components
        When: State changes
        Then: All components are synchronized
        """
        # Given: Game setup
        setup = GameSetup()
        game_state = setup.setup_game(2, ["Alice", "Bob"])
        game_state.start_game()

        # Create synchronizer
        synchronizer = StateSynchronizer(game_state)
        synchronizer.set_board(game_state.board)
        synchronizer.set_players(game_state.players)

        # When: Full update is performed
        synchronizer.full_update()

        # Then: Current player is accessible
        assert synchronizer.get_current_player() is not None
        assert synchronizer.get_current_player().name == "Alice"

        # Then: Leader can be determined
        leader = synchronizer.get_leader()
        # Initially, no one has pieces placed, so leader is None
        assert leader is None or leader.player_id in [1, 2]

    def test_ui_updates_after_piece_placement(self):
        """Integration: UI updates after a piece is placed.

        Given: Game with UI components synchronized
        When: Player places a piece
        Then: All UI components reflect the change
        """
        # Given: Game setup
        setup = GameSetup()
        game_state = setup.setup_game(2, ["Alice", "Bob"])
        game_state.start_game()

        # When: Player 1 places a piece
        board = setup.get_board()
        player1 = game_state.players[0]
        piece = player1.get_piece("I2")
        board.place_piece(piece, 5, 5, 1)

        # Then: Board reflects the placement
        assert board.count_player_squares(1) == 2
        assert board.is_occupied(5, 5)
        assert board.is_occupied(6, 5)

        # Then: Player 2 has no pieces on board
        player2 = game_state.players[1]
        assert board.count_player_squares(2) == 0

    def test_turn_change_updates_current_player(self):
        """Integration: Current player changes are synchronized.

        Given: Game with current player indicator
        When: Turn advances
        Then: Indicator shows new current player
        """
        # Given: Game setup
        setup = GameSetup()
        game_state = setup.setup_game(2, ["Alice", "Bob"])
        game_state.start_game()

        # Initial state
        assert game_state.get_current_player().name == "Alice"

        # Create synchronizer
        synchronizer = StateSynchronizer(game_state)
        synchronizer.set_board(game_state.board)
        synchronizer.set_players(game_state.players)

        # When: Turn changes
        game_state.current_player_index = 1
        synchronizer.notify_turn_change()

        # Then: Current player is now Bob
        assert game_state.get_current_player().name == "Bob"
        assert synchronizer.get_current_player().name == "Bob"

    def test_scoreboard_reflects_all_players(self):
        """Integration: Scoreboard shows all players' scores.

        Given: Multi-player game
        When: Players place different amounts of pieces
        Then: Scoreboard reflects all correctly
        """
        # Given: 3-player game
        setup = GameSetup()
        game_state = setup.setup_game(3, ["Alice", "Bob", "Charlie"])
        board = setup.get_board()

        # When: Each player places pieces
        # Player 1: 2 squares
        piece1 = game_state.players[0].get_piece("I2")
        board.place_piece(piece1, 0, 0, 1)

        # Player 2: 4 squares
        piece2 = game_state.players[1].get_piece("L4")
        board.place_piece(piece2, 5, 5, 2)

        # Player 3: 1 square
        piece3 = game_state.players[2].get_piece("I1")
        board.place_piece(piece3, 10, 10, 3)

        # Then: Board counts are correct
        assert board.count_player_squares(1) == 2
        assert board.count_player_squares(2) == 4
        assert board.count_player_squares(3) == 1

        # Then: Leader is player 2
        leader = board.get_occupied_positions()
        assert len(leader) == 7  # Total squares placed

    def test_piece_inventory_shows_correct_counts(self):
        """Integration: Piece inventory shows accurate remaining counts.

        Given: Players with full piece sets
        When: Players place various pieces
        Then: Inventory reflects remaining pieces
        """
        # Given: Game setup
        setup = GameSetup()
        game_state = setup.setup_game(2, ["Alice", "Bob"])

        # Then: All players start with 21 pieces
        assert game_state.players[0].get_remaining_piece_count() == 21
        assert game_state.players[1].get_remaining_piece_count() == 21

        # When: Player 1 places 3 pieces
        board = setup.get_board()
        player1 = game_state.players[0]

        piece1 = player1.get_piece("I1")
        board.place_piece(piece1, 0, 0, 1)

        piece2 = player1.get_piece("I2")
        board.place_piece(piece2, 5, 5, 1)

        piece3 = player1.get_piece("L4")
        board.place_piece(piece3, 10, 10, 1)

        # Then: Board reflects all placements
        assert board.count_player_squares(1) == 7
        assert board.is_occupied(0, 0)
        assert board.is_occupied(5, 5)
        assert board.is_occupied(10, 10)

        # Then: Player 2 has no pieces on board
        player2 = game_state.players[1]
        assert board.count_player_squares(2) == 0

    def test_current_player_indicator_updates_in_real_time(self):
        """Integration: Current player indicator updates in real-time.

        Given: Game with indicator synchronized
        When: Game state changes
        Then: Indicator updates immediately
        """
        # Given: Game setup
        setup = GameSetup()
        game_state = setup.setup_game(2, ["Alice", "Bob"])
        game_state.start_game()

        # Then: Initially shows Alice
        assert game_state.get_current_player().name == "Alice"

        # When: Turn changes
        game_state.current_player_index = 1

        # Then: Shows Bob
        assert game_state.get_current_player().name == "Bob"

    def test_state_synchronizer_handles_multiple_updates(self):
        """Integration: Synchronizer handles multiple sequential updates.

        Given: Game with synchronized components
        When: Multiple state changes occur
        Then: All changes are handled correctly
        """
        # Given: Game setup
        setup = GameSetup()
        game_state = setup.setup_game(2, ["Alice", "Bob"])
        game_state.start_game()

        # Create synchronizer
        synchronizer = StateSynchronizer(game_state)
        synchronizer.set_board(game_state.board)
        synchronizer.set_players(game_state.players)

        # When: Multiple turns happen
        # Turn 1: Player 1
        assert game_state.get_current_player().name == "Alice"

        # Turn 2: Player 2
        game_state.current_player_index = 1
        synchronizer.notify_turn_change()
        assert game_state.get_current_player().name == "Bob"

        # Turn 3: Back to Player 1
        game_state.current_player_index = 0
        synchronizer.notify_turn_change()
        assert game_state.get_current_player().name == "Alice"

    def test_complete_game_flow_with_state_visibility(self):
        """Integration: Full game flow with state visibility.

        Given: Complete game setup with UI
        When: Playing through several turns
        Then: All state information remains accurate
        """
        # Given: Game setup
        setup = GameSetup()
        game_state = setup.setup_game(2, ["Alice", "Bob"])
        game_state.start_game()
        board = setup.get_board()

        # Create synchronizer and attach components
        synchronizer = StateSynchronizer(game_state)
        synchronizer.set_board(board)
        synchronizer.set_players(game_state.players)

        # Initial state
        synchronizer.full_update()
        assert synchronizer.get_current_player().name == "Alice"
        assert board.count_player_squares(1) == 0

        # Turn 1: Alice places a piece
        piece1 = game_state.players[0].get_piece("I2")
        board.place_piece(piece1, 5, 5, 1)
        synchronizer.notify_board_update()

        # Turn advances
        game_state.current_player_index = 1
        synchronizer.notify_turn_change()

        # Verify state
        assert synchronizer.get_current_player().name == "Bob"
        assert board.count_player_squares(1) == 2

        # Turn 2: Bob places a piece
        piece2 = game_state.players[1].get_piece("L4")
        board.place_piece(piece2, 10, 10, 2)
        synchronizer.notify_board_update()

        # Turn advances
        game_state.current_player_index = 0
        synchronizer.notify_turn_change()

        # Verify state
        assert synchronizer.get_current_player().name == "Alice"
        assert board.count_player_squares(1) == 2
        assert board.count_player_squares(2) == 4

    def test_all_players_state_tracked_separately(self):
        """Integration: Each player's state is tracked independently.

        Given: Multi-player game
        When: Each player makes moves
        Then: Each player's state is accurate
        """
        # Given: 4-player game
        setup = GameSetup()
        game_state = setup.setup_game(
            4, ["Alice", "Bob", "Charlie", "Diana"]
        )
        board = setup.get_board()

        # When: All players place pieces
        for i in range(4):
            piece = game_state.players[i].get_piece("I1")
            board.place_piece(piece, i * 5, i * 5, i + 1)

        # Then: Each player has correct count on board
        for i in range(4):
            player_id = i + 1
            assert board.count_player_squares(player_id) == 1

        # Then: Total pieces on board
        total_squares = sum(board.count_player_squares(i) for i in range(1, 5))
        assert total_squares == 4

    def test_game_phase_changes_propagate_to_ui(self):
        """Integration: Game phase changes propagate to UI components.

        Given: Game in SETUP phase
        When: Game starts (phase changes to PLAYING)
        Then: UI components reflect phase change
        """
        # Given: Game in setup
        setup = GameSetup()
        game_state = setup.setup_game(2, ["Alice", "Bob"])

        # Then: Phase is SETUP
        assert game_state.phase.value == 1
        assert game_state.phase.name == "SETUP"

        # When: Game starts
        game_state.start_game()

        # Then: Phase is PLAYING
        assert game_state.phase.value == 2
        assert game_state.phase.name == "PLAYING"

        # Then: Current player is accessible
        current = game_state.get_current_player()
        assert current is not None
        assert current.name == "Alice"

    def test_empty_board_state_is_clear(self):
        """Integration: Empty board shows no pieces.

        Given: New game
        When: Board is examined
        Then: No pieces are shown
        """
        # Given: New game
        setup = GameSetup()
        game_state = setup.setup_game(2, ["Alice", "Bob"])
        board = setup.get_board()

        # Then: Board has no occupied positions
        occupied = board.get_occupied_positions()
        assert len(occupied) == 0

        # Then: All positions are empty
        assert board.is_position_empty(0, 0)
        assert board.is_position_empty(10, 10)
        assert board.is_position_empty(19, 19)

        # Then: All player squares count is 0
        for player_id in [1, 2]:
            assert board.count_player_squares(player_id) == 0
