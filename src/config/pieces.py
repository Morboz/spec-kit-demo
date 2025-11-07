"""
Blokus Piece Definitions

This module contains the definitions of all 21 standard Blokus pieces.
Each piece is defined by its name and coordinates relative to an origin (0,0).

All coordinates represent connected squares (orthogonally adjacent).
"""

from typing import List, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from src.models.piece import Piece

# Standard Blokus piece definitions (21 total)
# Each piece is defined by its coordinates relative to the origin (0,0)
PIECE_DEFINITIONS = {
    # 1-square piece (1 piece)
    "I1": [(0, 0)],
    
    # 2-square piece (1 piece)
    "I2": [(0, 0), (1, 0)],
    
    # 3-square pieces (2 pieces)
    "I3": [(0, 0), (1, 0), (2, 0)],  # Straight line
    "V3": [(0, 0), (1, 0), (1, 1)],  # L-shape (corner)
    
    # 4-square pieces (5 pieces)
    "I4": [(0, 0), (1, 0), (2, 0), (3, 0)],  # Straight line
    "L4": [(0, 0), (0, 1), (0, 2), (1, 2)],  # L-shape
    "O4": [(0, 0), (0, 1), (1, 0), (1, 1)],  # Square (2x2)
    "T4": [(0, 0), (0, 1), (0, 2), (1, 1)],  # T-shape
    "Z4": [(0, 0), (0, 1), (1, 1), (1, 2)],  # Z-shape
    
    # 5-square pieces (12 pieces)
    "I5": [(0, 0), (1, 0), (2, 0), (3, 0), (4, 0)],  # Straight line
    "L5": [(0, 0), (0, 1), (0, 2), (0, 3), (1, 3)],  # L-shape
    "V5": [(0, 0), (1, 0), (2, 0), (2, 1), (2, 2)],  # V-shape (elongated L)
    "U5": [(0, 0), (0, 1), (1, 0), (1, 2), (0, 2)],  # U-shape
    "T5": [(0, 0), (0, 1), (0, 2), (1, 1), (2, 1)],  # T-shape
    "W5": [(0, 0), (1, 0), (1, 1), (2, 1), (2, 2)],  # W-shape (stairs)
    "X5": [(1, 0), (0, 1), (1, 1), (2, 1), (1, 2)],  # Plus/Cross
    "Y5": [(0, 0), (1, 0), (2, 0), (3, 0), (2, 1)],  # Y-shape
    "F5": [(1, 0), (2, 0), (0, 1), (1, 1), (1, 2)],  # F-shape
    "P5": [(0, 0), (1, 0), (0, 1), (1, 1), (0, 2)],  # P-shape
    "Z5": [(0, 0), (0, 1), (1, 1), (2, 1), (2, 2)],  # Z-shape (elongated)
    "N5": [(0, 0), (1, 0), (1, 1), (2, 1), (3, 1)],  # N-shape
}

# Player colors (RGB hex values)
PLAYER_COLORS = {
    1: "#FF0000",  # Red
    2: "#00FF00",  # Green
    3: "#0000FF",  # Blue
    4: "#FFFF00",  # Yellow
}

# Starting corner positions for each player
# Player 1: top-left (0, 0)
# Player 2: top-right (0, 19)
# Player 3: bottom-right (19, 19)
# Player 4: bottom-left (19, 0)
PLAYER_STARTING_CORNERS = {
    1: (0, 0),
    2: (0, 19),
    3: (19, 19),
    4: (19, 0),
}


def get_piece_coordinates(piece_name: str) -> List[Tuple[int, int]]:
    """
    Get the coordinates for a specific piece.

    Args:
        piece_name: Name of the piece (e.g., "I1", "L4", "X5")

    Returns:
        List of (row, col) coordinate tuples

    Raises:
        KeyError: If piece_name is not found in PIECE_DEFINITIONS
    """
    if piece_name not in PIECE_DEFINITIONS:
        raise KeyError(f"Unknown piece: {piece_name}")
    return PIECE_DEFINITIONS[piece_name]


def get_all_piece_names() -> List[str]:
    """
    Get a list of all available piece names.

    Returns:
        Sorted list of all 21 piece names
    """
    return sorted(PIECE_DEFINITIONS.keys())


def get_piece_size(piece_name: str) -> int:
    """
    Get the size (number of squares) for a specific piece.

    Args:
        piece_name: Name of the piece

    Returns:
        Number of squares in the piece
    """
    return len(PIECE_DEFINITIONS[piece_name])


def get_player_color(player_id: int) -> str:
    """
    Get the color for a specific player.

    Args:
        player_id: Player ID (1-4)

    Returns:
        Hex color string

    Raises:
        ValueError: If player_id is not in range 1-4
    """
    if player_id not in PLAYER_COLORS:
        raise ValueError(f"Invalid player_id: {player_id}. Must be 1-4.")
    return PLAYER_COLORS[player_id]


def get_starting_corner(player_id: int) -> Tuple[int, int]:
    """
    Get the starting corner position for a specific player.

    Args:
        player_id: Player ID (1-4)

    Returns:
        Tuple of (row, col) for the player's starting corner

    Raises:
        ValueError: If player_id is not in range 1-4
    """
    if player_id not in PLAYER_STARTING_CORNERS:
        raise ValueError(f"Invalid player_id: {player_id}. Must be 1-4.")
    return PLAYER_STARTING_CORNERS[player_id]


def validate_piece_coordinates(coordinates: List[Tuple[int, int]]) -> bool:
    """
    Validate that a set of coordinates represents a connected piece.

    Args:
        coordinates: List of (row, col) tuples

    Returns:
        True if coordinates are valid, False otherwise

    Note:
        A valid piece must:
        1. Have at least 1 square
        2. All squares must be orthogonally connected (no diagonal-only
           connections)
    """
    if not coordinates:
        return False

    # Check that all coordinates are unique
    if len(coordinates) != len(set(coordinates)):
        return False

    # Convert to set for O(1) lookup
    coord_set = set(coordinates)

    # Check connectivity using BFS
    visited = set()
    to_visit = [coordinates[0]]

    while to_visit:
        current = to_visit.pop(0)
        if current in visited:
            continue

        visited.add(current)

        # Check all 4 orthogonal neighbors
        row, col = current
        neighbors = [
            (row - 1, col),  # Up
            (row + 1, col),  # Down
            (row, col - 1),  # Left
            (row, col + 1),  # Right
        ]

        for neighbor in neighbors:
            if neighbor in coord_set and neighbor not in visited:
                to_visit.append(neighbor)

    # All coordinates must be reachable
    return len(visited) == len(coordinates)


def get_piece(piece_name: str) -> "Piece":
    """
    Create and return a new Piece object.

    Args:
        piece_name: Name of the piece (e.g., "I1", "L4", "X5")

    Returns:
        A new Piece instance

    Raises:
        KeyError: If piece_name is not found in PIECE_DEFINITIONS
    """
    from src.models.piece import Piece
    return Piece(piece_name)


def get_full_piece_set() -> List["Piece"]:
    """
    Create and return a complete set of all 21 standard Blokus pieces.

    Returns:
        List of all 21 Piece instances

    Example:
        >>> pieces = get_full_piece_set()
        >>> len(pieces)
        21
    """
    from src.models.piece import Piece
    return [Piece(name) for name in get_all_piece_names()]
