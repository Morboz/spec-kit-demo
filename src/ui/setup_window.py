"""
Game Setup UI Window

This module provides the user interface for setting up a new Blokus game,
allowing players to configure the number of players and their names.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, List, Dict


class SetupWindow:
    """Game setup dialog window."""

    def __init__(self, parent: Optional[tk.Widget] = None):
        """
        Initialize the setup window.

        Args:
            parent: Parent tkinter widget
        """
        self.parent = parent
        self.result: Optional[Dict] = None
        self.dialog: Optional[tk.Toplevel] = None

        # Player configuration
        self.num_players_var = tk.IntVar(value=2)
        self.player_names: List[tk.StringVar] = [
            tk.StringVar(value=f"Player {i+1}") for i in range(4)
        ]

    def show(self) -> Optional[Dict]:
        """
        Show the setup dialog and wait for user input.

        Returns:
            Dictionary with game configuration or None if cancelled
        """
        self._create_dialog()
        self.dialog.wait_window()
        return self.result

    def _create_dialog(self) -> None:
        """Create and display the setup dialog."""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("New Blokus Game")
        self.dialog.geometry("400x500")
        self.dialog.resizable(False, False)

        # Make dialog modal
        if self.parent:
            self.dialog.transient(self.parent)
            self.dialog.grab_set()

        # Center the dialog
        self.dialog.geometry(
            "+%d+%d"
            % (
                self.dialog.winfo_screenwidth() // 2 - 200,
                self.dialog.winfo_screenheight() // 2 - 250,
            )
        )

        # Main frame
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        title_label = ttk.Label(
            main_frame, text="New Blokus Game", font=("Arial", 16, "bold")
        )
        title_label.pack(pady=(0, 20))

        # Number of players selection
        players_frame = ttk.LabelFrame(
            main_frame, text="Number of Players", padding="10"
        )
        players_frame.pack(fill=tk.X, pady=(0, 10))

        for num in [2, 3, 4]:
            rb = ttk.Radiobutton(
                players_frame,
                text=str(num),
                value=num,
                variable=self.num_players_var,
                command=self._on_num_players_change,
            )
            rb.pack(side=tk.LEFT, padx=(0, 20))

        # Player names section
        names_frame = ttk.LabelFrame(main_frame, text="Player Names", padding="10")
        names_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        self.name_entries: List[ttk.Entry] = []
        for i in range(4):
            row_frame = ttk.Frame(names_frame)
            row_frame.pack(fill=tk.X, pady=2)

            label = ttk.Label(row_frame, text=f"Player {i+1}:", width=10)
            label.pack(side=tk.LEFT)

            entry = ttk.Entry(row_frame, textvariable=self.player_names[i], width=30)
            entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

            self.name_entries.append(entry)

        # Update which entries are enabled
        self._on_num_players_change()

        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))

        cancel_btn = ttk.Button(button_frame, text="Cancel", command=self._on_cancel)
        cancel_btn.pack(side=tk.RIGHT, padx=(10, 0))

        start_btn = ttk.Button(
            button_frame, text="Start Game", command=self._on_start_game
        )
        start_btn.pack(side=tk.RIGHT)

        # Focus on first entry
        self.name_entries[0].focus_set()

    def _on_num_players_change(self) -> None:
        """Handle change in number of players."""
        num_players = self.num_players_var.get()

        # Enable/disable name entries based on player count
        for i, entry in enumerate(self.name_entries):
            if i < num_players:
                entry.config(state="normal")
            else:
                entry.config(state="disabled")

    def _on_cancel(self) -> None:
        """Handle cancel button click."""
        self.result = None
        self.dialog.destroy()

    def _on_start_game(self) -> None:
        """Handle start game button click."""
        num_players = self.num_players_var.get()
        player_names = [self.player_names[i].get().strip() for i in range(num_players)]

        # Validate player names
        if num_players < 2:
            messagebox.showerror("Error", "At least 2 players are required")
            return

        # Check for empty names
        for i, name in enumerate(player_names):
            if not name:
                messagebox.showerror("Error", f"Player {i+1} name cannot be empty")
                return

        # Check for duplicate names
        if len(player_names) != len(set(player_names)):
            messagebox.showerror("Error", "Player names must be unique")
            return

        # Store result and close dialog
        self.result = {"num_players": num_players, "player_names": player_names}
        self.dialog.destroy()
