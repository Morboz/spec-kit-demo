"""
Current Player Indicator UI Component

This module provides the CurrentPlayerIndicator class which displays
the current player's turn and information.
"""

import tkinter as tk
from tkinter import ttk

from blokus_game.models.game_state import GameState
from blokus_game.models.player import Player


class CurrentPlayerIndicator(ttk.Frame):
    """UI component for displaying current player turn."""

    def __init__(
        self,
        parent: tk.Widget,
        game_state: GameState | None = None,
    ) -> None:
        """
        Initialize the current player indicator.

        Args:
            parent: Parent widget
            game_state: Game state to observe
        """
        super().__init__(parent)
        self.game_state = game_state
        self.players: list[Player] = []
        self.current_player: Player | None = None

        # Create widget
        self._create_widgets()

        # Initialize with game state if provided
        if self.game_state:
            self.update_from_game_state()

    def _create_widgets(self) -> None:
        """Create and arrange UI widgets."""
        # Title
        title_label = ttk.Label(self, text="Current Turn", font=("Arial", 12, "bold"))
        title_label.pack(pady=(0, 10))

        # Player info frame
        info_frame = ttk.Frame(self)
        info_frame.pack(fill=tk.X, pady=(0, 10))

        # Current player name
        self.player_name_var = tk.StringVar(value="No player")
        self.player_name_label = ttk.Label(
            info_frame,
            textvariable=self.player_name_var,
            font=("Arial", 14, "bold"),
            foreground="blue",
        )
        self.player_name_label.pack()

        # Player ID
        self.player_id_var = tk.StringVar(value="")
        self.player_id_label = ttk.Label(
            info_frame,
            textvariable=self.player_id_var,
            font=("Arial", 10),
        )
        self.player_id_label.pack()

        # AI thinking indicator
        self.ai_thinking_var = tk.StringVar(value="")
        self.ai_thinking_label = ttk.Label(
            info_frame,
            textvariable=self.ai_thinking_var,
            font=("Arial", 10, "italic"),
            foreground="orange",
        )
        self.ai_thinking_label.pack()

        # Separator
        separator = ttk.Separator(self, orient="horizontal")
        separator.pack(fill=tk.X, pady=10)

        # Turn info
        turn_frame = ttk.Frame(self)
        turn_frame.pack(fill=tk.X)

        turn_label = ttk.Label(
            turn_frame,
            text="Turn:",
            font=("Arial", 10, "bold"),
        )
        turn_label.pack(side=tk.LEFT)

        self.turn_number_var = tk.StringVar(value="1")
        self.turn_number_label = ttk.Label(
            turn_frame,
            textvariable=self.turn_number_var,
            font=("Arial", 10),
        )
        self.turn_number_label.pack(side=tk.RIGHT)

    def set_game_state(self, game_state: GameState) -> None:
        """
        Set the game state to observe.

        Args:
            game_state: Game state to observe
        """
        self.game_state = game_state
        self.update_from_game_state()

    def update_from_game_state(self) -> None:
        """Update indicator from current game state."""
        if not self.game_state:
            return

        # Update player list
        self.players = self.game_state.players

        # Update current player
        if self.game_state.phase.value >= 2:  # PLAYING or later
            self.current_player = self.game_state.get_current_player()
            if self.current_player:
                self.player_name_var.set(self.current_player.name)
                self.player_id_var.set(f"Player {self.current_player.player_id}")
        else:
            self.current_player = None
            self.player_name_var.set("Game not started")
            self.player_id_var.set("")

    def get_current_player(self) -> Player | None:
        """
        Get the currently displayed player.

        Returns:
            Current player or None
        """
        return self.current_player

    def set_highlight(self, highlight: bool) -> None:
        """
        Set highlight for the current player indicator.

        Args:
            highlight: Whether to highlight the indicator
        """
        if highlight:
            self.player_name_label.config(foreground="red")
        else:
            self.player_name_label.config(foreground="blue")

    def clear(self) -> None:
        """Clear the indicator display."""
        self.players = []
        self.current_player = None
        self.player_name_var.set("No player")
        self.player_id_var.set("")
        self.ai_thinking_var.set("")
        self.turn_number_var.set("1")

    def show_ai_thinking(self) -> None:
        """Show AI thinking indicator."""
        self.ai_thinking_var.set("AI thinking...")

    def hide_ai_thinking(self) -> None:
        """Hide AI thinking indicator."""
        self.ai_thinking_var.set("")

    def is_ai_thinking(self) -> bool:
        """
        Check if AI thinking indicator is currently shown.

        Returns:
            True if thinking indicator is shown
        """
        return self.ai_thinking_var.get() != ""
