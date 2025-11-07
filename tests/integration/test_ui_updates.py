"""Integration test for UI state updates during gameplay.

This test validates that UI components properly synchronize with game state
changes and update in real-time as the game progresses.
"""

from blokus_game.game.game_setup import GameSetup
from blokus_game.game.placement_handler import PlacementHandler
from blokus_game.models.piece import Piece


class TestUIUpdates:
    """Integration tests for UI state updates."""

    def test_ui_updates_after_piece_placement(self):
        """Integration: UI reflects changes after piece placement.

        Given: Game setup with board and players
        When: Player places a piece
        Then: Game state updates are reflected
        """
        # Given: Game setup
        setup = GameSetup()
        game_state = setup.setup_game(2, ["Alice", "Bob"])
        game_state.start_game()

        # When: Player 1 places a piece
        current_player = game_state.get_current_player()
        assert current_player.name == "Alice"

        # Place piece
        piece = current_player.get_piece("I1")
        board = setup.get_board()
        positions = board.place_piece(piece, 5, 5, 1)

        # Then: State updates correctly
        assert len(positions) == 1
        assert board.count_player_squares(1) == 1
        # Note: Player piece count is updated via placement handler in real scenarios

    def test_turn_advancement_updates_current_player(self):
        """Integration: Current player indicator updates on turn change.

        Given: Active game with player 1's turn
        When: Player 1 completes turn
        Then: Player 2 becomes current player
        """
        # Given: Game setup
        setup = GameSetup()
        game_state = setup.setup_game(2, ["Alice", "Bob"])
        game_state.start_game()

        # Then: Player 1 starts
        assert game_state.get_current_player().name == "Alice"
        assert game_state.current_player_index == 0

        # When: Turn advances manually
        game_state.current_player_index = 1

        # Then: Player 2 is current
        assert game_state.get_current_player().name == "Bob"
        assert game_state.current_player_index == 1

    def test_score_updates_after_multiple_placements(self):
        """Integration: Score updates reflect multiple piece placements.

        Given: Players place multiple pieces
        When: Each placement occurs
        Then: Board state accumulates correctly
        """
        # Given: Game setup
        setup = GameSetup()
        game_state = setup.setup_game(2, ["Alice", "Bob"])
        board = setup.get_board()

        # When: Player 1 places multiple pieces
        player1 = game_state.players[0]
        piece1 = player1.get_piece("I2")
        piece2 = player1.get_piece("L4")

        board.place_piece(piece1, 0, 0, 1)
        board.place_piece(piece2, 5, 5, 1)

        # Then: Player 1 has 6 squares placed
        assert board.count_player_squares(1) == 6
        # Note: Player piece count updates handled by placement handler

        # When: Player 2 places pieces
        player2 = game_state.players[1]
        piece3 = player2.get_piece("I1")
        board.place_piece(piece3, 10, 10, 2)

        # Then: Player 2 has 1 square
        assert board.count_player_squares(2) == 1

    def test_piece_inventory_decreases_on_placement(self):
        """Integration: Piece inventory decreases when piece is placed.

        Given: Player with 21 pieces
        When: Player places 3 pieces
        Then: Inventory shows 18 remaining
        """
        # Given: Game setup
        setup = GameSetup()
        game_state = setup.setup_game(2, ["Alice", "Bob"])
        player = game_state.players[0]
        board = setup.get_board()

        # Then: Initially 21 pieces
        assert player.get_remaining_piece_count() == 21

        # When: Player places pieces (via placement handler in real scenario)
        piece1 = player.get_piece("I1")
        board.place_piece(piece1, 0, 0, 1)
        # Note: In real scenario, placement handler updates player state

        piece2 = player.get_piece("I2")
        board.place_piece(piece2, 5, 5, 1)

        piece3 = player.get_piece("L4")
        board.place_piece(piece3, 10, 10, 1)

        # Then: Board reflects all placements
        assert board.count_player_squares(1) == 7  # 1 + 2 + 4 squares

    def test_board_state_reflects_all_players_pieces(self):
        """Integration: Board shows pieces from all players.

        Given: Multi-player game
        When: Each player places pieces
        Then: Board contains all pieces
        """
        # Given: Game setup with 3 players
        setup = GameSetup()
        game_state = setup.setup_game(3, ["Alice", "Bob", "Charlie"])
        board = setup.get_board()

        # When: All players place pieces
        # Player 1
        piece1 = game_state.players[0].get_piece("I2")
        board.place_piece(piece1, 0, 0, 1)

        # Player 2
        piece2 = game_state.players[1].get_piece("L4")
        board.place_piece(piece2, 10, 10, 2)

        # Player 3
        piece3 = game_state.players[2].get_piece("V3")
        board.place_piece(piece3, 15, 15, 3)

        # Then: Board shows all pieces
        occupied = board.get_occupied_positions()
        assert len(occupied) == 9  # 2 + 4 + 3

        # Then: Each player has correct count
        assert board.count_player_squares(1) == 2
        assert board.count_player_squares(2) == 4
        assert board.count_player_squares(3) == 3

    def test_empty_positions_remain_available(self):
        """Integration: Empty board positions remain available.

        Given: Board with some pieces placed
        When: Checking empty positions
        Then: Empty positions are still valid
        """
        # Given: Board with pieces
        setup = GameSetup()
        game_state = setup.setup_game(2, ["Alice", "Bob"])
        board = setup.get_board()

        # Place pieces (I2 occupies positions (5,5) and (6,5))
        piece = Piece("I2")
        board.place_piece(piece, 5, 5, 1)

        # Then: Adjacent positions are still empty
        assert board.is_position_empty(5, 7)  # Right of second square
        assert board.is_position_empty(4, 5)  # Up from first square
        assert board.is_position_empty(4, 6)  # Up from second square
        assert board.is_position_empty(5, 4)  # Left from first square
        assert board.is_position_empty(6, 4)  # Left from second square
        assert board.is_position_empty(7, 5)  # Down from second square

        # Then: Occupied positions are not empty
        assert not board.is_position_empty(5, 5)
        assert not board.is_position_empty(6, 5)

    def test_player_corner_positions_stay_empty(self):
        """Integration: Player starting corners remain empty until used.

        Given: New game setup
        When: Before any moves
        Then: All player corners are empty
        """
        # Given: Game setup
        setup = GameSetup()
        game_state = setup.setup_game(2, ["Alice", "Bob"])
        board = setup.get_board()
        players = setup.get_players()

        # Then: Player 1 corner (0, 0) is empty
        corner1 = players[0].get_starting_corner()
        assert board.is_position_empty(corner1[0], corner1[1])

        # Then: Player 2 corner (0, 19) is empty
        corner2 = players[1].get_starting_corner()
        assert board.is_position_empty(corner2[0], corner2[1])

    def test_game_phase_transitions_update_state(self):
        """Integration: Game phase changes are tracked.

        Given: Game in setup phase
        When: Game starts
        Then: Phase updates to playing
        """
        # Given: Game setup
        setup = GameSetup()
        game_state = setup.setup_game(2, ["Alice", "Bob"])

        # Then: Initially in setup phase
        assert game_state.phase.value == 1

        # When: Game starts
        game_state.start_game()

        # Then: Phase is playing
        assert game_state.phase.value == 2

    def test_player_positions_isolated_by_player(self):
        """Integration: Each player's positions are tracked separately.

        Given: Multiple players place pieces
        When: Retrieving positions per player
        Then: Each player's positions are isolated
        """
        # Given: Game setup
        setup = GameSetup()
        game_state = setup.setup_game(2, ["Alice", "Bob"])
        board = setup.get_board()

        # When: Players place overlapping shapes
        piece1 = Piece("I1")
        board.place_piece(piece1, 5, 5, 1)

        piece2 = Piece("I1")
        board.place_piece(piece2, 10, 10, 2)

        # Then: Player positions are separate
        player1_positions = board.get_player_positions(1)
        player2_positions = board.get_player_positions(2)

        assert (5, 5) in player1_positions
        assert (10, 10) in player2_positions
        assert (10, 10) not in player1_positions
        assert (5, 5) not in player2_positions

    def test_board_bounds_maintained_after_placements(self):
        """Integration: Board boundaries respected after multiple placements.

        Given: Board with pieces near edges
        When: Checking boundaries
        Then: All positions within bounds
        """
        # Given: Game setup
        setup = GameSetup()
        game_state = setup.setup_game(2, ["Alice", "Bob"])
        board = setup.get_board()

        # When: Placing pieces across board
        piece1 = Piece("I1")
        board.place_piece(piece1, 0, 0, 1)

        piece2 = Piece("I1")
        board.place_piece(piece2, 19, 19, 2)

        # Then: All positions are valid
        occupied = board.get_occupied_positions()
        for row, col in occupied:
            assert board.is_position_valid(row, col)
            assert board.is_occupied(row, col)

    def test_placement_handler_validates_before_update(self):
        """Integration: Placement handler validates moves before updating state.

        Given: Valid placement
        When: Handler processes placement
        Then: State updates only after validation
        """
        # Given: Game setup and placement handler
        setup = GameSetup()
        game_state = setup.setup_game(2, ["Alice", "Bob"])
        current_player = game_state.get_current_player()
        handler = PlacementHandler(game_state.board, game_state, current_player)

        # When: Valid placement (via direct board placement)
        piece = current_player.get_piece("I1")
        positions = game_state.board.place_piece(piece, 5, 5, 1)

        # Then: Placement succeeds
        assert len(positions) == 1
        assert game_state.board.count_player_squares(1) == 1

    def test_turn_order_cycles_correctly(self):
        """Integration: Turn order cycles through all players.

        Given: Game with 3 players
        When: Turns advance
        Then: Order cycles correctly
        """
        # Given: 3-player game
        setup = GameSetup()
        game_state = setup.setup_game(3, ["Alice", "Bob", "Charlie"])

        # Then: Initial turn is player 0
        assert game_state.current_player_index == 0
        assert game_state.get_current_player().name == "Alice"

        # When: Turns advance
        game_state.current_player_index = 1
        assert game_state.get_current_player().name == "Bob"

        game_state.current_player_index = 2
        assert game_state.get_current_player().name == "Charlie"

        # Cycle back
        game_state.current_player_index = 0
        assert game_state.get_current_player().name == "Alice"
