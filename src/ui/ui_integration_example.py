"""
UI Integration Example

This module provides an example of how to integrate the game end detection
and winner determination with the UI components.

This is a demonstration/example file showing the integration pattern.
"""

import tkinter as tk
from tkinter import ttk

from src.game.game_loop import GameLoop
from src.models.game_state import GameState
from src.ui.game_results import GameResults


class BlokusGameUI(ttk.Frame):
    """
    Example main game UI showing integration with game end detection.

    This is a simplified example demonstrating the integration pattern.
    In a full implementation, this would be the main game window.
    """

    def __init__(self, parent: tk.Widget):
        """
        Initialize the game UI.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.game_state: GameState | None = None
        self.game_loop: GameLoop | None = None

        # Create UI
        self._create_ui()

    def _create_ui(self) -> None:
        """Create the UI components."""
        # Title
        title_label = ttk.Label(
            self,
            text="Blokus Game",
            font=("Arial", 16, "bold"),
        )
        title_label.pack(pady=10)

        # Game info
        self.game_info_label = ttk.Label(
            self,
            text="No game started",
        )
        self.game_info_label.pack(pady=5)

        # Start Game button
        self.start_button = ttk.Button(
            self,
            text="Start Demo Game",
            command=self._start_demo_game,
        )
        self.start_button.pack(pady=10)

        # Place Piece button
        self.place_button = ttk.Button(
            self,
            text="Place Random Piece",
            command=self._place_random_piece,
            state=tk.DISABLED,
        )
        self.place_button.pack(pady=5)

        # Pass Turn button
        self.pass_button = ttk.Button(
            self,
            text="Pass Turn",
            command=self._pass_turn,
            state=tk.DISABLED,
        )
        self.pass_button.pack(pady=5)

        # End Game button (for testing)
        self.end_game_button = ttk.Button(
            self,
            text="End Game (Test)",
            command=self._end_game,
            state=tk.DISABLED,
        )
        self.end_game_button.pack(pady=5)

    def _start_demo_game(self) -> None:
        """Start a demo game with sample data."""
        # Create game state
        self.game_state = GameState()

        # Add players
        from src.models.player import Player

        player1 = Player(1, "Alice")
        player2 = Player(2, "Bob")
        self.game_state.add_player(player1)
        self.game_state.add_player(player2)

        # Start game
        self.game_state.start_game()

        # Create game loop with end game callback
        self.game_loop = GameLoop(
            self.game_state,
            on_game_end=self._on_game_end,
        )

        # Update UI
        self._update_ui_for_game_started()

        print("Demo game started!")

    def _place_random_piece(self) -> None:
        """Place a random piece (demo)."""
        if not self.game_state or not self.game_loop:
            return

        current_player = self.game_state.get_current_player()
        if not current_player:
            return

        # Get unplaced pieces
        unplaced = current_player.get_unplaced_pieces()
        if not unplaced:
            # No pieces left, pass turn
            self._pass_turn()
            return

        # Place first available piece (demo)
        piece = unplaced[0]
        piece.is_placed = True

        print(f"{current_player.name} placed piece: {piece.name}")

        # Advance turn
        self.game_loop.next_turn()

        # Update UI
        self._update_ui_for_turn_change()

    def _pass_turn(self) -> None:
        """Pass the current turn."""
        if not self.game_state or not self.game_loop:
            return

        current_player = self.game_state.get_current_player()
        if current_player:
            print(f"{current_player.name} passed their turn")
            self.game_loop.pass_turn(current_player.player_id)

            # Update UI
            self._update_ui_for_turn_change()

    def _end_game(self) -> None:
        """Manually end the game (for testing)."""
        if not self.game_loop:
            return

        self.game_loop.end_game()
        self._on_game_end(self.game_state)

    def _on_game_end(self, game_state: GameState) -> None:
        """Callback when game ends - show results."""
        print("Game Over!")
        print(f"Game end reason: {self.game_loop.get_end_game_reason()}")

        # Calculate final scores
        final_scores = self.game_loop.calculate_final_scores()
        print("Final scores:")
        for player_id, score in final_scores.items():
            player = game_state.get_player_by_id(player_id)
            if player:
                print(f"  {player.name}: {score}")

        # Get winners
        winners = self.game_loop.get_winners()
        winner_names = [w.name for w in winners]
        print(f"Winner(s): {', '.join(winner_names)}")

        # Show results UI (if we have a parent window)
        if self.winfo_toplevel():
            self._show_game_results_ui()

        # Update UI for game over
        self._update_ui_for_game_over()

    def _show_game_results_ui(self) -> None:
        """Show the game results UI window."""
        if not self.game_state or not self.game_loop:
            return

        # Create results window
        results_window = GameResults(
            self.winfo_toplevel(),
            self.game_state,
            self.game_loop.winner_determiner,
        )

        # Set callback for new game
        results_window.set_new_game_callback(self._start_demo_game)

        # Focus the results window
        results_window.grab_set()

    def _update_ui_for_game_started(self) -> None:
        """Update UI for game started state."""
        self.start_button.config(state=tk.DISABLED)
        self.place_button.config(state=tk.NORMAL)
        self.pass_button.config(state=tk.NORMAL)
        self.end_game_button.config(state=tk.NORMAL)
        self._update_ui_for_turn_change()

    def _update_ui_for_turn_change(self) -> None:
        """Update UI for turn change."""
        if not self.game_state:
            return

        current_player = self.game_state.get_current_player()
        if current_player:
            self.game_info_label.config(
                text=f"Current Player: {current_player.name} "
                f"(Round {self.game_state.get_round_number()})"
            )
        else:
            self.game_info_label.config(text="No current player")

    def _update_ui_for_game_over(self) -> None:
        """Update UI for game over state."""
        self.place_button.config(state=tk.DISABLED)
        self.pass_button.config(state=tk.DISABLED)
        self.end_game_button.config(state=tk.DISABLED)
        self.start_button.config(state=tk.NORMAL)
        self.game_info_label.config(text="Game Over - See results window")


def run_demo() -> None:
    """Run the UI integration demo."""
    root = tk.Tk()
    root.title("Blokus Game - UI Integration Demo")
    root.geometry("600x400")

    # Create game UI
    game_ui = BlokusGameUI(root)
    game_ui.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

    # Run the main loop
    root.mainloop()


if __name__ == "__main__":
    run_demo()
