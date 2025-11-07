"""
Game Loop Module

This module provides the GameLoop class which manages the main game loop,
including turn management and game end detection.
"""

from collections.abc import Callable

from src.game.end_game_detector import EndGameDetector
from src.game.scoring import ScoringSystem
from src.game.turn_manager import TurnManager
from src.game.winner_determiner import WinnerDeterminer
from src.models.game_state import GameState


class GameLoop:
    """Manages the game loop and turn progression."""

    def __init__(
        self,
        game_state: GameState,
        on_game_end: Callable | None = None,
    ) -> None:
        """
        Initialize the game loop.

        Args:
            game_state: Current game state
            on_game_end: Callback when game ends
        """
        self.game_state = game_state
        self.on_game_end = on_game_end

        # Initialize detectors
        self.end_game_detector = EndGameDetector(game_state)
        self.winner_determiner = WinnerDeterminer(game_state)

        # Initialize turn manager for advanced turn management
        self.turn_manager = TurnManager(game_state)

    def check_and_handle_game_end(self) -> bool:
        """
        Check if game should end and handle it if necessary.

        Returns:
            True if game ended, False otherwise
        """
        # Only trigger callback if game just ended
        was_game_over = self.end_game_detector.is_game_over()

        if self.end_game_detector.detect_and_end_game_if_necessary():
            # Game has ended, trigger callback if available
            if self.on_game_end and not was_game_over:
                self.on_game_end(self.game_state)
            return True
        return False

    def detect_and_end_game_if_necessary(self) -> bool:
        """
        Alias for check_and_handle_game_end for backwards compatibility.

        Returns:
            True if game ended, False otherwise
        """
        return self.check_and_handle_game_end()

    def next_turn(self) -> None:
        """
        Advance to the next player's turn.
        Checks for game end conditions after each turn.
        """
        # Advance turn
        self.game_state.next_turn()

        # Check if game should end
        self.check_and_handle_game_end()

    def pass_turn(self, player_id: int) -> None:
        """
        Handle a player passing their turn.

        Args:
            player_id: ID of the player passing
        """
        player = self.game_state.get_player_by_id(player_id)
        if player:
            player.pass_turn()

        # Check if game should end after pass
        self.check_and_handle_game_end()

    def should_end_game(self) -> bool:
        """
        Check if the game should end.

        Returns:
            True if game should end, False otherwise
        """
        return self.end_game_detector.should_end_game()

    def get_end_game_reason(self) -> str | None:
        """
        Get reason for game end.

        Returns:
            Reason string if game should end, None otherwise
        """
        return self.end_game_detector.get_end_game_reason()

    def get_winners(self):
        """
        Get the winner(s) of the game.

        Returns:
            List of winning players

        Raises:
            ValueError: If game is not over yet
        """
        return self.winner_determiner.get_winners()

    def calculate_final_scores(self):
        """
        Calculate final scores for all players.

        Returns:
            Dictionary mapping player_id to final score
        """
        return self.winner_determiner.calculate_final_scores()

    def update_player_scores(self) -> None:
        """
        Update all players' scores to final calculated values.
        """
        self.winner_determiner.update_all_player_scores()

    def update_current_player_score(self) -> None:
        """
        Update the current player's score based on current game state.

        This should be called after each piece placement to keep scores
        up-to-date during gameplay.
        """
        current_player = self.game_state.get_current_player()
        if current_player:
            ScoringSystem.update_player_score(current_player)

    def update_all_active_player_scores(self) -> None:
        """
        Update scores for all active (not eliminated) players.

        This should be called after significant game state changes
        to ensure all UI displays are synchronized.
        """
        for player in self.game_state.players:
            if player.is_active:
                ScoringSystem.update_player_score(player)

    def is_game_over(self) -> bool:
        """
        Check if game is already in GAME_OVER state.

        Returns:
            True if game is over, False otherwise
        """
        return self.end_game_detector.is_game_over()

    def end_game(self) -> None:
        """
        End the game immediately.
        """
        self.end_game_detector.end_game()

        # Trigger callback if available
        if self.on_game_end:
            self.on_game_end(self.game_state)

    # Enhanced turn management methods using TurnManager

    def advance_to_next_active_player(self):
        """
        Advance turn to the next active (not eliminated) player.

        Returns:
            The player who now has the turn, or None if no active players

        Note:
            This method uses TurnManager to skip inactive players
        """
        return self.turn_manager.advance_to_next_active_player()

    def skip_current_player(self):
        """
        Mark current player as passed and advance to next player.

        Returns:
            The next player who has the turn, or None

        Note:
            This method uses TurnManager to handle skip logic
        """
        return self.turn_manager.skip_current_player()

    def can_current_player_move(self) -> bool:
        """
        Check if the current player can make a move.

        Returns:
            True if current player can move, False otherwise
        """
        current_player = self.game_state.get_current_player()
        if current_player is None:
            return False

        return self.turn_manager.can_player_move(current_player.player_id)

    def should_end_round(self) -> bool:
        """
        Check if the current round should end.

        Returns:
            True if round should end, False otherwise
        """
        return self.turn_manager.should_end_round()

    def should_end_game(self) -> bool:
        """
        Check if the game should end.

        Returns:
            True if game should end, False otherwise
        """
        return self.turn_manager.should_end_game()

    def get_next_player(self):
        """
        Get the next player who will have a turn.

        Returns:
            Next player, or None if no active players
        """
        return self.turn_manager.get_next_player()

    def get_turn_info(self):
        """
        Get current turn information.

        Returns:
            Tuple of (round_number, turn_number, current_player)
        """
        return self.turn_manager.get_turn_info()

    def get_turn_manager(self) -> TurnManager:
        """
        Get the TurnManager instance.

        Returns:
            TurnManager for advanced turn operations
        """
        return self.turn_manager
