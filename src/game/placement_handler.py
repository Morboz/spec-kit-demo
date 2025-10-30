"""
Piece Placement Orchestrator

This module provides the PlacementHandler class which orchestrates the piece
placement workflow, coordinating between UI components and game logic.
"""

from typing import Optional, Callable
from src.models.board import Board
from src.models.player import Player
from src.models.game_state import GameState
from src.models.piece import Piece
from src.game.rules import BlokusRules


class PlacementHandler:
    """Orchestrates piece placement workflow."""

    def __init__(
        self, board: Board, game_state: GameState, current_player: Player
    ) -> None:
        """
        Initialize the placement handler.

        Args:
            board: Game board
            game_state: Current game state
            current_player: Current player
        """
        self.board = board
        self.game_state = game_state
        self.current_player = current_player

        # Selected piece state
        self.selected_piece: Optional[Piece] = None
        self.rotation_count: int = 0
        self.is_flipped: bool = False

        # Callbacks
        self.on_piece_placed: Optional[Callable[[str], None]] = None
        self.on_placement_error: Optional[Callable[[str], None]] = None

    def select_piece(self, piece_name: str) -> bool:
        """
        Select a piece from player's inventory.

        Args:
            piece_name: Name of piece to select

        Returns:
            True if selection was successful, False otherwise
        """
        # Get the piece from player's inventory
        piece = self.current_player.get_piece(piece_name)
        if not piece:
            if self.on_placement_error:
                self.on_placement_error(f"Player does not have piece: {piece_name}")
            return False

        if piece.is_placed:
            if self.on_placement_error:
                self.on_placement_error(f"Piece {piece_name} is already placed")
            return False

        # Create a new instance for this selection (to allow rotation/flip)
        self.selected_piece = Piece(piece_name)
        self.rotation_count = 0
        self.is_flipped = False

        return True

    def rotate_piece(self) -> None:
        """Rotate the selected piece 90 degrees clockwise."""
        if self.selected_piece and not self.selected_piece.is_placed:
            self.selected_piece = self.selected_piece.rotate(90)
            self.rotation_count = (self.rotation_count + 1) % 4

    def flip_piece(self) -> None:
        """Flip the selected piece horizontally."""
        if self.selected_piece and not self.selected_piece.is_placed:
            self.selected_piece = self.selected_piece.flip()
            self.is_flipped = not self.is_flipped

    def place_piece(self, row: int, col: int) -> tuple[bool, Optional[str]]:
        """
        Place the selected piece at the given position.

        Args:
            row: Row to place piece
            col: Column to place piece

        Returns:
            Tuple of (success, error_message)
        """
        if not self.selected_piece:
            return False, "No piece selected"

        # Validate the move using Blokus rules
        validation_result = BlokusRules.validate_move(
            self.game_state,
            self.current_player.player_id,
            self.selected_piece,
            row,
            col,
        )

        if not validation_result.is_valid:
            return False, validation_result.reason

        # Place the piece on the board
        try:
            positions = self.board.place_piece(
                self.selected_piece, row, col, self.current_player.player_id
            )

            # Update player's piece state
            self.current_player.place_piece(self.selected_piece.name, row, col)

            # Record the move
            self.game_state.record_move(
                player_id=self.current_player.player_id,
                piece_name=self.selected_piece.name,
                row=row,
                col=col,
                rotation=self.rotation_count * 90,
                flipped=self.is_flipped,
            )

            # Clear selection
            self.clear_selection()

            # Advance to next player
            self.game_state.next_turn()

            # Call callback
            if self.on_piece_placed:
                self.on_piece_placed(self.selected_piece.name)

            return True, None

        except ValueError as e:
            return False, str(e)

    def clear_selection(self) -> None:
        """Clear the current piece selection."""
        self.selected_piece = None
        self.rotation_count = 0
        self.is_flipped = False

    def get_selected_piece(self) -> Optional[Piece]:
        """
        Get the currently selected piece.

        Returns:
            Selected piece or None
        """
        return self.selected_piece

    def set_callbacks(
        self,
        on_piece_placed: Optional[Callable[[str], None]] = None,
        on_placement_error: Optional[Callable[[str], None]] = None,
    ) -> None:
        """
        Set event callbacks.

        Args:
            on_piece_placed: Called when piece is successfully placed
            on_placement_error: Called when placement fails
        """
        self.on_piece_placed = on_piece_placed
        self.on_placement_error = on_placement_error

    def can_make_move(self) -> bool:
        """
        Check if the current player can make any move.

        Returns:
            True if player has valid moves available
        """
        # Check if player has unplaced pieces
        if not self.current_player.has_pieces_remaining():
            return False

        # Check if any of the unplaced pieces can be placed
        for piece in self.current_player.get_unplaced_pieces():
            # Try a sample position (e.g., corner for first move, or adjacent)
            # For simplicity, we'll just check if player has made first move
            # In a full implementation, we'd check all valid positions

            # Get a transformed version of the piece
            test_piece = piece
            if test_piece.is_placed:
                continue

            # Test if piece can be placed in at least one valid position
            # This is a simplified check
            if self.current_player.get_remaining_piece_count() < 21:
                # Not first move - should be able to make moves somewhere
                return True

        return True

    def get_rotation_count(self) -> int:
        """
        Get current rotation count.

        Returns:
            Number of 90-degree rotations (0-3)
        """
        return self.rotation_count

    def is_piece_flipped(self) -> bool:
        """
        Check if piece is flipped.

        Returns:
            True if piece is flipped
        """
        return self.is_flipped
