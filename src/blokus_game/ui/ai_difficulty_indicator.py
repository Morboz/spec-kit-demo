"""
AI Difficulty Indicator UI Component

This module provides UI components for displaying AI difficulty levels
and information during gameplay.
"""

import tkinter as tk
from dataclasses import dataclass
from tkinter import ttk


@dataclass
class AIPlayerInfo:
    """Information about an AI player."""

    player_id: int
    name: str
    difficulty: str
    color: str
    is_active: bool = True
    score: int = 0


class AIDifficultyIndicator(ttk.Frame):
    """
    UI component for displaying AI difficulty levels.

    Shows all AI players with their difficulty settings,
    allowing players to understand their opponents' capabilities.
    """

    def __init__(
        self,
        parent: tk.Widget,
        show_scores: bool = True,
        show_colors: bool = True,
        **kwargs,
    ):
        """
        Initialize the AI difficulty indicator.

        Args:
            parent: Parent widget
            show_scores: Whether to display player scores
            show_colors: Whether to display player colors
            **kwargs: Additional ttk.Frame arguments
        """
        super().__init__(parent, **kwargs)

        # Configuration
        self.show_scores = show_scores
        self.show_colors = show_colors

        # State
        self.ai_players: dict[int, AIPlayerInfo] = {}
        self.human_player_id: int | None = None

        # Create widgets
        self._create_widgets()

        # Apply styling
        self._apply_styling()

    def _create_widgets(self):
        """Create and arrange UI widgets."""
        # Title
        title_label = ttk.Label(self, text="AI Players", font=("Arial", 12, "bold"))
        title_label.pack(pady=(0, 10))

        # Scrollable frame for players
        self.canvas = tk.Canvas(self, height=200)
        self.scrollbar = ttk.Scrollbar(
            self, orient="vertical", command=self.canvas.yview
        )
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")),
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Frame for player info
        self.players_frame = ttk.Frame(self.scrollable_frame)
        self.players_frame.pack(fill=tk.X, pady=2)

        # Info label
        self.info_var = tk.StringVar(value="")
        self.info_label = ttk.Label(
            self, textvariable=self.info_var, font=("Arial", 9), foreground="gray"
        )
        self.info_label.pack(pady=(10, 0))

        # Legend frame
        self.legend_frame = ttk.LabelFrame(self, text="Difficulty Levels", padding="5")
        self.legend_frame.pack(fill=tk.X, pady=(10, 0))

        self._create_legend()

    def _create_legend(self):
        """Create difficulty level legend."""
        difficulties = [
            ("Easy", "Simple random placement", "#90EE90"),
            ("Medium", "Balanced corner strategy", "#FFD700"),
            ("Hard", "Advanced strategic play", "#FF6B6B"),
        ]

        for i, (level, description, color) in enumerate(difficulties):
            frame = ttk.Frame(self.legend_frame)
            frame.pack(fill=tk.X, pady=2)

            # Color indicator
            color_label = tk.Label(
                frame, text="●", font=("Arial", 12), foreground=color
            )
            color_label.pack(side=tk.LEFT, padx=(0, 5))

            # Level and description
            text_label = ttk.Label(
                frame, text=f"{level}: {description}", font=("Arial", 9)
            )
            text_label.pack(side=tk.LEFT)

    def _apply_styling(self):
        """Apply custom styling for difficulty indicator."""
        style = ttk.Style()
        style.configure("AIPlayer.TFrame", relief="groove", borderwidth=1)

    def set_ai_players(
        self, players: list[AIPlayerInfo], human_player_id: int | None = None
    ):
        """
        Set the list of AI players to display.

        Args:
            players: List of AI player information
            human_player_id: ID of human player (to filter out if needed)
        """
        self.ai_players = {p.player_id: p for p in players}
        self.human_player_id = human_player_id

        self._update_display()

    def update_player_info(self, player_id: int, **kwargs):
        """
        Update information for a specific player.

        Args:
            player_id: ID of player to update
            **kwargs: Fields to update (score, is_active, etc.)
        """
        if player_id in self.ai_players:
            for key, value in kwargs.items():
                if hasattr(self.ai_players[player_id], key):
                    setattr(self.ai_players[player_id], key, value)
            self._update_display()

    def _update_display(self):
        """Refresh the display with current player information."""
        # Clear existing widgets
        for widget in self.players_frame.winfo_children():
            widget.destroy()

        # Sort players by ID
        sorted_players = sorted(self.ai_players.values(), key=lambda p: p.player_id)

        # Display each player
        for player in sorted_players:
            # Skip human player if specified
            if self.human_player_id and player.player_id == self.human_player_id:
                continue

            self._create_player_row(player)

        # Update info text
        active_ais = sum(1 for p in self.ai_players.values() if p.is_active)
        total_ais = len(self.ai_players)
        self.info_var.set(f"{active_ais}/{total_ais} AI players active")

    def _create_player_row(self, player: AIPlayerInfo):
        """Create a display row for a single player."""
        row_frame = ttk.Frame(self.players_frame, style="AIPlayer.TFrame")
        row_frame.pack(fill=tk.X, pady=2, padx=5)

        # Main content
        content_frame = ttk.Frame(row_frame)
        content_frame.pack(fill=tk.X, padx=10, pady=5)

        # Color indicator (left)
        if self.show_colors:
            color_label = tk.Label(
                content_frame, text="●", font=("Arial", 16), foreground=player.color
            )
            color_label.pack(side=tk.LEFT, padx=(0, 10))

        # Player info (center)
        info_frame = ttk.Frame(content_frame)
        info_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Player name and ID
        name_text = f"Player {player.player_id}"
        if player.name:
            name_text = f"{player.name}"

        name_label = ttk.Label(info_frame, text=name_text, font=("Arial", 10, "bold"))
        name_label.pack(anchor=tk.W)

        # Difficulty level
        difficulty_frame = ttk.Frame(info_frame)
        difficulty_frame.pack(anchor=tk.W, fill=tk.X)

        difficulty_label = ttk.Label(
            difficulty_frame, text="Difficulty:", font=("Arial", 9)
        )
        difficulty_label.pack(side=tk.LEFT)

        # Difficulty with color coding
        diff_color = self._get_difficulty_color(player.difficulty)
        difficulty_value = ttk.Label(
            difficulty_frame,
            text=player.difficulty,
            font=("Arial", 9, "bold"),
            foreground=diff_color,
        )
        difficulty_value.pack(side=tk.LEFT, padx=(5, 0))

        # Score (right)
        if self.show_scores:
            score_frame = ttk.Frame(content_frame)
            score_frame.pack(side=tk.RIGHT, padx=(10, 0))

            score_label = ttk.Label(score_frame, text="Score:", font=("Arial", 9))
            score_label.pack()

            score_value = ttk.Label(
                score_frame,
                text=str(player.score),
                font=("Arial", 10, "bold"),
                foreground=player.color,
            )
            score_value.pack()

        # Active/inactive indicator
        if not player.is_active:
            inactive_label = ttk.Label(
                row_frame,
                text="(Inactive)",
                font=("Arial", 8, "italic"),
                foreground="gray",
            )
            inactive_label.pack(side=tk.RIGHT, padx=10)

    def _get_difficulty_color(self, difficulty: str) -> str:
        """
        Get color for difficulty level.

        Args:
            difficulty: Difficulty level string

        Returns:
            Color code for the difficulty
        """
        color_map = {
            "Easy": "#90EE90",  # Light green
            "Medium": "#FFD700",  # Gold
            "Hard": "#FF6B6B",  # Light red
        }
        return color_map.get(difficulty, "#808080")  # Gray as default

    def highlight_player(self, player_id: int):
        """
        Highlight a specific player's row.

        Args:
            player_id: ID of player to highlight
        """
        # Remove previous highlights
        for widget in self.players_frame.winfo_children():
            widget.configure(style="AIPlayer.TFrame")

        # Add highlight to current player
        if player_id in self.ai_players:
            # Find and highlight the player's frame
            for widget in self.players_frame.winfo_children():
                widget.configure(style="AIPlayer.TFrame")
                break

    def get_difficulty_summary(self) -> dict[str, int]:
        """
        Get summary of difficulty levels.

        Returns:
            Dictionary mapping difficulty to count
        """
        summary = {"Easy": 0, "Medium": 0, "Hard": 0}
        for player in self.ai_players.values():
            if player.difficulty in summary:
                summary[player.difficulty] += 1
        return summary

    def get_player_by_id(self, player_id: int) -> AIPlayerInfo | None:
        """
        Get player information by ID.

        Args:
            player_id: Player ID

        Returns:
            AIPlayerInfo or None if not found
        """
        return self.ai_players.get(player_id)


class GameModeIndicator(ttk.Frame):
    """
    UI component for displaying current game mode and settings.
    """

    def __init__(self, parent: tk.Widget, **kwargs):
        """
        Initialize the game mode indicator.

        Args:
            parent: Parent widget
            **kwargs: Additional ttk.Frame arguments
        """
        super().__init__(parent, **kwargs)

        # Create widgets
        self._create_widgets()

    def _create_widgets(self):
        """Create and arrange UI widgets."""
        # Title
        title_label = ttk.Label(self, text="Game Mode", font=("Arial", 12, "bold"))
        title_label.pack(pady=(0, 10))

        # Mode display
        self.mode_var = tk.StringVar(value="")
        self.mode_label = ttk.Label(
            self, textvariable=self.mode_var, font=("Arial", 11), foreground="blue"
        )
        self.mode_label.pack(pady=(0, 5))

        # Difficulty setting
        self.difficulty_var = tk.StringVar(value="")
        self.difficulty_label = ttk.Label(
            self,
            textvariable=self.difficulty_var,
            font=("Arial", 10),
            foreground="gray",
        )
        self.difficulty_label.pack()

    def set_game_mode(self, mode: str, difficulty: str | None = None):
        """
        Set the current game mode display.

        Args:
            mode: Game mode name
            difficulty: Difficulty setting (optional)
        """
        self.mode_var.set(mode)

        if difficulty:
            self.difficulty_var.set(f"Difficulty: {difficulty}")
        else:
            self.difficulty_var.set("")


# Convenience functions
def create_ai_difficulty_display(
    parent: tk.Widget,
    ai_players: list[AIPlayerInfo],
    human_player_id: int | None = None,
    show_scores: bool = True,
) -> AIDifficultyIndicator:
    """
    Create and configure an AI difficulty indicator.

    Args:
        parent: Parent widget
        ai_players: List of AI players
        human_player_id: ID of human player to filter out
        show_scores: Whether to show scores

    Returns:
        Configured AIDifficultyIndicator
    """
    indicator = AIDifficultyIndicator(parent, show_scores=show_scores)
    indicator.set_ai_players(ai_players, human_player_id)
    return indicator


# Example usage
if __name__ == "__main__":
    root = tk.Tk()
    root.title("AI Difficulty Indicator Test")
    root.geometry("400x500")

    # Create test data
    test_players = [
        AIPlayerInfo(1, "Human Player", "Human", "#0000FF", False, 0),
        AIPlayerInfo(2, "AI Player 1", "Easy", "#FF0000", True, 25),
        AIPlayerInfo(3, "AI Player 2", "Medium", "#00FF00", True, 30),
        AIPlayerInfo(4, "AI Player 3", "Hard", "#FFFF00", True, 28),
    ]

    # Create indicator
    indicator = AIDifficultyIndicator(root, show_scores=True, show_colors=True)
    indicator.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    indicator.set_ai_players(test_players, human_player_id=1)

    # Add test button to update scores
    def update_scores():
        for i, player in enumerate(test_players):
            if player.is_active:
                new_score = player.score + 10
                indicator.update_player_info(player.player_id, score=new_score)

    update_btn = ttk.Button(root, text="Update Scores", command=update_scores)
    update_btn.pack(pady=10)

    root.mainloop()
