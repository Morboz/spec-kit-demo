"""
Spectator Mode Visual Indicator

This module provides UI components for displaying spectator mode information,
including current AI player, turn count, and game statistics.
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional, Callable
from datetime import datetime


class SpectatorModeIndicator(ttk.Frame):
    """
    Visual indicator for spectator mode.

    Displays:
    - Current AI player information
    - Turn count
    - Game statistics
    - Automatic gameplay indicator
    """

    def __init__(
        self,
        parent,
        game_mode,
        on_statistics_requested: Optional[Callable] = None,
        **kwargs
    ):
        """
        Initialize spectator mode indicator.

        Args:
            parent: Parent widget
            game_mode: GameMode instance (should be SPECTATE type)
            on_statistics_requested: Callback when stats button is clicked
            **kwargs: Additional ttk.Frame arguments
        """
        super().__init__(parent, **kwargs)
        self.game_mode = game_mode
        self.on_statistics_requested = on_statistics_requested

        # State variables
        self._current_player = 1
        self._turn_count = 0
        self._game_start_time = datetime.now()

        self._create_widgets()
        self._update_display()

    def _create_widgets(self):
        """Create and layout indicator widgets."""
        # Background styling for spectator mode
        self.configure(style="Spectator.TFrame")

        # Title
        title_label = ttk.Label(
            self,
            text="🎮 SPECTATOR MODE",
            font=("Arial", 14, "bold"),
            foreground="purple"
        )
        title_label.pack(pady=(0, 10))

        # Current player frame
        player_frame = ttk.LabelFrame(self, text="Current Player", padding="10")
        player_frame.pack(fill=tk.X, pady=(0, 5))

        self.player_label = ttk.Label(
            player_frame,
            text="Player 1 (AI - Medium)",
            font=("Arial", 12, "bold"),
            foreground="blue"
        )
        self.player_label.pack()

        # AI thinking indicator
        self.thinking_label = ttk.Label(
            self,
            text="",
            font=("Arial", 10, "italic"),
            foreground="orange"
        )
        self.thinking_label.pack()

        # Turn count
        turn_frame = ttk.LabelFrame(self, text="Game Progress", padding="10")
        turn_frame.pack(fill=tk.X, pady=(5, 0))

        self.turn_label = ttk.Label(
            turn_frame,
            text="Turn 0 / ~200",
            font=("Arial", 11)
        )
        self.turn_label.pack()

        # Game timer
        self.timer_label = ttk.Label(
            turn_frame,
            text="⏱️ 00:00",
            font=("Arial", 10),
            foreground="gray"
        )
        self.timer_label.pack()

        # Automatic gameplay indicator
        auto_frame = ttk.LabelFrame(self, text="Status", padding="10")
        auto_frame.pack(fill=tk.X, pady=(5, 0))

        self.auto_label = ttk.Label(
            auto_frame,
            text="▶️ Autonomous gameplay",
            font=("Arial", 10, "bold"),
            foreground="green"
        )
        self.auto_label.pack()

        # Note about human input
        note_label = ttk.Label(
            self,
            text="No human input required\nGames play automatically",
            font=("Arial", 9),
            foreground="gray",
            justify=tk.CENTER
        )
        note_label.pack(pady=(10, 0))

    def update_current_player(self, player_id: int, difficulty: str):
        """
        Update current player display.

        Args:
            player_id: Player ID (1-4)
            difficulty: AI difficulty level
        """
        self._current_player = player_id
        color_map = {1: "blue", 2: "red", 3: "green", 4: "yellow"}
        color = color_map.get(player_id, "black")

        self.player_label.configure(
            text=f"Player {player_id} (AI - {difficulty})",
            foreground=color
        )

    def update_turn_count(self, turn_count: int):
        """
        Update turn count display.

        Args:
            turn_count: Current turn number
        """
        self._turn_count = turn_count
        self.turn_label.configure(text=f"Turn {turn_count} / ~200")

    def update_timer(self, elapsed_seconds: int):
        """
        Update game timer display.

        Args:
            elapsed_seconds: Elapsed time in seconds
        """
        minutes = elapsed_seconds // 60
        seconds = elapsed_seconds % 60
        self.timer_label.configure(text=f"⏱️ {minutes:02d}:{seconds:02d}")

    def set_thinking_state(self, is_thinking: bool, message: str = ""):
        """
        Update AI thinking state indicator.

        Args:
            is_thinking: Whether AI is currently calculating
            message: Optional message to display
        """
        if is_thinking:
            self.thinking_label.configure(
                text=f"🤖 {message or 'AI is thinking...'}",
                foreground="orange"
            )
        else:
            self.thinking_label.configure(text="")

    def set_game_over(self, winner_player_id: int, final_scores: dict):
        """
        Update display for game over state.

        Args:
            winner_player_id: ID of winning player
            final_scores: Dictionary of player scores
        """
        # Update status
        self.auto_label.configure(
            text="🏁 Game Complete",
            foreground="red"
        )

        # Show winner
        winner_label = ttk.Label(
            self,
            text=f"🏆 Winner: Player {winner_player_id}",
            font=("Arial", 12, "bold"),
            foreground="gold"
        )
        winner_label.pack(pady=(5, 0))

        # Calculate final time
        elapsed = int((datetime.now() - self._game_start_time).total_seconds())
        self.update_timer(elapsed)

    def enable_statistics_button(self):
        """Enable statistics button if callback provided."""
        if self.on_statistics_requested:
            stats_button = ttk.Button(
                self,
                text="📊 View Statistics",
                command=self._on_statistics_clicked
            )
            stats_button.pack(pady=(10, 0))

    def _on_statistics_clicked(self):
        """Handle statistics button click."""
        if self.on_statistics_requested:
            self.on_statistics_requested()

    def _update_display(self):
        """Update all display elements."""
        self.update_timer(int((datetime.now() - self._game_start_time).total_seconds()))

        # Schedule next update
        self.after(1000, self._update_display)


class GameStatisticsDialog(tk.Toplevel):
    """
    Dialog for displaying game statistics after spectator game.
    """

    def __init__(self, parent, game_stats: dict, **kwargs):
        """
        Initialize statistics dialog.

        Args:
            parent: Parent widget
            game_stats: Dictionary containing game statistics
            **kwargs: Additional Toplevel arguments
        """
        super().__init__(parent, **kwargs)
        self.title("Game Statistics")
        self.geometry("500x400")
        self.resizable(False, False)

        # Make modal
        self.transient(parent)
        self.grab_set()

        self._create_widgets(game_stats)

    def _create_widgets(self, game_stats: dict):
        """Create statistics display widgets."""
        # Main frame
        main_frame = ttk.Frame(self, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        title_label = ttk.Label(
            main_frame,
            text="Game Statistics",
            font=("Arial", 16, "bold")
        )
        title_label.pack(pady=(0, 20))

        # Game summary
        summary_frame = ttk.LabelFrame(main_frame, text="Summary", padding="10")
        summary_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(
            summary_frame,
            text=f"Game Mode: {game_stats.get('mode', 'Unknown')}",
            font=("Arial", 10)
        ).pack(anchor=tk.W)

        ttk.Label(
            summary_frame,
            text=f"Duration: {game_stats.get('duration', 'Unknown')}",
            font=("Arial", 10)
        ).pack(anchor=tk.W)

        ttk.Label(
            summary_frame,
            text=f"Total Turns: {game_stats.get('total_turns', 0)}",
            font=("Arial", 10)
        ).pack(anchor=tk.W)

        # Player scores
        scores_frame = ttk.LabelFrame(main_frame, text="Final Scores", padding="10")
        scores_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        scores = game_stats.get('scores', {})
        for player_id in sorted(scores.keys()):
            score = scores[player_id]
            ttk.Label(
                scores_frame,
                text=f"Player {player_id}: {score} points",
                font=("Arial", 11, "bold")
            ).pack(anchor=tk.W, pady=2)

        # Close button
        close_button = ttk.Button(
            main_frame,
            text="Close",
            command=self.destroy
        )
        close_button.pack(pady=(10, 0))


# Convenience function
def show_spectator_indicator(
    parent,
    game_mode,
    on_statistics_requested: Optional[Callable] = None
) -> SpectatorModeIndicator:
    """
    Create and display spectator mode indicator.

    Args:
        parent: Parent widget
        game_mode: GameMode instance
        on_statistics_requested: Callback for statistics button

    Returns:
        SpectatorModeIndicator instance
    """
    indicator = SpectatorModeIndicator(
        parent,
        game_mode,
        on_statistics_requested=on_statistics_requested
    )
    return indicator
