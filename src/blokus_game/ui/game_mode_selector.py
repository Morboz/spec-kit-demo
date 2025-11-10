"""
Game Mode Selection UI

This module provides the user interface for selecting AI battle modes
and configuring AI difficulty levels.
"""

import tkinter as tk
from collections.abc import Callable
from tkinter import messagebox, ttk
from typing import Any

from blokus_game.config.logger_config import get_logger
from blokus_game.models.game_mode import Difficulty, GameMode

# Create logger for this module
logger = get_logger(__name__)


class GameModeSelector:
    """UI for selecting AI battle mode."""

    def __init__(
        self, parent: tk.Widget | None = None, callback: Callable | None = None
    ):
        """
        Initialize the game mode selector.

        Args:
            parent: Parent tkinter widget
            callback: Callback function called with (mode_type, difficulty)
                when mode is selected
        """
        self.parent = parent
        self.callback = callback
        self.result: dict[str, Any] | None = None
        self.dialog: tk.Toplevel | None = None

        # Selection variables
        self.selected_mode_var = tk.StringVar(value="single_ai")

        # Load saved difficulty preference
        try:
            from blokus_game.models.game_mode import GameMode, GameModeType

            saved_difficulty = GameMode.get_difficulty_preference(
                GameModeType.SINGLE_AI
            )
            self.selected_difficulty_var = tk.StringVar(value=saved_difficulty.value)
        except Exception:
            # Fallback to default if loading fails
            self.selected_difficulty_var = tk.StringVar(value="Medium")

    def show(self) -> dict[str, Any] | None:
        """
        Show the mode selection dialog and wait for user input.

        Returns:
            Dictionary with mode configuration or None if cancelled
        """
        self._create_dialog()
        self.dialog.wait_window()
        return self.result

    def _create_dialog(self) -> None:
        """Create and display the mode selection dialog."""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Select Game Mode")
        self.dialog.geometry("500x500")
        self.dialog.resizable(False, False)
        self.dialog.transient(self.parent)
        self.dialog.grab_set()

        # Main frame
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Title
        title_label = ttk.Label(
            main_frame, text="AI Battle Mode", font=("Arial", 16, "bold")
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))

        # Mode selection frame
        mode_frame = ttk.LabelFrame(main_frame, text="Game Mode", padding="10")
        mode_frame.grid(
            row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10)
        )

        # Mode options
        modes = [
            ("Single AI", "single_ai", "Play against one AI opponent"),
            ("Three AI", "three_ai", "Play against three AI opponents"),
            ("Spectate AI", "spectate", "Watch AI vs AI match"),
        ]

        for i, (text, value, description) in enumerate(modes):
            rb = ttk.Radiobutton(
                mode_frame,
                text=text,
                variable=self.selected_mode_var,
                value=value,
                command=self._on_mode_selected,
            )
            rb.grid(row=i, column=0, sticky=tk.W, pady=5)

            desc_label = ttk.Label(
                mode_frame, text=description, font=("Arial", 9), foreground="gray"
            )
            desc_label.grid(row=i, column=1, sticky=tk.W, padx=(10, 0), pady=5)

        # Difficulty selection frame
        self.difficulty_frame = ttk.LabelFrame(
            main_frame, text="AI Difficulty", padding="10"
        )
        self.difficulty_frame.grid(
            row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0)
        )

        # Difficulty options
        difficulties = [
            ("Easy", "Easy", "Simple random placement"),
            ("Medium", "Medium", "Balanced corner strategy"),
            ("Hard", "Hard", "Advanced strategic play"),
        ]

        for i, (text, value, description) in enumerate(difficulties):
            rb = ttk.Radiobutton(
                self.difficulty_frame,
                text=text,
                variable=self.selected_difficulty_var,
                value=value,
            )
            rb.grid(row=i, column=0, sticky=tk.W, pady=5)

            desc_label = ttk.Label(
                self.difficulty_frame,
                text=description,
                font=("Arial", 9),
                foreground="gray",
            )
            desc_label.grid(row=i, column=1, sticky=tk.W, padx=(10, 0), pady=5)

        # Hint for spectate mode
        self.hint_label = ttk.Label(
            main_frame,
            text="Spectate mode uses mixed difficulty levels",
            font=("Arial", 9, "italic"),
            foreground="blue",
        )
        self.hint_label.grid(row=3, column=0, columnspan=2, pady=(5, 0))

        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=(20, 0))

        # Start button
        start_button = ttk.Button(
            button_frame, text="Start Game", command=self._on_start_clicked
        )
        start_button.grid(row=0, column=0, padx=(0, 10))

        # Cancel button
        cancel_button = ttk.Button(
            button_frame, text="Cancel", command=self._on_cancel_clicked
        )
        cancel_button.grid(row=0, column=1)

        # Initialize UI state
        self._on_mode_selected()

    def _on_mode_selected(self):
        """Handle mode selection change."""
        mode = self.selected_mode_var.get()

        if mode == "spectate":
            # Disable difficulty selection for spectate mode
            for widget in self.difficulty_frame.winfo_children():
                widget.configure(state="disabled")
            self.hint_label.configure(text="Spectate mode uses mixed difficulty levels")
        else:
            # Enable difficulty selection
            for widget in self.difficulty_frame.winfo_children():
                widget.configure(state="normal")
            self.hint_label.configure(text="Choose AI difficulty level")

    def _on_start_clicked(self):
        """Handle start button click."""
        mode = self.selected_mode_var.get()
        difficulty = self.selected_difficulty_var.get()

        # Save difficulty preference for non-spectate modes
        if mode != "spectate":
            try:
                from blokus_game.models.ai_config import Difficulty as AIDifficulty
                from blokus_game.models.game_mode import GameMode, GameModeType

                # Convert string to Difficulty enum
                diff_enum = AIDifficulty(difficulty)

                # Save preference
                game_mode = GameMode(GameModeType.SINGLE_AI, diff_enum)
                game_mode.save_difficulty_preference(GameModeType.SINGLE_AI, diff_enum)
                game_mode.save_difficulty_preference(GameModeType.THREE_AI, diff_enum)
            except Exception as e:
                logger.warning(f"Failed to save difficulty preference: {e}")

        # Create configuration
        if mode == "spectate":
            config = {
                "mode_type": mode,
                "difficulty": None,
                "description": "Spectate AI vs AI match",
            }
        else:
            config = {
                "mode_type": mode,
                "difficulty": difficulty,
                "description": f"Human vs {difficulty} AI",
            }

        self.result = config
        self.dialog.destroy()

        # Call callback if provided
        if self.callback:
            try:
                self.callback(mode, difficulty)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to start game: {e}")

    def _on_cancel_clicked(self):
        """Handle cancel button click."""
        self.result = None
        self.dialog.destroy()

    @staticmethod
    def create_game_mode(mode_type: str, difficulty: str | None = None) -> GameMode:
        """
        Create a GameMode instance from selected options.

        Args:
            mode_type: Type of game mode
            difficulty: Difficulty level (None for spectate)

        Returns:
            Configured GameMode instance
        """
        if mode_type == "single_ai":
            diff_enum = Difficulty(difficulty) if difficulty else Difficulty.MEDIUM
            return GameMode.single_ai(diff_enum)
        elif mode_type == "three_ai":
            diff_enum = Difficulty(difficulty) if difficulty else Difficulty.MEDIUM
            return GameMode.three_ai(diff_enum)
        elif mode_type == "spectate":
            return GameMode.spectate_ai()
        else:
            raise ValueError(f"Unknown game mode: {mode_type}")


def show_game_mode_selector(
    parent: tk.Widget | None = None, callback: Callable | None = None
) -> dict[str, Any] | None:
    """
    Convenience function to show game mode selector.

    Args:
        parent: Parent tkinter widget
        callback: Callback function

    Returns:
        Selected configuration or None
    """
    selector = GameModeSelector(parent, callback)
    return selector.show()


# Example usage
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # Hide main window

    def on_mode_selected(mode_type: str, difficulty: str):
        """Callback for mode selection."""
        logger.info(f"Mode selected: {mode_type}, Difficulty: {difficulty}")

        # Create and display game mode
        try:
            game_mode = GameModeSelector.create_game_mode(mode_type, difficulty)
            logger.info(f"Created game mode: {game_mode}")
        except Exception as e:
            logger.error(f"Error creating game mode: {e}")

    # Show selector
    result = show_game_mode_selector(root, on_mode_selected)

    if result:
        logger.info(f"Selected: {result}")
    else:
        logger.info("Cancelled")

    root.destroy()
