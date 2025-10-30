"""
Piece Selector UI Component

This module provides the PieceSelector class which allows players to select
from their available pieces during gameplay.
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional, List, Callable
from src.models.player import Player


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
        self.piece_buttons: List[ttk.Button] = []

        self._create_widgets()
        self._update_piece_list()

    def _create_widgets(self) -> None:
        """Create and arrange UI widgets."""
        # Title
        title_label = ttk.Label(
            self, text=f"{self.player.name}'s Pieces", font=("Arial", 12, "bold")
        )
        title_label.pack(pady=(0, 10))

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
        """Update the list of available pieces."""
        # Clear existing buttons
        for button in self.piece_buttons:
            button.destroy()
        self.piece_buttons.clear()

        # Get unplaced pieces
        unplaced_pieces = self.player.get_unplaced_pieces()

        # Create button for each piece
        for piece in unplaced_pieces:
            button = ttk.Button(
                self.scrollable_frame,
                text=f"{piece.name} ({piece.size} squares)",
                command=lambda p=piece.name: self._select_piece(p),
            )
            button.pack(fill=tk.X, padx=5, pady=2)
            self.piece_buttons.append(button)

    def _select_piece(self, piece_name: str) -> None:
        """Handle piece selection.

        Args:
            piece_name: Name of selected piece
        """
        self.selected_piece = piece_name

        # Highlight selected button
        for button in self.piece_buttons:
            button.state(["!pressed"])

        # Find and highlight selected button
        for piece in self.player.get_unplaced_pieces():
            if piece.name == piece_name:
                # Find corresponding button by text
                for button in self.piece_buttons:
                    if piece_name in button.cget("text"):
                        button.state(["pressed"])
                        break
                break

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
        for button in self.piece_buttons:
            button.state(["!pressed"])

    def refresh(self) -> None:
        """Refresh the piece list (e.g., after placing a piece)."""
        self._update_piece_list()
        self.clear_selection()
