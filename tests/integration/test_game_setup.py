"""Integration tests for complete game setup flow.

This test validates the entire game setup process from initialization
to a ready-to-play game state.
"""

import pytest
from src.models.board import Board
from src.models.player import Player
from src.models.game_state import GameState


class TestGameSetupFlow:
    """Integration tests for game setup workflow."""

    def test_setup_game_with_two_players(self):
        """Integration: Complete setup flow for 2-player game.

        Given: Initiating game setup
        When: Creating game with 2 players
        Then: Game state should be ready for gameplay
        """
        # Setup: Create board
        board = Board()

        # Setup: Create players
        players = [
            Player(player_id=1, name="Alice"),
            Player(player_id=2, name="Bob"),
        ]

        # Setup: Create game state
        game_state = GameState()
        game_state.board = board
        for player in players:
            game_state.add_player(player)

        # Verify: Board is initialized
        assert game_state.board.size == 20
        assert len(game_state.board.get_occupied_positions()) == 0

        # Verify: Players are added
        assert len(game_state.players) == 2
        assert game_state.get_player_by_id(1) == players[0]
        assert game_state.get_player_by_id(2) == players[1]

        # Verify: Each player has correct attributes
        for player in players:
            assert player.name is not None
            assert player.player_id in [1, 2]
            assert len(player.get_all_pieces()) == 21
            assert player.score == 0

        # Verify: Starting corners are assigned
        assert players[0].get_starting_corner() == (0, 0)
        assert players[1].get_starting_corner() == (0, 19)

        # Verify: Game state is in setup phase
        assert game_state.phase.value == 1  # GamePhase.SETUP = 1

    def test_setup_game_with_four_players(self):
        """Integration: Complete setup flow for 4-player game.

        Given: Initiating game setup
        When: Creating game with 4 players
        Then: All players should be ready with unique corners
        """
        # Setup: Create board
        board = Board()

        # Setup: Create 4 players
        players = [
            Player(player_id=1, name="Alice"),
            Player(player_id=2, name="Bob"),
            Player(player_id=3, name="Charlie"),
            Player(player_id=4, name="Diana"),
        ]

        # Setup: Create game state
        game_state = GameState()
        game_state.board = board
        for player in players:
            game_state.add_player(player)

        # Verify: All 4 players added
        assert len(game_state.players) == 4

        # Verify: Each player has unique corner
        corners = [p.get_starting_corner() for p in players]
        assert len(corners) == len(set(corners)), "All corners must be unique"
        assert (0, 0) in corners
        assert (0, 19) in corners
        assert (19, 19) in corners
        assert (19, 0) in corners

        # Verify: Each player has all pieces
        for player in players:
            assert len(player.get_all_pieces()) == 21
            assert player.get_remaining_piece_count() == 21

        # Verify: Game state is ready to start
        assert game_state.phase.value == 1  # GamePhase.SETUP = 1

    def test_game_state_ready_for_first_turn(self):
        """Integration: Game state is ready to begin gameplay.

        Given: Game setup is complete with players
        When: Game is started
        Then: Game should transition to playing phase with first player active
        """
        # Setup: Create ready game state
        board = Board()
        players = [
            Player(player_id=1, name="Alice"),
            Player(player_id=2, name="Bob"),
        ]

        game_state = GameState()
        game_state.board = board
        for player in players:
            game_state.add_player(player)

        # Exercise: Start the game
        game_state.start_game()

        # Verify: Game phase is playing
        assert game_state.phase.value == 2  # GamePhase.PLAYING = 2

        # Verify: Current player is set (should be player 1)
        assert game_state.current_player_index == 0
        assert game_state.players[0] == players[0]

        # Verify: No moves recorded yet
        assert len(game_state.get_move_history()) == 0

    def test_board_is_ready_for_first_moves(self):
        """Integration: Board is ready to accept first moves from corners.

        Given: Game setup is complete
        When: Game starts
        Then: Board should allow first moves in player corners
        """
        # Setup: Create ready game state
        board = Board()
        players = [
            Player(player_id=1, name="Alice"),
            Player(player_id=2, name="Bob"),
        ]

        game_state = GameState()
        game_state.board = board
        for player in players:
            game_state.add_player(player)

        game_state.start_game()

        # Verify: Corners are empty and valid
        for player in players:
            corner_row, corner_col = player.get_starting_corner()
            assert board.is_position_valid(corner_row, corner_col)
            assert board.is_position_empty(corner_row, corner_col)

        # Verify: Board can report empty positions for all corners
        expected_corners = [(0, 0), (0, 19)]
        for corner in expected_corners:
            assert board.is_position_empty(corner[0], corner[1])

        # Verify: No occupied positions
        assert len(board.get_occupied_positions()) == 0

        # Verify: All player square counts are 0
        for player in players:
            assert board.count_player_squares(player.player_id) == 0
