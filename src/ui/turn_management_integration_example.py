"""
Turn Management Integration Example

This module demonstrates how to integrate the turn management system
with UI state updates and the complete game flow.
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional, Callable
from src.models.game_state import GameState, GamePhase
from src.models.player import Player
from src.game.game_loop import GameLoop
from src.ui.current_player_indicator import CurrentPlayerIndicator
from src.ui.skip_turn_button import SkipTurnButton
from src.ui.scoreboard import Scoreboard


class TurnManagementIntegration:
    """
    Example integration of turn management with UI state updates.

    This class demonstrates how to wire together:
    - GameState
    - GameLoop with TurnManager
    - UI components for turn display and skip functionality
    - Automatic turn advancement and game end detection
    """

    def __init__(self, root: tk.Tk):
        """
        Initialize the turn management integration.

        Args:
            root: Root Tkinter window
        """
        self.root = root
        self.game_state: Optional[GameState] = None
        self.game_loop: Optional[GameLoop] = None
        self.on_ui_update: Optional[Callable[[], None]] = None

        # Create UI layout
        self._create_layout()

    def _create_layout(self) -> None:
        """Create the UI layout for turn management."""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Title
        title_label = ttk.Label(
            main_frame, text="Blokus - Turn Management", font=("Arial", 16, "bold")
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))

        # Left panel - Player info
        left_panel = ttk.LabelFrame(main_frame, text="Player Info", padding="10")
        left_panel.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))

        # Current player indicator
        self.current_player_indicator = CurrentPlayerIndicator(left_panel)
        self.current_player_indicator.grid(row=0, column=0, sticky=(tk.W, tk.E))

        # Skip turn button
        self.skip_turn_button = SkipTurnButton(
            left_panel,
            on_skip_turn=self._on_skip_turn,
        )
        self.skip_turn_button.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(10, 0))

        # Right panel - Game info
        right_panel = ttk.LabelFrame(main_frame, text="Game Info", padding="10")
        right_panel.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Scoreboard
        self.scoreboard = Scoreboard(right_panel)
        self.scoreboard.grid(row=0, column=0, sticky=(tk.W, tk.E))

        # Game status frame
        status_frame = ttk.LabelFrame(right_panel, text="Game Status", padding="10")
        status_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(10, 0))

        # Round and turn info
        round_frame = ttk.Frame(status_frame)
        round_frame.pack(fill=tk.X, pady=2)

        ttk.Label(round_frame, text="Round:", font=("Arial", 10, "bold")).pack(side=tk.LEFT)
        self.round_var = tk.StringVar(value="1")
        ttk.Label(
            round_frame, textvariable=self.round_var, font=("Arial", 10)
        ).pack(side=tk.RIGHT)

        turn_frame = ttk.Frame(status_frame)
        turn_frame.pack(fill=tk.X, pady=2)

        ttk.Label(turn_frame, text="Turn:", font=("Arial", 10, "bold")).pack(side=tk.LEFT)
        self.turn_var = tk.StringVar(value="1")
        ttk.Label(turn_frame, textvariable=self.turn_var, font=("Arial", 10)).pack(
            side=tk.RIGHT
        )

        phase_frame = ttk.Frame(status_frame)
        phase_frame.pack(fill=tk.X, pady=2)

        ttk.Label(phase_frame, text="Phase:", font=("Arial", 10, "bold")).pack(side=tk.LEFT)
        self.phase_var = tk.StringVar(value="SETUP")
        ttk.Label(
            turn_frame, textvariable=self.phase_var, font=("Arial", 10)
        ).pack(side=tk.RIGHT)

        # Control buttons
        control_frame = ttk.LabelFrame(main_frame, text="Controls", padding="10")
        control_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(20, 0))

        ttk.Button(
            control_frame,
            text="Start New Game (2 Players)",
            command=self._start_two_player_game,
        ).pack(side=tk.LEFT, padx=(0, 10))

        ttk.Button(
            control_frame,
            text="Start New Game (4 Players)",
            command=self._start_four_player_game,
        ).pack(side=tk.LEFT, padx=(0, 10))

        ttk.Button(
            control_frame, text="Advance Turn", command=self._advance_turn
        ).pack(side=tk.LEFT, padx=(0, 10))

        ttk.Button(
            control_frame, text="End Game", command=self._end_game
        ).pack(side=tk.LEFT)

    def _start_two_player_game(self) -> None:
        """Start a new two-player game."""
        self._start_game(num_players=2)

    def _start_four_player_game(self) -> None:
        """Start a new four-player game."""
        self._start_game(num_players=4)

    def _start_game(self, num_players: int) -> None:
        """
        Start a new game with specified number of players.

        Args:
            num_players: Number of players (2-4)
        """
        # Create new game state
        self.game_state = GameState()

        # Add players
        player_names = ["Alice", "Bob", "Carol", "Dave"]
        for i in range(num_players):
            player = Player(player_id=i + 1, name=player_names[i])
            self.game_state.add_player(player)

        # Start the game
        self.game_state.start_game()

        # Create game loop
        self.game_loop = GameLoop(
            self.game_state,
            on_game_end=self._on_game_end,
        )

        # Update UI components
        self._update_ui()

    def _advance_turn(self) -> None:
        """Advance to the next player's turn."""
        if not self.game_loop or not self.game_state:
            return

        # Use GameLoop's next_turn method
        self.game_loop.next_turn()

        # Check if game should end
        if self.game_loop.should_end_game():
            self._on_game_end(self.game_state)
            return

        # Update UI
        self._update_ui()

    def _on_skip_turn(self) -> None:
        """Handle skip turn action."""
        if not self.game_loop or not self.game_state:
            return

        # Use TurnManager to skip current player
        self.game_loop.skip_current_player()

        # Check if game should end
        if self.game_loop.should_end_game():
            self._on_game_end(self.game_state)
            return

        # Update UI
        self._update_ui()

    def _end_game(self) -> None:
        """End the current game."""
        if self.game_state:
            self.game_state.end_game()
            self._update_ui()

    def _on_game_end(self, game_state: GameState) -> None:
        """
        Handle game end event.

        Args:
            game_state: Final game state
        """
        # End the game
        game_state.end_game()

        # Update UI
        self._update_ui()

        # Show winner message
        if game_state.players:
            winners = game_state.get_winners()
            if winners:
                winner_names = ", ".join(w.name for w in winners)
                tk.messagebox.showinfo(
                    "Game Over",
                    f"Game Over!\n\nWinner(s): {winner_names}\n\n"
                    f"Final Scores:\n"
                    + "\n".join(
                        f"{p.name}: {p.get_score()} points"
                        for p in game_state.players
                    ),
                )

    def _update_ui(self) -> None:
        """Update all UI components from current game state."""
        if not self.game_state:
            return

        # Update current player indicator
        self.current_player_indicator.set_game_state(self.game_state)

        # Update skip turn button
        self.skip_turn_button.set_game_state(self.game_state)

        # Update scoreboard
        self.scoreboard.set_game_state(self.game_state)

        # Update game status
        self.round_var.set(str(self.game_state.get_round_number()))
        self.turn_var.set(str(self.game_state.get_turn_number()))
        self.phase_var.set(self.game_state.phase.name)

        # Enable/disable controls based on game state
        if self.game_state.is_setup_phase():
            # Game not started yet
            pass
        elif self.game_state.is_playing_phase():
            # Game in progress
            pass
        elif self.game_state.is_game_over():
            # Game over
            pass

    def set_ui_update_callback(self, callback: Callable[[], None]) -> None:
        """
        Set a callback for UI updates.

        Args:
            callback: Function to call when UI should update
        """
        self.on_ui_update = callback


def main():
    """Main function to run the turn management integration example."""
    # Create root window
    root = tk.Tk()
    root.title("Blokus - Turn Management Integration")
    root.geometry("800x600")

    # Create integration
    integration = TurnManagementIntegration(root)

    # Start the main loop
    root.mainloop()


if __name__ == "__main__":
    main()
