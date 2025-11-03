"""
AI Player Module

This module defines the AIPlayer class which represents an AI-controlled
player in the Blokus game with configurable strategy.
"""

from typing import Optional, List
import time
from src.services.ai_strategy import AIStrategy, Move
from src.models.piece import Piece
from src.config.pieces import get_full_piece_set


class AIPlayer:
    """
    AI-controlled player in the Blokus game.

    Attributes:
        player_id: Unique identifier (1-4)
        strategy: Strategy instance for move calculation
        color: Display color for pieces
        name: Display name
        pieces: List of remaining pieces to place
        score: Current game score
        has_passed: Whether player passed on current turn
        is_calculating: Whether player is currently calculating a move
    """

    def __init__(
        self,
        player_id: int,
        strategy: AIStrategy,
        color: str,
        name: str = None,
    ):
        """
        Initialize AI player.

        Args:
            player_id: Unique identifier (1-4)
            strategy: AIStrategy implementation for move calculation
            color: Display color for pieces
            name: Display name (default: "AI Player {player_id}")

        Raises:
            ValueError: If player_id is not in valid range
        """
        if not 1 <= player_id <= 4:
            raise ValueError(f"Player ID must be 1-4, got {player_id}")

        self.player_id = player_id
        self.strategy = strategy
        self.color = color
        self.name = name or f"AI Player {player_id}"
        self.pieces = get_full_piece_set()
        self.score = 0
        self.has_passed = False
        self.is_calculating = False
        self._calculation_start_time = None

    @property
    def difficulty(self) -> str:
        """
        Get AI difficulty level.

        Returns:
            Difficulty name from strategy
        """
        return self.strategy.difficulty_name

    def calculate_move(
        self,
        board: List[List[int]],
        pieces: List[Piece],
        time_limit: int = None,
    ) -> Optional[Move]:
        """
        Calculate best move for current game state.

        Args:
            board: 2D array representing game board (20x20)
            pieces: List of available pieces to place
            time_limit: Maximum calculation time in seconds (optional)

        Returns:
            Move object with piece, position, and rotation, or None if no valid moves

        Raises:
            StrategyTimeoutError: If calculation exceeds time limit
            NoValidMovesError: If no valid moves exist
        """
        self.is_calculating = True
        self._calculation_start_time = time.time()

        try:
            move = self.strategy.calculate_move(
                board, pieces, self.player_id, time_limit
            )

            # Check if move is valid
            if move and not move.is_pass:
                if move.piece not in self.pieces:
                    raise ValueError(f"AI attempted to use piece not in inventory: {move.piece.name}")

            return move
        except Exception as e:
            # Log error but don't crash
            print(f"AI Player {self.player_id} calculation error: {e}")
            return None
        finally:
            self.is_calculating = False

    def is_ai_turn(self) -> bool:
        """
        Check if it's this AI player's turn.

        Returns:
            Always True for AI players
        """
        return True

    def get_available_moves(
        self, board: List[List[int]], pieces: List[Piece]
    ) -> List[Move]:
        """
        Generate all valid moves for current state.

        Args:
            board: Current board state
            pieces: Available pieces

        Returns:
            List of all valid Move objects

        Note:
            This uses the strategy's implementation which may not fully
            validate against Blokus rules. For full validation, use
            the game's turn validator.
        """
        return self.strategy.get_available_moves(board, pieces, self.player_id)

    def evaluate_position(self, board: List[List[int]]) -> float:
        """
        Evaluate board position from this player's perspective.

        Args:
            board: Current board state

        Returns:
            Float score (higher = better for this player)
        """
        return self.strategy.evaluate_board(board, self.player_id)

    def pass_turn(self):
        """
        Indicate that player passes (no valid moves).

        This sets the player's passed flag. The flag should be cleared
        at the start of the player's next turn.
        """
        self.has_passed = True

    def reset_pass(self):
        """
        Reset the passed flag at the start of a new turn.

        This should be called at the beginning of each turn.
        """
        self.has_passed = False

    def has_pieces_remaining(self) -> bool:
        """
        Check if player has any pieces remaining.

        Returns:
            True if player has unplaced pieces
        """
        return len(self.pieces) > 0

    def remove_piece(self, piece: Piece):
        """
        Remove a piece from the player's inventory (after placing it).

        Args:
            piece: Piece to remove

        Raises:
            ValueError: If piece not in inventory
        """
        if piece not in self.pieces:
            raise ValueError(f"Attempted to remove piece {piece.name} not in inventory")
        self.pieces.remove(piece)

    def get_elapsed_calculation_time(self) -> Optional[float]:
        """
        Get elapsed time for current calculation.

        Returns:
            Seconds elapsed since calculation started, or None if not calculating
        """
        if not self.is_calculating or self._calculation_start_time is None:
            return None
        return time.time() - self._calculation_start_time

    def get_piece_count(self) -> int:
        """
        Get number of pieces remaining.

        Returns:
            Count of unplaced pieces
        """
        return len(self.pieces)

    def __repr__(self):
        """String representation of AI player."""
        return f"AIPlayer(id={self.player_id}, name='{self.name}', difficulty='{self.difficulty}')"
