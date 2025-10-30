"""
Scoreboard UI Component

This module provides the Scoreboard class which displays scores
for all players in the game.
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional, List, Dict
from src.models.player import Player
from src.models.board import Board


class Scoreboard(ttk.Frame):
    """UI component for displaying player scores."""

    def __init__(
        self,
        parent: tk.Widget,
        board: Optional[Board] = None,
        players: Optional[List[Player]] = None,
    ) -> None:
        """
        Initialize the scoreboard.

        Args:
            parent: Parent widget
            board: Board to read scores from
            players: List of players
        """
        super().__init__(parent)
        self.board = board
        self.players = players or []
        self.score_vars: Dict[int, tk.StringVar] = {}

        # Create widget
        self._create_widgets()

        # Initialize scores
        self.update_scores()

    def _create_widgets(self) -> None:
        """Create and arrange UI widgets."""
        # Title
        title_label = ttk.Label(self, text="Scoreboard", font=("Arial", 12, "bold"))
        title_label.pack(pady=(0, 10))

        # Create treeview for scores
        columns = ("Player", "Squares", "Pieces Left")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=6)

        # Define column headings
        self.tree.heading("Player", text="Player")
        self.tree.heading("Squares", text="Squares Placed")
        self.tree.heading("Pieces Left", text="Pieces Remaining")

        # Define column widths
        self.tree.column("Player", width=100)
        self.tree.column("Squares", width=100)
        self.tree.column("Pieces Left", width=120)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Pack treeview and scrollbar
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def set_board(self, board: Board) -> None:
        """
        Set the board to read scores from.

        Args:
            board: Game board
        """
        self.board = board
        self.update_scores()

    def set_players(self, players: List[Player]) -> None:
        """
        Set the players to display.

        Args:
            players: List of players
        """
        self.players = players
        self.update_scores()

    def update_scores(self) -> None:
        """Update scoreboard with current scores."""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Add score rows for each player
        if self.players:
            for player in self.players:
                # Calculate squares placed
                squares = 0
                if self.board:
                    squares = self.board.count_player_squares(player.player_id)

                # Get pieces remaining
                pieces_left = player.get_remaining_piece_count()

                # Insert row
                self.tree.insert(
                    "",
                    tk.END,
                    values=(player.name, squares, pieces_left),
                )

    def get_player_score(self, player_id: int) -> int:
        """
        Get the score for a specific player.

        Args:
            player_id: Player ID

        Returns:
            Number of squares placed
        """
        if not self.board:
            return 0
        return self.board.count_player_squares(player_id)

    def get_leader(self) -> Optional[Player]:
        """
        Get the current leader (player with highest score).

        Returns:
            Player with highest score or None
        """
        if not self.players or not self.board:
            return None

        leader = None
        highest_score = -1

        for player in self.players:
            score = self.board.count_player_squares(player.player_id)
            if score > highest_score:
                highest_score = score
                leader = player

        return leader

    def highlight_leader(self) -> None:
        """Highlight the current leader in the scoreboard."""
        leader = self.get_leader()
        if not leader:
            return

        # Find leader row and highlight it
        for item in self.tree.get_children():
            values = self.tree.item(item)["values"]
            if values and values[0] == leader.name:
                self.tree.set(item, "Player", f"★ {leader.name}")
                break

    def clear(self) -> None:
        """Clear the scoreboard."""
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.players = []
        self.board = None
