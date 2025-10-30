"""
Main application entry point for Blokus game.

This module provides the main application class that initializes the game,
handles the setup flow, and manages the overall game lifecycle.
"""

import tkinter as tk
from tkinter import messagebox
from typing import Optional
from src.ui.setup_window import SetupWindow
from src.game.game_setup import GameSetup


class BlokusApp:
    """Main application class for Blokus game."""

    def __init__(self) -> None:
        """Initialize the application."""
        self.root = tk.Tk()
        self.root.title("Blokus - Local Multiplayer")

        # Game state
        self.game_setup: Optional[GameSetup] = None
        self.game_state = None

        # Setup window
        self.setup_window: Optional[SetupWindow] = None

    def run(self) -> None:
        """Run the application main loop."""
        # Show setup dialog
        self._show_setup()

        # Start the main loop
        self.root.mainloop()

    def _show_setup(self) -> None:
        """Show the game setup dialog."""
        self.setup_window = SetupWindow(self.root)
        result = self.setup_window.show()

        if result is None:
            # User cancelled
            self.root.quit()
            return

        try:
            # Setup the game
            self.game_setup = GameSetup()
            self.game_state = self.game_setup.setup_game(
                num_players=result["num_players"], player_names=result["player_names"]
            )

            # Show success message
            self._show_setup_success()

        except ValueError as e:
            # Show error
            messagebox.showerror("Setup Error", str(e))
            self.root.quit()

    def _show_setup_success(self) -> None:
        """
        Show setup completion message and transition to game.

        For now, just display a success message. In future phases,
        this will transition to the actual game UI.
        """
        num_players = len(self.game_setup.get_players())

        message = f"Game setup complete!\n\n" f"Players: {num_players}\n"

        for i, player in enumerate(self.game_setup.get_players()):
            corner = player.get_starting_corner()
            message += f"\n{player.name} (Player {player.player_id}) - Corner: {corner}"

        message += (
            "\n\nGame is ready to start!" "\n\n(Next phase will implement actual gameplay UI)"
        )

        # Create a simple info window
        info_window = tk.Toplevel(self.root)
        info_window.title("Game Ready")
        info_window.geometry("400x300")
        info_window.resizable(False, False)

        # Center the window
        info_window.geometry(
            "+%d+%d"
            % (
                info_window.winfo_screenwidth() // 2 - 200,
                info_window.winfo_screenheight() // 2 - 150,
            )
        )

        # Text widget to show info
        text_frame = tk.Frame(info_window, padx=20, pady=20)
        text_frame.pack(fill=tk.BOTH, expand=True)

        text_widget = tk.Text(text_frame, wrap=tk.WORD, font=("Arial", 11), height=12, width=45)
        text_widget.pack(fill=tk.BOTH, expand=True)
        text_widget.insert(tk.END, message)
        text_widget.config(state=tk.DISABLED)

        # Button frame
        button_frame = tk.Frame(info_window, pady=10)
        button_frame.pack()

        # Close button
        close_btn = tk.Button(
            button_frame,
            text="Close",
            command=self.root.quit,
            bg="#FF6B6B",
            fg="white",
            padx=20,
            pady=5,
        )
        close_btn.pack()


def main() -> None:
    """Main entry point."""
    app = BlokusApp()
    app.run()


if __name__ == "__main__":
    main()
