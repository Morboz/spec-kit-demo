"""
Placement Preview UI Component

This module provides real-time validation feedback for piece placement.
It validates moves as the player hovers over board positions and shows
preview of valid/invalid placement with visual indicators.
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional, List, Tuple, Dict
from src.models.board import Board
from src.models.player import Player
from src.models.game_state import GameState
from src.game.rules import BlokusRules, ValidationResult


class PlacementPreview:
    """
    Manages real-time validation feedback for piece placement.

    This class provides:
    - Real-time validation as player hovers over positions
    - Visual indicators for valid/invalid placements
    - Preview of piece position before actual placement
    """

    def __init__(
        self,
        board_canvas: tk.Canvas,
        game_state: GameState,
        error_display: Optional[ttk.Frame] = None,
    ):
        """
        Initialize the placement preview.

        Args:
            board_canvas: The game board canvas
            game_state: Current game state
            error_display: Optional error display component
        """
        self.board_canvas = board_canvas
        self.game_state = game_state
        self.error_display = error_display

        # Current preview state
        self.current_piece: Optional[object] = None
        self.current_player_id: Optional[int] = None
        self.preview_positions: List[Tuple[int, int]] = []
        self.preview_rectangles: List[int] = []
        self.is_active = False

        # Visual settings
        self.valid_color = "#00AA00"  # Green for valid
        self.invalid_color = "#CC0000"  # Red for invalid
        self.preview_alpha = 0.5  # Transparency for preview

        # Bind mouse events
        self.board_canvas.bind("<Motion>", self.on_mouse_move)
        self.board_canvas.bind("<Leave>", self.on_mouse_leave)

    def activate(
        self, piece: object, player_id: int, rotated_piece: Optional[object] = None
    ):
        """
        Activate preview mode for a piece.

        Args:
            piece: The piece to preview
            player_id: ID of the player
            rotated_piece: Optional pre-rotated piece
        """
        if rotated_piece is not None:
            self.current_piece = rotated_piece
        else:
            self.current_piece = piece

        self.current_player_id = player_id
        self.is_active = True

    def deactivate(self):
        """Deactivate preview mode and clear preview."""
        self.is_active = False
        self.current_piece = None
        self.current_player_id = None
        self.clear_preview()

    def on_mouse_move(self, event):
        """
        Handle mouse movement over the board.

        Args:
            event: Tkinter mouse event
        """
        if not self.is_active or self.current_piece is None:
            return

        # Get board position from mouse coordinates
        row, col = self.get_board_position(event.x, event.y)

        if row is None or col is None:
            self.clear_preview()
            return

        # Validate move at this position
        result = BlokusRules.validate_move(
            self.game_state, self.current_player_id, self.current_piece, row, col
        )

        # Update preview
        self.show_preview(row, col, result)

        # Show error message if invalid
        if self.error_display and not result.is_valid:
            self.error_display.show_validation_error(
                result.reason, self._get_rule_type(result.reason)
            )

    def on_mouse_leave(self, event):
        """
        Handle mouse leaving the board.

        Args:
            event: Tkinter mouse event
        """
        self.clear_preview()
        if self.error_display:
            self.error_display.hide()

    def get_board_position(self, x: int, y: int) -> Tuple[Optional[int], Optional[int]]:
        """
        Convert canvas coordinates to board position.

        Args:
            x: Canvas x coordinate
            y: Canvas y coordinate

        Returns:
            Tuple of (row, col) or (None, None) if invalid
        """
        # This would depend on your board canvas implementation
        # Assuming 20x20 grid with known cell size
        cell_size = 25  # pixels per cell
        board_origin_x = 50  # offset from canvas edge
        board_origin_y = 50

        col = int((x - board_origin_x) / cell_size)
        row = int((y - board_origin_y) / cell_size)

        # Validate bounds
        if 0 <= row < 20 and 0 <= col < 20:
            return row, col

        return None, None

    def show_preview(
        self, row: int, col: int, validation_result: ValidationResult
    ):
        """
        Show preview of piece at specified position.

        Args:
            row: Board row
            col: Board column
            validation_result: Result of validation
        """
        # Clear previous preview
        self.clear_preview()

        # Get piece positions
        positions = self.current_piece.get_absolute_positions(row, col)

        # Store for cleanup
        self.preview_positions = positions

        # Choose color based on validity
        color = self.valid_color if validation_result.is_valid else self.invalid_color

        # Draw preview rectangles
        cell_size = 25
        board_origin_x = 50
        board_origin_y = 50

        for pos_row, pos_col in positions:
            # Calculate pixel coordinates
            x1 = board_origin_x + pos_col * cell_size
            y1 = board_origin_y + pos_row * cell_size
            x2 = x1 + cell_size
            y2 = y1 + cell_size

            # Draw rectangle
            rect_id = self.board_canvas.create_rectangle(
                x1, y1, x2, y2, fill=color, outline=color, stipple="gray50"
            )
            self.preview_rectangles.append(rect_id)

    def clear_preview(self):
        """Clear all preview indicators."""
        for rect_id in self.preview_rectangles:
            self.board_canvas.delete(rect_id)

        self.preview_rectangles.clear()
        self.preview_positions.clear()

    def _get_rule_type(self, reason: str) -> Optional[str]:
        """
        Determine rule type from error message.

        Args:
            reason: Error message

        Returns:
            Rule type string or None
        """
        reason_lower = reason.lower()

        if "corner" in reason_lower:
            return "corner"
        elif "bounds" in reason_lower or "outside" in reason_lower:
            return "bounds"
        elif "occupied" in reason_lower or "overlap" in reason_lower:
            return "overlap"
        elif "contact" in reason_lower:
            return "adjacency"

        return None

    def get_valid_moves(self, piece: object, player_id: int) -> Dict[Tuple[int, int], str]:
        """
        Get all valid moves for a piece with reasons for invalid moves.

        Args:
            piece: The piece to check
            player_id: ID of the player

        Returns:
            Dictionary mapping (row, col) to error reason for invalid moves
        """
        return BlokusRules.get_invalid_positions(self.game_state, player_id, piece)

    def is_position_valid(self, row: int, col: int) -> bool:
        """
        Check if current piece can be placed at position.

        Args:
            row: Board row
            col: Board column

        Returns:
            True if valid, False otherwise
        """
        if not self.is_active or self.current_piece is None:
            return False

        result = BlokusRules.validate_move(
            self.game_state, self.current_player_id, self.current_piece, row, col
        )

        return result.is_valid

    def get_validation_result(self, row: int, col: int) -> Optional[ValidationResult]:
        """
        Get validation result for current piece at position.

        Args:
            row: Board row
            col: Board column

        Returns:
            ValidationResult or None if not active
        """
        if not self.is_active or self.current_piece is None:
            return None

        return BlokusRules.validate_move(
            self.game_state, self.current_player_id, self.current_piece, row, col
        )
