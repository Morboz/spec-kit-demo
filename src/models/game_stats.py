"""
Game Statistics Module

This module provides functionality for tracking and managing game statistics
during AI matches, particularly for spectator mode.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json
import time


class StatType(Enum):
    """Type of statistic being tracked."""
    MOVE_COUNT = "move_count"
    PASS_COUNT = "pass_count"
    PIECES_PLACED = "pieces_placed"
    TOTAL_SCORE = "total_score"
    AI_TIME = "ai_time"
    TURN_NUMBER = "turn_number"


@dataclass
class PlayerStats:
    """
    Statistics for a single player during a game.

    Attributes:
        player_id: Player ID (1-4)
        moves_made: Number of moves made
        passes: Number of times passed
        pieces_placed: Number of pieces placed on board
        total_score: Final score
        ai_calculation_times: List of AI calculation times
        difficulties: List of difficulties used
    """

    player_id: int
    moves_made: int = 0
    passes: int = 0
    pieces_placed: int = 0
    total_score: int = 0
    ai_calculation_times: List[float] = field(default_factory=list)
    difficulties: List[str] = field(default_factory=list)

    def add_move(self, ai_time: Optional[float] = None, difficulty: Optional[str] = None):
        """Record a move made by this player."""
        self.moves_made += 1
        self.pieces_placed += 1
        if ai_time is not None:
            self.ai_calculation_times.append(ai_time)
        if difficulty:
            self.difficulties.append(difficulty)

    def add_pass(self, ai_time: Optional[float] = None, difficulty: Optional[str] = None):
        """Record a pass turn."""
        self.passes += 1
        if ai_time is not None:
            self.ai_calculation_times.append(ai_time)
        if difficulty:
            self.difficulties.append(difficulty)

    def set_final_score(self, score: int):
        """Set final game score."""
        self.total_score = score

    def get_average_ai_time(self) -> float:
        """Get average AI calculation time."""
        if not self.ai_calculation_times:
            return 0.0
        return sum(self.ai_calculation_times) / len(self.ai_calculation_times)

    def get_max_ai_time(self) -> float:
        """Get maximum AI calculation time."""
        if not self.ai_calculation_times:
            return 0.0
        return max(self.ai_calculation_times)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "player_id": self.player_id,
            "moves_made": self.moves_made,
            "passes": self.passes,
            "pieces_placed": self.pieces_placed,
            "total_score": self.total_score,
            "average_ai_time": round(self.get_average_ai_time(), 3),
            "max_ai_time": round(self.get_max_ai_time(), 3),
            "difficulties_used": list(set(self.difficulties))
        }


@dataclass
class GameStatistics:
    """
    Complete game statistics tracker.

    Tracks all events during a game for later analysis and display.
    """

    # Game metadata
    game_mode: str
    start_time: datetime
    end_time: Optional[datetime] = None

    # Turn tracking
    total_turns: int = 0
    turn_history: List[Dict[str, Any]] = field(default_factory=list)

    # Player statistics
    player_stats: Dict[int, PlayerStats] = field(default_factory=dict)

    # Game events
    events: List[Dict[str, Any]] = field(default_factory=list)

    # Winner tracking
    winner_player_id: Optional[int] = None

    def __post_init__(self):
        """Initialize player stats for all 4 players."""
        for player_id in range(1, 5):
            if player_id not in self.player_stats:
                self.player_stats[player_id] = PlayerStats(player_id=player_id)

    def record_move(
        self,
        player_id: int,
        piece_id: Optional[str] = None,
        position: Optional[tuple] = None,
        ai_time: Optional[float] = None,
        difficulty: Optional[str] = None
    ):
        """
        Record a move in the game.

        Args:
            player_id: Player making the move
            piece_id: ID of piece placed
            position: Position on board
            ai_time: Time AI took to calculate
            difficulty: AI difficulty level
        """
        if player_id in self.player_stats:
            self.player_stats[player_id].add_move(ai_time, difficulty)

        self.total_turns += 1

        event = {
            "type": "MOVE",
            "turn": self.total_turns,
            "player_id": player_id,
            "timestamp": datetime.now().isoformat(),
            "ai_time": ai_time,
            "piece_id": piece_id,
            "position": position,
            "difficulty": difficulty
        }
        self.turn_history.append(event)
        self.events.append(event)

    def record_pass(
        self,
        player_id: int,
        ai_time: Optional[float] = None,
        difficulty: Optional[str] = None
    ):
        """
        Record a pass turn.

        Args:
            player_id: Player passing
            ai_time: Time AI took to calculate (if AI)
            difficulty: AI difficulty level
        """
        if player_id in self.player_stats:
            self.player_stats[player_id].add_pass(ai_time, difficulty)

        self.total_turns += 1

        event = {
            "type": "PASS",
            "turn": self.total_turns,
            "player_id": player_id,
            "timestamp": datetime.now().isoformat(),
            "ai_time": ai_time,
            "difficulty": difficulty
        }
        self.turn_history.append(event)
        self.events.append(event)

    def set_final_scores(self, scores: Dict[int, int]):
        """
        Set final scores for all players.

        Args:
            scores: Dictionary mapping player_id to score
        """
        for player_id, score in scores.items():
            if player_id in self.player_stats:
                self.player_stats[player_id].set_final_score(score)

        # Determine winner
        if scores:
            self.winner_player_id = max(scores.items(), key=lambda x: x[1])[0]

    def end_game(self):
        """Mark game as ended and record end time."""
        self.end_time = datetime.now()

        event = {
            "type": "GAME_END",
            "total_turns": self.total_turns,
            "timestamp": self.end_time.isoformat(),
            "winner": self.winner_player_id
        }
        self.events.append(event)

    def get_game_duration(self) -> float:
        """
        Get game duration in seconds.

        Returns:
            Duration in seconds (if game ended) or current elapsed time
        """
        end = self.end_time if self.end_time else datetime.now()
        return (end - self.start_time).total_seconds()

    def get_duration_string(self) -> str:
        """
        Get formatted duration string.

        Returns:
            Duration as "MM:SS" string
        """
        duration = self.get_game_duration()
        minutes = int(duration // 60)
        seconds = int(duration % 60)
        return f"{minutes:02d}:{seconds:02d}"

    def get_player_score(self, player_id: int) -> int:
        """
        Get final score for a player.

        Args:
            player_id: Player ID

        Returns:
            Player's final score or 0
        """
        if player_id in self.player_stats:
            return self.player_stats[player_id].total_score
        return 0

    def get_winner_score(self) -> int:
        """Get winner's score."""
        if self.winner_player_id:
            return self.get_player_score(self.winner_player_id)
        return 0

    def get_scores_dict(self) -> Dict[int, int]:
        """
        Get all final scores.

        Returns:
            Dictionary mapping player_id to score
        """
        return {pid: stats.total_score for pid, stats in self.player_stats.items()}

    def get_summary(self) -> Dict[str, Any]:
        """
        Get game summary statistics.

        Returns:
            Dictionary with game summary
        """
        return {
            "game_mode": self.game_mode,
            "duration": self.get_duration_string(),
            "total_turns": self.total_turns,
            "winner": self.winner_player_id,
            "winner_score": self.get_winner_score(),
            "scores": self.get_scores_dict(),
            "total_ai_turns": sum(1 for e in self.events if e.get("type") in ["MOVE", "PASS"]),
            "average_turn_time": round(self.get_game_duration() / max(1, self.total_turns), 2)
        }

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary for serialization.

        Returns:
            Complete game statistics as dictionary
        """
        return {
            "game_mode": self.game_mode,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "total_turns": self.total_turns,
            "winner_player_id": self.winner_player_id,
            "player_stats": {pid: stats.to_dict() for pid, stats in self.player_stats.items()},
            "turn_history": self.turn_history,
            "events": self.events
        }

    def save_to_file(self, filename: str):
        """
        Save statistics to JSON file.

        Args:
            filename: Path to save file
        """
        with open(filename, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load_from_file(cls, filename: str) -> "GameStatistics":
        """
        Load statistics from JSON file.

        Args:
            filename: Path to file

        Returns:
            Loaded GameStatistics instance
        """
        with open(filename, 'r') as f:
            data = json.load(f)

        # Convert to GameStatistics
        stats = cls(
            game_mode=data["game_mode"],
            start_time=datetime.fromisoformat(data["start_time"])
        )

        if data.get("end_time"):
            stats.end_time = datetime.fromisoformat(data["end_time"])

        stats.total_turns = data.get("total_turns", 0)
        stats.winner_player_id = data.get("winner_player_id")

        # Load player stats
        for pid_str, ps_data in data.get("player_stats", {}).items():
            pid = int(pid_str)
            stats.player_stats[pid] = PlayerStats(
                player_id=pid,
                moves_made=ps_data.get("moves_made", 0),
                passes=ps_data.get("passes", 0),
                pieces_placed=ps_data.get("pieces_placed", 0),
                total_score=ps_data.get("total_score", 0),
                ai_calculation_times=ps_data.get("ai_calculation_times", []),
                difficulties=ps_data.get("difficulties", [])
            )

        stats.turn_history = data.get("turn_history", [])
        stats.events = data.get("events", [])

        return stats


# Convenience functions
def create_game_statistics(game_mode: str) -> GameStatistics:
    """
    Create new game statistics tracker.

    Args:
        game_mode: Type of game mode

    Returns:
        New GameStatistics instance
    """
    return GameStatistics(
        game_mode=game_mode,
        start_time=datetime.now()
    )


def export_statistics(stats: GameStatistics, filename: str):
    """
    Export statistics to file.

    Args:
        stats: GameStatistics instance
        filename: Output filename
    """
    stats.save_to_file(filename)


# Example usage
if __name__ == "__main__":
    # Create statistics tracker
    stats = create_game_statistics("spectate")

    # Simulate game events
    stats.record_move(1, ai_time=2.5, difficulty="Medium")
    stats.record_move(2, ai_time=3.1, difficulty="Hard")
    stats.record_move(3, ai_time=1.8, difficulty="Easy")
    stats.record_move(4, ai_time=4.2, difficulty="Medium")

    stats.record_pass(1, ai_time=1.0, difficulty="Medium")

    # Set final scores
    stats.set_final_scores({1: 45, 2: 52, 3: 38, 4: 41})

    # End game
    stats.end_game()

    # Print summary
    print("Game Summary:")
    print(f"  Mode: {stats.game_mode}")
    print(f"  Duration: {stats.get_duration_string()}")
    print(f"  Total Turns: {stats.total_turns}")
    print(f"  Winner: Player {stats.winner_player_id} with {stats.get_winner_score()} points")

    # Print player stats
    print("\nPlayer Statistics:")
    for player_id, pstats in stats.player_stats.items():
        print(f"  Player {player_id}:")
        print(f"    Moves: {pstats.moves_made}")
        print(f"    Passes: {pstats.passes}")
        print(f"    Score: {pstats.total_score}")
        print(f"    Avg AI Time: {pstats.get_average_ai_time():.2f}s")
