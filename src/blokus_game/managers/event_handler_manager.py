"""
Event Handler Manager for Blokus

This manager handles player interaction events, including piece selection,
rotation, flipping, and placement preview updates.
"""

from collections.abc import Callable
from typing import Any

from blokus_game.game.error_handler import get_error_handler


class EventHandlerManager:
    """
    Manages player interaction events.

    This manager handles:
    - Piece selection events
    - Piece rotation and flip operations
    - Placement preview updates
    - Event callback coordination
    """

    def __init__(
        self,
        on_set_piece: Callable[[Any], None],
        on_activate_preview: Callable[[Any, int], None],
    ) -> None:
        """
        Initialize the EventHandlerManager.

        Args:
            on_set_piece: Callback to set piece in display
            on_activate_preview: Callback to activate placement preview
        """
        self.on_set_piece = on_set_piece
        self.on_activate_preview = on_activate_preview

        # Game state attributes
        self.game_state: Any | None = None
        self.placement_handler: Any | None = None

    def set_context(
        self,
        game_state: Any,
        placement_handler: Any,
    ) -> None:
        """
        Set the game context for event handling.

        Args:
            game_state: The current game state
            placement_handler: The placement handler instance
        """
        self.game_state = game_state
        self.placement_handler = placement_handler

    def on_piece_selected(self, piece_name: str) -> None:
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
            if selected_piece:
                self.on_set_piece(selected_piece)

            # Activate placement preview
            if selected_piece and self.game_state:
                current_player = self.game_state.get_current_player()
                if current_player:
                    self.on_activate_preview(selected_piece, current_player.player_id)

    def on_rotate_piece(self) -> None:
        """Handle piece rotation."""
        if not self.placement_handler:
            return

        # Rotate in placement handler
        self.placement_handler.rotate_piece()

        # Update display
        selected_piece = self.placement_handler.get_selected_piece()
        if selected_piece:
            self.on_set_piece(selected_piece)

        # Update placement preview
        if selected_piece and self.game_state:
            current_player = self.game_state.get_current_player()
            if current_player:
                self.on_activate_preview(selected_piece, current_player.player_id)

    def on_flip_piece(self) -> None:
        """Handle piece flip."""
        if not self.placement_handler:
            return

        # Flip in placement handler
        self.placement_handler.flip_piece()

        # Update display
        selected_piece = self.placement_handler.get_selected_piece()
        if selected_piece:
            self.on_set_piece(selected_piece)

        # Update placement preview
        if selected_piece and self.game_state:
            current_player = self.game_state.get_current_player()
            if current_player:
                self.on_activate_preview(selected_piece, current_player.player_id)
