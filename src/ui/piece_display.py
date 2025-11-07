"""
Piece Display UI Component

This module provides the PieceDisplay class which shows a piece with
rotation and flip controls for gameplay.
"""

import tkinter as tk
from collections.abc import Callable
from tkinter import ttk

from src.models.piece import Piece


class PieceDisplay(ttk.Frame):
    """UI component for displaying and manipulating a piece."""

    def __init__(
        self,
        parent: tk.Widget,
        on_place_piece: Callable[[int, int], None] | None = None,
        on_rotate: Callable[[], None] | None = None,
        on_flip: Callable[[], None] | None = None,
    ) -> None:
        """
        Initialize the piece display.

        Args:
            parent: Parent widget
            on_place_piece: Callback when piece is placed (receives row, col)
            on_rotate: Callback when rotate button is clicked
            on_flip: Callback when flip button is clicked
        """
        super().__init__(parent)
        self.on_place_piece = on_place_piece
        self.on_rotate = on_rotate
        self.on_flip = on_flip
        self.current_piece: Piece | None = None
        self.canvas: tk.Canvas | None = None

        # Create widget
        self._create_widgets()

    def _create_widgets(self) -> None:
        """Create and arrange UI widgets."""
        # Title
        title_label = ttk.Label(self, text="Selected Piece", font=("Arial", 12, "bold"))
        title_label.pack(pady=(0, 10))

        # Canvas for piece display
        self.canvas = tk.Canvas(
            self,
            width=200,
            height=200,
            bg="white",
            highlightbackground="black",
            highlightthickness=1,
        )
        self.canvas.pack(pady=(0, 10))

        # Control buttons frame
        controls_frame = ttk.Frame(self)
        controls_frame.pack(fill=tk.X, pady=(0, 10))

        # Rotate button
        rotate_btn = ttk.Button(
            controls_frame, text="⟲ Rotate", command=self.rotate_piece
        )
        rotate_btn.pack(side=tk.LEFT, padx=(0, 5))

        # Flip button
        flip_btn = ttk.Button(controls_frame, text="⇋ Flip", command=self.flip_piece)
        flip_btn.pack(side=tk.LEFT, padx=(0, 5))

        # Place button
        place_btn = ttk.Button(
            controls_frame, text="✓ Place", command=self._on_place_clicked
        )
        place_btn.pack(side=tk.RIGHT)

        # Instructions
        instructions = ttk.Label(
            self,
            text="Select a piece, rotate/flip as needed,\nthen click board to place",
            font=("Arial", 9),
            justify=tk.CENTER,
        )
        instructions.pack(pady=(5, 0))

    def set_piece(self, piece: Piece | None) -> None:
        """
        Set the piece to display.

        Args:
            piece: Piece to display, or None to clear
        """
        self.current_piece = piece
        self._redraw()

    def rotate_piece(self) -> None:
        """Rotate the current piece 90 degrees clockwise."""
        if self.on_rotate:
            # Call the external handler to rotate the piece
            self.on_rotate()
        elif self.current_piece and not self.current_piece.is_placed:
            # Fallback: rotate locally if no callback
            self.current_piece = self.current_piece.rotate(90)
            self._redraw()

    def flip_piece(self) -> None:
        """Flip the current piece horizontally."""
        if self.on_flip:
            # Call the external handler to flip the piece
            self.on_flip()
        elif self.current_piece and not self.current_piece.is_placed:
            # Fallback: flip locally if no callback
            self.current_piece = self.current_piece.flip()
            self._redraw()

    def _on_place_clicked(self) -> None:
        """Handle place button click.

        This is a stub - actual placement happens via board clicks.
        The place button is provided for future keyboard shortcuts.
        """
        pass

    def _redraw(self) -> None:
        """Redraw the piece on the canvas."""
        if not self.canvas:
            return

        # Clear canvas
        self.canvas.delete("all")

        if not self.current_piece:
            # Draw placeholder
            self.canvas.create_text(
                100,
                100,
                text="No piece selected",
                fill="gray",
                font=("Arial", 10),
                justify=tk.CENTER,
            )
            return

        # Calculate drawing parameters
        piece_coords = self.current_piece.coordinates
        if not piece_coords:
            return

        # Find bounds
        min_row = min(row for row, col in piece_coords)
        max_row = max(row for row, col in piece_coords)
        min_col = min(col for row, col in piece_coords)
        max_col = max(col for row, col in piece_coords)

        # Calculate scaling
        width = max_col - min_col + 1
        height = max_row - min_row + 1
        cell_size = min(180 // width, 180 // height)

        # Center the piece
        offset_x = (200 - width * cell_size) // 2
        offset_y = (200 - height * cell_size) // 2

        # Draw piece squares
        for row, col in piece_coords:
            # Normalize to top-left
            norm_row = row - min_row
            norm_col = col - min_col

            # Calculate pixel positions
            x1 = offset_x + norm_col * cell_size
            y1 = offset_y + norm_row * cell_size
            x2 = x1 + cell_size
            y2 = y1 + cell_size

            # Draw square
            self.canvas.create_rectangle(
                x1, y1, x2, y2, fill="lightblue", outline="black", width=2
            )

            # Draw grid lines for better visibility
            for i in range(1, cell_size, max(1, cell_size // 4)):
                self.canvas.create_line(x1 + i, y1, x1 + i, y2, fill="black", width=1)
                self.canvas.create_line(x1, y1 + i, x2, y1 + i, fill="black", width=1)

    def clear(self) -> None:
        """Clear the display."""
        self.current_piece = None
        self._redraw()
