"""
AI Manager for Blokus

This manager handles all AI-related logic, including AI player creation,
strategy allocation, move calculation and execution.
"""

from collections.abc import Callable
from typing import Any


class AIManager:
    """
    Manages AI players and their decision-making.

    This manager handles:
    - AI player creation and strategy allocation
    - AI move calculation and execution
    - AI-related callbacks
    """

    def __init__(
        self,
        on_show_ai_thinking: Callable[[], None],
        on_hide_ai_thinking: Callable[[], None],
        on_ai_turn_complete: Callable[[], None],
        on_pass_turn: Callable[[], None],
        on_game_end: Callable[[], None],
    ) -> None:
        """
        Initialize the AIManager.

        Args:
            on_show_ai_thinking: Callback to show AI thinking indicator
            on_hide_ai_thinking: Callback to hide AI thinking indicator
            on_ai_turn_complete: Callback when AI turn completes
            on_pass_turn: Callback to pass turn
            on_game_end: Callback when game should end
        """
        self.on_show_ai_thinking = on_show_ai_thinking
        self.on_hide_ai_thinking = on_hide_ai_thinking
        self.on_ai_turn_complete = on_ai_turn_complete
        self.on_pass_turn = on_pass_turn
        self.on_game_end = on_game_end

        # Game state attributes
        self.game_state: Any | None = None
        self.placement_handler: Any | None = None
        self.game_mode: Any | None = None
        self.root: Any | None = None

    def set_context(
        self,
        game_state: Any,
        placement_handler: Any,
        game_mode: Any | None = None,
        root: Any | None = None,
    ) -> None:
        """
        Set the game context for AI operations.

        Args:
            game_state: The current game state
            placement_handler: The placement handler instance
            game_mode: The game mode (for AI turn checking)
            root: The main window (for scheduling)
        """
        self.game_state = game_state
        self.placement_handler = placement_handler
        self.game_mode = game_mode
        self.root = root

    def setup_ai_callbacks(self) -> None:
        """Setup callbacks for AI game."""
        if not self.placement_handler:
            return

        # Set callback for successful piece placement
        def on_piece_placed(piece_name: str):
            """Handle successful piece placement - AI version."""
            # Update current player
            current_player = self.game_state.get_current_player()
            if current_player:
                self.placement_handler.current_player = current_player
                self.placement_handler.clear_selection()

                # Check if game should end (all players have passed or no moves left)
                if self.game_state.should_end_game():
                    self.on_game_end()
                    return

                # Check if it's an AI turn and trigger AI move
                if self.game_mode and self.game_mode.is_ai_turn(
                    current_player.player_id
                ):
                    # Use after() to schedule AI move with delay for rendering
                    if self.root:
                        self.root.after(
                            500, lambda: self.trigger_ai_move(current_player)
                        )

            # Notify that AI turn is complete
            self.on_ai_turn_complete()

        # Set callback for placement errors
        def on_placement_error(error_msg: str):
            """Handle placement error - for AI players."""
            # For AI mode, just print to console instead of showing error popup
            print(f"AI placement error: {error_msg}")

        # Configure callbacks
        self.placement_handler.set_callbacks(
            on_piece_placed=on_piece_placed, on_placement_error=on_placement_error
        )

    def convert_board_to_2d_array(self) -> list[list[int]]:
        """
        Convert board.grid dict to 2D array format expected by AI strategies.

        Returns:
            20x20 2D list where board[row][col] = player_id (0 if empty)
        """
        board_2d = [[0 for _ in range(20)] for _ in range(20)]
        for (row, col), player_id in self.game_state.board.grid.items():
            board_2d[row][col] = player_id
        return board_2d

    def trigger_ai_move(self, ai_player) -> None:
        """
        Trigger AI move calculation and execution.

        Args:
            ai_player: AI player instance
        """
        # Show AI thinking indicator
        self.on_show_ai_thinking()

        try:
            # Convert board dict to 2D array format for AI strategy
            board_state = self.convert_board_to_2d_array()
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
                    self.on_pass_turn()
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
                    self.on_pass_turn()
            else:
                # No valid moves or pass action
                print(
                    f"AI Player {ai_player.player_id} has no valid moves, passing turn"
                )
                self.on_pass_turn()

        except Exception as e:
            print(f"AI calculation error: {e}")
            import traceback

            traceback.print_exc()
            # Pass turn on error
            self.on_pass_turn()
        finally:
            # Hide thinking indicator
            self.on_hide_ai_thinking()
