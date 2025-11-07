"""
Skip Turn Button UI Component

This module provides the SkipTurnButton class which allows players to
skip their turn when they have no valid moves available.
"""

import tkinter as tk
from collections.abc import Callable
from tkinter import messagebox, ttk

from src.game.turn_manager import TurnManager
from src.game.turn_validator import TurnValidator
from src.models.game_state import GameState
from src.models.player import Player


class SkipTurnButton(ttk.Frame):
    """UI component for skipping a player's turn."""

    def __init__(
        self,
        parent: tk.Widget,
        game_state: GameState | None = None,
        on_skip_turn: Callable[[], None] | None = None,
    ) -> None:
        """
        Initialize the skip turn button.

        Args:
            parent: Parent widget
            game_state: Game state to observe
            on_skip_turn: Callback when turn is skipped
        """
        super().__init__(parent)
        self.game_state = game_state
        self.on_skip_turn = on_skip_turn
        self.turn_manager: TurnManager | None = None
        self.turn_validator: TurnValidator | None = None
        self.current_player: Player | None = None

        # Create widget
        self._create_widgets()

        # Initialize with game state if provided
        if self.game_state:
            self.update_from_game_state()

    def _create_widgets(self) -> None:
        """Create and arrange UI widgets."""
        # Title
        title_label = ttk.Label(self, text="Turn Actions", font=("Arial", 12, "bold"))
        title_label.pack(pady=(0, 10))

        # Skip turn button
        self.skip_button = ttk.Button(
            self,
            text="Skip Turn",
            command=self._on_skip_clicked,
            state="disabled",
        )
        self.skip_button.pack(fill=tk.X, pady=5)

        # Info frame for skip reason
        info_frame = ttk.Frame(self)
        info_frame.pack(fill=tk.X, pady=(10, 0))

        self.info_label = ttk.Label(
            info_frame,
            text="",
            font=("Arial", 9),
            foreground="gray",
            wraplength=150,
        )
        self.info_label.pack()

        # Warning frame for no moves
        warning_frame = ttk.Frame(self)
        warning_frame.pack(fill=tk.X, pady=(10, 0))

        self.warning_label = ttk.Label(
            warning_frame,
            text="",
            font=("Arial", 9, "bold"),
            foreground="orange",
            wraplength=150,
        )
        self.warning_label.pack()

    def set_game_state(self, game_state: GameState) -> None:
        """
        Set the game state to observe.

        Args:
            game_state: Game state to observe
        """
        self.game_state = game_state
        self.turn_manager = TurnManager(game_state)
        self.turn_validator = TurnValidator(game_state)
        self.update_from_game_state()

    def update_from_game_state(self) -> None:
        """Update button state from current game state."""
        if not self.game_state or not self.turn_validator:
            self._set_button_state(False, "Game not initialized")
            return

        # Check if game is in playing phase
        if not self.game_state.is_playing_phase():
            self._set_button_state(False, "Game not in progress")
            return

        # Get current player
        self.current_player = self.game_state.get_current_player()

        if not self.current_player:
            self._set_button_state(False, "No current player")
            return

        # Validate player can move
        is_valid, error_msg = self.turn_validator.validate_player_can_move(
            self.current_player.player_id
        )

        if is_valid:
            # Player can move - check if they have valid moves
            has_valid_moves = self.turn_validator.player_has_any_valid_move(
                self.current_player.player_id
            )

            if has_valid_moves:
                self._set_button_state(False, "You have valid moves available")
            else:
                self._set_button_state(
                    True,
                    "You have no valid moves.\nClick Skip Turn.",
                    warning="No valid moves available",
                )
        # Player cannot move for some reason
        elif error_msg:
            self._set_button_state(False, error_msg)
        else:
            self._set_button_state(False, "Cannot skip turn")

    def _set_button_state(
        self, enabled: bool, info_text: str, warning: str = ""
    ) -> None:
        """
        Set the button state and info text.

        Args:
            enabled: Whether button should be enabled
            info_text: Information text to display
            warning: Optional warning text
        """
        if enabled:
            self.skip_button.config(state="normal")
        else:
            self.skip_button.config(state="disabled")

        self.info_label.config(text=info_text)

        if warning:
            self.warning_label.config(text=warning)
        else:
            self.warning_label.config(text="")

    def _on_skip_clicked(self) -> None:
        """Handle skip turn button click."""
        if not self.game_state or not self.current_player:
            return

        # Confirm skip if player has valid moves
        has_valid_moves = (
            self.turn_validator
            and self.turn_validator.player_has_any_valid_move(
                self.current_player.player_id
            )
        )

        if has_valid_moves:
            # Ask for confirmation
            result = messagebox.askyesno(
                "Skip Turn",
                "You have valid moves available.\nAre you sure you want to skip?",
                icon="question",
            )

            if not result:
                return

        # Skip the turn
        if self.turn_manager:
            self.turn_manager.skip_current_player()

            # Trigger callback if provided
            if self.on_skip_turn:
                self.on_skip_turn()

        # Update display
        self.update_from_game_state()

    def get_turn_manager(self) -> TurnManager | None:
        """
        Get the turn manager.

        Returns:
            TurnManager instance or None
        """
        return self.turn_manager

    def get_turn_validator(self) -> TurnValidator | None:
        """
        Get the turn validator.

        Returns:
            TurnValidator instance or None
        """
        return self.turn_validator

    def clear(self) -> None:
        """Clear the component display."""
        self.current_player = None
        self._set_button_state(False, "")
