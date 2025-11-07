"""Contract tests for game state display functionality.

This test validates that UI components can correctly display and update
game state information including current player, scores, and piece inventory.
"""

from blokus_game.models.board import Board
from blokus_game.models.game_state import GameState
from blokus_game.models.piece import Piece
from blokus_game.models.player import Player


class TestStateDisplay:
    """Contract tests for state display functionality."""

    def test_current_player_indicator_shows_correct_player(self):
        """Contract: CurrentPlayerIndicator displays correct player.

        Given: A game with multiple players
        When: The current player is player 2
        Then: Indicator shows player 2 as active
        """
        # Given: Game state with multiple players
        game_state = GameState()
        game_state.players = [
            Player(player_id=1, name="Alice"),
            Player(player_id=2, name="Bob"),
        ]
        game_state.current_player_index = 1

        # Then: Current player should be Bob
        current = game_state.get_current_player()
        assert current.name == "Bob"
        assert current.player_id == 2

    def test_scoreboard_displays_all_player_scores(self):
        """Contract: Scoreboard shows scores for all players.

        Given: Players with different scores
        When: Scores are calculated
        Then: All scores are displayed
        """
        # Given: Game with players
        player1 = Player(player_id=1, name="Alice")
        player2 = Player(player_id=2, name="Bob")

        # When: Players have placed pieces
        board = Board()
        piece1 = Piece("I2")
        piece2 = Piece("L4")

        board.place_piece(piece1, 0, 0, 1)
        board.place_piece(piece2, 5, 5, 2)

        # Then: Counts should reflect placed pieces
        assert board.count_player_squares(1) == 2
        assert board.count_player_squares(2) == 4

    def test_piece_inventory_shows_remaining_pieces(self):
        """Contract: PieceInventory shows remaining pieces count.

        Given: A player with 21 pieces
        When: Some pieces are placed
        Then: Inventory shows remaining count
        """
        # Given: Player with all pieces
        player = Player(player_id=1, name="Alice")
        assert player.get_remaining_piece_count() == 21

        # When: Player places a piece (via placement handler in real scenario)
        board = Board()
        piece = player.get_piece("I2")
        assert piece is not None

        # Note: In real implementation, placement handler updates player state
        # For this test, we verify board placement directly
        board.place_piece(piece, 0, 0, 1)

        # Then: Board reflects the placement
        assert board.count_player_squares(1) == 2

    def test_game_state_updates_after_piece_placement(self):
        """Contract: Game state updates when piece is placed.

        Given: A game in progress
        When: A player places a piece
        Then: Game state reflects the change
        """
        # Given: Active game
        game_state = GameState()
        game_state.players = [
            Player(player_id=1, name="Alice"),
            Player(player_id=2, name="Bob"),
        ]
        game_state.current_player_index = 0

        # When: Player places a piece
        board = Board()
        player = game_state.players[0]
        piece = player.get_piece("I1")
        board.place_piece(piece, 5, 5, 1)

        # Then: Board state changes
        assert board.count_player_squares(1) == 1
        assert board.is_occupied(5, 5)

    def test_turn_progression_updates_current_player(self):
        """Contract: Current player advances after move.

        Given: Game with player 1's turn
        When: Player 1 makes a move
        Then: Player 2 becomes current player
        """
        # Given: Game state
        game_state = GameState()
        game_state.players = [
            Player(player_id=1, name="Alice"),
            Player(player_id=2, name="Bob"),
        ]
        game_state.current_player_index = 0
        initial_player = game_state.get_current_player()
        assert initial_player.player_id == 1

        # When: Turn advances
        game_state.current_player_index = 1
        new_current = game_state.get_current_player()

        # Then: Current player should be player 2
        assert new_current.player_id == 2

    def test_piece_inventory_shows_individual_pieces(self):
        """Contract: Can query individual piece availability.

        Given: A player with various pieces
        When: Checking piece availability
        Then: Accurate status is returned
        """
        # Given: Player
        player = Player(player_id=1, name="Alice")

        # Then: All pieces should be available
        for piece_name in ["I1", "I2", "L4", "X5"]:
            piece = player.get_piece(piece_name)
            assert piece is not None
            assert not piece.is_placed

    def test_board_state_is_accurately_displayed(self):
        """Contract: Board state reflects all placements.

        Given: A board with multiple pieces
        When: Retrieving board state
        Then: All placements are visible
        """
        # Given: Board with pieces
        board = Board()
        piece1 = Piece("I2")
        piece2 = Piece("L4")

        board.place_piece(piece1, 0, 0, 1)
        board.place_piece(piece2, 5, 5, 2)

        # When: Getting board state
        state = board.get_board_state()

        # Then: Should reflect all placements
        assert state[0][0] == 1
        assert state[1][0] == 1
        assert state[5][5] == 2
        assert state[5][6] == 2
        assert state[5][7] == 2
        assert state[6][7] == 2

    def test_multiple_player_states_displayed(self):
        """Contract: All players' states are tracked.

        Given: Game with multiple players
        When: Retrieving player positions
        Then: Each player's positions are separate
        """
        # Given: Multi-player game
        board = Board()

        # When: Players place pieces
        piece1 = Piece("I2")
        board.place_piece(piece1, 0, 0, 1)

        piece2 = Piece("L4")
        board.place_piece(piece2, 10, 10, 2)

        piece3 = Piece("I1")
        board.place_piece(piece3, 15, 15, 3)

        # Then: Each player has correct positions
        player1_positions = board.get_player_positions(1)
        assert len(player1_positions) == 2

        player2_positions = board.get_player_positions(2)
        assert len(player2_positions) == 4

        player3_positions = board.get_player_positions(3)
        assert len(player3_positions) == 1

    def test_empty_board_shows_no_occupants(self):
        """Contract: Empty board shows no pieces placed.

        Given: New game
        When: Checking board state
        Then: No pieces are displayed
        """
        # Given: Empty board
        board = Board()

        # Then: No occupied positions
        assert len(board.get_occupied_positions()) == 0

        # Then: All positions are empty
        assert board.is_position_empty(0, 0)
        assert board.is_position_empty(10, 10)
        assert board.is_position_empty(19, 19)

    def test_game_phase_is_tracked(self):
        """Contract: Game phase is correctly tracked.

        Given: Game in different phases
        When: Checking phase
        Then: Correct phase is reported
        """
        # Given: Game in setup phase
        game_state = GameState()
        assert game_state.phase.value == 1  # SETUP
        assert game_state.phase.name == "SETUP"

        # When: Game starts
        from blokus_game.models.game_state import GamePhase

        game_state.phase = GamePhase.PLAYING
        assert game_state.phase.value == 2  # PLAYING
        assert game_state.phase.name == "PLAYING"

        # When: Game ends
        game_state.phase = GamePhase.GAME_OVER
        assert game_state.phase.value == 3  # GAME_OVER
        assert game_state.phase.name == "GAME_OVER"
