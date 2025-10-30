"""
Board Click Handler

This module provides the BoardClickHandler class which manages click events
on the game board for piece placement.
"""

from typing import Optional, Callable, Tuple
from src.models.board import Board
from src.models.player import Player
from src.models.game_state import GameState


class BoardClickHandler:
    """Handler for board click events."""

    def __init__(
        self, board: Board, game_state: GameState, current_player: Player
    ) -> None:
        """
        Initialize the click handler.

        Args:
            board: Game board
            game_state: Current game state
            current_player: Current player
        """
        self.board = board
        self.game_state = game_state
        self.current_player = current_player
        self.selected_piece: Optional[str] = None
        self.on_placement_attempt: Optional[Callable[[str, int, int], None]] = None

    def set_selected_piece(self, piece_name: str) -> None:
        """
        Set the currently selected piece.

        Args:
            piece_name: Name of selected piece
        """
        self.selected_piece = piece_name

    def handle_click(self, row: int, col: int) -> Tuple[bool, Optional[str]]:
        """
        Handle a click on the board.

        Args:
            row: Clicked row
            col: Clicked column

        Returns:
            Tuple of (success, error_message)
                - success: True if placement was successful
                - error_message: Error message if failed, None if successful
        """
        # Check if a piece is selected
        if not self.selected_piece:
            return False, "No piece selected"

        # Get the piece
        piece = self.current_player.get_piece(self.selected_piece)
        if not piece:
            return False, f"Player does not have piece: {self.selected_piece}"

        if piece.is_placed:
            return False, f"Piece {self.selected_piece} is already placed"

        # Try to place the piece
        try:
            # Get the transformed piece (with rotation/flips applied in PieceDisplay)
            # For now, we use the base piece
            positions = self.board.place_piece(
                piece, row, col, self.current_player.player_id
            )

            # Mark piece as placed on player
            self.current_player.place_piece(self.selected_piece, row, col)

            # Record the move in game state
            self.game_state.record_move(
                player_id=self.current_player.player_id,
                piece_name=self.selected_piece,
                row=row,
                col=col,
            )

            # Advance to next player's turn
            self.game_state.next_turn()

            return True, None

        except ValueError as e:
            # Validation failed
            return False, str(e)

    def get_current_piece(self) -> Optional[str]:
        """
        Get the currently selected piece name.

        Returns:
            Name of selected piece or None
        """
        return self.selected_piece

    def clear_selection(self) -> None:
        """Clear the selected piece."""
        self.selected_piece = None
