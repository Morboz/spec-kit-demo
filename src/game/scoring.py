"""
Blokus Scoring System

This module implements the scoring system for the Blokus game.
Players score points based on:
- +1 point per square placed on the board
- -1 point for each remaining square not placed
- +15 points bonus for placing all pieces
"""

from typing import List, Dict, Tuple
from src.models.game_state import GameState
from src.models.player import Player
from src.models.board import Board


class ScoringSystem:
    """Manages scoring for Blokus game."""

    @staticmethod
    def calculate_final_scores(game_state: GameState) -> Dict[int, int]:
        """
        Calculate final scores for all players.

        Scoring rules:
        - +1 point per square placed on the board
        - -1 point per unplaced square
        - +15 bonus for placing all pieces

        Args:
            game_state: Current game state

        Returns:
            Dictionary mapping player_id to final score
        """
        scores = {}

        for player in game_state.players:
            score = ScoringSystem._calculate_player_score(player)
            scores[player.player_id] = score

        return scores

    @staticmethod
    def _calculate_player_score(player: Player) -> int:
        """
        Calculate score for a single player.

        Args:
            player: Player to calculate score for

        Returns:
            Final score for the player
        """
        # +1 point per placed square
        placed_score = ScoringSystem.calculate_squares_placed(player)

        # -1 point per unplaced square
        unplaced_score = ScoringSystem.calculate_squares_remaining(player)

        # Calculate base score
        score = placed_score - unplaced_score

        # +15 bonus for placing all pieces
        if ScoringSystem.check_bonus_eligibility(player):
            score += 15

        return score

    @staticmethod
    def update_player_score(player: Player) -> None:
        """
        Update a player's score based on current game state.

        Args:
            player: Player to update
        """
        player.score = ScoringSystem._calculate_player_score(player)

    @staticmethod
    def calculate_squares_placed(player: Player) -> int:
        """
        Calculate total number of squares placed by a player.

        Args:
            player: Player to calculate for

        Returns:
            Number of squares placed
        """
        return sum(piece.size for piece in player.get_placed_pieces())

    @staticmethod
    def calculate_squares_remaining(player: Player) -> int:
        """
        Calculate total number of squares remaining (unplaced).

        Args:
            player: Player to calculate for

        Returns:
            Number of squares remaining
        """
        return player.get_remaining_squares()

    @staticmethod
    def check_bonus_eligibility(player: Player) -> bool:
        """
        Check if player is eligible for the "all pieces placed" bonus.

        Args:
            player: Player to check

        Returns:
            True if player has placed all pieces, False otherwise
        """
        return player.get_remaining_piece_count() == 0

    @staticmethod
    def get_score_breakdown(player: Player) -> Dict[str, int]:
        """
        Get detailed breakdown of player's score.

        Args:
            player: Player to analyze

        Returns:
            Dictionary with score components
        """
        placed_squares = ScoringSystem.calculate_squares_placed(player)
        unplaced_squares = ScoringSystem.calculate_squares_remaining(player)
        base_score = placed_squares - unplaced_squares
        bonus = 15 if ScoringSystem.check_bonus_eligibility(player) else 0
        final_score = base_score + bonus

        return {
            "placed_squares": placed_squares,
            "unplaced_squares": unplaced_squares,
            "base_score": base_score,
            "all_pieces_bonus": bonus,
            "final_score": final_score,
        }

    @staticmethod
    def rank_players(game_state: GameState) -> List[Tuple[int, int, str]]:
        """
        Rank players by their final scores.

        Args:
            game_state: Current game state

        Returns:
            List of (rank, player_id, name) tuples, sorted by rank
        """
        scores = ScoringSystem.calculate_final_scores(game_state)

        # Create list of (score, player_id, name) tuples
        player_scores = []
        for player in game_state.players:
            score = scores[player.player_id]
            player_scores.append((score, player.player_id, player.name))

        # Sort by score (descending), then by player_id for stability
        player_scores.sort(key=lambda x: (-x[0], x[1]))

        # Assign ranks
        ranked_players = []
        current_rank = 1
        previous_score = None

        for score, player_id, name in player_scores:
            if previous_score is not None and score < previous_score:
                current_rank = len(ranked_players) + 1

            ranked_players.append((current_rank, player_id, name))
            previous_score = score

        return ranked_players

    @staticmethod
    def determine_winner(game_state: GameState) -> List[Player]:
        """
        Determine the winner(s) of the game.

        Args:
            game_state: Current game state

        Returns:
            List of winning players (can be multiple in case of tie)
        """
        scores = ScoringSystem.calculate_final_scores(game_state)

        if not scores:
            return []

        # Find highest score
        max_score = max(scores.values())

        # Find all players with the highest score
        winners = []
        for player in game_state.players:
            if scores[player.player_id] == max_score:
                winners.append(player)

        return winners
