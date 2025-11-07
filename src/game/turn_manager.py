"""
Turn Manager Module

This module provides the TurnManager class which manages advanced turn-based
gameplay flow, including skipping inactive players, handling passes, and
coordinating with game end detection.
"""

from typing import List, Optional, Tuple
from src.models.game_state import GameState, GamePhase
from src.models.player import Player


class TurnManager:
    """Manages advanced turn-based gameplay flow."""

    def __init__(self, game_state: GameState) -> None:
        """
        Initialize the TurnManager.

        Args:
            game_state: Current game state
        """
        self.game_state = game_state

    def advance_to_next_active_player(self) -> Optional[Player]:
        """
        Advance turn to the next active (not eliminated) player.

        Returns:
            The player who now has the turn, or None if no active players
        """
        if not self.game_state.players:
            return None

        # Get current player before advancing
        current_player = self.game_state.get_current_player()

        # If game is over, don't advance
        if self.game_state.phase == GamePhase.GAME_OVER:
            return current_player

        # Advance one position
        self.game_state.next_turn()

        # Keep advancing until we find an active player or loop back
        attempts = 0
        max_attempts = len(self.game_state.players)

        while attempts < max_attempts:
            next_player = self.game_state.get_current_player()

            # Check if player is active and can play
            if self._is_player_eligible(next_player):
                return next_player

            # Skip this player and try next
            self.game_state.next_turn()
            attempts += 1

        # No active players found
        return None

    def skip_current_player(self) -> Optional[Player]:
        """
        Mark current player as passed and advance to next player.

        Returns:
            The next player who has the turn, or None
        """
        current_player = self.game_state.get_current_player()

        if current_player is None:
            return None

        # Mark current player as passed
        current_player.pass_turn()

        # Advance to next player
        return self.advance_to_next_active_player()

    def can_player_move(self, player_id: int) -> bool:
        """
        Check if a specific player can make a move.

        Args:
            player_id: ID of the player to check

        Returns:
            True if player can move, False otherwise
        """
        player = self.game_state.get_player_by_id(player_id)

        if player is None:
            return False

        # Check if player is eligible
        if not self._is_player_eligible(player):
            return False

        # Check if player has pieces remaining
        if not player.has_pieces_remaining():
            return False

        # Check if player has already passed
        if player.has_passed:
            return False

        # Check if game is in playing phase
        if self.game_state.phase != GamePhase.PLAYING:
            return False

        return True

    def get_next_player(self) -> Optional[Player]:
        """
        Get the next player who will have a turn.

        Returns:
            Next player, or None if no active players
        """
        if not self.game_state.players:
            return None

        # Save current state
        original_index = self.game_state.current_player_index

        # Advance one turn temporarily
        self.game_state.next_turn()

        # Get next player
        next_player = self.game_state.get_current_player()

        # Restore original state
        self.game_state.current_player_index = original_index

        # Verify player is eligible
        if next_player and not self._is_player_eligible(next_player):
            # Try to find next eligible player
            temp_state = GameState(
                players=self.game_state.players,
                board=self.game_state.board,
            )
            temp_state.current_player_index = original_index
            temp_state.phase = self.game_state.phase

            temp_manager = TurnManager(temp_state)
            return temp_manager.advance_to_next_active_player()

        return next_player

    def should_end_round(self) -> bool:
        """
        Check if the current round should end.

        A round ends when all active players have passed.

        Returns:
            True if round should end, False otherwise
        """
        active_players = self._get_active_players()

        if not active_players:
            return True

        # Check if all active players have passed
        return all(player.has_passed for player in active_players)

    def should_end_game(self) -> bool:
        """
        Check if the game should end.

        The game ends when:
        - All active players have passed (round ends), AND
        - At least one player has no pieces remaining

        Returns:
            True if game should end, False otherwise
        """
        # End round check
        if not self.should_end_round():
            return False

        # Check if any player has placed all their pieces
        for player in self.game_state.players:
            if not player.has_pieces_remaining():
                return True

        # Alternative: if all active players can't move
        active_players = self._get_active_players()
        if len(active_players) == 0:
            return True

        return False

    def reset_pass_states_for_new_round(self) -> None:
        """
        Reset pass states for all players at the start of a new round.
        """
        for player in self.game_state.players:
            player.reset_pass()

    def get_turn_info(self) -> Tuple[int, int, Optional[Player]]:
        """
        Get current turn information.

        Returns:
            Tuple of (round_number, turn_number, current_player)
        """
        current_player = self.game_state.get_current_player()
        return (
            self.game_state.get_round_number(),
            self.game_state.get_turn_number(),
            current_player,
        )

    def is_game_over(self) -> bool:
        """
        Check if game is in GAME_OVER state.

        Returns:
            True if game is over, False otherwise
        """
        return self.game_state.phase == GamePhase.GAME_OVER

    def get_eligible_players(self) -> List[Player]:
        """
        Get all players who are eligible to play.

        Returns:
            List of eligible players (active, not passed, have pieces)
        """
        return [
            player
            for player in self.game_state.players
            if self._is_player_eligible(player)
        ]

    def get_passed_players(self) -> List[Player]:
        """
        Get all players who have passed in the current round.

        Returns:
            List of players who have passed
        """
        return [
            player
            for player in self._get_active_players()
            if player.has_passed
        ]

    def _is_player_eligible(self, player: Optional[Player]) -> bool:
        """
        Check if a player is eligible to play.

        Args:
            player: Player to check

        Returns:
            True if eligible, False otherwise
        """
        if player is None:
            return False

        # Check if player is active
        if not player.is_active:
            return False

        # Check if player has pieces remaining
        if not player.has_pieces_remaining():
            return False

        # Check if player has already passed in current round
        if player.has_passed:
            return False

        return True

    def _get_active_players(self) -> List[Player]:
        """
        Get all active players who still have pieces.

        Returns:
            List of active players
        """
        return [
            player
            for player in self.game_state.players
            if player.is_active and player.has_pieces_remaining()
        ]
