"""Contract tests for Board initialization in game setup flow.

This test validates that Board can be properly initialized during game setup,
ensuring it meets the requirements for a new Blokus game.
"""

import pytest
from src.models.board import Board


class TestBoardInitializationContract:
    """Contract tests for Board initialization during game setup."""

    def test_board_creates_empty_20x20_grid(self):
        """Contract: Game setup must create a 20x20 empty board.

        Given: A new game setup is initiated
        When: Board is initialized
        Then: Board must be exactly 20x20 with all positions empty
        """
        board = Board()

        # Verify board size is exactly 20x20
        assert board.size == 20
        assert board.get_board_state() is not None

        # Verify all positions are initially empty
        state = board.get_board_state()
        for row in state:
            for cell in row:
                assert cell is None, "All board positions must be empty during setup"

    def test_board_has_valid_starting_positions(self):
        """Contract: Board must provide valid starting corner positions.

        Given: A new game setup is initiated
        When: Board is initialized
        Then: Board must have four valid corner positions for player placement
        """
        board = Board()

        # Verify corners are valid positions
        assert board.is_position_valid(0, 0), "Top-left corner must be valid"
        assert board.is_position_valid(0, 19), "Top-right corner must be valid"
        assert board.is_position_valid(19, 19), "Bottom-right corner must be valid"
        assert board.is_position_valid(19, 0), "Bottom-left corner must be valid"

        # Verify corners are initially empty
        assert board.is_position_empty(0, 0)
        assert board.is_position_empty(0, 19)
        assert board.is_position_empty(19, 19)
        assert board.is_position_empty(19, 0)

    def test_board_ready_for_piece_placement(self):
        """Contract: Board must be ready to accept piece placements.

        Given: A new game setup is initiated
        When: Board is initialized
        Then: Board must be able to accept piece placements from any corner
        """
        board = Board()

        # Verify board can report empty status (returns set)
        assert (
            len(board.get_occupied_positions()) == 0
        ), "Board should have no occupied positions"

        # Verify board can count player squares (initially 0)
        for player_id in [1, 2, 3, 4]:
            assert (
                board.count_player_squares(player_id) == 0
            ), f"Player {player_id} should have 0 squares initially"
