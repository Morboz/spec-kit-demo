"""
Game State Synchronization Module

This module provides the StateSynchronizer class which coordinates
updates between UI components and the game state.
"""

from typing import Optional, List, Callable
from src.models.game_state import GameState
from src.models.board import Board
from src.models.player import Player
from src.ui.current_player_indicator import CurrentPlayerIndicator
from src.ui.scoreboard import Scoreboard
from src.ui.piece_inventory import PieceInventory


class StateSynchronizer:
    """Synchronizes game state with UI components."""

    def __init__(self, game_state: GameState) -> None:
        """
        Initialize the state synchronizer.

        Args:
            game_state: Game state to synchronize with
        """
        self.game_state = game_state
        self.board: Optional[Board] = None
        self.players: List[Player] = []

        # UI components
        self.current_player_indicator: Optional[CurrentPlayerIndicator] = None
        self.scoreboard: Optional[Scoreboard] = None
        self.piece_inventory: Optional[PieceInventory] = None

        # Update callbacks
        self.update_callbacks: List[Callable[[], None]] = []

    def attach_current_player_indicator(
        self, indicator: CurrentPlayerIndicator
    ) -> None:
        """
        Attach current player indicator component.

        Args:
            indicator: CurrentPlayerIndicator instance
        """
        self.current_player_indicator = indicator
        indicator.set_game_state(self.game_state)
        self._register_update_callback(indicator.update_from_game_state)

    def attach_scoreboard(self, scoreboard: Scoreboard) -> None:
        """
        Attach scoreboard component.

        Args:
            scoreboard: Scoreboard instance
        """
        self.scoreboard = scoreboard
        if self.board:
            scoreboard.set_board(self.board)
        if self.players:
            scoreboard.set_players(self.players)
        self._register_update_callback(scoreboard.update_scores)

    def attach_piece_inventory(self, inventory: PieceInventory) -> None:
        """
        Attach piece inventory component.

        Args:
            inventory: PieceInventory instance
        """
        self.piece_inventory = inventory
        if self.players:
            inventory.set_players(self.players)
        self._register_update_callback(self._update_inventory)

    def set_board(self, board: Board) -> None:
        """
        Set the game board.

        Args:
            board: Game board
        """
        self.board = board

    def set_players(self, players: List[Player]) -> None:
        """
        Set the game players.

        Args:
            players: List of players
        """
        self.players = players
        if self.scoreboard:
            self.scoreboard.set_players(players)
        if self.piece_inventory:
            self.piece_inventory.set_players(players)

    def _register_update_callback(self, callback: Callable[[], None]) -> None:
        """
        Register a callback for state updates.

        Args:
            callback: Function to call on updates
        """
        if callback not in self.update_callbacks:
            self.update_callbacks.append(callback)

    def notify_board_update(self) -> None:
        """Notify all components of board state change."""
        # Update scoreboard
        if self.scoreboard and self.board:
            self.scoreboard.update_scores()

        # Update piece inventory
        if self.piece_inventory and self.players:
            self._update_inventory()

        # Execute all registered callbacks
        self._execute_callbacks()

    def notify_turn_change(self) -> None:
        """Notify all components of turn change."""
        # Update current player indicator
        if self.current_player_indicator:
            self.current_player_indicator.update_from_game_state()

        # Update piece inventory tab
        if self.piece_inventory and self.game_state.get_current_player():
            current = self.game_state.get_current_player()
            self.piece_inventory.select_player_tab(current.player_id)

        # Execute all registered callbacks
        self._execute_callbacks()

    def notify_player_update(self, player_id: int) -> None:
        """
        Notify all components of player state change.

        Args:
            player_id: ID of updated player
        """
        # Update scoreboard
        if self.scoreboard:
            self.scoreboard.update_scores()

        # Update piece inventory
        if self.piece_inventory:
            self.piece_inventory.update_inventory(player_id)

        # Execute all registered callbacks
        self._execute_callbacks()

    def notify_game_phase_change(self) -> None:
        """Notify all components of game phase change."""
        # Update current player indicator
        if self.current_player_indicator:
            self.current_player_indicator.update_from_game_state()

        # Execute all registered callbacks
        self._execute_callbacks()

    def full_update(self) -> None:
        """Perform a full state synchronization."""
        # Update current player indicator
        if self.current_player_indicator:
            self.current_player_indicator.update_from_game_state()

        # Update scoreboard
        if self.scoreboard:
            self.scoreboard.update_scores()

        # Update piece inventory
        self._update_inventory()

        # Execute all registered callbacks
        self._execute_callbacks()

    def _update_inventory(self) -> None:
        """Update the piece inventory."""
        if self.piece_inventory and self.players:
            # Refresh all tabs
            self.piece_inventory._refresh_tabs()

            # Select current player's tab if game is in progress
            if self.game_state.phase.value >= 2:  # PLAYING or later
                current = self.game_state.get_current_player()
                if current:
                    self.piece_inventory.select_player_tab(current.player_id)

    def _execute_callbacks(self) -> None:
        """Execute all registered update callbacks."""
        for callback in self.update_callbacks:
            try:
                callback()
            except Exception as e:
                # Log error but don't crash
                print(f"Error in update callback: {e}")

    def get_current_player(self) -> Optional[Player]:
        """
        Get the current player.

        Returns:
            Current player or None
        """
        return self.game_state.get_current_player()

    def get_leader(self) -> Optional[Player]:
        """
        Get the current leader.

        Returns:
            Player with highest score or None
        """
        if not self.scoreboard:
            return None
        return self.scoreboard.get_leader()

    def clear(self) -> None:
        """Clear all synchronizations."""
        self.board = None
        self.players = []
        self.update_callbacks.clear()

        # Clear UI components
        if self.current_player_indicator:
            self.current_player_indicator.clear()
        if self.scoreboard:
            self.scoreboard.clear()
        if self.piece_inventory:
            self.piece_inventory.clear()
