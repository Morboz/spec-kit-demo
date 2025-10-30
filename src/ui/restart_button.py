"""
Restart button component for Blokus game.

This module provides functionality to restart the game with
options to:
- Start a new game with same players
- Start a new game with different settings
- Confirm restart with dialog
- Preserve game statistics if desired
"""

import tkinter as tk
from tkinter import messagebox
from typing import Optional, Callable, Any


class RestartButton:
    """Button component for restarting the game."""

    def __init__(
        self,
        parent: tk.Widget,
        game_state: Any,
        board: Any,
        on_restart: Optional[Callable[[], None]] = None,
        preserve_stats: bool = True,
    ):
        """
        Initialize restart button.

        Args:
            parent: Parent widget
            game_state: Game state object
            board: Board object
            on_restart: Callback function to call after restart
            preserve_stats: Whether to preserve statistics
        """
        self.parent = parent
        self.game_state = game_state
        self.board = board
        self.on_restart = on_restart
        self.preserve_stats = preserve_stats

        self.button: Optional[tk.Button] = None

    def create_button(
        self,
        text: str = "Restart Game",
        tooltip: str = "Start a new game",
    ) -> tk.Button:
        """
        Create and return the restart button widget.

        Args:
            text: Button text
            tooltip: Tooltip text

        Returns:
            The created button widget
        """
        self.button = tk.Button(
            self.parent,
            text=text,
            command=self._handle_click,
            bg="#FF6B6B",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=10,
            pady=5,
        )

        # Add tooltip
        self._add_tooltip(self.button, tooltip)

        return self.button

    def _handle_click(self):
        """Handle button click event."""
        self.show_restart_dialog()

    def show_restart_dialog(self) -> bool:
        """
        Show restart confirmation dialog.

        Returns:
            True if restart should proceed, False otherwise
        """
        result = messagebox.askyesnocancel(
            "Restart Game",
            "Do you want to start a new game?\n\n"
            "Yes   - Restart with current settings\n"
            "No    - Restart with different settings\n"
            "Cancel - Do not restart",
            icon="question",
        )

        if result is None:  # Cancel
            return False
        elif result:  # Yes - restart with current settings
            return self._restart_game(preserve_settings=True)
        else:  # No - restart with different settings
            return self._restart_game(preserve_settings=False)

    def _restart_game(self, preserve_settings: bool) -> bool:
        """
        Restart the game.

        Args:
            preserve_settings: Whether to preserve current game settings

        Returns:
            True if restart successful, False otherwise
        """
        try:
            # Store current game configuration if preserving
            saved_config = None
            if preserve_settings and hasattr(self.game_state, "get_config"):
                saved_config = self.game_state.get_config()

            # Reset game state
            self._reset_game_state()

            # Reset board
            self._reset_board()

            # Call restart callback if provided
            if self.on_restart:
                self.on_restart()

            # Show confirmation message
            messagebox.showinfo(
                "Game Restarted",
                "New game has started!",
                icon="info",
            )

            return True

        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Failed to restart game: {str(e)}",
                icon="error",
            )
            return False

    def _reset_game_state(self):
        """Reset game state to initial values."""
        if hasattr(self.game_state, "reset"):
            self.game_state.reset()
        else:
            # Manually reset common attributes
            if hasattr(self.game_state, "players"):
                for player in self.game_state.players:
                    if hasattr(player, "reset"):
                        player.reset()

            if hasattr(self.game_state, "current_player_index"):
                self.game_state.current_player_index = 0

            if hasattr(self.game_state, "game_phase"):
                self.game_state.game_phase = "setup"

            if hasattr(self.game_state, "turn_count"):
                self.game_state.turn_count = 0

    def _reset_board(self):
        """Reset board to initial state."""
        if hasattr(self.board, "reset"):
            self.board.reset()
        else:
            # Manually reset board
            if hasattr(self.board, "grid"):
                rows = len(self.board.grid)
                cols = len(self.board.grid[0]) if rows > 0 else 0
                self.board.grid = [[0 for _ in range(cols)] for _ in range(rows)]

            if hasattr(self.board, "placed_pieces"):
                self.board.placed_pieces = {}

    def _add_tooltip(self, widget: tk.Widget, text: str):
        """
        Add tooltip to widget.

        Args:
            widget: Widget to add tooltip to
            text: Tooltip text
        """
        def on_enter(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.configure(bg="#FFFF99")
            label = tk.Label(tooltip, text=text, bg="#FFFF99", justify=tk.LEFT)
            label.pack()
            x, y, _, _ = widget.bbox("insert")
            x += widget.winfo_rootx() + 20
            y += widget.winfo_rooty() + 20
            tooltip.wm_geometry(f"+{x}+{y}")
            widget.tooltip = tooltip

        def on_leave(event):
            if hasattr(widget, "tooltip"):
                widget.tooltip.destroy()
                del widget.tooltip

        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)

    def enable(self):
        """Enable the restart button."""
        if self.button:
            self.button.config(state=tk.NORMAL)

    def disable(self):
        """Disable the restart button."""
        if self.button:
            self.button.config(state=tk.DISABLED)

    def update_text(self, text: str):
        """Update button text."""
        if self.button:
            self.button.config(text=text)

    def destroy(self):
        """Destroy the button widget."""
        if self.button:
            self.button.destroy()


class GameRestartDialog:
    """Dialog for configuring game restart options."""

    def __init__(self, parent: tk.Widget):
        """
        Initialize restart dialog.

        Args:
            parent: Parent widget
        """
        self.parent = parent
        self.result: Optional[dict] = None
        self.dialog: Optional[tk.Toplevel] = None

    def show(self) -> Optional[dict]:
        """
        Show the restart dialog and return configuration.

        Returns:
            Dictionary with restart configuration or None if cancelled
        """
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("New Game Configuration")
        self.dialog.geometry("400x500")
        self.dialog.transient(self.parent)
        self.dialog.grab_set()

        # Center the dialog
        self.dialog.geometry("+%d+%d" % (
            self.parent.winfo_rootx() + 50,
            self.parent.winfo_rooty() + 50
        ))

        # Store result
        self.result = {}

        # Create UI
        self._create_ui()

        # Wait for dialog to close
        self.dialog.wait_window()

        return self.result

    def _create_ui(self):
        """Create the dialog UI."""
        # Main frame
        main_frame = tk.Frame(self.dialog, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        title_label = tk.Label(
            main_frame,
            text="Configure New Game",
            font=("Arial", 14, "bold"),
        )
        title_label.pack(pady=(0, 20))

        # Player configuration frame
        player_frame = tk.LabelFrame(main_frame, text="Players", padx=10, pady=10)
        player_frame.pack(fill=tk.X, pady=(0, 10))

        # Number of players
        tk.Label(player_frame, text="Number of players:").grid(
            row=0, column=0, sticky=tk.W, pady=5
        )
        self.player_count_var = tk.IntVar(value=2)
        player_count_spinbox = tk.Spinbox(
            player_frame,
            from_=2,
            to=4,
            textvariable=self.player_count_var,
            width=5,
            command=self._on_player_count_change,
        )
        player_count_spinbox.grid(row=0, column=1, sticky=tk.W, padx=10, pady=5)

        # Player names
        self.player_name_vars = []
        for i in range(1, 5):
            var = tk.StringVar(value=f"Player {i}")
            self.player_name_vars.append(var)

            if i <= 2:  # Show first two by default
                tk.Label(player_frame, text=f"Player {i} name:").grid(
                    row=i, column=0, sticky=tk.W, pady=5
                )
                entry = tk.Entry(player_frame, textvariable=var, width=20)
                entry.grid(row=i, column=1, sticky=tk.W, padx=10, pady=5)

        # Game settings frame
        settings_frame = tk.LabelFrame(main_frame, text="Settings", padx=10, pady=10)
        settings_frame.pack(fill=tk.X, pady=(0, 10))

        # Board size
        tk.Label(settings_frame, text="Board size:").grid(
            row=0, column=0, sticky=tk.W, pady=5
        )
        self.board_size_var = tk.IntVar(value=20)
        board_size_spinbox = tk.Spinbox(
            settings_frame,
            from_=10,
            to=30,
            increment=2,
            textvariable=self.board_size_var,
            width=5,
        )
        board_size_spinbox.grid(row=0, column=1, sticky=tk.W, padx=10, pady=5)

        # Color scheme
        tk.Label(settings_frame, text="Color scheme:").grid(
            row=1, column=0, sticky=tk.W, pady=5
        )
        self.color_scheme_var = tk.StringVar(value="default")
        color_scheme_combo = tk.Combobox(
            settings_frame,
            textvariable=self.color_scheme_var,
            values=["default", "pastel", "vibrant", "high_contrast"],
            state="readonly",
            width=17,
        )
        color_scheme_combo.grid(row=1, column=1, sticky=tk.W, padx=10, pady=5)

        # Show grid lines
        self.show_grid_var = tk.BooleanVar(value=True)
        tk.Checkbutton(
            settings_frame,
            text="Show grid lines",
            variable=self.show_grid_var,
        ).grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=5)

        # Show coordinates
        self.show_coords_var = tk.BooleanVar(value=False)
        tk.Checkbutton(
            settings_frame,
            text="Show board coordinates",
            variable=self.show_coords_var,
        ).grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=5)

        # Buttons frame
        button_frame = tk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))

        # Cancel button
        cancel_button = tk.Button(
            button_frame,
            text="Cancel",
            command=self._cancel,
            width=10,
        )
        cancel_button.pack(side=tk.RIGHT, padx=5)

        # Start button
        start_button = tk.Button(
            button_frame,
            text="Start Game",
            command=self._start_game,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 10, "bold"),
            width=10,
        )
        start_button.pack(side=tk.RIGHT, padx=5)

    def _on_player_count_change(self):
        """Handle player count change."""
        count = self.player_count_var.get()

        # Update visibility of player name entries
        for i in range(1, 5):
            for widget in player_frame.winfo_children():
                pass  # Will be handled automatically by grid

    def _cancel(self):
        """Cancel dialog."""
        self.result = None
        self.dialog.destroy()

    def _start_game(self):
        """Start new game with selected configuration."""
        # Validate inputs
        if not self.player_name_vars[0].get().strip():
            messagebox.showerror("Error", "Player 1 name cannot be empty")
            return

        if not self.player_name_vars[1].get().strip():
            messagebox.showerror("Error", "Player 2 name cannot be empty")
            return

        # Store configuration
        self.result = {
            "player_count": self.player_count_var.get(),
            "player_names": [
                self.player_name_vars[i].get()
                for i in range(self.player_count_var.get())
            ],
            "board_size": self.board_size_var.get(),
            "color_scheme": self.color_scheme_var.get(),
            "show_grid": self.show_grid_var.get(),
            "show_coordinates": self.show_coords_var.get(),
        }

        self.dialog.destroy()

    def get_config(self) -> Optional[dict]:
        """
        Get the configuration from dialog.

        Returns:
            Configuration dictionary or None if cancelled
        """
        return self.result