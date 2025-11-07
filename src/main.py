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
from typing import Any

from src.config.game_config import GameConfig, create_config_from_preset
from src.game.error_handler import get_error_handler, setup_error_handling
from src.game.game_setup import GameSetup
from src.game.placement_handler import PlacementHandler
from src.models.ai_config import Difficulty
from src.models.ai_player import AIPlayer
from src.models.game_mode import GameMode
from src.services.ai_strategy import CornerStrategy, RandomStrategy, StrategicStrategy
from src.ui.board_renderer import OptimizedBoardRenderer
from src.ui.current_player_indicator import CurrentPlayerIndicator
from src.ui.game_mode_selector import GameModeSelector, show_game_mode_selector
from src.ui.keyboard_shortcuts import GameKeyboardHandler
from src.ui.piece_display import PieceDisplay
from src.ui.piece_inventory import PieceInventory
from src.ui.piece_selector import PieceSelector
from src.ui.placement_preview import PlacementPreview
from src.ui.restart_button import GameRestartDialog, RestartButton
from src.ui.scoreboard import Scoreboard
from src.ui.setup_window import SetupWindow
from src.ui.skip_turn_button import SkipTurnButton
from src.ui.state_sync import StateSynchronizer


class BlokusApp:
    """Main application class for Blokus game."""

    def __init__(self, auto_spectate: bool = False) -> None:
        """Initialize the application."""
        # Setup error handling first
        setup_error_handling(log_file="blokus_errors.log")

        # Create root window
        self.root = tk.Tk()
        self.root.title("Blokus - Local Multiplayer")
        self.root.geometry("1200x800")

        # Game configuration
        self.game_config: GameConfig | None = None
        self.game_mode: GameMode | None = None

        # AI-related
        self.game_setup: GameSetup | None = None
        self.game_state = None
        self.placement_handler: PlacementHandler | None = None
        self.state_synchronizer: StateSynchronizer | None = None

        # Setup window
        self.setup_window: SetupWindow | None = None

        # UI components
        self.game_window: tk.Toplevel | None = None
        self.board_canvas: tk.Canvas | None = None
        self.board_renderer: OptimizedBoardRenderer | None = None
        self.piece_selector: PieceSelector | None = None
        self.piece_display: PieceDisplay | None = None
        self.current_player_indicator: CurrentPlayerIndicator | None = None
        self.scoreboard: Scoreboard | None = None
        self.piece_inventory: PieceInventory | None = None
        self.placement_preview: PlacementPreview | None = None
        self.skip_turn_button: SkipTurnButton | None = None

        # Phase 10 additions
        self.keyboard_handler: GameKeyboardHandler | None = None
        self.restart_button: RestartButton | None = None

        # Performance metrics
        self.performance_metrics: dict[str, Any] = {}

        # If True, skip interactive setup and start Spectate AI mode
        self.auto_spectate = auto_spectate

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
        # If auto_spectate flag is set, skip all interactive dialogs and
        # start a Spectate (AI vs AI) game immediately. This is useful for
        # automated debugging or CI runs where GUI prompts block execution.
        if getattr(self, "auto_spectate", False):
            try:
                # Create spectate game mode and setup game
                self.game_mode = GameMode.spectate_ai()
                self._setup_ai_game()
            except Exception as e:
                error_handler = get_error_handler()
                error_handler.handle_error(e, show_user_message=True)
                self.root.quit()
            return
        # First, ask if user wants AI battle mode
        use_ai_mode = messagebox.askyesno(
            "Blokus Game Setup",
            "Play against AI?\n\n"
            "Yes - Select AI battle mode (Single AI, Three AI, Spectate)\n"
            "No - Traditional multiplayer (2-4 players)",
            icon="question",
        )

        if use_ai_mode:
            # Show AI game mode selector
            result = show_game_mode_selector(self.root)
            if result is None:
                self.root.quit()
                return

            # Create game mode from selection
            try:
                self.game_mode = GameModeSelector.create_game_mode(
                    result["mode_type"], result.get("difficulty")
                )
            except Exception as e:
                messagebox.showerror("Error", f"Failed to create game mode: {e}")
                self.root.quit()
                return

            # Setup the game with AI mode
            try:
                self._setup_ai_game()
            except Exception as e:
                error_handler = get_error_handler()
                error_handler.handle_error(e, show_user_message=True)
                self.root.quit()
        else:
            # Traditional multiplayer setup
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

    def _choose_preset(self, preset_names: list) -> str | None:
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
            player_names=[p.name for p in self.game_config.players],
        )

        # Initialize placement handler (but don't setup callbacks yet)
        current_player = self.game_state.get_current_player()
        if current_player:
            self.placement_handler = PlacementHandler(
                self.game_state.board, self.game_state, current_player
            )

        # Show the game UI (this creates PieceSelector)
        self._show_game_ui()

        # NOW setup callbacks after PieceSelector is created
        if current_player:
            self._setup_callbacks()

    def _setup_ai_game(self):
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
                # Ensure AI names are unique and contain only allowed characters
                # Allowed: letters, numbers, spaces, underscores, hyphens, apostrophes
                # Use format like: "AI EASY P3" (no parentheses or '#')
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
        self._show_game_ui()

        # Setup callbacks
        if current_player:
            self._setup_ai_callbacks()

            # If the first player is AI, trigger the first move
            if self.game_mode and self.game_mode.is_ai_turn(current_player.player_id):
                self.root.after(500, lambda: self._trigger_ai_move(current_player))

    def _setup_ai_callbacks(self) -> None:
        """Setup callbacks for AI game."""
        if not self.placement_handler:
            return

        # Set callback for successful piece placement
        def on_piece_placed(piece_name: str):
            """Handle successful piece placement."""
            # Re-render board to show the new piece
            self._render_board()

            # Deactivate placement preview
            if self.placement_preview:
                self.placement_preview.deactivate()

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

            # Force UI update after all updates
            if self.root:
                self.root.update_idletasks()

            # Update current player
            current_player = self.game_state.get_current_player()
            if current_player:
                self.placement_handler.current_player = current_player
                self.placement_handler.clear_selection()

                # Notify turn change
                if self.state_synchronizer:
                    self.state_synchronizer.notify_turn_change()

                # Update skip turn button state
                if self.skip_turn_button:
                    self.skip_turn_button.update_from_game_state()

                # Update piece selector with new current player
                if self.piece_selector and current_player:
                    self.piece_selector.set_player(current_player)

                # Update piece inventory tab to show current player's pieces
                if self.piece_inventory and current_player:
                    self.piece_inventory.select_player_tab(current_player.player_id)

                # Force UI update after player change
                if self.root:
                    self.root.update_idletasks()

                # Check if game should end (all players have passed or no moves left)
                if self.game_state.should_end_game():
                    self._end_game()
                    return

                # Check if it's an AI turn and trigger AI move
                if self.game_mode and self.game_mode.is_ai_turn(
                    current_player.player_id
                ):
                    # Force UI update before scheduling next AI move
                    self.root.update_idletasks()
                    # Use after() to schedule AI move with delay for rendering
                    self.root.after(500, lambda: self._trigger_ai_move(current_player))
                else:
                    # Only show message for human players
                    messagebox.showinfo(
                        "Piece Placed",
                        f"{piece_name} placed! Turn passes to next player.",
                    )

        # Set callback for placement errors - check if current player is AI or human
        def on_placement_error(error_msg: str):
            """Handle placement error - different behavior for AI vs human."""
            current_player = self.game_state.get_current_player()
            if current_player:
                # Check if current player is AI
                if self.game_mode and self.game_mode.is_ai_turn(
                    current_player.player_id
                ):
                    # For AI mode, just print to console instead of showing error popup
                    print(f"AI placement error: {error_msg}")
                else:
                    # For human players, show error dialog
                    messagebox.showerror("Invalid Move", error_msg)
            else:
                # Fallback: just log
                print(f"Placement error: {error_msg}")

        # Configure callbacks
        self.placement_handler.set_callbacks(
            on_piece_placed=on_piece_placed, on_placement_error=on_placement_error
        )

    def _convert_board_to_2d_array(self) -> list[list[int]]:
        """
        Convert board.grid dict to 2D array format expected by AI strategies.

        Returns:
            20x20 2D list where board[row][col] = player_id (0 if empty)
        """
        board_2d = [[0 for _ in range(20)] for _ in range(20)]
        for (row, col), player_id in self.game_state.board.grid.items():
            board_2d[row][col] = player_id
        return board_2d

    def _trigger_ai_move(self, ai_player):
        """
        Trigger AI move calculation and execution using calculate_move().

        Args:
            ai_player: AI player instance
        """
        # Force UI update before AI calculation
        if self.root:
            self.root.update_idletasks()

        # Show AI thinking indicator
        if self.current_player_indicator:
            self.current_player_indicator.show_ai_thinking()
            # Force UI update to show thinking indicator
            if self.root:
                self.root.update_idletasks()

        try:
            # Convert board dict to 2D array format for AI strategy
            board_state = self._convert_board_to_2d_array()
            pieces = list(ai_player.pieces)

            # Pass game_state to AI for rule validation
            move = ai_player.calculate_move_with_game_state(
                board_state, pieces, self.game_state
            )

            if move and not move.is_pass:
                # Select the piece
                piece_selected = self.placement_handler.select_piece(move.piece.name)
                if not piece_selected:
                    print(f"AI failed to select piece: {move.piece.name}")
                    self._pass_turn()
                    return

                # Apply flip (if needed)
                if move.flip:
                    self.placement_handler.flip_piece()

                # Apply rotation (if needed)
                rotation_count = move.rotation // 90
                for _ in range(rotation_count):
                    self.placement_handler.rotate_piece()

                # Place the piece
                success, error_msg = self.placement_handler.place_piece(
                    move.position[0], move.position[1]
                )

                if not success:
                    print(f"AI placement failed: {error_msg}")
                    self._pass_turn()
                # Force UI update after successful placement
                elif self.root:
                    self.root.update_idletasks()
            else:
                # No valid moves or pass action
                print(
                    f"AI Player {ai_player.player_id} has no valid moves, passing turn"
                )
                self._pass_turn()

        except Exception as e:
            print(f"AI calculation error: {e}")
            import traceback

            traceback.print_exc()
            # Pass turn on error
            self._pass_turn()
        finally:
            # Hide thinking indicator
            if self.current_player_indicator:
                self.current_player_indicator.hide_ai_thinking()
                # Force UI update to hide thinking indicator
                if self.root:
                    self.root.update_idletasks()

    def _pass_turn(self):
        """Pass the current player's turn."""
        from src.game.turn_manager import TurnManager

        current_player = self.game_state.get_current_player()
        if current_player:
            current_player.pass_turn()

            # Check if all players have passed (game should end)
            if self.game_state.should_end_game():
                self._end_game()
                return

            # Use TurnManager to advance to next active player (skips passed players)
            turn_manager = TurnManager(self.game_state)
            next_player = turn_manager.advance_to_next_active_player()

            # CRITICAL: Update placement handler's current player
            if next_player and self.placement_handler:
                self.placement_handler.current_player = next_player
                self.placement_handler.clear_selection()

            # Update UI
            self._render_board()
            if self.state_synchronizer:
                self.state_synchronizer.notify_turn_change()
            # Update piece inventory tab to show current player's pieces
            if next_player and self.piece_inventory:
                self.piece_inventory.select_player_tab(next_player.player_id)
            # Update piece selector to show next player's pieces
            if next_player and self.piece_selector:
                self.piece_selector.set_player(next_player)
            # Update skip turn button state
            if self.skip_turn_button:
                self.skip_turn_button.update_from_game_state()
            # Force UI update
            if self.root:
                self.root.update_idletasks()
            # Check if next player is AI
            if (
                next_player
                and self.game_mode
                and self.game_mode.is_ai_turn(next_player.player_id)
            ):
                # Use after() to schedule AI move with sufficient delay
                self.root.after(500, lambda: self._trigger_ai_move(next_player))

    def _on_skip_turn_clicked(self) -> None:
        """Handle skip turn button click."""
        self._pass_turn()

        # Update skip turn button state
        if self.skip_turn_button:
            self.skip_turn_button.update_from_game_state()

    def _setup_callbacks(self) -> None:
        """Setup callbacks for placement handler."""
        if not self.placement_handler:
            return

        # Set callback for successful piece placement
        def on_piece_placed(piece_name: str):
            """Handle successful piece placement."""
            # Re-render board to show the new piece
            self._render_board()

            # Deactivate placement preview
            if self.placement_preview:
                self.placement_preview.deactivate()

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

                # Update skip turn button state
                if self.skip_turn_button:
                    self.skip_turn_button.update_from_game_state()

            # Update piece inventory tab to show current player's pieces
            if self.piece_inventory and current_player:
                self.piece_inventory.select_player_tab(current_player.player_id)

            # Update piece selector with new current player
            if self.piece_selector and current_player:
                self.piece_selector.set_player(current_player)

            # Check if game should end
            if self.game_state.should_end_game():
                self._end_game()
                return

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
            if self.game_config
            else "1400x900"
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

        # Left side of top panel - Current Player Indicator and Skip Turn Button
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

        # Skip turn button - placed right after current player indicator
        self.skip_turn_button = SkipTurnButton(
            current_player_frame, on_skip_turn=self._on_skip_turn_clicked
        )
        self.skip_turn_button.pack(fill=tk.X, pady=(10, 0))

        # Center of top panel - Restart button (temp frame, init button later)
        restart_frame = ttk.Frame(top_panel)
        restart_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)

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
        self.piece_display = PieceDisplay(
            middle_left_panel,
            on_rotate=self._on_rotate_piece,
            on_flip=self._on_flip_piece,
        )
        self.piece_display.pack(fill=tk.X)

        # Create middle-right panel (piece inventory) - increased width
        middle_right_panel = ttk.Frame(main_frame, width=350)
        middle_right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(10, 0))
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

        # Setup board click handling for piece placement
        self._setup_board_click_handling()

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
        close_btn = ttk.Button(
            status_frame, text="Quit (Ctrl+Q)", command=self._quit_game
        )
        close_btn.pack(side=tk.RIGHT)

        # Setup restart button and add to the restart frame created earlier
        self.restart_button = RestartButton(
            restart_frame,
            self.game_state,
            self.game_state.board,
            on_restart=self._on_restart_game,
            preserve_stats=True,
        )
        restart_button_widget = self.restart_button.create_button(
            text="New Game (Ctrl+N)",
            tooltip="Start a new game with current or different settings",
        )
        restart_button_widget.pack(expand=True)

        # Perform initial state sync
        if self.state_synchronizer:
            self.state_synchronizer.full_update()

        # Setup skip turn button with game state
        if self.skip_turn_button:
            self.skip_turn_button.set_game_state(self.game_state)

        # Initialize placement preview for visual feedback
        cell_size = self.game_config.cell_size if self.game_config else 30
        board_size = self.game_config.board_size if self.game_config else 20
        self.placement_preview = PlacementPreview(
            self.board_canvas,
            self.game_state,
            cell_size=cell_size,
            board_size=board_size,
        )

    def _setup_keyboard_handler(self):
        """Setup keyboard shortcuts handler."""
        if not self.keyboard_handler:
            self.keyboard_handler = GameKeyboardHandler(
                self.game_window,
                self.game_state,
                self.game_state.board,
                self.piece_display,
                on_rotate=self._on_rotate_piece,
                on_flip=self._on_flip_piece,
            )

    def _render_board(self):
        """Render the game board."""
        if not self.board_renderer or not self.game_state:
            return

        # Get board state - grid is a dict {(row, col): player_id}
        board_state = self.game_state.board.grid.copy()

        # Convert to format expected by renderer (dict of positions)
        # Render with performance metrics
        metrics = self.board_renderer.render_board(
            board_state=board_state,
            pieces=None,
            show_grid=self.game_config.show_grid_lines if self.game_config else True,
            show_coordinates=(
                self.game_config.show_coordinates if self.game_config else False
            ),
        )

        # Store metrics
        self.performance_metrics["board_render"] = metrics

        # Force UI update after board render
        if self.root:
            self.root.update_idletasks()

    def _setup_board_click_handling(self):
        """Setup click handling for piece placement on the board."""
        if not self.board_canvas or not self.placement_handler:
            return

        # Bind canvas click event for piece placement
        def on_canvas_click(event):
            """Handle canvas click for piece placement."""
            if not self.placement_handler:
                return

            if not self.placement_handler.selected_piece:
                return

            # Calculate board position from click
            canvas_x = event.x
            canvas_y = event.y

            # Get cell size from renderer
            cell_size = self.game_config.cell_size if self.game_config else 30

            # Calculate board row and column
            board_row = canvas_y // cell_size
            board_col = canvas_x // cell_size

            # Validate position
            if not self.game_state.board.is_position_valid(board_row, board_col):
                messagebox.showerror(
                    "Invalid Position", "Position is outside board bounds"
                )
                return

            # Attempt to place piece
            try:
                # Use placement handler to place piece
                # Note: place_piece returns (success, error_message) tuple
                # The placement_handler will call on_piece_placed callback if successful
                success, error_msg = self.placement_handler.place_piece(
                    board_row, board_col
                )

                if not success:
                    # Show error message (success case is handled by callback)
                    messagebox.showerror(
                        "Invalid Move",
                        error_msg or "Cannot place piece at this position",
                    )
            except Exception as e:
                messagebox.showerror("Error", f"Failed to place piece: {str(e)}")

        # Bind the click event
        self.board_canvas.bind("<Button-1>", on_canvas_click)

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
            # Log piece selection event
            if self.game_state:
                current_player = self.game_state.get_current_player()
                if current_player:
                    error_handler = get_error_handler()
                    error_handler.log_structured_event(
                        event_type="piece_selected",
                        player_id=current_player.player_id,
                        piece_name=piece_name,
                    )

            # Display the piece
            selected_piece = self.placement_handler.get_selected_piece()
            if selected_piece and self.piece_display:
                self.piece_display.set_piece(selected_piece)

            # Activate placement preview
            if self.placement_preview and selected_piece and self.game_state:
                current_player = self.game_state.get_current_player()
                if current_player:
                    self.placement_preview.activate(
                        piece=selected_piece, player_id=current_player.player_id
                    )

    def _on_rotate_piece(self) -> None:
        """Handle piece rotation."""
        if not self.placement_handler:
            return

        # Rotate in placement handler
        self.placement_handler.rotate_piece()

        # Update display
        selected_piece = self.placement_handler.get_selected_piece()
        if selected_piece and self.piece_display:
            self.piece_display.set_piece(selected_piece)

        # Update placement preview
        if self.placement_preview and selected_piece and self.game_state:
            current_player = self.game_state.get_current_player()
            if current_player:
                self.placement_preview.activate(
                    piece=selected_piece, player_id=current_player.player_id
                )

    def _on_flip_piece(self) -> None:
        """Handle piece flip."""
        if not self.placement_handler:
            return

        # Flip in placement handler
        self.placement_handler.flip_piece()

        # Update display
        selected_piece = self.placement_handler.get_selected_piece()
        if selected_piece and self.piece_display:
            self.piece_display.set_piece(selected_piece)

        # Update placement preview
        if self.placement_preview and selected_piece and self.game_state:
            current_player = self.game_state.get_current_player()
            if current_player:
                self.placement_preview.activate(
                    piece=selected_piece, player_id=current_player.player_id
                )

    def _end_game(self) -> None:
        """End the game and display results."""
        # Transition to game over state
        self.game_state.end_game()

        # Calculate final scores using the ScoringSystem
        from src.game.scoring import ScoringSystem

        final_scores = ScoringSystem.calculate_final_scores(self.game_state)

        # Update each player's score
        for player in self.game_state.players:
            player.score = final_scores[player.player_id]

        # Show game results
        self._show_game_results()

    def _show_game_results(self) -> None:
        """Display game over dialog with final scores and winner(s)."""
        if not self.game_state or not self.game_state.is_game_over():
            return

        # Get winners
        winners = self.game_state.get_winners()

        # Build results message with better formatting
        results_msg = "╔" + "═" * 48 + "╗\n"
        results_msg += "║" + " " * 16 + "游戏结束" + " " * 16 + "║\n"
        results_msg += "╚" + "═" * 48 + "╝\n\n"

        results_msg += "📊 最终得分排名:\n"
        results_msg += "─" * 50 + "\n"

        # Sort players by score (descending)
        sorted_players = sorted(
            self.game_state.players, key=lambda p: p.score, reverse=True
        )

        for i, player in enumerate(sorted_players, 1):
            remaining_squares = player.get_remaining_squares()
            placed_squares = sum(piece.size for piece in player.get_placed_pieces())

            # Add medal emoji for top 3
            medal = ""
            if i == 1:
                medal = "🥇 "
            elif i == 2:
                medal = "🥈 "
            elif i == 3:
                medal = "🥉 "

            results_msg += f"{medal}{i}. {player.name}:\n"
            results_msg += f"   得分: {player.score} 分\n"
            results_msg += f"   已放置: {placed_squares} 个方块\n"
            results_msg += f"   剩余: {remaining_squares} 个方块\n"
            results_msg += "─" * 50 + "\n"

        results_msg += "\n"

        # Display winner(s)
        if len(winners) == 1:
            results_msg += f"🏆 获胜者: {winners[0].name}!\n"
            results_msg += f"恭喜获得 {winners[0].score} 分!"
        elif len(winners) > 1:
            winner_names = ", ".join([w.name for w in winners])
            results_msg += "🏆 平局!\n"
            results_msg += f"获胜者: {winner_names}\n"
            results_msg += f"得分: {winners[0].score} 分"

        # Show results in message box with larger window
        messagebox.showinfo("🎮 游戏结束", results_msg)

        # Ask if user wants to play again
        play_again = messagebox.askyesno(
            "再来一局?", "是否开始新游戏?", icon="question"
        )

        if play_again:
            # Close current game window if exists
            if self.game_window:
                self.game_window.destroy()
                self.game_window = None
            # Restart the game
            self._show_setup()
        else:
            self.root.quit()


def main() -> None:
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Blokus game launcher")
    parser.add_argument(
        "--spectate",
        action="store_true",
        help="Skip interactive setup and immediately run Spectate (AI vs AI) mode",
    )
    args = parser.parse_args()

    app = BlokusApp(auto_spectate=args.spectate)
    app.run()


if __name__ == "__main__":
    main()
