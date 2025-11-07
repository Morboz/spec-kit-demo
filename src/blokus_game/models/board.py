"""
Board model for Blokus game.

This module defines the Board class which represents the 20x20 game board
where players place their pieces.
"""

from blokus_game.models.piece import Piece


class Board:
    """Represents the Blokus game board."""

    BOARD_SIZE = 20

    def __init__(self) -> None:
        """
        Initialize a new 20x20 Blokus board.

        The board is represented as a dictionary mapping (row, col) tuples
        to player IDs who have occupied those positions.
        """
        self.grid: dict[tuple[int, int], int] = {}
        self.size = self.BOARD_SIZE

    def is_position_valid(self, row: int, col: int) -> bool:
        """
        Check if a position is within board bounds.

        Args:
            row: Row coordinate
            col: Column coordinate

        Returns:
            True if position is on the board, False otherwise
        """
        return 0 <= row < self.size and 0 <= col < self.size

    def is_position_empty(self, row: int, col: int) -> bool:
        """
        Check if a board position is empty.

        Args:
            row: Row coordinate
            col: Column coordinate

        Returns:
            True if position is empty and valid, False otherwise
        """
        return self.is_position_valid(row, col) and (row, col) not in self.grid

    def place_piece(
        self, piece: Piece, anchor_row: int, anchor_col: int, player_id: int
    ) -> list[tuple[int, int]]:
        """
        Place a piece on the board at the specified anchor position.

        Args:
            piece: The piece to place
            anchor_row: Row where piece's origin (0,0) will be placed
            anchor_col: Column where piece's origin (0,0) will be placed
            player_id: ID of the player placing the piece

        Returns:
            List of (row, col) positions where the piece was placed

        Raises:
            ValueError: If the position is invalid or already occupied
        """
        # Get absolute positions for all piece squares
        positions = piece.get_absolute_positions(anchor_row, anchor_col)

        # Validate all positions
        for pos_row, pos_col in positions:
            if not self.is_position_valid(pos_row, pos_col):
                raise ValueError(
                    f"Position ({pos_row}, {pos_col}) is outside board bounds"
                )
            if not self.is_position_empty(pos_row, pos_col):
                raise ValueError(f"Position ({pos_row}, {pos_col}) is already occupied")

        # Place the piece
        for pos_row, pos_col in positions:
            self.grid[(pos_row, pos_col)] = player_id

        return positions

    def get_occupied_positions(self) -> set[tuple[int, int]]:
        """
        Get all currently occupied positions on the board.

        Returns:
            Set of (row, col) tuples for occupied positions
        """
        return set(self.grid.keys())

    def get_player_positions(self, player_id: int) -> set[tuple[int, int]]:
        """
        Get all positions occupied by a specific player.

        Args:
            player_id: ID of the player

        Returns:
            Set of (row, col) tuples for the player's pieces
        """
        return {pos for pos, pid in self.grid.items() if pid == player_id}

    def get_occupant(self, row: int, col: int) -> int | None:
        """
        Get the player ID occupying a specific position.

        Args:
            row: Row coordinate
            col: Column coordinate

        Returns:
            Player ID if position is occupied, None otherwise
        """
        return self.grid.get((row, col))

    def is_occupied(self, row: int, col: int) -> bool:
        """
        Check if a position is occupied.

        Args:
            row: Row coordinate
            col: Column coordinate

        Returns:
            True if position is occupied, False otherwise
        """
        return (row, col) in self.grid

    def get_adjacent_positions(
        self, row: int, col: int, include_diagonal: bool = False
    ) -> list[tuple[int, int]]:
        """
        Get all orthogonal (or diagonal) adjacent positions to a given cell.

        Args:
            row: Row coordinate
            col: Column coordinate
            include_diagonal: If True, include diagonal positions

        Returns:
            List of adjacent (row, col) tuples that are within board bounds
        """
        positions = []

        # Orthogonal neighbors
        orthogonal = [
            (row - 1, col),  # Up
            (row + 1, col),  # Down
            (row, col - 1),  # Left
            (row, col + 1),  # Right
        ]

        for pos_row, pos_col in orthogonal:
            if self.is_position_valid(pos_row, pos_col):
                positions.append((pos_row, pos_col))

        # Diagonal neighbors
        if include_diagonal:
            diagonal = [
                (row - 1, col - 1),  # Up-left
                (row - 1, col + 1),  # Up-right
                (row + 1, col - 1),  # Down-left
                (row + 1, col + 1),  # Down-right
            ]
            for pos_row, pos_col in diagonal:
                if self.is_position_valid(pos_row, pos_col):
                    positions.append((pos_row, pos_col))

        return positions

    def get_board_state(self) -> list[list[int | None]]:
        """
        Get the complete board state as a 2D list.

        Returns:
            2D list where each cell contains player ID or None
        """
        state = [[None for _ in range(self.size)] for _ in range(self.size)]

        for (row, col), player_id in self.grid.items():
            state[row][col] = player_id

        return state

    def count_player_squares(self, player_id: int) -> int:
        """
        Count the total number of squares occupied by a player.

        Args:
            player_id: ID of the player

        Returns:
            Number of squares occupied by the player
        """
        return len(self.get_player_positions(player_id))

    def __repr__(self) -> str:
        """String representation of Board."""
        occupied_count = len(self.grid)
        return f"Board(size={self.size}x{self.size}, occupied={occupied_count})"
