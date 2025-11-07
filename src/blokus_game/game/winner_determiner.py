"""
Winner Determination Module

This module provides functionality for determining the winner(s) of a Blokus game.
It wraps the scoring system logic to provide a clean interface for winner determination.
"""

from blokus_game.game.scoring import ScoringSystem
from blokus_game.models.game_state import GameState
from blokus_game.models.player import Player


class WinnerDeterminer:
    """Determines the winner(s) of a Blokus game."""

    def __init__(self, game_state: GameState) -> None:
        """
        Initialize the winner determiner.

        Args:
            game_state: The current game state
        """
        self.game_state = game_state

    def get_winners(self) -> list[Player]:
        """
        Get the winner(s) of the game.

        Returns:
            List of winning players (can be multiple in case of tie)

        Raises:
            ValueError: If game is not over yet
        """
        # Check if game is over
        if not self.game_state.is_game_over():
            raise ValueError("Game is not over yet")

        # Use ScoringSystem to determine winners
        return ScoringSystem.determine_winner(self.game_state)

    def get_winner_names(self) -> list[str]:
        """
        Get the names of the winner(s).

        Returns:
            List of winner names
        """
        winners = self.get_winners()
        return [player.name for player in winners]

    def get_winner_ids(self) -> list[int]:
        """
        Get the IDs of the winner(s).

        Returns:
            List of winner IDs
        """
        winners = self.get_winners()
        return [player.player_id for player in winners]

    def calculate_final_scores(self) -> dict[int, int]:
        """
        Calculate final scores for all players.

        Returns:
            Dictionary mapping player_id to final score
        """
        return ScoringSystem.calculate_final_scores(self.game_state)

    def get_player_score(self, player_id: int) -> int:
        """
        Get the final score for a specific player.

        Args:
            player_id: ID of the player

        Returns:
            Final score for the player
        """
        scores = self.calculate_final_scores()
        return scores.get(player_id, 0)

    def rank_players(self) -> list[tuple[int, int, str]]:
        """
        Rank all players by their final scores.

        Returns:
            List of (rank, player_id, name) tuples, sorted by rank
        """
        return ScoringSystem.rank_players(self.game_state)

    def get_score_breakdown(self, player: Player) -> dict[str, int]:
        """
        Get detailed score breakdown for a player.

        Args:
            player: Player to get breakdown for

        Returns:
            Dictionary with score components
        """
        return ScoringSystem.get_score_breakdown(player)

    def determine_winner(self) -> list[Player]:
        """
        Determine the winner(s) using the scoring system.

        Returns:
            List of winning players
        """
        return ScoringSystem.determine_winner(self.game_state)

    def is_tie(self) -> bool:
        """
        Check if the game ended in a tie.

        Returns:
            True if there are multiple winners with same score
        """
        winners = self.get_winners()
        return len(winners) > 1

    def get_winning_score(self) -> int:
        """
        Get the winning score.

        Returns:
            The score of the winner(s)

        Raises:
            ValueError: If no winners
        """
        scores = self.calculate_final_scores()
        if not scores:
            raise ValueError("No scores available")

        return max(scores.values())

    def update_all_player_scores(self) -> None:
        """
        Update all players' score attributes to match final calculated scores.
        """
        scores = self.calculate_final_scores()
        for player in self.game_state.players:
            if player.player_id in scores:
                player.score = scores[player.player_id]
