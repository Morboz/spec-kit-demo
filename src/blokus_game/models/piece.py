"""
Piece model for Blokus game.

This module defines the Piece class which represents a geometric piece
that players place on the board.
"""

from blokus_game.config.pieces import get_piece_coordinates


class Piece:
    """Represents a Blokus game piece."""

    def __init__(self, name: str) -> None:
        """
        Initialize a new Piece.

        Args:
            name: Name of the piece (e.g., "I1", "L4", "X5")

        Raises:
            KeyError: If piece name is not found in standard definitions
        """
        self.name = name
        self.coordinates = get_piece_coordinates(name).copy()
        self.size = len(self.coordinates)
        self.is_placed = False
        self.placed_position: tuple[int, int] | None = None

    @classmethod
    def from_coordinates(cls, name: str, coordinates: list[tuple[int, int]]) -> "Piece":
        """
        Create a piece from explicit coordinates.

        Args:
            name: Name for the piece
            coordinates: List of (row, col) tuples

        Returns:
            New Piece instance
        """
        piece = cls.__new__(cls)
        piece.name = name
        piece.coordinates = coordinates.copy()
        piece.size = len(coordinates)
        piece.is_placed = False
        piece.placed_position = None
        return piece

    def rotate(self, degrees: int) -> "Piece":
        """
        Create a new piece rotated 90, 180, or 270 degrees clockwise.

        Args:
            degrees: Rotation angle (90, 180, or 270)

        Returns:
            New Piece instance with rotated coordinates

        Raises:
            ValueError: If degrees is not 90, 180, or 270
        """
        if degrees not in [90, 180, 270]:
            raise ValueError("Rotation angle must be 90, 180, or 270")

        # Create a new piece instance
        rotated = Piece.__new__(Piece)
        rotated.name = self.name
        rotated.size = self.size
        rotated.is_placed = False
        rotated.placed_position = None

        # Apply rotation transformation
        rotated.coordinates = self._rotate_coordinates(self.coordinates, degrees)
        return rotated

    def _rotate_coordinates(
        self, coords: list[tuple[int, int]], degrees: int
    ) -> list[tuple[int, int]]:
        """
        Rotate coordinates by specified degrees.

        Args:
            coords: List of (row, col) coordinates
            degrees: Rotation angle

        Returns:
            List of rotated coordinates
        """
        if degrees == 90:
            # (x, y) -> (-y, x)
            return [(-y, x) for x, y in coords]
        elif degrees == 180:
            # (x, y) -> (-x, -y)
            return [(-x, -y) for x, y in coords]
        elif degrees == 270:
            # (x, y) -> (y, -x)
            return [(y, -x) for x, y in coords]
        else:
            raise ValueError(f"Invalid rotation angle: {degrees}")

    def flip(self) -> "Piece":
        """
        Create a new piece mirrored horizontally.

        Returns:
            New Piece instance with flipped coordinates
        """
        # Create a new piece instance
        flipped = Piece.__new__(Piece)
        flipped.name = self.name
        flipped.size = self.size
        flipped.is_placed = False
        flipped.placed_position = None

        # Apply flip transformation: (x, y) -> (x, -y)
        flipped.coordinates = [(x, -y) for x, y in self.coordinates]
        return flipped

    def get_absolute_positions(
        self, anchor_row: int, anchor_col: int
    ) -> list[tuple[int, int]]:
        """
        Calculate actual board positions when piece is anchored at position.

        Args:
            anchor_row: Row where piece's origin (0,0) will be placed
            anchor_col: Column where piece's origin (0,0) will be placed

        Returns:
            List of (row, col) tuples for all piece squares
        """
        return [(anchor_row + x, anchor_col + y) for x, y in self.coordinates]

    def place_at(self, row: int, col: int) -> None:
        """
        Mark piece as placed at given position.

        Args:
            row: Row where piece was placed
            col: Column where piece was placed

        Raises:
            ValueError: If piece is already placed
        """
        if self.is_placed:
            raise ValueError("Piece is already placed")

        self.is_placed = True
        self.placed_position = (row, col)

    def __repr__(self) -> str:
        """String representation of Piece."""
        return f"Piece(name={self.name}, size={self.size}, is_placed={self.is_placed})"
