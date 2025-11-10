"""
Game Flow Manager for Blokus

This manager handles game flow control, including turn management,
game state transitions, scoring, and game results display.
"""

import tkinter as tk
from collections.abc import Callable
from tkinter import messagebox
from typing import Any

from blokus_game.game.turn_manager import TurnManager


class GameFlowManager:
    """
    Manages game flow and state transitions.

    This manager handles:
    - Turn switching and player rotation
    - Game end detection
    - Final score calculation
    - Game results display
    - Restart logic
    """

    def __init__(
        self,
        root: tk.Tk,
        on_render_board: Callable[[], None],
        on_state_update: Callable[[], None],
        on_turn_change: Callable[[], None],
        on_show_setup: Callable[[], None],
        on_game_ui_update: Callable[[], None],
        on_trigger_ai_move: Callable[[Any], None],
    ) -> None:
        """
        Initialize the GameFlowManager.

        Args:
            root: The main application window
            on_render_board: Callback to render the board
            on_state_update: Callback to update state synchronizer
            on_turn_change: Callback when turn changes
            on_show_setup: Callback to show setup dialog
            on_game_ui_update: Callback to update game UI components
            on_trigger_ai_move: Callback to trigger AI move
        """
        self.root = root
        self.on_render_board = on_render_board
        self.on_state_update = on_state_update
        self.on_turn_change = on_turn_change
        self.on_show_setup = on_show_setup
        self.on_game_ui_update = on_game_ui_update
        self.on_trigger_ai_move = on_trigger_ai_move

        # Game state attributes
        self.game_state: Any | None = None
        self.placement_handler: Any | None = None
        self.game_mode: Any | None = None
        self.game_window: tk.Toplevel | None = None
        self.state_synchronizer: Any | None = None
        self.piece_inventory: Any | None = None
        self.piece_selector: Any | None = None
        self.skip_turn_button: Any | None = None

    def set_context(
        self,
        game_state: Any,
        placement_handler: Any,
        game_mode: Any | None = None,
        game_window: tk.Toplevel | None = None,
        state_synchronizer: Any | None = None,
        piece_inventory: Any | None = None,
        piece_selector: Any | None = None,
        skip_turn_button: Any | None = None,
    ) -> None:
        """
        Set the game context for flow operations.

        Args:
            game_state: The current game state
            placement_handler: The placement handler instance
            game_mode: The game mode (for AI turn checking)
            game_window: The game window (for destruction on restart)
            state_synchronizer: The state synchronizer instance
            piece_inventory: The piece inventory widget
            piece_selector: The piece selector widget
            skip_turn_button: The skip turn button widget
        """
        self.game_state = game_state
        self.placement_handler = placement_handler
        self.game_mode = game_mode
        self.game_window = game_window
        self.state_synchronizer = state_synchronizer
        self.piece_inventory = piece_inventory
        self.piece_selector = piece_selector
        self.skip_turn_button = skip_turn_button

    def pass_turn(self) -> None:
        """Pass the current player's turn."""
        current_player = self.game_state.get_current_player()
        if current_player:
            current_player.pass_turn()

            # Check if all players have passed (game should end)
            if self.game_state.should_end_game():
                self.end_game()
                return

            # Use TurnManager to advance to next active player (skips passed players)
            turn_manager = TurnManager(self.game_state)
            next_player = turn_manager.advance_to_next_active_player()

            # CRITICAL: Update placement handler's current player
            if next_player and self.placement_handler:
                self.placement_handler.current_player = next_player
                self.placement_handler.clear_selection()

            # Update UI
            self.on_render_board()
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
                self.root.after(500, lambda: self.on_trigger_ai_move(next_player))

    def on_skip_turn_clicked(self) -> None:
        """Handle skip turn button click."""
        self.pass_turn()

        # Update skip turn button state
        if self.skip_turn_button:
            self.skip_turn_button.update_from_game_state()

    def setup_callbacks(self) -> None:
        """Setup callbacks for placement handler (human player version)."""
        if not self.placement_handler:
            return

        # Set callback for successful piece placement
        def on_piece_placed(piece_name: str):
            """Handle successful piece placement."""
            # Re-render board to show the new piece
            self.on_render_board()

            # Deactivate placement preview
            # Note: This will be handled by the UI manager

            # Refresh piece selector
            if self.piece_selector:
                self.piece_selector.refresh()

            # Clear piece display
            # Note: This will be handled by the UI manager

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
                self.end_game()
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

    def end_game(self) -> None:
        """End the game and display results."""
        # Transition to game over state
        self.game_state.end_game()

        # Calculate final scores using the ScoringSystem
        from blokus_game.game.scoring import ScoringSystem

        final_scores = ScoringSystem.calculate_final_scores(self.game_state)

        # Update each player's score
        for player in self.game_state.players:
            player.score = final_scores[player.player_id]

        # Show game results
        self.show_game_results()

    def show_game_results(self) -> None:
        """Display game over dialog with final scores and winner(s)."""
        if not self.game_state or not self.game_state.is_game_over():
            return

        # Get winners
        winners = self.game_state.get_winners()

        # Build results message with better formatting
        results_msg = "╔" + "═" * 32 + "╗\n"
        results_msg += "║" + " " * 16 + "游戏结束" + " " * 16 + "║\n"
        results_msg += "╚" + "═" * 32 + "╝\n\n"

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
            self.on_show_setup()
        else:
            self.root.quit()

    def on_restart_game(self) -> None:
        """Handle game restart."""
        # Close current game window if exists
        if self.game_window:
            self.game_window.destroy()
            self.game_window = None
        # Restart the game
        self.on_show_setup()
