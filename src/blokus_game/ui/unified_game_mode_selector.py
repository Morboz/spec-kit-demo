"""
Unified Game Mode Selection UI

This module provides a single dialog for selecting all game modes (AI and PvP)
with their respective configurations, eliminating the need for multiple sequential dialogs.
"""

import tkinter as tk
from collections.abc import Callable
from tkinter import messagebox, ttk
from typing import Any

from blokus_game.config.logger_config import get_logger
from blokus_game.models.game_mode import GameMode, GameModeType

# Create logger for this module
logger = get_logger(__name__)


class UnifiedGameModeSelector:
    """
    Unified game mode selector providing all mode options in a single dialog.

    Features:
    - Single dialog for all game modes (AI and PvP)
    - Dynamic configuration UI based on selected mode
    - Form validation
    - Support for all mode types with their respective settings
    """

    def __init__(
        self, parent: tk.Widget | None = None, callback: Callable | None = None
    ):
        """
        Initialize the unified game mode selector.

        Args:
            parent: Parent tkinter widget
            callback: Callback function called with (mode_type, config) when mode is selected
        """
        self.parent = parent
        self.callback = callback
        self.result: dict[str, Any] | None = None
        self.dialog: tk.Toplevel | None = None

        # Selection variables
        self.selected_mode_var = tk.StringVar(value="single_ai")
        self.selected_difficulty_var = tk.StringVar(value="Medium")
        self.player_count_var = tk.IntVar(value=2)
        self.board_size_var = tk.IntVar(value=20)
        self.color_scheme_var = tk.StringVar(value="default")
        self.show_grid_var = tk.BooleanVar(value=True)
        self.show_coordinates_var = tk.BooleanVar(value=False)

        # Player name variables
        self.player_name_vars = []
        for i in range(1, 5):
            var = tk.StringVar(value=f"Player {i}")
            self.player_name_vars.append(var)

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
        """Create and display the unified mode selection dialog."""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Select Game Mode")
        self.dialog.geometry("600x650")
        self.dialog.resizable(False, False)
        self.dialog.transient(self.parent)
        self.dialog.grab_set()

        # Main frame
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.grid(row=0, column=0, sticky="nsew")

        # Title
        title_label = ttk.Label(
            main_frame, text="Blokus Game Mode Selection", font=("Arial", 16, "bold")
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))

        # Mode selection frame
        mode_frame = ttk.LabelFrame(main_frame, text="Game Mode", padding="10")
        mode_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 10))

        # Mode options
        modes = [
            ("Single AI", "single_ai", "Play against one AI opponent"),
            ("Three AI", "three_ai", "Play against three AI opponents"),
            ("Spectate", "spectate", "Watch AI vs AI match"),
            ("PvP Local", "pvp_local", "Local multiplayer (2-4 players)"),
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

        # AI Configuration frame (shown for AI modes)
        self.ai_config_frame = ttk.LabelFrame(
            main_frame, text="AI Configuration", padding="10"
        )
        self.ai_config_frame.grid(
            row=2, column=0, columnspan=2, sticky="ew", pady=(10, 0)
        )

        # Difficulty options
        difficulties = [
            ("Easy", "Easy", "Simple random placement"),
            ("Medium", "Medium", "Balanced corner strategy"),
            ("Hard", "Hard", "Advanced strategic play"),
        ]

        for i, (text, value, description) in enumerate(difficulties):
            rb = ttk.Radiobutton(
                self.ai_config_frame,
                text=text,
                variable=self.selected_difficulty_var,
                value=value,
            )
            rb.grid(row=i, column=0, sticky=tk.W, pady=5)

            desc_label = ttk.Label(
                self.ai_config_frame,
                text=description,
                font=("Arial", 9),
                foreground="gray",
            )
            desc_label.grid(row=i, column=1, sticky=tk.W, padx=(10, 0), pady=5)

        # PvP Configuration frame (shown for PvP mode)
        self.pvp_config_frame = ttk.LabelFrame(
            main_frame, text="PvP Configuration", padding="10"
        )
        self.pvp_config_frame.grid(
            row=2, column=0, columnspan=2, sticky="ew", pady=(10, 0)
        )

        # Player count
        tk.Label(self.pvp_config_frame, text="Number of players:").grid(
            row=0, column=0, sticky=tk.W, pady=5
        )
        player_count_spinbox = ttk.Spinbox(
            self.pvp_config_frame,
            from_=2,
            to=4,
            textvariable=self.player_count_var,
            width=5,
            command=self._on_player_count_change,
        )
        player_count_spinbox.grid(row=0, column=1, sticky=tk.W, padx=(10, 0), pady=5)

        # Player names
        self.pvp_name_frames = []
        for i in range(1, 5):
            frame = ttk.Frame(self.pvp_config_frame)
            self.pvp_name_frames.append(frame)

            tk.Label(frame, text=f"Player {i} name:").grid(
                row=0, column=0, sticky=tk.W, pady=5
            )
            entry = ttk.Entry(
                frame, textvariable=self.player_name_vars[i - 1], width=25
            )
            entry.grid(row=0, column=1, sticky=tk.W, padx=(10, 0), pady=5)

        # Spectate info frame (shown for spectate mode)
        self.spectate_frame = ttk.LabelFrame(
            main_frame, text="Spectate Mode", padding="10"
        )
        self.spectate_frame.grid(
            row=2, column=0, columnspan=2, sticky="ew", pady=(10, 0)
        )

        info_label = ttk.Label(
            self.spectate_frame,
            text="Watch AI vs AI match with mixed difficulty levels",
            font=("Arial", 10),
            foreground="blue",
        )
        info_label.grid(row=0, column=0, sticky=tk.W, pady=5)

        # Game Settings frame
        settings_frame = ttk.LabelFrame(main_frame, text="Game Settings", padding="10")
        settings_frame.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(10, 0))

        # Board size
        tk.Label(settings_frame, text="Board size:").grid(
            row=0, column=0, sticky=tk.W, pady=5
        )
        board_size_spinbox = ttk.Spinbox(
            settings_frame,
            from_=10,
            to=30,
            increment=2,
            textvariable=self.board_size_var,
            width=5,
        )
        board_size_spinbox.grid(row=0, column=1, sticky=tk.W, padx=(10, 0), pady=5)

        # Color scheme
        tk.Label(settings_frame, text="Color scheme:").grid(
            row=1, column=0, sticky=tk.W, pady=5
        )
        color_scheme_combo = ttk.Combobox(
            settings_frame,
            textvariable=self.color_scheme_var,
            values=["default", "pastel", "vibrant", "high_contrast"],
            state="readonly",
            width=22,
        )
        color_scheme_combo.grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=5)

        # Show grid lines
        ttk.Checkbutton(
            settings_frame,
            text="Show grid lines",
            variable=self.show_grid_var,
        ).grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=5)

        # Show coordinates
        ttk.Checkbutton(
            settings_frame,
            text="Show board coordinates",
            variable=self.show_coordinates_var,
        ).grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=5)

        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=(20, 0))

        # Start button
        start_button = ttk.Button(
            button_frame, text="Start Game", command=self._on_start_clicked
        )
        start_button.grid(row=0, column=0, padx=(0, 10))
        self.start_button = start_button

        # Cancel button
        cancel_button = ttk.Button(
            button_frame, text="Cancel", command=self._on_cancel_clicked
        )
        cancel_button.grid(row=0, column=1)

        # Initialize UI state
        self._on_mode_selected()
        self._on_player_count_change()

    def _on_mode_selected(self) -> None:
        """Handle mode selection change."""
        mode = self.selected_mode_var.get()

        # Hide all config frames first
        self.ai_config_frame.grid_remove()
        self.pvp_config_frame.grid_remove()
        self.spectate_frame.grid_remove()

        # Show relevant config frame
        if mode in ["single_ai", "three_ai"]:
            self.ai_config_frame.grid(
                row=2, column=0, columnspan=2, sticky="ew", pady=(10, 0)
            )
        elif mode == "pvp_local":
            self.pvp_config_frame.grid(
                row=2, column=0, columnspan=2, sticky="ew", pady=(10, 0)
            )
        elif mode == "spectate":
            self.spectate_frame.grid(
                row=2, column=0, columnspan=2, sticky="ew", pady=(10, 0)
            )

        # Update validation
        self._validate_form()

    def _on_player_count_change(self) -> None:
        """Handle player count change."""
        count = self.player_count_var.get()

        # Show/hide player name frames based on count
        for i, frame in enumerate(self.pvp_name_frames):
            if i < count:
                frame.grid(row=i + 1, column=0, columnspan=2, sticky="ew")
            else:
                frame.grid_remove()

        # Update validation
        self._validate_form()

    def _validate_form(self) -> bool:
        """
        Validate form inputs.

        Returns:
            True if form is valid, False otherwise
        """
        is_valid = True

        # Check PvP mode player names
        if self.selected_mode_var.get() == "pvp_local":
            count = self.player_count_var.get()
            for i in range(count):
                name: str = self.player_name_vars[i].get()
                if not name.strip():
                    is_valid = False
                    break

        # Enable/disable start button
        if self.start_button:
            self.start_button.config(state=tk.NORMAL if is_valid else tk.DISABLED)

        return is_valid

    def _on_start_clicked(self) -> None:
        """Handle start button click."""
        mode = self.selected_mode_var.get()
        difficulty = self.selected_difficulty_var.get()

        # Create configuration object
        config = {
            "mode_type": mode,
            "board_size": self.board_size_var.get(),
            "color_scheme": self.color_scheme_var.get(),
            "show_grid": self.show_grid_var.get(),
            "show_coordinates": self.show_coordinates_var.get(),
        }

        # Add mode-specific configuration
        if mode in ["single_ai", "three_ai"]:
            config["difficulty"] = difficulty
        elif mode == "pvp_local":
            config["player_count"] = self.player_count_var.get()
            config["player_names"] = [
                self.player_name_vars[i].get()
                for i in range(self.player_count_var.get())
            ]

        # Validate PvP player names
        if mode == "pvp_local":
            for i, name in enumerate(config["player_names"]):
                if not name.strip():
                    messagebox.showerror(
                        "Validation Error",
                        f"Player {i + 1} name cannot be empty",
                    )
                    return

        self.result = config
        self.dialog.destroy()

        # Call callback if provided
        if self.callback:
            try:
                self.callback(mode, config)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to start game: {e}")

    def _on_cancel_clicked(self) -> None:
        """Handle cancel button click."""
        self.result = None
        self.dialog.destroy()

    @staticmethod
    def create_game_mode(mode_type: str, config: dict[str, Any]) -> GameMode:
        """
        Create a GameMode instance from selected options.

        Args:
            mode_type: Type of game mode
            config: Configuration dictionary

        Returns:
            Configured GameMode instance
        """
        from blokus_game.models.game_mode import Difficulty

        if mode_type == "single_ai":
            diff_enum = Difficulty(config.get("difficulty", "Medium"))
            return GameMode.single_ai(diff_enum)
        elif mode_type == "three_ai":
            diff_enum = Difficulty(config.get("difficulty", "Medium"))
            return GameMode.three_ai(diff_enum)
        elif mode_type == "spectate":
            return GameMode.spectate_ai()
        elif mode_type == "pvp_local":
            player_count = config.get("player_count", 2)
            return GameMode.pvp_local(player_count)
        else:
            raise ValueError(f"Unknown game mode: {mode_type}")


def show_unified_game_mode_selector(
    parent: tk.Widget | None = None, callback: Callable | None = None
) -> dict[str, Any] | None:
    """
    Convenience function to show unified game mode selector.

    Args:
        parent: Parent tkinter widget
        callback: Callback function

    Returns:
        Selected configuration or None
    """
    selector = UnifiedGameModeSelector(parent, callback)
    return selector.show()


# Example usage
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # Hide main window

    def on_mode_selected(mode_type: str, config: dict):
        """Callback for mode selection."""
        logger.info(f"Mode selected: {mode_type}, Config: {config}")

        # Create and display game mode
        try:
            game_mode = UnifiedGameModeSelector.create_game_mode(mode_type, config)
            logger.info(f"Created game mode: {game_mode}")
        except Exception as e:
            logger.error(f"Error creating game mode: {e}")

    # Show selector
    result = show_unified_game_mode_selector(root, on_mode_selected)

    if result:
        logger.info(f"Selected: {result}")
    else:
        logger.info("Cancelled")

    root.destroy()
