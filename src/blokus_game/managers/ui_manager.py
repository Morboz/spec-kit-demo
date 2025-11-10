"""
UI Manager for Blokus

This manager handles all user interface components, including window creation,
layout management, rendering, and user input handling.
"""

import tkinter as tk
from collections.abc import Callable
from tkinter import messagebox, ttk
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from blokus_game.ui.current_player_indicator import CurrentPlayerIndicator
    from blokus_game.ui.keyboard_shortcuts import GameKeyboardHandler
    from blokus_game.ui.piece_display import PieceDisplay
    from blokus_game.ui.piece_inventory import PieceInventory
    from blokus_game.ui.piece_selector import PieceSelector
    from blokus_game.ui.placement_preview import PlacementPreview
    from blokus_game.ui.restart_button import RestartButton
    from blokus_game.ui.scoreboard import Scoreboard
    from blokus_game.ui.skip_turn_button import SkipTurnButton
    from blokus_game.ui.state_sync import StateSynchronizer

from blokus_game.ui.current_player_indicator import CurrentPlayerIndicator
from blokus_game.ui.keyboard_shortcuts import GameKeyboardHandler
from blokus_game.ui.piece_display import PieceDisplay
from blokus_game.ui.piece_inventory import PieceInventory
from blokus_game.ui.piece_selector import PieceSelector
from blokus_game.ui.placement_preview import PlacementPreview
from blokus_game.ui.restart_button import RestartButton
from blokus_game.ui.scoreboard import Scoreboard
from blokus_game.ui.skip_turn_button import SkipTurnButton
from blokus_game.ui.state_sync import StateSynchronizer


class UIManager:
    """
    Manages all user interface components.

    This manager handles:
    - Window creation and layout
    - Component initialization
    - Board rendering
    - Keyboard and mouse event handling
    - Status and performance displays
    """

    def __init__(
        self,
        root: tk.Tk,
        on_piece_selected: Callable[[str], None],
        on_rotate_piece: Callable[[], None],
        on_flip_piece: Callable[[], None],
        on_skip_turn: Callable[[], None],
        on_restart: Callable[[], None],
        on_quit: Callable[[], None],
    ) -> None:
        """
        Initialize the UIManager.

        Args:
            root: The main application window
            on_piece_selected: Callback when piece is selected
            on_rotate_piece: Callback when piece is rotated
            on_flip_piece: Callback when piece is flipped
            on_skip_turn: Callback when skip turn button is clicked
            on_restart: Callback when restart button is clicked
            on_quit: Callback when quit button is clicked
        """
        self.root = root

        # Event callbacks
        self.on_piece_selected = on_piece_selected
        self.on_rotate_piece = on_rotate_piece
        self.on_flip_piece = on_flip_piece
        self.on_skip_turn = on_skip_turn
        self.on_restart = on_restart
        self.on_quit = on_quit

        # UI components
        self.game_window: tk.Toplevel | None = None
        self.board_canvas: tk.Canvas | None = None
        self.board_renderer: Any | None = None
        self.piece_selector: PieceSelector | None = None
        self.piece_display: PieceDisplay | None = None
        self.current_player_indicator: CurrentPlayerIndicator | None = None
        self.scoreboard: Scoreboard | None = None
        self.piece_inventory: PieceInventory | None = None
        self.placement_preview: PlacementPreview | None = None
        self.skip_turn_button: SkipTurnButton | None = None
        self.keyboard_handler: GameKeyboardHandler | None = None
        self.state_synchronizer: StateSynchronizer | None = None

        # Game state
        self.game_state: Any | None = None
        self.game_config: Any | None = None
        self.placement_handler: Any | None = None
        self.game_mode: Any | None = None
        self.performance_metrics: dict[str, Any] = {}

    def set_context(
        self,
        game_state: Any,
        game_config: Any,
        placement_handler: Any,
        game_mode: Any | None = None,
    ) -> None:
        """
        Set the game context for UI operations.

        Args:
            game_state: The current game state
            game_config: The game configuration
            placement_handler: The placement handler instance
            game_mode: The game mode (optional)
        """
        self.game_state = game_state
        self.game_config = game_config
        self.placement_handler = placement_handler
        self.game_mode = game_mode

    def show_game_ui(self) -> None:
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
            current_player_frame, on_skip_turn=self.on_skip_turn
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
                on_piece_selected=self.on_piece_selected,
            )
            self.piece_selector.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Piece display with controls
        self.piece_display = PieceDisplay(
            middle_left_panel,
            on_rotate=self.on_rotate_piece,
            on_flip=self.on_flip_piece,
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
        from blokus_game.ui.board_renderer import OptimizedBoardRenderer

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
        self.render_board()

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
            command=self.show_help,
        )
        help_btn.pack(side=tk.LEFT, padx=(10, 0))

        # Performance metrics button (debug mode)
        if self.game_config and self.game_config.debug_mode:
            metrics_btn = ttk.Button(
                status_frame,
                text="Metrics",
                command=self.show_performance_metrics,
            )
            metrics_btn.pack(side=tk.LEFT, padx=(10, 0))

        # Close button
        close_btn = ttk.Button(status_frame, text="Quit (Ctrl+Q)", command=self.on_quit)
        close_btn.pack(side=tk.RIGHT)

        # Setup restart button and add to the restart frame created earlier
        self.restart_button = RestartButton(
            restart_frame,
            self.game_state,
            self.game_state.board,
            on_restart=self.on_restart,
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

    def _setup_keyboard_handler(self) -> None:
        """Setup keyboard shortcuts handler."""
        if not self.keyboard_handler and self.game_window:
            self.keyboard_handler = GameKeyboardHandler(
                self.game_window,
                self.game_state,
                self.game_state.board,
                self.piece_display,
                on_rotate=self.on_rotate_piece,
                on_flip=self.on_flip_piece,
            )

    def render_board(self) -> None:
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

    def _setup_board_click_handling(self) -> None:
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

    def show_help(self) -> None:
        """Show help dialog with keyboard shortcuts."""
        if self.keyboard_handler:
            self.keyboard_handler._display_help()

    def show_performance_metrics(self) -> None:
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

    def update_ui(self) -> None:
        """Force UI update."""
        if self.root:
            self.root.update_idletasks()

    def show_ai_thinking(self) -> None:
        """Show AI thinking indicator."""
        if self.current_player_indicator:
            self.current_player_indicator.show_ai_thinking()
            self.update_ui()

    def hide_ai_thinking(self) -> None:
        """Hide AI thinking indicator."""
        if self.current_player_indicator:
            self.current_player_indicator.hide_ai_thinking()
            self.update_ui()
