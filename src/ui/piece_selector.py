"""
Piece Selector UI Component

This module provides the PieceSelector class which allows players to select
from their available pieces during gameplay with visual representations.
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional, Callable, Dict
from src.models.player import Player
from src.config.pieces import PIECE_DEFINITIONS, get_player_color


class PieceSelector(ttk.Frame):
    """UI component for selecting pieces from player's inventory."""

    def __init__(
        self,
        parent: tk.Widget,
        player: Player,
        on_piece_selected: Optional[Callable[[str], None]] = None,
    ) -> None:
        """
        Initialize the piece selector.

        Args:
            parent: Parent widget
            player: Player whose pieces to display
            on_piece_selected: Callback when a piece is selected
        """
        super().__init__(parent)
        self.player = player
        self.on_piece_selected = on_piece_selected
        self.selected_piece: Optional[str] = None
        self.piece_canvases: Dict[str, tk.Canvas] = {}  # Map piece name to canvas
        self.selected_canvas: Optional[tk.Canvas] = None

        self._create_widgets()
        self._update_piece_list()

    def _create_widgets(self) -> None:
        """Create and arrange UI widgets."""
        # Title (use StringVar so we can update it)
        self.title_var = tk.StringVar(value=f"{self.player.name}'s Pieces")
        self.title_label = ttk.Label(
            self, textvariable=self.title_var, font=("Arial", 12, "bold")
        )
        self.title_label.pack(pady=(0, 10))

        # Scrollable frame for pieces
        self.canvas = tk.Canvas(self, height=200)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")),
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def _update_piece_list(self) -> None:
        """Update the list of available pieces with visual representations."""
        # Clear existing widgets
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.piece_canvases.clear()

        # Get unplaced pieces sorted by size
        unplaced_pieces = self.player.get_unplaced_pieces()
        
        # Sort by size (number of squares)
        unplaced_pieces.sort(key=lambda p: (p.size, p.name))

        # Group by size and create visual representations
        current_size = None
        for piece in unplaced_pieces:
            # Add separator between different sizes
            if current_size is not None and current_size != piece.size:
                ttk.Separator(self.scrollable_frame, orient='horizontal').pack(
                    fill=tk.X, pady=3
                )
            current_size = piece.size
            
            # Create piece frame
            piece_frame = ttk.Frame(self.scrollable_frame)
            piece_frame.pack(fill=tk.X, pady=3, padx=5)

            # Create canvas for piece visualization
            canvas = tk.Canvas(
                piece_frame,
                width=100,
                height=100,
                bg="white",
                highlightthickness=2,
                highlightbackground="gray",
                cursor="hand2"
            )
            canvas.pack(side=tk.LEFT, padx=(0, 8))
            
            # Store canvas reference
            self.piece_canvases[piece.name] = canvas
            
            # Draw the piece
            self._draw_piece_on_canvas(canvas, piece.name)
            
            # Make canvas clickable
            canvas.bind("<Button-1>", lambda e, pn=piece.name: self._select_piece(pn))
            
            # Info label
            info_frame = ttk.Frame(piece_frame)
            info_frame.pack(side=tk.LEFT, fill=tk.Y)
            
            name_label = ttk.Label(
                info_frame,
                text=piece.name,
                font=("Arial", 10, "bold")
            )
            name_label.pack(anchor=tk.W)
            
            size_label = ttk.Label(
                info_frame,
                text=f"{piece.size} square{'s' if piece.size > 1 else ''}",
                font=("Arial", 8),
                foreground="gray"
            )
            size_label.pack(anchor=tk.W)
    
    def _draw_piece_on_canvas(
        self, 
        canvas: tk.Canvas, 
        piece_name: str
    ) -> None:
        """
        Draw a visual representation of a piece on canvas.

        Args:
            canvas: Canvas to draw on
            piece_name: Name of the piece
        """
        if piece_name not in PIECE_DEFINITIONS:
            return
        
        coords = PIECE_DEFINITIONS[piece_name]
        
        # Calculate bounds
        rows = [r for r, c in coords]
        cols = [c for r, c in coords]
        min_row, max_row = min(rows), max(rows)
        min_col, max_col = min(cols), max(cols)
        
        piece_height = max_row - min_row + 1
        piece_width = max_col - min_col + 1
        
        # Calculate cell size to fit in canvas
        canvas_width = 100
        canvas_height = 100
        padding = 8
        
        cell_size = min(
            (canvas_width - 2 * padding) // max(piece_width, 1),
            (canvas_height - 2 * padding) // max(piece_height, 1)
        )
        cell_size = min(cell_size, 22)  # Max cell size
        
        # Calculate offset to center the piece
        total_width = piece_width * cell_size
        total_height = piece_height * cell_size
        offset_x = (canvas_width - total_width) // 2
        offset_y = (canvas_height - total_height) // 2
        
        # Get player color
        color = get_player_color(self.player.player_id)
        
        # Draw each square
        for row, col in coords:
            x = offset_x + (col - min_col) * cell_size
            y = offset_y + (row - min_row) * cell_size
            
            # Draw filled rectangle
            canvas.create_rectangle(
                x, y,
                x + cell_size, y + cell_size,
                fill=color,
                outline="black",
                width=2
            )

    def _select_piece(self, piece_name: str) -> None:
        """Handle piece selection.

        Args:
            piece_name: Name of selected piece
        """
        self.selected_piece = piece_name

        # Clear all canvas highlights
        for canvas in self.piece_canvases.values():
            canvas.configure(highlightbackground="gray", highlightthickness=2)

        # Highlight selected canvas
        if piece_name in self.piece_canvases:
            canvas = self.piece_canvases[piece_name]
            canvas.configure(highlightbackground="blue", highlightthickness=3)
            self.selected_canvas = canvas

        # Call callback if provided
        if self.on_piece_selected:
            self.on_piece_selected(piece_name)

    def get_selected_piece(self) -> Optional[str]:
        """
        Get the currently selected piece.

        Returns:
            Name of selected piece or None
        """
        return self.selected_piece

    def clear_selection(self) -> None:
        """Clear the current selection."""
        self.selected_piece = None
        self.selected_canvas = None
        # Reset all canvas borders
        for canvas in self.piece_canvases.values():
            canvas.configure(highlightbackground="gray", highlightthickness=2)

    def refresh(self) -> None:
        """Refresh the piece list (e.g., after placing a piece)."""
        self._update_piece_list()
        self.clear_selection()

    def set_player(self, new_player: Player) -> None:
        """Update the player reference and refresh the display.

        Args:
            new_player: The new player whose pieces to display
        """
        self.player = new_player
        # Update the title to show the new player's name
        self.title_var.set(f"{new_player.name}'s Pieces")
        self.refresh()
