"""Integration test for complete game setup workflow.

This test validates that the entire game setup process works correctly,
from configuration through to a ready game state.
"""

import pytest

from src.game.game_setup import GameSetup
from src.models.board import Board
from src.models.game_state import GameState


class TestCompleteSetupFlow:
    """Integration tests for complete setup workflow."""

    def test_complete_setup_with_two_players(self):
        """Integration: Full setup flow creates ready game state.

        Given: Configuration for 2-player game
        When: GameSetup orchestrator sets up the game
        Then: Complete game state is created and ready
        """
        # Given: Configuration
        num_players = 2
        player_names = ["Alice", "Bob"]

        # When: Setup is executed
        setup = GameSetup()
        game_state = setup.setup_game(num_players, player_names)

        # Then: Board is created
        assert setup.get_board() is not None
        assert isinstance(setup.get_board(), Board)
        assert setup.get_board().size == 20

        # Then: Game state is created
        assert game_state is not None
        assert isinstance(game_state, GameState)
        assert game_state.phase.value == 1  # SETUP phase

        # Then: Players are created
        players = setup.get_players()
        assert len(players) == 2

        assert players[0].name == "Alice"
        assert players[0].player_id == 1
        assert players[0].get_starting_corner() == (0, 0)
        assert len(players[0].get_all_pieces()) == 21

        assert players[1].name == "Bob"
        assert players[1].player_id == 2
        assert players[1].get_starting_corner() == (0, 19)
        assert len(players[1].get_all_pieces()) == 21

        # Then: Game state is properly configured
        assert game_state.board == setup.get_board()
        assert len(game_state.players) == 2
        assert game_state.get_player_count() == 2

    def test_complete_setup_with_four_players(self):
        """Integration: Full setup flow with maximum players.

        Given: Configuration for 4-player game
        When: GameSetup orchestrator sets up the game
        Then: All players are created with unique corners
        """
        # Given: Configuration
        num_players = 4
        player_names = ["Alice", "Bob", "Charlie", "Diana"]

        # When: Setup is executed
        setup = GameSetup()
        game_state = setup.setup_game(num_players, player_names)

        # Then: All 4 players created
        players = setup.get_players()
        assert len(players) == 4

        # Then: Each player has unique corner
        corners = [p.get_starting_corner() for p in players]
        assert len(set(corners)) == 4  # All unique
        assert (0, 0) in corners
        assert (0, 19) in corners
        assert (19, 19) in corners
        assert (19, 0) in corners

        # Then: Each player has all pieces
        for player in players:
            assert len(player.get_all_pieces()) == 21
            assert player.get_remaining_piece_count() == 21

    def test_setup_validation_rejects_invalid_configs(self):
        """Integration: Setup validates configuration and rejects invalid input.

        Given: Various invalid configurations
        When: GameSetup attempts to set up game
        Then: Appropriate errors are raised
        """
        setup = GameSetup()

        # Test: Too few players
        with pytest.raises(
            ValueError, match="Number of players must be between 2 and 4"
        ):
            setup.setup_game(1, ["Alice"])

        # Test: Too many players
        with pytest.raises(
            ValueError, match="Number of players must be between 2 and 4"
        ):
            setup.setup_game(5, ["Alice", "Bob", "Charlie", "Diana", "Eve"])

        # Test: Empty player name
        with pytest.raises(ValueError, match="Player 1 name cannot be empty"):
            setup.setup_game(2, ["", "Bob"])

        # Test: Whitespace-only name
        with pytest.raises(ValueError, match="Player 1 name cannot be empty"):
            setup.setup_game(2, ["   ", "Bob"])

        # Test: Duplicate names
        with pytest.raises(ValueError, match="Duplicate player name"):
            setup.setup_game(2, ["Alice", "Alice"])

        # Test: Name too long
        with pytest.raises(ValueError, match="name is too long"):
            setup.setup_game(2, ["A" * 21, "Bob"])

        # Test: Name count mismatch
        with pytest.raises(ValueError, match="Number of player names"):
            setup.setup_game(2, ["Alice"])

    def test_setup_can_be_retrieved_after_completion(self):
        """Integration: Setup components are retrievable after setup.

        Given: Game setup is complete
        When: Accessing setup components
        Then: All components are available and valid
        """
        # Given: Completed setup
        setup = GameSetup()
        game_state = setup.setup_game(2, ["Alice", "Bob"])

        # When: Retrieving components
        retrieved_state = setup.get_game_state()
        retrieved_board = setup.get_board()
        retrieved_players = setup.get_players()

        # Then: All components match
        assert retrieved_state == game_state
        assert retrieved_board is not None
        assert len(retrieved_players) == 2
        assert setup.is_setup_complete() is True

    def test_board_ready_for_first_turn_after_setup(self):
        """Integration: Board is ready for gameplay after setup.

        Given: Game setup is complete
        When: Game is started
        Then: Board and game state are ready for first moves
        """
        # Given: Completed setup
        setup = GameSetup()
        game_state = setup.setup_game(2, ["Alice", "Bob"])

        # When: Game is started
        game_state.start_game()

        # Then: Game is in playing phase
        assert game_state.phase.value == 2  # PLAYING phase

        # Then: Current player is set
        assert game_state.current_player_index == 0
        assert game_state.get_current_player() == setup.get_players()[0]

        # Then: Board is empty and ready
        board = setup.get_board()
        assert len(board.get_occupied_positions()) == 0
        for player in setup.get_players():
            assert board.count_player_squares(player.player_id) == 0

        # Then: Player corners are empty
        for player in setup.get_players():
            corner_row, corner_col = player.get_starting_corner()
            assert board.is_position_empty(corner_row, corner_col)
