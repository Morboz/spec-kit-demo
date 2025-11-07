"""
Game State model for Blokus game.

This module defines the GameState class which manages the overall state of the game,
including players, board, current turn, and game phase.
"""

from enum import Enum, auto

from src.models.board import Board
from src.models.player import Player


class GamePhase(Enum):
    """Enumeration of possible game phases."""

    SETUP = auto()
    PLAYING = auto()
    GAME_OVER = auto()


class GameState:
    """Manages the complete state of a Blokus game."""

    def __init__(
        self, players: list[Player] | None = None, board: Board | None = None
    ) -> None:
        """
        Initialize a new game state.

        Args:
            players: List of players (defaults to empty)
            board: Game board (creates new 20x20 board if None)
        """
        self.board = board if board is not None else Board()
        self.players = players if players is not None else []
        self.current_player_index = 0
        self.phase = GamePhase.SETUP
        self.round_number = 1
        self.move_history: list[dict] = []
        self.last_move: dict | None = None

    def add_player(self, player: Player) -> None:
        """
        Add a player to the game.

        Args:
            player: Player instance to add

        Raises:
            ValueError: If player already exists or max players reached
        """
        if len(self.players) >= 4:
            raise ValueError("Maximum of 4 players allowed")

        if any(p.player_id == player.player_id for p in self.players):
            raise ValueError(f"Player {player.player_id} already in game")

        self.players.append(player)

    def get_player_count(self) -> int:
        """
        Get the number of players in the game.

        Returns:
            Number of players
        """
        return len(self.players)

    def get_current_player(self) -> Player | None:
        """
        Get the current player whose turn it is.

        Returns:
            Current player or None if no players
        """
        if not self.players or self.current_player_index >= len(self.players):
            return None
        return self.players[self.current_player_index]

    def get_player_by_id(self, player_id: int) -> Player | None:
        """
        Get a player by their ID.

        Args:
            player_id: ID of the player

        Returns:
            Player instance if found, None otherwise
        """
        for player in self.players:
            if player.player_id == player_id:
                return player
        return None

    def next_turn(self) -> None:
        """Advance to the next player's turn."""
        if self.phase == GamePhase.GAME_OVER:
            return

        if not self.players:
            return

        self.current_player_index = (self.current_player_index + 1) % len(self.players)

        # If we've looped back to player 0, increment round number
        if self.current_player_index == 0:
            self.round_number += 1
            # Note: Do NOT reset pass states here, as we need to detect when all passed  # noqa: E501

    def previous_player(self) -> None:
        """Go back to the previous player's turn."""
        if not self.players:
            return

        self.current_player_index = (self.current_player_index - 1) % len(self.players)

    def start_game(self) -> None:
        """Transition from setup phase to playing phase."""
        if len(self.players) < 2:
            raise ValueError("Need at least 2 players to start game")

        self.phase = GamePhase.PLAYING
        self.current_player_index = 0
        self.round_number = 1

    def end_game(self) -> None:
        """Transition to game over phase."""
        self.phase = GamePhase.GAME_OVER

    def record_move(
        self,
        player_id: int,
        piece_name: str,
        row: int,
        col: int,
        rotation: int = 0,
        flipped: bool = False,
    ) -> None:
        """
        Record a move in the game history.

        Args:
            player_id: ID of the player making the move
            piece_name: Name of the piece placed
            row: Row where piece was placed
            col: Column where piece was placed
            rotation: Rotation angle applied (0, 90, 180, 270)
            flipped: Whether the piece was flipped
        """
        move = {
            "player_id": player_id,
            "piece_name": piece_name,
            "row": row,
            "col": col,
            "rotation": rotation,
            "flipped": flipped,
            "round": self.round_number,
        }

        self.move_history.append(move)
        self.last_move = move

    def can_player_move(self, player_id: int) -> bool:
        """
        Check if a player can make a move.

        Args:
            player_id: ID of the player to check

        Returns:
            True if player can move, False otherwise
        """
        player = self.get_player_by_id(player_id)
        if player is None or not player.has_pieces_remaining():
            return False

        return not player.has_passed and player.is_active

    def get_active_players(self) -> list[Player]:
        """
        Get all players who can still make moves.

        Returns:
            List of active players
        """
        return [p for p in self.players if p.is_active and p.has_pieces_remaining()]

    def get_eliminated_players(self) -> list[Player]:
        """
        Get all players who can no longer make moves.

        Returns:
            List of eliminated players
        """
        return [
            p for p in self.players if not p.has_pieces_remaining() or not p.is_active
        ]

    def should_end_round(self) -> bool:
        """
        Check if the current round should end.

        A round ends when all active players have passed.

        Returns:
            True if all active players have passed, False otherwise
        """
        active_players = self.get_active_players()
        if not active_players:
            return True

        return all(p.has_passed for p in active_players)

    def should_end_game(self) -> bool:
        """
        Check if the game should end.

        The game ends when all active players have passed or no one can move.

        Returns:
            True if game should end, False otherwise
        """
        active_players = self.get_active_players()
        return len(active_players) == 0 or self.should_end_round()

    def get_winners(self) -> list[Player]:
        """
        Determine the winner(s) based on final scores.

        Returns:
            List of winning players (can be multiple in case of tie)
        """
        if self.phase != GamePhase.GAME_OVER:
            raise ValueError("Game is not over yet")

        if not self.players:
            return []

        max_score = max(p.get_score() for p in self.players)
        winners = [p for p in self.players if p.get_score() == max_score]

        return winners

    def get_move_history(self) -> list[dict]:
        """
        Get the complete move history.

        Returns:
            List of all moves made in the game
        """
        return self.move_history.copy()

    def get_player_positions(self, player_id: int) -> set[tuple]:
        """
        Get all positions occupied by a specific player on the board.

        Args:
            player_id: ID of the player

        Returns:
            Set of (row, col) positions
        """
        return self.board.get_player_positions(player_id)

    def get_board_state(self) -> list[list[int | None]]:
        """
        Get the current board state.

        Returns:
            2D grid representing the board
        """
        return self.board.get_board_state()

    def get_turn_number(self) -> int:
        """
        Get the current turn number.

        Returns:
            Current turn number within the round
        """
        if not self.players:
            return 0
        return self.current_player_index + 1

    def get_round_number(self) -> int:
        """
        Get the current round number.

        Returns:
            Current round number
        """
        return self.round_number

    def is_setup_phase(self) -> bool:
        """Check if game is in setup phase."""
        return self.phase == GamePhase.SETUP

    def is_playing_phase(self) -> bool:
        """Check if game is in playing phase."""
        return self.phase == GamePhase.PLAYING

    def is_game_over(self) -> bool:
        """Check if game is in game over phase."""
        return self.phase == GamePhase.GAME_OVER

    def __repr__(self) -> str:
        """String representation of GameState."""
        return (
            f"GameState(phase={self.phase.name}, players={len(self.players)}, "
            f"round={self.round_number}, current_player={self.current_player_index})"
        )
