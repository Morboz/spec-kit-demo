"""
Main application entry point for Blokus game.

This module provides the main application class that initializes the game,
handles the setup flow, and manages the overall game lifecycle.
"""

import tkinter as tk
from tkinter import messagebox, ttk
from typing import Optional
from src.ui.setup_window import SetupWindow
from src.game.game_setup import GameSetup
from src.game.placement_handler import PlacementHandler
from src.ui.piece_selector import PieceSelector
from src.ui.piece_display import PieceDisplay
from src.ui.current_player_indicator import CurrentPlayerIndicator
from src.ui.scoreboard import Scoreboard
from src.ui.piece_inventory import PieceInventory
from src.ui.state_sync import StateSynchronizer


class BlokusApp:
    """Main application class for Blokus game."""

    def __init__(self) -> None:
        """Initialize the application."""
        self.root = tk.Tk()
        self.root.title("Blokus - Local Multiplayer")

        # Game state
        self.game_setup: Optional[GameSetup] = None
        self.game_state = None
        self.placement_handler: Optional[PlacementHandler] = None
        self.state_synchronizer: Optional[StateSynchronizer] = None

        # Setup window
        self.setup_window: Optional[SetupWindow] = None

        # UI components
        self.game_window: Optional[tk.Toplevel] = None
        self.piece_selector: Optional[PieceSelector] = None
        self.piece_display: Optional[PieceDisplay] = None
        self.current_player_indicator: Optional[CurrentPlayerIndicator] = None
        self.scoreboard: Optional[Scoreboard] = None
        self.piece_inventory: Optional[PieceInventory] = None

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

            # Initialize placement handler
            current_player = self.game_state.get_current_player()
            if current_player:
                self.placement_handler = PlacementHandler(
                    self.game_state.board, self.game_state, current_player
                )
                self._setup_callbacks()

            # Show the game UI
            self._show_game_ui()

        except ValueError as e:
            # Show error
            messagebox.showerror("Setup Error", str(e))
            self.root.quit()

    def _setup_callbacks(self) -> None:
        """Setup callbacks for placement handler."""
        if not self.placement_handler:
            return

        # Set callback for successful piece placement
        def on_piece_placed(piece_name: str):
            """Handle successful piece placement."""
            # Refresh piece selector
            if self.piece_selector:
                self.piece_selector.refresh()

            # Clear piece display
            if self.piece_display:
                self.piece_display.clear()

            # Update state synchronizer
            if self.state_synchronizer:
                self.state_synchronizer.notify_board_update()
                self.state_synchronizer.notify_player_update(
                    self.placement_handler.current_player.player_id
                )

            # Update current player
            current_player = self.game_state.get_current_player()
            if current_player:
                self.placement_handler.current_player = current_player
                self.placement_handler.clear_selection()

                # Notify turn change
                if self.state_synchronizer:
                    self.state_synchronizer.notify_turn_change()

            # Update piece selector with new current player
            if self.piece_selector and current_player:
                self.piece_selector.set_player(current_player)

            # Show success message
            messagebox.showinfo(
                "Piece Placed",
                f"{piece_name} placed successfully! Turn passes to next player.",
            )

        # Set callback for placement errors
        def on_placement_error(error_msg: str):
            """Handle placement error."""
            messagebox.showerror("Invalid Move", error_msg)

        # Configure callbacks
        self.placement_handler.set_callbacks(
            on_piece_placed=on_piece_placed, on_placement_error=on_placement_error
        )

    def _show_game_ui(self) -> None:
        """Show the main game UI window."""
        if not self.game_state or not self.placement_handler:
            return

        # Create state synchronizer
        self.state_synchronizer = StateSynchronizer(self.game_state)
        self.state_synchronizer.set_board(self.game_state.board)
        self.state_synchronizer.set_players(self.game_state.players)

        # Create game window
        self.game_window = tk.Toplevel(self.root)
        self.game_window.title("Blokus - Game")
        self.game_window.geometry("1400x900")
        self.game_window.resizable(True, True)

        # Create main container
        main_frame = ttk.Frame(self.game_window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Create top panel (current player indicator and scoreboard)
        top_panel = ttk.Frame(main_frame)
        top_panel.pack(side=tk.TOP, fill=tk.X, pady=(0, 10))

        # Left side of top panel - Current Player Indicator
        current_player_frame = ttk.Frame(top_panel)
        current_player_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        current_player = self.game_state.get_current_player()
        self.current_player_indicator = CurrentPlayerIndicator(
            current_player_frame, self.game_state
        )
        self.current_player_indicator.pack(fill=tk.X)
        self.state_synchronizer.attach_current_player_indicator(
            self.current_player_indicator
        )

        # Right side of top panel - Scoreboard
        scoreboard_frame = ttk.Frame(top_panel)
        scoreboard_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.scoreboard = Scoreboard(
            scoreboard_frame, self.game_state.board, self.game_state.players
        )
        self.scoreboard.pack(fill=tk.BOTH, expand=True)
        self.state_synchronizer.attach_scoreboard(self.scoreboard)

        # Create middle-left panel (piece selector and display)
        middle_left_panel = ttk.Frame(main_frame, width=350)
        middle_left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        middle_left_panel.pack_propagate(False)

        # Piece selector
        if current_player:
            self.piece_selector = PieceSelector(
                middle_left_panel,
                current_player,
                on_piece_selected=self._on_piece_selected,
            )
            self.piece_selector.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Piece display with controls
        self.piece_display = PieceDisplay(middle_left_panel)
        self.piece_display.pack(fill=tk.X)

        # Create middle-right panel (piece inventory)
        middle_right_panel = ttk.Frame(main_frame, width=300)
        middle_right_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        middle_right_panel.pack_propagate(False)

        self.piece_inventory = PieceInventory(
            middle_right_panel, self.game_state.players
        )
        self.piece_inventory.pack(fill=tk.BOTH, expand=True)
        self.state_synchronizer.attach_piece_inventory(self.piece_inventory)

        # Select current player's tab in inventory
        if current_player:
            self.piece_inventory.select_player_tab(current_player.player_id)

        # Create center panel (game board placeholder)
        center_panel = ttk.Frame(main_frame)
        center_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Board placeholder
        board_placeholder = ttk.Label(
            center_panel,
            text="Game Board\n\n(Board rendering will be implemented in future phases)",
            font=("Arial", 16),
            justify=tk.CENTER,
            relief="solid",
            borderwidth=2,
        )
        board_placeholder.pack(fill=tk.BOTH, expand=True, padx=10, pady=0)

        # Game status bar
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(10, 0))

        self.status_label = ttk.Label(
            status_frame,
            text=f"Game Phase: {self.game_state.phase.name} | "
            f"Players: {self.game_state.get_player_count()} | "
            f"Current: {current_player.name if current_player else 'N/A'}",
            font=("Arial", 10),
        )
        self.status_label.pack(side=tk.LEFT)

        # Close button
        close_btn = ttk.Button(status_frame, text="Quit Game", command=self.root.quit)
        close_btn.pack(side=tk.RIGHT)

        # Perform initial state sync
        if self.state_synchronizer:
            self.state_synchronizer.full_update()

    def _on_piece_selected(self, piece_name: str) -> None:
        """
        Handle piece selection from piece selector.

        Args:
            piece_name: Name of selected piece
        """
        if not self.placement_handler:
            return

        # Select the piece
        if self.placement_handler.select_piece(piece_name):
            # Display the piece
            selected_piece = self.placement_handler.get_selected_piece()
            if selected_piece and self.piece_display:
                self.piece_display.set_piece(selected_piece)


def main() -> None:
    """Main entry point."""
    app = BlokusApp()
    app.run()


if __name__ == "__main__":
    main()
