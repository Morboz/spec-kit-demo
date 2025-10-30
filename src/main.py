"""
Main application entry point for Blokus game.

This module provides the main application class that initializes the game,
handles the setup flow, and manages the overall game lifecycle.

Phase 10: Complete application with:
- Game configuration support
- Keyboard shortcuts
- Game restart functionality
- Optimized board rendering
- Comprehensive error handling
"""

import tkinter as tk
from tkinter import messagebox, ttk
from typing import Optional, Dict, Any
from src.ui.setup_window import SetupWindow
from src.game.game_setup import GameSetup
from src.game.placement_handler import PlacementHandler
from src.ui.piece_selector import PieceSelector
from src.ui.piece_display import PieceDisplay
from src.ui.current_player_indicator import CurrentPlayerIndicator
from src.ui.scoreboard import Scoreboard
from src.ui.piece_inventory import PieceInventory
from src.ui.state_sync import StateSynchronizer
from src.ui.keyboard_shortcuts import GameKeyboardHandler
from src.ui.restart_button import RestartButton, GameRestartDialog
from src.ui.board_renderer import OptimizedBoardRenderer
from src.config.game_config import GameConfig, create_config_from_preset
from src.game.error_handler import setup_error_handling, get_error_handler


class BlokusApp:
    """Main application class for Blokus game."""

    def __init__(self) -> None:
        """Initialize the application."""
        # Setup error handling first
        setup_error_handling(log_file="blokus_errors.log")

        # Create root window
        self.root = tk.Tk()
        self.root.title("Blokus - Local Multiplayer")
        self.root.geometry("1200x800")

        # Game configuration
        self.game_config: Optional[GameConfig] = None

        # Game state
        self.game_setup: Optional[GameSetup] = None
        self.game_state = None
        self.placement_handler: Optional[PlacementHandler] = None
        self.state_synchronizer: Optional[StateSynchronizer] = None

        # Setup window
        self.setup_window: Optional[SetupWindow] = None

        # UI components
        self.game_window: Optional[tk.Toplevel] = None
        self.board_canvas: Optional[tk.Canvas] = None
        self.board_renderer: Optional[OptimizedBoardRenderer] = None
        self.piece_selector: Optional[PieceSelector] = None
        self.piece_display: Optional[PieceDisplay] = None
        self.current_player_indicator: Optional[CurrentPlayerIndicator] = None
        self.scoreboard: Optional[Scoreboard] = None
        self.piece_inventory: Optional[PieceInventory] = None

        # Phase 10 additions
        self.keyboard_handler: Optional[GameKeyboardHandler] = None
        self.restart_button: Optional[RestartButton] = None

        # Performance metrics
        self.performance_metrics: Dict[str, Any] = {}

    def run(self) -> None:
        """Run the application main loop."""
        # Show setup dialog
        self._show_setup()

        # Start the main loop
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            print("Game interrupted by user")
        except Exception as e:
            error_handler = get_error_handler()
            error_handler.handle_error(e, show_user_message=True)
        finally:
            self._cleanup()

    def _cleanup(self):
        """Clean up resources before exit."""
        if self.board_renderer:
            self.board_renderer.cleanup()

    def _show_setup(self) -> None:
        """Show the game setup dialog."""
        # Ask user if they want to use a preset or custom config
        use_preset = messagebox.askyesno(
            "Game Setup",
            "Use a preset configuration?\n\n"
            "Yes - Choose from preset (Casual, Tournament, etc.)\n"
            "No - Custom configuration",
            icon="question",
        )

        if use_preset:
            # Show preset selection
            preset_names = ["casual", "tournament", "high_contrast"]
            preset_choice = self._choose_preset(preset_names)
            if preset_choice:
                self.game_config = create_config_from_preset(preset_choice)
            else:
                self.root.quit()
                return
        else:
            # Use custom configuration dialog
            dialog = GameRestartDialog(self.root)
            config_dict = dialog.show()
            if config_dict is None:
                self.root.quit()
                return

            # Create config from dialog result
            self.game_config = GameConfig()
            for i, name in enumerate(config_dict["player_names"]):
                color = self.game_config.get_player_color(i + 1)
                self.game_config.add_player(i + 1, name, color)

        # Setup the game with config
        try:
            self._setup_game_from_config()
        except Exception as e:
            error_handler = get_error_handler()
            error_handler.handle_error(e, show_user_message=True)
            self.root.quit()

    def _choose_preset(self, preset_names: list) -> Optional[str]:
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
        preset_window.geometry("+%d+%d" % (
            self.root.winfo_rootx() + 50,
            self.root.winfo_rooty() + 50
        ))

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
                command=lambda n=preset_name: self._select_preset(n, preset_window, selected_preset),
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

    def _select_preset(self, preset_name: str, window: tk.Toplevel, selected: dict):
        """Select a preset and close dialog."""
        selected["name"] = preset_name
        window.destroy()

    def _setup_game_from_config(self):
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
            player_names=[p.name for p in self.game_config.players]
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
        self.game_window.geometry(
            f"{self.game_config.window_width}x{self.game_config.window_height}"
            if self.game_config else "1400x900"
        )
        self.game_window.resizable(True, True)

        # Setup keyboard shortcuts
        self._setup_keyboard_handler()

        # Create main container
        main_frame = ttk.Frame(self.game_window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Create top panel (current player indicator, scoreboard, restart button)
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

        # Center of top panel - Restart button
        if self.restart_button:
            restart_frame = ttk.Frame(top_panel)
            restart_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
            restart_button_widget = self.restart_button.create_button(
                text="New Game (Ctrl+N)",
                tooltip="Start a new game with current or different settings"
            )
            restart_button_widget.pack(expand=True)

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

        # Create center panel (game board with optimized renderer)
        center_panel = ttk.Frame(main_frame)
        center_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Board canvas with optimized rendering
        self.board_canvas = tk.Canvas(
            center_panel,
            bg="white",
            highlightthickness=0,
        )
        self.board_canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=0)

        # Initialize optimized board renderer
        if self.game_config:
            self.board_renderer = OptimizedBoardRenderer(
                self.board_canvas,
                board_size=self.game_config.board_size,
                cell_size=self.game_config.cell_size,
            )
            self.board_renderer.configure(
                double_buffer=True,
                region_updates=True,
                caching=True,
                quality="high" if not self.game_config.debug_mode else "medium",
            )
        else:
            # Use default settings
            self.board_renderer = OptimizedBoardRenderer(self.board_canvas)

        # Initial board render
        self._render_board()

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

        # Keyboard shortcuts help
        help_btn = ttk.Button(
            status_frame,
            text="Help (?)",
            command=self._show_help,
        )
        help_btn.pack(side=tk.LEFT, padx=(10, 0))

        # Performance metrics button (debug mode)
        if self.game_config and self.game_config.debug_mode:
            metrics_btn = ttk.Button(
                status_frame,
                text="Metrics",
                command=self._show_performance_metrics,
            )
            metrics_btn.pack(side=tk.LEFT, padx=(10, 0))

        # Close button
        close_btn = ttk.Button(status_frame, text="Quit (Ctrl+Q)", command=self._quit_game)
        close_btn.pack(side=tk.RIGHT)

        # Setup restart button
        self.restart_button = RestartButton(
            status_frame,
            self.game_state,
            self.game_state.board,
            on_restart=self._on_restart_game,
            preserve_stats=True,
        )

        # Perform initial state sync
        if self.state_synchronizer:
            self.state_synchronizer.full_update()

    def _setup_keyboard_handler(self):
        """Setup keyboard shortcuts handler."""
        if not self.keyboard_handler:
            self.keyboard_handler = GameKeyboardHandler(
                self.game_window,
                self.game_state,
                self.game_state.board,
                self.piece_display,
            )

    def _render_board(self):
        """Render the game board."""
        if not self.board_renderer or not self.game_state:
            return

        # Get board state - grid is a dict {(row, col): player_id}
        board_state = self.game_state.board.grid.copy()

        # Render with performance metrics
        metrics = self.board_renderer.render_board(
            board_state=board_state,
            pieces=None,
            show_grid=self.game_config.show_grid_lines if self.game_config else True,
            show_coordinates=self.game_config.show_coordinates if self.game_config else False,
        )

        # Store metrics
        self.performance_metrics["board_render"] = metrics

    def _on_restart_game(self):
        """Handle game restart."""
        # Reset game state
        self._show_setup()

    def _show_help(self):
        """Show help dialog with keyboard shortcuts."""
        if self.keyboard_handler:
            self.keyboard_handler._display_help()

    def _show_performance_metrics(self):
        """Show performance metrics (debug mode)."""
        if not self.performance_metrics:
            messagebox.showinfo("Performance Metrics", "No metrics available yet")
            return

        metrics_window = tk.Toplevel(self.game_window)
        metrics_window.title("Performance Metrics")
        metrics_window.geometry("500x400")

        text_widget = tk.Text(metrics_window, wrap=tk.WORD)
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Format metrics
        metrics_text = "=== PERFORMANCE METRICS ===\n\n"
        for key, value in self.performance_metrics.items():
            metrics_text += f"{key}:\n{value}\n\n"

        text_widget.insert(tk.END, metrics_text)
        text_widget.config(state=tk.DISABLED)

    def _quit_game(self):
        """Quit the game with confirmation."""
        result = messagebox.askyesno(
            "Quit Game",
            "Are you sure you want to quit?",
            icon="question",
        )
        if result:
            self.root.quit()

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
