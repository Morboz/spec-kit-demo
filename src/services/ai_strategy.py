"""
AI Strategy Module for Blokus Game

This module provides AI strategy implementations for different difficulty levels:
- Easy: Random valid placement
- Medium: Corner-focused placement
- Hard: Strategic evaluation with lookahead
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Tuple
import random
import time
import copy
from src.models.piece import Piece


class Move:
    """Represents a piece placement action in the game."""

    def __init__(
        self,
        piece: Optional[Piece],
        position: Optional[Tuple[int, int]],
        rotation: int,
        player_id: int,
        is_pass: bool = False,
    ):
        """
        Initialize a move.

        Args:
            piece: Piece to place (None if passing)
            position: (row, col) position on board (None if passing)
            rotation: Rotation in degrees (0, 90, 180, 270)
            player_id: ID of player making the move
            is_pass: True if this is a pass move
        """
        self.piece = piece
        self.position = position
        self.rotation = rotation
        self.player_id = player_id
        self.is_pass = is_pass

    def __repr__(self):
        """String representation of the move."""
        if self.is_pass:
            return f"Move(player={self.player_id}, action=pass)"
        return f"Move(player={self.player_id}, piece={self.piece.name if self.piece else None}, position={self.position}, rotation={self.rotation}°)"


class AIStrategy(ABC):
    """Abstract base class for AI strategies."""

    @property
    @abstractmethod
    def difficulty_name(self) -> str:
        """
        Get difficulty level name.

        Returns:
            One of: "Easy", "Medium", "Hard"
        """
        pass

    @property
    @abstractmethod
    def timeout_seconds(self) -> int:
        """
        Get maximum calculation time in seconds.

        Returns:
            Maximum time limit for move calculation
        """
        pass

    @abstractmethod
    def calculate_move(
        self,
        board: List[List[int]],
        pieces: List[Piece],
        player_id: int,
        time_limit: int = None,
    ) -> Optional[Move]:
        """
        Calculate best move for current game state.

        Args:
            board: 2D array representing game board (20x20)
            pieces: List of available pieces to place
            player_id: ID of player making the move (1-4)
            time_limit: Override timeout in seconds (optional)

        Returns:
            Move object representing best move, or None if no valid moves
        """
        pass

    def get_available_moves(
        self,
        board: List[List[int]],
        pieces: List[Piece],
        player_id: int,
    ) -> List[Move]:
        """
        Generate all valid moves for given state (base implementation).

        Args:
            board: Current board state
            pieces: Available pieces
            player_id: Player making moves

        Returns:
            List of all valid Move objects
        """
        # Note: This is a placeholder implementation
        # Actual validation should use BlokusRules.validate_move
        # which requires game_state, not just board
        moves = []
        for piece in pieces:
            for rotation in [0, 90, 180, 270]:
                for row in range(20):
                    for col in range(20):
                        # Basic bounds check
                        piece_positions = self._get_piece_positions(piece, row, col, rotation)
                        if all(0 <= r < 20 and 0 <= c < 20 for r, c in piece_positions):
                            # Basic overlap check
                            valid = True
                            for r, c in piece_positions:
                                if board[r][c] != 0:
                                    valid = False
                                    break
                            if valid:
                                moves.append(Move(piece, (row, col), rotation, player_id))
        return moves

    def evaluate_board(self, board: List[List[int]], player_id: int) -> float:
        """
        Evaluate board position from player's perspective.

        Args:
            board: Current board state
            player_id: Player to evaluate for

        Returns:
            Float score (higher = better for player)
        """
        # Count squares controlled by player
        score = 0
        for row in board:
            for cell in row:
                if cell == player_id:
                    score += 1
        return score

    def _get_piece_positions(
        self, piece: Piece, row: int, col: int, rotation: int
    ) -> List[Tuple[int, int]]:
        """
        Get absolute positions for a piece at given location.

        Args:
            piece: Piece to place
            row: Anchor row
            col: Anchor column
            rotation: Rotation in degrees

        Returns:
            List of (row, col) positions
        """
        # Rotate piece if needed
        rotated_piece = piece
        if rotation > 0:
            rotated_piece = piece.rotate(rotation)

        # Get relative positions
        positions = rotated_piece.get_absolute_positions(row, col)
        return positions


class RandomStrategy(AIStrategy):
    """Easy AI: Random valid placement."""

    @property
    def difficulty_name(self) -> str:
        return "Easy"

    @property
    def timeout_seconds(self) -> int:
        return 3

    def calculate_move(
        self,
        board: List[List[int]],
        pieces: List[Piece],
        player_id: int,
        time_limit: int = None,
    ) -> Optional[Move]:
        """
        Select random valid move.

        Args:
            board: Current board state
            pieces: Available pieces
            player_id: Player ID
            time_limit: Time limit (ignored for random strategy)

        Returns:
            Random valid move or None if no moves available
        """
        valid_moves = self.get_available_moves(board, pieces, player_id)
        if not valid_moves:
            return None

        return random.choice(valid_moves)


class CornerStrategy(AIStrategy):
    """Medium AI: Corner-focused placement."""

    @property
    def difficulty_name(self) -> str:
        return "Medium"

    @property
    def timeout_seconds(self) -> int:
        return 5

    def calculate_move(
        self,
        board: List[List[int]],
        pieces: List[Piece],
        player_id: int,
        time_limit: int = None,
    ) -> Optional[Move]:
        """
        Select move that maximizes corner connections.

        Args:
            board: Current board state
            pieces: Available pieces
            player_id: Player ID
            time_limit: Time limit for calculation

        Returns:
            Best move based on corner strategy or None if no moves
        """
        valid_moves = self.get_available_moves(board, pieces, player_id)
        if not valid_moves:
            return None

        # Score moves by corner connections
        scored_moves = []
        for move in valid_moves:
            score = self._score_move(board, move, player_id)
            scored_moves.append((score, move))

        # Return highest scoring move
        scored_moves.sort(key=lambda x: x[0], reverse=True)
        return scored_moves[0][1]

    def _score_move(self, board: List[List[int]], move: Move, player_id: int) -> float:
        """
        Score a move based on corner strategy.

        Args:
            board: Current board state
            move: Move to score
            player_id: Player ID

        Returns:
            Score for the move (higher is better)
        """
        if move.is_pass or not move.piece or not move.position:
            return 0

        # Count corner connections
        corners_touched = self._count_corner_connections(board, move, player_id)

        # Base score from corner connections
        score = corners_touched * 10

        # Bonus for larger pieces (encourages using big pieces early)
        score += move.piece.size * 2

        # Bonus for placing near edges (for future expansion)
        row, col = move.position
        if row < 2 or row > 17 or col < 2 or col > 17:
            score += 3

        return score

    def _count_corner_connections(
        self, board: List[List[int]], move: Move, player_id: int
    ) -> int:
        """
        Count how many corners this move touches.

        Args:
            board: Current board state
            move: Move to evaluate
            player_id: Player ID

        Returns:
            Number of corner connections
        """
        if not move.position or not move.piece:
            return 0

        positions = self._get_piece_positions(move.piece, move.position[0], move.position[1], move.rotation)
        corners = 0

        for row, col in positions:
            # Check corners around this position
            adjacent_positions = [
                (row - 1, col - 1),  # top-left
                (row - 1, col + 1),  # top-right
                (row + 1, col - 1),  # bottom-left
                (row + 1, col + 1),  # bottom-right
            ]

            for adj_row, adj_col in adjacent_positions:
                if 0 <= adj_row < 20 and 0 <= adj_col < 20:
                    if board[adj_row][adj_col] == player_id:
                        corners += 1

        return corners


class StrategicStrategy(AIStrategy):
    """Hard AI: Multi-factor evaluation with lookahead."""

    @property
    def difficulty_name(self) -> str:
        return "Hard"

    @property
    def timeout_seconds(self) -> int:
        return 8

    def calculate_move(
        self,
        board: List[List[int]],
        pieces: List[Piece],
        player_id: int,
        time_limit: int = None,
    ) -> Optional[Move]:
        """
        Calculate move using lookahead and evaluation.

        Args:
            board: Current board state
            pieces: Available pieces
            player_id: Player ID
            time_limit: Override timeout

        Returns:
            Best move found within timeout
        """
        valid_moves = self.get_available_moves(board, pieces, player_id)
        if not valid_moves:
            return None

        timeout = time_limit or self.timeout_seconds
        start_time = time.time()

        best_move = None
        best_score = float("-inf")

        for move in valid_moves:
            # Check timeout
            if time.time() - start_time >= timeout:
                break

            # Evaluate move
            score = self._evaluate_with_lookahead(board, move, player_id, timeout)

            if score > best_score:
                best_score = score
                best_move = move

        return best_move or valid_moves[0]  # Fallback to any valid move

    def _evaluate_with_lookahead(
        self, board: List[List[int]], move: Move, player_id: int, timeout: float
    ) -> float:
        """
        Evaluate move using multi-move lookahead.

        Args:
            board: Current board state
            move: Move to evaluate
            player_id: Player ID
            timeout: Time budget

        Returns:
            Evaluated score for this move
        """
        # Simulate move on board copy
        simulated_board = copy.deepcopy(board)
        self._apply_move_to_board(simulated_board, move)

        # Evaluate board state
        score = self.evaluate_board(simulated_board, player_id)

        # Add positional bonuses
        score += self._evaluate_position(simulated_board, move, player_id)

        return score

    def _apply_move_to_board(self, board: List[List[int]], move: Move):
        """Apply move to board in-place."""
        if move.is_pass or not move.position or not move.piece:
            return

        positions = self._get_piece_positions(
            move.piece, move.position[0], move.position[1], move.rotation
        )
        for row, col in positions:
            board[row][col] = move.player_id

    def _evaluate_position(
        self, board: List[List[int]], move: Move, player_id: int
    ) -> float:
        """
        Evaluate positional advantages.

        Args:
            board: Board state after move
            move: Move that was made
            player_id: Player ID

        Returns:
            Positional score
        """
        score = 0

        # Count corners established
        corners = self._count_corner_connections(board, move, player_id)
        score += corners * 15

        # Count area control
        player_positions = sum(1 for row in board for cell in row if cell == player_id)
        score += player_positions * 1

        # Evaluate mobility (number of possible next moves)
        # This is simplified - in practice would need deeper analysis
        score += self._estimate_mobility(board, player_id) * 2

        return score

    def _estimate_mobility(self, board: List[List[int]], player_id: int) -> int:
        """
        Estimate player's mobility (future move options).

        Args:
            board: Current board state
            player_id: Player ID

        Returns:
            Estimated mobility score
        """
        # Simple estimate: count empty positions adjacent to player's pieces
        mobility = 0
        for row in range(20):
            for col in range(20):
                if board[row][col] == player_id:
                    # Check adjacent positions
                    for adj_row, adj_col in [(row-1, col), (row+1, col), (row, col-1), (row, col+1)]:
                        if 0 <= adj_row < 20 and 0 <= adj_col < 20:
                            if board[adj_row][adj_col] == 0:
                                mobility += 1
        return mobility
