"""
ScoreBreakdown UI Component

This module provides the ScoreBreakdown class which displays detailed
score breakdown for a player in the game.
"""

import tkinter as tk
from tkinter import ttk

from blokus_game.game.scoring import ScoringSystem
from blokus_game.models.player import Player


class ScoreBreakdown(ttk.Frame):
    """UI component for displaying detailed score breakdown."""

    def __init__(
        self,
        parent: tk.Widget,
        player: Player | None = None,
    ) -> None:
        """
        Initialize the score breakdown component.

        Args:
            parent: Parent widget
            player: Player to display breakdown for
        """
        super().__init__(parent)
        self.player = player
        self.score_vars: dict[str, tk.StringVar] = {}

        # Create widget
        self._create_widgets()

        # Initialize with current player data
        if self.player:
            self.update_breakdown()

    def _create_widgets(self) -> None:
        """Create and arrange UI widgets."""
        # Title
        title_label = ttk.Label(
            self, text="Score Breakdown", font=("Arial", 12, "bold")
        )
        title_label.pack(pady=(0, 10))

        # Create main frame for breakdown items
        self.breakdown_frame = ttk.Frame(self)
        self.breakdown_frame.pack(fill=tk.BOTH, expand=True)

        # Create score component labels and variables
        self.score_vars = {
            "placed_squares": tk.StringVar(value="0"),
            "unplaced_squares": tk.StringVar(value="0"),
            "base_score": tk.StringVar(value="0"),
            "all_pieces_bonus": tk.StringVar(value="0"),
            "final_score": tk.StringVar(value="0"),
        }

        # Labels for each component
        labels = {
            "placed_squares": "Squares Placed:",
            "unplaced_squares": "Squares Remaining:",
            "base_score": "Base Score:",
            "all_pieces_bonus": "All Pieces Bonus:",
            "final_score": "Final Score:",
        }

        # Create labels and value displays
        for key, label_text in labels.items():
            # Frame for each component
            component_frame = ttk.Frame(self.breakdown_frame)
            component_frame.pack(fill=tk.X, pady=2)

            # Label
            label = ttk.Label(component_frame, text=label_text, font=("Arial", 10))
            label.pack(side=tk.LEFT, padx=(0, 10))

            # Value
            value_label = ttk.Label(
                component_frame,
                textvariable=self.score_vars[key],
                font=("Arial", 10, "bold"),
            )
            value_label.pack(side=tk.RIGHT)

        # Highlight final score
        self.score_vars["final_score"].set("0")

    def set_player(self, player: Player) -> None:
        """
        Set the player to display breakdown for.

        Args:
            player: Player to analyze
        """
        self.player = player
        self.update_breakdown()

    def update_breakdown(self) -> None:
        """Update the breakdown display with current player data."""
        if not self.player:
            # Clear all values
            for var in self.score_vars.values():
                var.set("0")
            return

        # Get detailed breakdown from scoring system
        breakdown = ScoringSystem.get_score_breakdown(self.player)

        # Update display
        self.score_vars["placed_squares"].set(str(breakdown["placed_squares"]))
        self.score_vars["unplaced_squares"].set(str(breakdown["unplaced_squares"]))
        self.score_vars["base_score"].set(str(breakdown["base_score"]))
        self.score_vars["all_pieces_bonus"].set(str(breakdown["all_pieces_bonus"]))
        self.score_vars["final_score"].set(str(breakdown["final_score"]))

    def get_current_breakdown(self) -> dict[str, int] | None:
        """
        Get the current breakdown values.

        Returns:
            Dictionary with breakdown values or None if no player set
        """
        if not self.player:
            return None

        return {
            "placed_squares": int(self.score_vars["placed_squares"].get()),
            "unplaced_squares": int(self.score_vars["unplaced_squares"].get()),
            "base_score": int(self.score_vars["base_score"].get()),
            "all_pieces_bonus": int(self.score_vars["all_pieces_bonus"].get()),
            "final_score": int(self.score_vars["final_score"].get()),
        }

    def clear(self) -> None:
        """Clear the display and reset to empty state."""
        self.player = None
        for var in self.score_vars.values():
            var.set("0")

    def highlight_final_score(self, color: str = "green") -> None:
        """
        Highlight the final score display.

        Args:
            color: Color to use for highlighting (default: green)
        """
        # This would need to be implemented if we want color coding
        # For now, we just keep the bold formatting
        pass
