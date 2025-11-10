"""
Main application entry point for Blokus game.

This module provides the main application class that initializes the game,
handles the setup flow, and manages the overall game lifecycle using a
coordinator pattern with specialized manager classes.

Managers:
- GameSetupManager: Handles game initialization and configuration
- AIManager: Manages AI players and their decision-making
- UIManager: Manages all user interface components
- GameFlowManager: Controls game flow and state transitions
- EventHandlerManager: Handles player interactions and events

Refactored: 2025-11-10
- Separated concerns into specialized manager classes
- Improved maintainability and testability
- Preserved all public APIs for backward compatibility
"""

import tkinter as tk

from blokus_game.game.error_handler import get_error_handler, setup_error_handling
from blokus_game.managers.ai_manager import AIManager
from blokus_game.managers.event_handler_manager import EventHandlerManager
from blokus_game.managers.game_flow_manager import GameFlowManager
from blokus_game.managers.game_setup_manager import GameSetupManager
from blokus_game.managers.ui_manager import UIManager


class BlokusApp:
    """Main application class for Blokus game.

    This class acts as a coordinator, delegating specific responsibilities
    to specialized manager classes. This architecture improves maintainability
    and testability while preserving all public APIs for backward compatibility.
    """

    def __init__(self, auto_spectate: bool = False) -> None:
        """Initialize the application."""
        # Setup error handling first
        setup_error_handling(log_file="blokus_errors.log")

        # Create root window
        self.root = tk.Tk()
        self.root.title("Blokus - Local Multiplayer")
        self.root.geometry("1200x800")

        # If True, skip interactive setup and start Spectate AI mode
        self.auto_spectate = auto_spectate

        # Initialize managers
        self._init_managers()

    def _init_managers(self) -> None:
        """Initialize all manager instances and set up their interactions."""
        # Create callbacks for协调 between managers
        self.game_setup_manager = GameSetupManager(
            root=self.root,
            on_show_ui=self._show_game_ui,
            on_setup_callbacks=self._setup_callbacks,
            on_setup_ai_callbacks=self._setup_ai_callbacks,
            on_trigger_ai_move=self._trigger_ai_move,
            auto_spectate=self.auto_spectate,
        )

        self.ui_manager = UIManager(
            root=self.root,
            on_piece_selected=self._on_piece_selected,
            on_rotate_piece=self._on_rotate_piece,
            on_flip_piece=self._on_flip_piece,
            on_skip_turn=self._on_skip_turn_clicked,
            on_restart=self._on_restart_game,
            on_quit=self._quit_game,
        )

        self.ai_manager = AIManager(
            on_show_ai_thinking=self.ui_manager.show_ai_thinking,
            on_hide_ai_thinking=self.ui_manager.hide_ai_thinking,
            on_ai_turn_complete=lambda: None,  # No-op for now
            on_pass_turn=self._pass_turn,
            on_game_end=self._end_game,
        )

        self.game_flow_manager = GameFlowManager(
            root=self.root,
            on_render_board=self.ui_manager.render_board,
            on_state_update=lambda: None,  # No-op for now
            on_turn_change=lambda: None,  # No-op for now
            on_show_setup=self._show_setup,
            on_game_ui_update=lambda: None,  # No-op for now
            on_trigger_ai_move=self._trigger_ai_move,
        )

        self.event_handler_manager = EventHandlerManager(
            on_set_piece=lambda piece: None,  # Will be set after UI is created
            on_activate_preview=lambda piece, player_id: None,  # Will be set after UI is created
        )

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

    def _cleanup(self) -> None:
        """Clean up resources before exit."""
        if self.ui_manager.board_renderer:
            self.ui_manager.board_renderer.cleanup()

    def _show_setup(self) -> None:
        """Show the game setup dialog (delegated to GameSetupManager)."""
        self.game_setup_manager.show_setup()

    def _show_game_ui(self) -> None:
        """Show the game UI (delegated to UIManager)."""
        # Get game state and placement handler from setup manager
        self.ui_manager.set_context(
            game_state=self.game_setup_manager.game_state,
            game_config=self.game_setup_manager.game_config,
            placement_handler=self.game_setup_manager.placement_handler,
            game_mode=self.game_setup_manager.game_mode,
        )
        self.ui_manager.show_game_ui()

        # Set up event handler callbacks now that UI components exist
        self.event_handler_manager.set_context(
            game_state=self.game_setup_manager.game_state,
            placement_handler=self.game_setup_manager.placement_handler,
        )
        self.event_handler_manager.on_set_piece = lambda piece: (
            self.ui_manager.piece_display.set_piece(piece)
            if self.ui_manager.piece_display
            else None
        )
        self.event_handler_manager.on_activate_preview = lambda piece, player_id: (
            self.ui_manager.placement_preview.activate(piece=piece, player_id=player_id)
            if self.ui_manager.placement_preview
            else None
        )

        # Set up AI manager context
        self.ai_manager.set_context(
            game_state=self.game_setup_manager.game_state,
            placement_handler=self.game_setup_manager.placement_handler,
            game_mode=self.game_setup_manager.game_mode,
            root=self.root,
        )

        # Set up game flow manager context
        self.game_flow_manager.set_context(
            game_state=self.game_setup_manager.game_state,
            placement_handler=self.game_setup_manager.placement_handler,
            game_mode=self.game_setup_manager.game_mode,
            game_window=self.ui_manager.game_window,
            state_synchronizer=self.ui_manager.state_synchronizer,
            piece_inventory=self.ui_manager.piece_inventory,
            piece_selector=self.ui_manager.piece_selector,
            skip_turn_button=self.ui_manager.skip_turn_button,
        )

    def _setup_callbacks(self) -> None:
        """Setup callbacks for placement handler (delegated to GameFlowManager)."""
        self.game_flow_manager.setup_callbacks()

    def _setup_ai_callbacks(self) -> None:
        """Setup callbacks for AI game (delegated to AIManager)."""
        self.ai_manager.setup_ai_callbacks()

    def _trigger_ai_move(self, ai_player: Any) -> None:
        """Trigger AI move (delegated to AIManager)."""
        self.ai_manager.trigger_ai_move(ai_player)

    def _pass_turn(self) -> None:
        """Pass the current player's turn (delegated to GameFlowManager)."""
        self.game_flow_manager.pass_turn()

    def _end_game(self) -> None:
        """End the game (delegated to GameFlowManager)."""
        self.game_flow_manager.end_game()

    def _on_skip_turn_clicked(self) -> None:
        """Handle skip turn button click (delegated to GameFlowManager)."""
        self.game_flow_manager.on_skip_turn_clicked()

    def _on_piece_selected(self, piece_name: str) -> None:
        """Handle piece selection (delegated to EventHandlerManager)."""
        self.event_handler_manager.on_piece_selected(piece_name)

    def _on_rotate_piece(self) -> None:
        """Handle piece rotation (delegated to EventHandlerManager)."""
        self.event_handler_manager.on_rotate_piece()

    def _on_flip_piece(self) -> None:
        """Handle piece flip (delegated to EventHandlerManager)."""
        self.event_handler_manager.on_flip_piece()

    def _on_restart_game(self) -> None:
        """Handle game restart (delegated to GameFlowManager)."""
        self.game_flow_manager.on_restart_game()

    def _quit_game(self) -> None:
        """Quit the game with confirmation."""
        from tkinter import messagebox

        result = messagebox.askyesno(
            "Quit Game",
            "Are you sure you want to quit?",
            icon="question",
        )
        if result:
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
