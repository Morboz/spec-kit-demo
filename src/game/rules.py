"""
Blokus Rules Validator

This module implements the rules validation for Blokus game moves.
It enforces the official Blokus rules including:
- First move must be in player's starting corner
- Pieces must not overlap
- Pieces must not have edge-to-edge contact with own pieces
- Pieces can touch opponent pieces
- Pieces must be within board bounds
"""

from typing import List, Tuple, Set, Dict, Optional
from src.models.board import Board
from src.models.player import Player
from src.models.piece import Piece
from src.models.game_state import GameState


class ValidationResult:
    """Result of a move validation."""

    def __init__(self, is_valid: bool, reason: str = "") -> None:
        """
        Initialize validation result.

        Args:
            is_valid: True if move is valid
            reason: Explanation if invalid
        """
        self.is_valid = is_valid
        self.reason = reason

    def __repr__(self) -> str:
        """String representation of validation result."""
        if self.is_valid:
            return "ValidationResult(valid=True)"
        return f"ValidationResult(valid=False, reason='{self.reason}')"


class BlokusRules:
    """Validates moves according to Blokus rules."""

    @staticmethod
    def validate_move(
        game_state: GameState,
        player_id: int,
        piece: Piece,
        anchor_row: int,
        anchor_col: int,
    ) -> ValidationResult:
        """
        Validate a piece placement move.

        Args:
            game_state: Current game state
            player_id: ID of the player making the move
            piece: Piece to place
            anchor_row: Row where piece origin will be placed
            anchor_col: Column where piece origin will be placed

        Returns:
            ValidationResult indicating if move is valid
        """
        # Get the player
        player = game_state.get_player_by_id(player_id)
        if player is None:
            return ValidationResult(False, "Player not found")

        # Check if piece belongs to player
        if player.get_piece(piece.name) is None:
            return ValidationResult(False, "Player does not own this piece")

        # Check if piece is already placed
        if piece.is_placed:
            return ValidationResult(False, "Piece is already placed")

        # Get absolute positions for the piece
        positions = piece.get_absolute_positions(anchor_row, anchor_col)

        # Check board bounds
        bounds_result = BlokusRules._check_board_bounds(positions, game_state.board)
        if not bounds_result.is_valid:
            return bounds_result

        # Check overlap with existing pieces
        overlap_result = BlokusRules._check_overlap(positions, game_state.board)
        if not overlap_result.is_valid:
            return overlap_result

        # Check adjacency rules (must not touch own pieces edge-to-edge)
        adjacency_result = BlokusRules._check_adjacency(
            positions, player_id, game_state.board
        )
        if not adjacency_result.is_valid:
            return adjacency_result

        # Check corner placement rule (first move must be in player's corner)
        if BlokusRules._is_first_move(player, game_state):
            corner_result = BlokusRules._check_first_move_corner(
                positions, player, game_state
            )
            if not corner_result.is_valid:
                return corner_result
        else:
            # For non-first moves, must have corner-to-corner contact with own pieces
            corner_contact_result = BlokusRules._check_corner_connection(
                positions, player_id, game_state.board
            )
            if not corner_contact_result.is_valid:
                return corner_contact_result

        return ValidationResult(True, "Move is valid")

    @staticmethod
    def _check_board_bounds(
        positions: List[Tuple[int, int]], board: Board
    ) -> ValidationResult:
        """
        Check that all positions are within board bounds.

        Args:
            positions: List of (row, col) positions
            board: Game board

        Returns:
            ValidationResult
        """
        for row, col in positions:
            if not board.is_position_valid(row, col):
                return ValidationResult(
                    False, f"Position ({row}, {col}) is outside board bounds"
                )
        return ValidationResult(True, "All positions within bounds")

    @staticmethod
    def _check_overlap(
        positions: List[Tuple[int, int]], board: Board
    ) -> ValidationResult:
        """
        Check that positions don't overlap with existing pieces.

        Args:
            positions: List of (row, col) positions
            board: Game board

        Returns:
            ValidationResult
        """
        occupied = board.get_occupied_positions()
        for row, col in positions:
            if (row, col) in occupied:
                return ValidationResult(
                    False, f"Position ({row}, {col}) is already occupied"
                )
        return ValidationResult(True, "No overlap")

    @staticmethod
    def _check_adjacency(
        positions: List[Tuple[int, int]], player_id: int, board: Board
    ) -> ValidationResult:
        """
        Check that piece doesn't have edge-to-edge contact with own pieces.

        Note: Diagonal contact is allowed, edge-to-edge is not.

        Args:
            positions: List of (row, col) positions for new piece
            player_id: ID of the player placing the piece
            board: Game board

        Returns:
            ValidationResult
        """
        player_positions = board.get_player_positions(player_id)

        for row, col in positions:
            # Check all 4 orthogonal neighbors
            neighbors = [
                (row - 1, col),  # Up
                (row + 1, col),  # Down
                (row, col - 1),  # Left
                (row, col + 1),  # Right
            ]

            for neighbor_row, neighbor_col in neighbors:
                if (neighbor_row, neighbor_col) in player_positions:
                    return ValidationResult(
                        False,
                        f"Piece would have edge-to-edge contact with own piece at "
                        f"({neighbor_row}, {neighbor_col})",
                    )

        return ValidationResult(True, "No edge-to-edge contact with own pieces")

    @staticmethod
    def _check_corner_connection(
        positions: List[Tuple[int, int]], player_id: int, board: Board
    ) -> ValidationResult:
        """
        Check that piece has corner-to-corner contact with at least one own piece.

        This is required for all moves after the first move.
        Diagonal (corner-to-corner) contact is required.

        Args:
            positions: List of (row, col) positions for new piece
            player_id: ID of the player placing the piece
            board: Game board

        Returns:
            ValidationResult
        """
        player_positions = board.get_player_positions(player_id)

        # If player has no pieces yet, this check should not be called
        if not player_positions:
            return ValidationResult(
                False, "Player has no pieces on board (should use first move rule)"
            )

        # Check if any square of the new piece has diagonal contact with own pieces
        for row, col in positions:
            # Check all 4 diagonal neighbors
            diagonal_neighbors = [
                (row - 1, col - 1),  # Upper-left
                (row - 1, col + 1),  # Upper-right
                (row + 1, col - 1),  # Lower-left
                (row + 1, col + 1),  # Lower-right
            ]

            for neighbor_row, neighbor_col in diagonal_neighbors:
                if (neighbor_row, neighbor_col) in player_positions:
                    # Found corner-to-corner contact with own piece
                    return ValidationResult(
                        True, "Piece has corner-to-corner contact with own piece"
                    )

        return ValidationResult(
            False,
            "Piece must touch at least one of your own pieces corner-to-corner (diagonally)",
        )

    @staticmethod
    def _is_first_move(player: Player, game_state: GameState) -> bool:
        """
        Check if this is the player's first move.

        Args:
            player: Player to check
            game_state: Current game state

        Returns:
            True if this is the player's first move
        """
        placed_pieces = player.get_placed_pieces()
        return len(placed_pieces) == 0

    @staticmethod
    def _check_first_move_corner(
        positions: List[Tuple[int, int]], player: Player, game_state: GameState
    ) -> ValidationResult:
        """
        Check that first move is in player's starting corner.

        Args:
            positions: List of (row, col) positions for the piece
            player: Player making the move
            game_state: Current game state

        Returns:
            ValidationResult
        """
        corner_row, corner_col = player.get_starting_corner()

        # At least one square of the piece must be in the corner
        for row, col in positions:
            if row == corner_row and col == corner_col:
                return ValidationResult(
                    True, "First move correctly placed in starting corner"
                )

        return ValidationResult(
            False,
            f"First move must include corner position ({corner_row}, {corner_col})",
        )

    @staticmethod
    def get_valid_moves(
        game_state: GameState, player_id: int, piece: Piece
    ) -> List[Tuple[int, int]]:
        """
        Get all valid anchor positions for a piece.

        This is a utility method that can be used for AI or to show
        valid moves to players.

        Args:
            game_state: Current game state
            player_id: ID of the player
            piece: Piece to check

        Returns:
            List of (row, col) tuples representing valid anchor positions
        """
        # Try all possible anchor positions on the board
        valid_moves = []
        board = game_state.board

        for row in range(board.size):
            for col in range(board.size):
                result = BlokusRules.validate_move(
                    game_state, player_id, piece, row, col
                )
                if result.is_valid:
                    valid_moves.append((row, col))

        return valid_moves

    @staticmethod
    def get_invalid_positions(
        game_state: GameState, player_id: int, piece: Piece
    ) -> Dict[Tuple[int, int], str]:
        """
        Get all invalid positions and their reasons.

        This is useful for displaying error messages to players.

        Args:
            game_state: Current game state
            player_id: ID of the player
            piece: Piece to check

        Returns:
            Dictionary mapping (row, col) to error reason
        """
        invalid_moves = {}
        board = game_state.board

        for row in range(board.size):
            for col in range(board.size):
                result = BlokusRules.validate_move(
                    game_state, player_id, piece, row, col
                )
                if not result.is_valid:
                    invalid_moves[(row, col)] = result.reason

        return invalid_moves
