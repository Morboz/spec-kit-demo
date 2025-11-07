"""
Game End Detection Module

This module provides functionality for detecting when a Blokus game should end.
It wraps the game state logic to provide a clean interface for game end detection.
"""

from blokus_game.models.game_state import GameState


class EndGameDetector:
    """Detects when a Blokus game should end."""

    def __init__(self, game_state: GameState) -> None:
        """
        Initialize the end game detector.

        Args:
            game_state: The current game state to monitor
        """
        self.game_state = game_state

    def should_end_game(self) -> bool:
        """
        Check if the game should end.

        Returns:
            True if game should end, False otherwise
        """
        return self.game_state.should_end_game()

    def should_end_round(self) -> bool:
        """
        Check if the current round should end.

        Returns:
            True if round should end, False otherwise
        """
        return self.game_state.should_end_round()

    def get_end_game_reason(self) -> str | None:
        """
        Get a human-readable reason for why the game should end.

        Returns:
            Reason string if game should end, None otherwise
        """
        if not self.should_end_game():
            return None

        active_players = self.game_state.get_active_players()

        if len(active_players) == 0:
            return "No active players remain"

        if self.should_end_round():
            return "All active players have passed"

        return "Game end conditions met"

    def is_game_over(self) -> bool:
        """
        Check if the game is already in GAME_OVER state.

        Returns:
            True if game is over, False otherwise
        """
        return self.game_state.is_game_over()

    def end_game(self) -> None:
        """
        Transition the game to GAME_OVER state.
        """
        self.game_state.end_game()

    def detect_and_end_game_if_necessary(self) -> bool:
        """
        Detect if game should end, and end it if so.

        Returns:
            True if game was ended, False otherwise
        """
        if self.should_end_game():
            self.end_game()
            return True
        return False
