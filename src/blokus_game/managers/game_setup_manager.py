"""
Game Setup Manager for Blokus

This manager handles all game initialization and configuration logic,
including preset selection, custom configuration, and AI game setup.
"""

import tkinter as tk
from collections.abc import Callable
from tkinter import messagebox
from typing import Any

from blokus_game.config.game_config import GameConfig, create_config_from_preset
from blokus_game.game.error_handler import get_error_handler
from blokus_game.game.game_setup import GameSetup
from blokus_game.game.placement_handler import PlacementHandler
from blokus_game.models.ai_config import Difficulty
from blokus_game.models.ai_player import AIPlayer
from blokus_game.models.game_mode import GameMode
from blokus_game.services.ai_strategy import (
    CornerStrategy,
    RandomStrategy,
    StrategicStrategy,
)
from blokus_game.ui.game_mode_selector import GameModeSelector, show_game_mode_selector
from blokus_game.ui.unified_game_mode_selector import (
    UnifiedGameModeSelector,
    show_unified_game_mode_selector,
)
from blokus_game.ui.restart_button import GameRestartDialog


class GameSetupManager:
    """
    Manages game initialization and configuration.

    This manager handles:
    - Game setup dialogs and user choices
    - Preset and custom configuration
    - AI game mode setup
    - Game state initialization
    """

    def __init__(
        self,
        root: tk.Tk,
        on_show_ui: Callable[[], None],
        on_setup_callbacks: Callable[[], None],
        on_setup_ai_callbacks: Callable[[], None],
        on_trigger_ai_move: Callable[[Any], None],
        auto_spectate: bool = False,
    ) -> None:
        """
        Initialize the GameSetupManager.

        Args:
            root: The main application window
            on_show_ui: Callback to show game UI
            on_setup_callbacks: Callback to setup human player callbacks
            on_setup_ai_callbacks: Callback to setup AI player callbacks
            on_trigger_ai_move: Callback to trigger AI move
            auto_spectate: If True, skip dialogs and start spectate mode
        """
        self.root = root
        self.on_show_ui = on_show_ui
        self.on_setup_callbacks = on_setup_callbacks
        self.on_setup_ai_callbacks = on_setup_ai_callbacks
        self.on_trigger_ai_move = on_trigger_ai_move
        self.auto_spectate = auto_spectate

        # Game state attributes
        self.game_config: GameConfig | None = None
        self.game_mode: GameMode | None = None
        self.game_setup: GameSetup | None = None
        self.game_state: Any | None = None
        self.placement_handler: PlacementHandler | None = None

    def show_setup(self) -> None:
        """
        Show the game setup dialog and handle user configuration.

        This is the main entry point for game setup.
        """
        # If auto_spectate flag is set, skip all interactive dialogs and
        # start a Spectate (AI vs AI) game immediately. This is useful for
        # automated debugging or CI runs where GUI prompts block execution.
        if self.auto_spectate:
            try:
                # Create spectate game mode and setup game
                self.game_mode = GameMode.spectate_ai()
                self._setup_ai_game()
            except Exception as e:
                error_handler = get_error_handler()
                error_handler.handle_error(e, show_user_message=True)
                self.root.quit()
            return

        # Show unified game mode selector
        result = show_unified_game_mode_selector(self.root)
        if result is None:
            self.root.quit()
            return

        mode_type = result["mode_type"]

        # Handle PvP Local mode
        if mode_type == "pvp_local":
            try:
                self._setup_pvp_game(result)
            except Exception as e:
                error_handler = get_error_handler()
                error_handler.handle_error(e, show_user_message=True)
                self.root.quit()
            return

        # Handle AI modes (single_ai, three_ai, spectate)
        try:
            # Create game mode from selection
            game_mode = UnifiedGameModeSelector.create_game_mode(mode_type, result)
            self.game_mode = game_mode

            # Setup the game with AI mode
            self._setup_ai_game()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to create game mode: {e}")
            self.root.quit()

    def _choose_preset(self, preset_names: list[str]) -> str | None:
        """
        Choose a preset configuration.

        Args:
            preset_names: List of available preset names

        Returns:
            Selected preset name or None
        """
        preset_window = tk.Toplevel(self.root)
        preset_window.title("Choose Preset")
        preset_window.geometry("400x300")
        preset_window.transient(self.root)
        preset_window.grab_set()

        selected_preset = {"name": None}

        # Center window
        preset_window.geometry(
            "+%d+%d" % (self.root.winfo_rootx() + 50, self.root.winfo_rooty() + 50)
        )

        # Preset descriptions
        descriptions = {
            "casual": "Relaxed game with animations and visual aids",
            "tournament": "Fast-paced game without animations",
            "high_contrast": "High contrast colors for accessibility",
        }

        # Create buttons for each preset
        for preset_name in preset_names:
            frame = tk.Frame(preset_window, relief=tk.RAISED, bd=2)
            frame.pack(fill=tk.X, padx=20, pady=10)

            btn = tk.Button(
                frame,
                text=preset_name.title(),
                command=lambda n=preset_name: self._select_preset(
                    n, preset_window, selected_preset
                ),
                font=("Arial", 12, "bold"),
                pady=10,
            )
            btn.pack(fill=tk.X)

            desc_label = tk.Label(
                frame,
                text=descriptions.get(preset_name, ""),
                font=("Arial", 9),
                wraplength=350,
            )
            desc_label.pack()

        # Wait for selection
        preset_window.wait_window()
        return selected_preset["name"]

    def _select_preset(
        self, preset_name: str, window: tk.Toplevel, selected: dict
    ) -> None:
        """Select a preset and close dialog."""
        selected["name"] = preset_name
        window.destroy()

    def _setup_game_from_config(self) -> None:
        """Setup game from configuration."""
        if not self.game_config:
            return

        # Validate config
        errors = self.game_config.validate()
        if errors:
            error_msg = "\n".join(errors)
            messagebox.showerror("Configuration Error", error_msg)
            self.root.quit()
            return

        # Setup the game
        self.game_setup = GameSetup()
        self.game_state = self.game_setup.setup_game(
            num_players=len(self.game_config.players),
            player_names=[p.name for p in self.game_config.players],
        )

        # Initialize placement handler (but don't setup callbacks yet)
        current_player = self.game_state.get_current_player()
        if current_player:
            self.placement_handler = PlacementHandler(
                self.game_state.board, self.game_state, current_player
            )

        # Show the game UI (this creates PieceSelector)
        self.on_show_ui()

        # NOW setup callbacks after PieceSelector is created
        if current_player:
            self.on_setup_callbacks()

    def _setup_pvp_game(self, config: dict) -> None:
        """
        Setup PvP local multiplayer game.

        Args:
            config: Configuration dictionary from unified selector
        """
        # Create game config
        self.game_config = GameConfig()

        # Add players from config
        player_count = config["player_count"]
        player_names = config["player_names"]

        for i, name in enumerate(player_names):
            player_id = i + 1
            color = self.game_config.get_player_color(player_id)
            self.game_config.add_player(player_id, name, color)

        # Validate config
        errors = self.game_config.validate()
        if errors:
            error_msg = "\n".join(errors)
            messagebox.showerror("Configuration Error", error_msg)
            self.root.quit()
            return

        # Setup the game
        self.game_setup = GameSetup()
        self.game_state = self.game_setup.setup_game(
            num_players=player_count,
            player_names=player_names,
        )

        # Initialize placement handler
        current_player = self.game_state.get_current_player()
        if current_player:
            self.placement_handler = PlacementHandler(
                self.game_state.board, self.game_state, current_player
            )

        # Show the game UI
        self.on_show_ui()

        # Setup callbacks
        if current_player:
            self.on_setup_callbacks()

    def _setup_ai_game(self) -> None:
        """Setup AI battle mode game."""
        if not self.game_mode:
            return

        # Create game config from game mode
        self.game_config = GameConfig()

        # Add human player if specified
        if self.game_mode.human_player_position:
            player_name = "Human"
            color = self.game_config.get_player_color(
                self.game_mode.human_player_position
            )
            self.game_config.add_player(
                self.game_mode.human_player_position, player_name, color
            )

        # Create AI players
        ai_players = []
        for ai_config in self.game_mode.ai_players:
            # Create strategy based on difficulty
            if ai_config.difficulty == Difficulty.EASY:
                strategy = RandomStrategy()
            elif ai_config.difficulty == Difficulty.MEDIUM:
                strategy = CornerStrategy()
            else:  # HARD
                strategy = StrategicStrategy()

            # Create AI player
            ai_player = AIPlayer(
                player_id=ai_config.position,
                strategy=strategy,
                color=self.game_config.get_player_color(ai_config.position),
                name=f"AI {ai_config.difficulty.name} P{ai_config.position}",
            )
            ai_players.append(ai_player)

            # Add to game config
            self.game_config.add_player(
                ai_config.position, ai_player.name, ai_player.color
            )

        # Setup the game
        self.game_setup = GameSetup()
        self.game_state = self.game_setup.setup_game(
            num_players=self.game_mode.get_player_count(),
            player_names=[p.name for p in self.game_config.players],
        )

        # Replace AI player placeholders with actual AIPlayer instances
        for ai_player in ai_players:
            for i, player in enumerate(self.game_state.players):
                if player.player_id == ai_player.player_id:
                    self.game_state.players[i] = ai_player
                    break

        # Initialize placement handler
        current_player = self.game_state.get_current_player()
        if current_player:
            self.placement_handler = PlacementHandler(
                self.game_state.board, self.game_state, current_player
            )

        # Show the game UI
        self.on_show_ui()

        # Setup callbacks
        if current_player:
            self.on_setup_ai_callbacks()

            # If the first player is AI, trigger the first move
            if self.game_mode and self.game_mode.is_ai_turn(current_player.player_id):
                self.root.after(500, lambda: self.on_trigger_ai_move(current_player))
