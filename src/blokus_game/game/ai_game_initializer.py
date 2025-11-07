"""
AI Game Initializer

This module provides integration between AI game modes and the main game initialization.
It handles spawning AI players and configuring the game for AI battles.
"""

import tkinter as tk
from tkinter import messagebox
from typing import Any

from blokus_game.models.ai_config import AIConfig
from blokus_game.models.ai_player import AIPlayer
from blokus_game.models.game_mode import GameMode
from blokus_game.ui.game_mode_selector import GameModeSelector


class AIGameInitializer:
    """
    Handles initialization of AI battle modes.

    Integrates with the main game setup to:
    - Show AI mode selection dialog
    - Spawn AI players
    - Configure game for AI battles
    """

    def __init__(self, parent_window: tk.Widget | None = None):
        """
        Initialize AI game initializer.

        Args:
            parent_window: Parent tkinter window for dialogs
        """
        self.parent_window = parent_window
        self.selected_mode: str | None = None
        self.selected_difficulty: str | None = None
        self.game_mode: GameMode | None = None

    def show_ai_mode_selector(self) -> bool:
        """
        Show AI mode selection dialog.

        Returns:
            True if mode was selected, False if cancelled
        """

        def on_mode_selected(mode_type: str, difficulty: str):
            """Callback for mode selection."""
            self.selected_mode = mode_type
            self.selected_difficulty = difficulty

        # Show selector dialog
        selector = GameModeSelector(self.parent_window, on_mode_selected)
        result = selector.show()

        if result is None:
            # User cancelled
            return False

        # Create GameMode from selection
        try:
            self.game_mode = GameModeSelector.create_game_mode(
                self.selected_mode, self.selected_difficulty
            )
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create game mode: {e}")
            return False

    def spawn_ai_players(self) -> list[AIPlayer]:
        """
        Spawn AI players based on selected mode.

        Returns:
            List of created AI players

        Raises:
            ValueError: If no game mode is configured
        """
        if self.game_mode is None:
            raise ValueError(
                "No game mode configured. Call show_ai_mode_selector() first."
            )

        ai_players: list[AIPlayer] = []

        for config in self.game_mode.ai_players:
            try:
                # Create strategy based on difficulty
                strategy = config._create_strategy()

                # Create AI player
                ai_player = config.create_player(strategy)
                ai_players.append(ai_player)

            except Exception as e:
                messagebox.showwarning(
                    "AI Player Error",
                    f"Failed to create AI player at position {config.position}: {e}",
                )

        return ai_players

    def get_human_player_position(self) -> int | None:
        """
        Get position of human player.

        Returns:
            Human player position (1-4) or None if spectate mode
        """
        if self.game_mode is None:
            return None
        return self.game_mode.human_player_position

    def get_ai_players(self) -> list[AIConfig]:
        """
        Get AI player configurations.

        Returns:
            List of AI player configurations
        """
        if self.game_mode is None:
            return []
        return self.game_mode.ai_players

    def configure_game_for_ai(self, game_config) -> bool:
        """
        Configure game for AI battle mode.

        Args:
            game_config: GameConfig instance to modify

        Returns:
            True if configuration successful
        """
        if self.game_mode is None:
            messagebox.showerror("Error", "No game mode selected")
            return False

        try:
            # Clear existing players
            game_config.players.clear()

            # Add human player (if not spectate)
            if self.game_mode.human_player_position:
                human_pos = self.game_mode.human_player_position
                color = game_config.get_player_color(human_pos)
                game_config.add_player(human_pos, "Human", color)

            # Add AI players
            for config in self.game_mode.ai_players:
                color = config.get_color()
                name = config.get_name()
                game_config.add_player(config.position, name, color)

            return True

        except Exception as e:
            messagebox.showerror(
                "Configuration Error", f"Failed to configure game: {e}"
            )
            return False

    def get_mode_description(self) -> str:
        """
        Get description of selected mode.

        Returns:
            Human-readable description of the mode
        """
        if not self.selected_mode:
            return "No mode selected"

        descriptions = {
            "single_ai": "Single AI Battle",
            "three_ai": "Three AI Battle",
            "spectate": "AI vs AI Spectator",
        }

        base_desc = descriptions.get(self.selected_mode, "Unknown Mode")

        if self.selected_difficulty and self.selected_mode != "spectate":
            return f"{base_desc} ({self.selected_difficulty} difficulty)"
        elif self.selected_mode == "spectate":
            return f"{base_desc} (Mixed difficulties)"
        else:
            return base_desc

    @staticmethod
    def integrate_with_main_menu(parent_window: tk.Widget) -> dict[str, Any] | None:
        """
        Integrate AI mode selector with main menu.

        Args:
            parent_window: Parent window for dialogs

        Returns:
            Configuration dictionary or None if cancelled
        """
        initializer = AIGameInitializer(parent_window)

        # Show mode selector
        if not initializer.show_ai_mode_selector():
            return None

        # Create result configuration
        result = {
            "mode_type": initializer.selected_mode,
            "difficulty": initializer.selected_difficulty,
            "game_mode": initializer.game_mode,
            "ai_players": initializer.spawn_ai_players(),
            "human_position": initializer.get_human_player_position(),
            "description": initializer.get_mode_description(),
        }

        return result

    @staticmethod
    def create_ai_players_from_config(
        mode_type: str, difficulty: str | None = None
    ) -> list[AIPlayer]:
        """
        Create AI players from mode configuration.

        Args:
            mode_type: Type of game mode
            difficulty: Difficulty level

        Returns:
            List of AI players
        """
        game_mode = GameModeSelector.create_game_mode(mode_type, difficulty)

        ai_players: list[AIPlayer] = []
        for config in game_mode.ai_players:
            try:
                strategy = config._create_strategy()
                ai_player = config.create_player(strategy)
                ai_players.append(ai_player)
            except Exception as e:
                print(f"Warning: Failed to create AI player: {e}")

        return ai_players


# Example integration with main menu
def show_ai_battle_mode(parent_window: tk.Widget) -> dict[str, Any] | None:
    """
    Show AI battle mode selector dialog.

    Args:
        parent_window: Parent tkinter window

    Returns:
        AI game configuration or None if cancelled
    """
    initializer = AIGameInitializer(parent_window)

    if not initializer.show_ai_mode_selector():
        return None

    # Create AI players
    ai_players = initializer.spawn_ai_players()

    # Return configuration
    return {
        "mode_type": initializer.selected_mode,
        "difficulty": initializer.selected_difficulty,
        "game_mode": initializer.game_mode,
        "ai_players": ai_players,
        "human_position": initializer.get_human_player_position(),
        "description": initializer.get_mode_description(),
    }


if __name__ == "__main__":
    # Test the AI game initializer
    root = tk.Tk()
    root.withdraw()  # Hide main window

    config = show_ai_battle_mode(root)

    if config:
        print("AI Battle Configuration:")
        print(f"  Mode: {config['mode_type']}")
        print(f"  Difficulty: {config['difficulty']}")
        print(f"  Human Position: {config['human_position']}")
        print(f"  AI Players: {len(config['ai_players'])}")

        for ai in config["ai_players"]:
            print(f"    - {ai}")
    else:
        print("Cancelled")

    root.destroy()
