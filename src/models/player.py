"""
Player model for Blokus game.

This module defines the Player class which represents a player in the game,
including their score, pieces, and turn state.
"""

from typing import Dict, List, Optional, Set
from src.models.piece import Piece
from src.config.pieces import get_all_piece_names, get_player_color, get_starting_corner


class Player:
    """Represents a Blokus game player."""

    def __init__(self, player_id: int, name: str, pieces: Optional[List[Piece]] = None) -> None:
        """
        Initialize a new player.

        Args:
            player_id: Unique ID (1-4)
            name: Player's display name
            pieces: List of pieces (defaults to all 21 standard pieces)

        Raises:
            ValueError: If player_id is not in range 1-4
        """
        if player_id not in [1, 2, 3, 4]:
            raise ValueError(f"Player ID must be 1-4, got {player_id}")

        self.player_id = player_id
        self.name = name
        self.score = 0

        # Initialize pieces
        if pieces is None:
            self.pieces = {name: Piece(name) for name in get_all_piece_names()}
        else:
            self.pieces = {piece.name: piece for piece in pieces}

        # Track placed positions for scoring
        self.placed_positions: Set[tuple] = set()

        # Game state
        self.has_passed = False
        self.is_active = True

    def get_piece(self, piece_name: str) -> Optional[Piece]:
        """
        Get a piece by name.

        Args:
            piece_name: Name of the piece

        Returns:
            Piece instance if available, None otherwise
        """
        return self.pieces.get(piece_name)

    def get_all_pieces(self) -> List[Piece]:
        """
        Get all pieces belonging to the player.

        Returns:
            List of Piece instances
        """
        return list(self.pieces.values())

    def get_unplaced_pieces(self) -> List[Piece]:
        """
        Get all pieces that have not been placed on the board.

        Returns:
            List of unplaced Piece instances
        """
        return [piece for piece in self.pieces.values() if not piece.is_placed]

    def get_placed_pieces(self) -> List[Piece]:
        """
        Get all pieces that have been placed on the board.

        Returns:
            List of placed Piece instances
        """
        return [piece for piece in self.pieces.values() if piece.is_placed]

    def remove_piece(self, piece_name: str) -> Optional[Piece]:
        """
        Remove a piece from the player's inventory.

        Args:
            piece_name: Name of the piece to remove

        Returns:
            Removed Piece instance if it existed, None otherwise
        """
        return self.pieces.pop(piece_name, None)

    def get_score(self) -> int:
        """
        Get the player's current score.

        Returns:
            Current score
        """
        return self.score

    def add_points(self, points: int) -> None:
        """
        Add points to the player's score.

        Args:
            points: Number of points to add
        """
        self.score += points

    def subtract_points(self, points: int) -> None:
        """
        Subtract points from the player's score.

        Args:
            points: Number of points to subtract
        """
        self.score -= points

    def get_remaining_piece_count(self) -> int:
        """
        Get the number of unplaced pieces remaining.

        Returns:
            Count of unplaced pieces
        """
        return len(self.get_unplaced_pieces())

    def get_remaining_squares(self) -> int:
        """
        Get the total number of squares in unplaced pieces.

        Returns:
            Total number of squares remaining
        """
        return sum(piece.size for piece in self.get_unplaced_pieces())

    def has_pieces_remaining(self) -> bool:
        """
        Check if player has any pieces remaining.

        Returns:
            True if player has unplaced pieces, False otherwise
        """
        return len(self.get_unplaced_pieces()) > 0

    def get_color(self) -> str:
        """
        Get the player's color.

        Returns:
            Hex color string for the player
        """
        return get_player_color(self.player_id)

    def get_starting_corner(self) -> tuple:
        """
        Get the player's starting corner position.

        Returns:
            Tuple of (row, col) for the player's corner
        """
        return get_starting_corner(self.player_id)

    def place_piece(self, piece_name: str, row: int, col: int) -> None:
        """
        Mark a piece as placed at given position.

        Args:
            piece_name: Name of the piece
            row: Row where piece was placed
            col: Column where piece was placed

        Raises:
            ValueError: If piece is not found or already placed
        """
        piece = self.get_piece(piece_name)
        if piece is None:
            raise ValueError(f"Player does not have piece: {piece_name}")
        if piece.is_placed:
            raise ValueError(f"Piece {piece_name} is already placed")

        piece.place_at(row, col)

    def pass_turn(self) -> None:
        """Mark that the player has passed their turn."""
        self.has_passed = True

    def reset_pass(self) -> None:
        """Reset the pass state (e.g., at the start of a new round)."""
        self.has_passed = False

    def set_inactive(self) -> None:
        """Mark the player as inactive (e.g., when they can no longer play)."""
        self.is_active = False

    def set_active(self) -> None:
        """Mark the player as active."""
        self.is_active = True

    def get_piece_names(self) -> List[str]:
        """
        Get a list of all piece names.

        Returns:
            Sorted list of piece names
        """
        return sorted(self.pieces.keys())

    def __repr__(self) -> str:
        """String representation of Player."""
        placed_count = len(self.get_placed_pieces())
        unplaced_count = len(self.get_unplaced_pieces())
        return (
            f"Player(id={self.player_id}, name='{self.name}', "
            f"score={self.score}, placed={placed_count}, "
            f"unplaced={unplaced_count})"
        )
