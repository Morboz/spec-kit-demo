"""
Piece Inventory UI Component

This module provides the PieceInventory class which displays the
remaining pieces for all players.
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional, List, Dict
from src.models.player import Player


class PieceInventory(ttk.Frame):
    """UI component for displaying players' remaining pieces."""

    def __init__(
        self,
        parent: tk.Widget,
        players: Optional[List[Player]] = None,
    ) -> None:
        """
        Initialize the piece inventory.

        Args:
            parent: Parent widget
            players: List of players to display
        """
        super().__init__(parent)
        self.players = players or []
        self.selected_piece: Optional[str] = None
        self.on_piece_selected: Optional[callable] = None

        # Create widget
        self._create_widgets()

    def _create_widgets(self) -> None:
        """Create and arrange UI widgets."""
        # Title
        title_label = ttk.Label(
            self, text="Piece Inventory", font=("Arial", 12, "bold")
        )
        title_label.pack(pady=(0, 10))

        # Create notebook for tabbed view
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Dictionary to store player tabs
        self.player_tabs: Dict[int, ttk.Frame] = {}

        # Create initial tabs
        if self.players:
            self._create_player_tabs()

    def _create_player_tabs(self) -> None:
        """Create tab for each player."""
        for player in self.players:
            self._create_player_tab(player)

    def _create_player_tab(self, player: Player) -> None:
        """
        Create a tab for a specific player.

        Args:
            player: Player to create tab for
        """
        # Create frame for player tab
        tab_frame = ttk.Frame(self.notebook)
        self.notebook.add(tab_frame, text=f"P{player.player_id}: {player.name}")

        # Store reference
        self.player_tabs[player.player_id] = tab_frame

        # Create scrollable frame for pieces
        canvas = tk.Canvas(tab_frame)
        scrollbar = ttk.Scrollbar(tab_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")),
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Display player's pieces
        self._display_player_pieces(scrollable_frame, player)

    def _display_player_pieces(self, parent: ttk.Frame, player: Player) -> None:
        """
        Display all pieces for a player.

        Args:
            parent: Parent frame
            player: Player whose pieces to display
        """
        # Get all piece names
        all_pieces = self._get_all_piece_names()

        # Track which pieces are placed vs remaining
        placed_pieces = set()
        remaining_pieces = []

        for piece_name in all_pieces:
            piece = player.get_piece(piece_name)
            if piece and piece.is_placed:
                placed_pieces.add(piece_name)
            elif piece:
                remaining_pieces.append(piece_name)

        # Display remaining pieces
        if remaining_pieces:
            remaining_label = ttk.Label(
                parent,
                text=f"Remaining Pieces ({len(remaining_pieces)})",
                font=("Arial", 10, "bold"),
                foreground="green",
            )
            remaining_label.pack(pady=(5, 2))

            for piece_name in sorted(remaining_pieces):
                piece_frame = ttk.Frame(parent)
                piece_frame.pack(fill=tk.X, pady=1)

                btn = ttk.Button(
                    piece_frame,
                    text=piece_name,
                    width=15,
                    command=lambda pn=piece_name: self._on_piece_click(pn),
                )
                btn.pack(side=tk.LEFT)

                size_label = ttk.Label(
                    piece_frame,
                    text=f"({self._get_piece_size(piece_name)} squares)",
                    font=("Arial", 8),
                )
                size_label.pack(side=tk.LEFT, padx=(5, 0))

        # Display placed pieces
        if placed_pieces:
            placed_label = ttk.Label(
                parent,
                text=f"Placed Pieces ({len(placed_pieces)})",
                font=("Arial", 10, "bold"),
                foreground="red",
            )
            placed_label.pack(pady=(15, 2))

            for piece_name in sorted(placed_pieces):
                piece_frame = ttk.Frame(parent)
                piece_frame.pack(fill=tk.X, pady=1)

                label = ttk.Label(
                    piece_frame,
                    text=f"✓ {piece_name} (placed)",
                    font=("Arial", 9),
                    foreground="gray",
                )
                label.pack(side=tk.LEFT)

    def _get_all_piece_names(self) -> List[str]:
        """
        Get list of all possible piece names.

        Returns:
            List of piece names
        """
        # All 21 Blokus pieces
        return [
            "I1",
            "I2",
            "I3",
            "I4",
            "I5",
            "L4",
            "L5",
            "T4",
            "T5",
            "V3",
            "U5",
            "W5",
            "X5",
            "Z5",
            "F5",
            "P5",
            "Y5",
            "N5",
            "T5",
            "V5",
            "Z4",
        ]

    def _get_piece_size(self, piece_name: str) -> int:
        """
        Get the size (number of squares) for a piece.

        Args:
            piece_name: Name of piece

        Returns:
            Size of piece
        """
        # Extract size from piece name
        if piece_name.startswith("I"):
            return int(piece_name[1])
        elif piece_name in ["L4", "T4", "Z4", "V3"]:
            return int(piece_name[1])
        else:
            # All other 5-piece pieces
            return 5

    def _on_piece_click(self, piece_name: str) -> None:
        """
        Handle piece selection.

        Args:
            piece_name: Name of selected piece
        """
        self.selected_piece = piece_name
        if self.on_piece_selected:
            self.on_piece_selected(piece_name)

    def set_players(self, players: List[Player]) -> None:
        """
        Set the players to display.

        Args:
            players: List of players
        """
        self.players = players
        self._refresh_tabs()

    def _refresh_tabs(self) -> None:
        """Refresh all player tabs."""
        # Clear existing tabs
        for tab in self.player_tabs.values():
            tab.destroy()
        self.player_tabs.clear()

        # Recreate tabs
        if self.players:
            self._create_player_tabs()

    def update_inventory(self, player_id: int) -> None:
        """
        Update inventory for a specific player.

        Args:
            player_id: ID of player to update
        """
        # Refresh the specific player's tab
        if player_id in self.player_tabs and self.players:
            for player in self.players:
                if player.player_id == player_id:
                    self._refresh_tabs()
                    break

    def select_player_tab(self, player_id: int) -> None:
        """
        Select the tab for a specific player.

        Args:
            player_id: ID of player to select
        """
        # Find tab index
        for i, (pid, _) in enumerate(self.player_tabs.items()):
            if pid == player_id:
                self.notebook.select(i)
                break

    def get_selected_piece(self) -> Optional[str]:
        """
        Get the currently selected piece.

        Returns:
            Name of selected piece or None
        """
        return self.selected_piece

    def set_piece_selected_callback(self, callback: callable) -> None:
        """
        Set callback for piece selection.

        Args:
            callback: Function to call when piece is selected
        """
        self.on_piece_selected = callback

    def clear(self) -> None:
        """Clear the inventory display."""
        for tab in self.player_tabs.values():
            tab.destroy()
        self.player_tabs.clear()
        self.players = []
        self.selected_piece = None
