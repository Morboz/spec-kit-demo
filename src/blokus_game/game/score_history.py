"""
Score History Module

This module provides the ScoreHistory class which tracks score changes
throughout the game for analysis and display purposes.
"""

from datetime import datetime

from blokus_game.models.game_state import GameState


class ScoreEntry:
    """Represents a single score entry in the game history."""

    def __init__(
        self,
        player_id: int,
        player_name: str,
        score: int,
        turn_number: int,
        round_number: int,
        timestamp: datetime | None = None,
    ) -> None:
        """
        Initialize a score entry.

        Args:
            player_id: ID of the player
            player_name: Name of the player
            score: Current score
            turn_number: Current turn number
            round_number: Current round number
            timestamp: When this entry was recorded (defaults to now)
        """
        self.player_id = player_id
        self.player_name = player_name
        self.score = score
        self.turn_number = turn_number
        self.round_number = round_number
        self.timestamp = timestamp or datetime.now()

    def to_dict(self) -> dict:
        """
        Convert to dictionary representation.

        Returns:
            Dictionary with score entry data
        """
        return {
            "player_id": self.player_id,
            "player_name": self.player_name,
            "score": self.score,
            "turn_number": self.turn_number,
            "round_number": self.round_number,
            "timestamp": self.timestamp.isoformat(),
        }

    def __repr__(self) -> str:
        """String representation of score entry."""
        return (
            f"ScoreEntry(player_id={self.player_id}, "
            f"player_name='{self.player_name}', "
            f"score={self.score}, "
            f"turn={self.turn_number}, "
            f"round={self.round_number})"
        )


class ScoreHistory:
    """Tracks score changes throughout the game."""

    def __init__(self, game_state: GameState | None = None) -> None:
        """
        Initialize score history tracker.

        Args:
            game_state: Game state to track (optional)
        """
        self.game_state = game_state
        self.entries: list[ScoreEntry] = []
        self.last_recorded_scores: dict[int, int] = {}

    def set_game_state(self, game_state: GameState) -> None:
        """
        Set the game state to track.

        Args:
            game_state: Game state to track
        """
        self.game_state = game_state

    def record_current_scores(self, turn_number: int, round_number: int) -> None:
        """
        Record current scores for all players.

        Args:
            turn_number: Current turn number
            round_number: Current round number
        """
        if not self.game_state:
            return

        for player in self.game_state.players:
            # Only record if score has changed
            current_score = player.score
            last_score = self.last_recorded_scores.get(player.player_id)

            if current_score != last_score:
                entry = ScoreEntry(
                    player_id=player.player_id,
                    player_name=player.name,
                    score=current_score,
                    turn_number=turn_number,
                    round_number=round_number,
                )
                self.entries.append(entry)
                self.last_recorded_scores[player.player_id] = current_score

    def get_player_history(self, player_id: int) -> list[ScoreEntry]:
        """
        Get score history for a specific player.

        Args:
            player_id: ID of the player

        Returns:
            List of score entries for the player
        """
        return [entry for entry in self.entries if entry.player_id == player_id]

    def get_all_histories(self) -> dict[int, list[ScoreEntry]]:
        """
        Get score history for all players.

        Returns:
            Dictionary mapping player_id to list of score entries
        """
        histories: dict[int, list[ScoreEntry]] = {}
        for entry in self.entries:
            if entry.player_id not in histories:
                histories[entry.player_id] = []
            histories[entry.player_id].append(entry)
        return histories

    def get_score_changes(self) -> list[dict]:
        """
        Get all score changes with details.

        Returns:
            List of dictionaries with score change information
        """
        changes = []
        histories = self.get_all_histories()

        for player_id, player_entries in histories.items():
            if len(player_entries) < 2:
                continue

            for i in range(1, len(player_entries)):
                prev_entry = player_entries[i - 1]
                curr_entry = player_entries[i]
                change = curr_entry.score - prev_entry.score

                changes.append(
                    {
                        "player_id": player_id,
                        "player_name": curr_entry.player_name,
                        "from_score": prev_entry.score,
                        "to_score": curr_entry.score,
                        "change": change,
                        "turn": curr_entry.turn_number,
                        "round": curr_entry.round_number,
                        "timestamp": curr_entry.timestamp,
                    }
                )

        return changes

    def get_final_rankings(self) -> list[dict]:
        """
        Get final score rankings.

        Returns:
            List of player rankings with final scores
        """
        if not self.entries:
            return []

        # Get latest entry for each player
        latest_scores: dict[int, ScoreEntry] = {}
        for entry in self.entries:
            if entry.player_id not in latest_scores:
                latest_scores[entry.player_id] = entry
            elif entry.timestamp > latest_scores[entry.player_id].timestamp:
                latest_scores[entry.player_id] = entry

        # Sort by score (descending)
        sorted_players = sorted(
            latest_scores.values(), key=lambda e: e.score, reverse=True
        )

        # Assign ranks
        rankings = []
        current_rank = 1
        previous_score = None

        for entry in sorted_players:
            if previous_score is not None and entry.score < previous_score:
                current_rank = len(rankings) + 1

            rankings.append(
                {
                    "rank": current_rank,
                    "player_id": entry.player_id,
                    "player_name": entry.player_name,
                    "final_score": entry.score,
                }
            )

            previous_score = entry.score

        return rankings

    def clear(self) -> None:
        """Clear all history."""
        self.entries.clear()
        self.last_recorded_scores.clear()

    def export_to_dict(self) -> dict:
        """
        Export history to dictionary.

        Returns:
            Dictionary with all history data
        """
        return {
            "entries": [entry.to_dict() for entry in self.entries],
            "last_recorded_scores": self.last_recorded_scores.copy(),
        }

    def import_from_dict(self, data: dict) -> None:
        """
        Import history from dictionary.

        Args:
            data: Dictionary with history data
        """
        self.entries = []
        for entry_data in data.get("entries", []):
            # Reconstruct datetime
            timestamp_str = entry_data.get("timestamp")
            timestamp = (
                datetime.fromisoformat(timestamp_str)
                if timestamp_str
                else datetime.now()
            )

            entry = ScoreEntry(
                player_id=entry_data["player_id"],
                player_name=entry_data["player_name"],
                score=entry_data["score"],
                turn_number=entry_data["turn_number"],
                round_number=entry_data["round_number"],
                timestamp=timestamp,
            )
            self.entries.append(entry)

        self.last_recorded_scores = data.get("last_recorded_scores", {})

    def get_summary(self) -> dict:
        """
        Get summary of score history.

        Returns:
            Dictionary with history summary
        """
        histories = self.get_all_histories()

        summary = {
            "total_entries": len(self.entries),
            "players_tracked": len(histories),
            "total_score_changes": len(self.get_score_changes()),
        }

        # Add per-player summary
        for player_id, entries in histories.items():
            if entries:
                player_name = entries[0].player_name
                summary[f"player_{player_id}_{player_name}"] = {
                    "total_changes": len(entries),
                    "initial_score": entries[0].score,
                    "final_score": entries[-1].score,
                    "net_change": entries[-1].score - entries[0].score,
                }

        return summary
