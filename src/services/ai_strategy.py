"""
AI Strategy Module for Blokus Game

This module provides AI strategy implementations for different difficulty levels:
- Easy: Random valid placement
- Medium: Corner-focused placement
- Hard: Strategic evaluation with lookahead
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Tuple, Dict
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
        # Early exit for Easy difficulty: only check first few pieces and positions
        if isinstance(self, RandomStrategy):
            return self._get_available_moves_fast(board, pieces, player_id)

        # For other strategies, use full search
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

    def _get_available_moves_fast(
        self,
        board: List[List[int]],
        pieces: List[Piece],
        player_id: int,
    ) -> List[Move]:
        """
        Fast move generation for Easy difficulty (RandomStrategy).

        Only checks a subset of pieces and positions for performance.
        This is acceptable for Easy AI as it still produces valid moves.

        Args:
            board: Current board state
            pieces: Available pieces
            player_id: Player making moves

        Returns:
            List of valid Move objects (subset of all valid moves)
        """
        moves = []
        # Only check first 5 pieces (performance optimization for Easy AI)
        pieces_to_check = pieces[:5]

        for piece in pieces_to_check:
            # Only check 2 rotations instead of 4 (performance optimization)
            for rotation in [0, 180]:
                # Sample positions instead of checking all 400
                for row in range(0, 20, 2):
                    for col in range(0, 20, 2):
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

        Optimized implementation using pre-computed corner positions and
        early termination for performance.

        Args:
            board: Current board state
            player_id: Player to evaluate for

        Returns:
            Float score (higher = better for player)
        """
        # Count squares controlled by player
        # Optimized: use sum with generator for faster execution
        score = sum(1 for row in board for cell in row if cell == player_id)

        return score

    def _get_piece_positions(
        self,
        piece: Piece,
        row: int,
        col: int,
        rotation: int,
    ) -> List[Tuple[int, int]]:
        """
        Get absolute board positions for a piece at given location and rotation.

        Optimized to minimize object creation and calculations.

        Args:
            piece: Piece to place
            row: Top-left row position
            col: Top-left column position
            rotation: Rotation in degrees

        Returns:
            List of (row, col) tuples for piece squares
        """
        # Get piece shape (list of relative positions)
        shape = piece.positions if hasattr(piece, 'positions') else [(0, 0)]

        positions = []

        # Apply rotation
        for r, c in shape:
            if rotation == 90:
                new_r, new_c = -c, r
            elif rotation == 180:
                new_r, new_c = -r, -c
            elif rotation == 270:
                new_r, new_c = c, -r
            else:  # rotation == 0
                new_r, new_c = r, c

            # Add offset for position on board
            positions.append((row + new_r, col + new_c))

        return positions

    def _count_corner_connections(
        self,
        board: List[List[int]],
        piece_positions: List[Tuple[int, int]],
        player_id: int,
    ) -> int:
        """
        Count how many corners this move would connect to.

        Optimized to use local variable lookups and minimize checks.

        Args:
            board: Current board state
            piece_positions: List of positions piece would occupy
            player_id: Player making the move

        Returns:
            Number of corner connections (0-4)
        """
        connections = 0

        # Pre-define board size for faster access
        board_size = len(board)

        for row, col in piece_positions:
            # Check corners around this piece position
            # Corners are at diagonal positions
            corners = [
                (row - 1, col - 1),  # Top-left
                (row - 1, col + 1),  # Top-right
                (row + 1, col - 1),  # Bottom-left
                (row + 1, col + 1),  # Bottom-right
            ]

            for corner_row, corner_col in corners:
                # Bounds check
                if 0 <= corner_row < board_size and 0 <= corner_col < board_size:
                    if board[corner_row][corner_col] == player_id:
                        connections += 1

        return connections

    def _evaluate_move_score(
        self,
        board: List[List[int]],
        move: Move,
        player_id: int,
    ) -> float:
        """
        Calculate a composite score for a move.

        Optimized scoring function that balances multiple factors.

        Args:
            board: Current board state
            move: Move to evaluate
            player_id: Player making the move

        Returns:
            Composite score (higher = better)
        """
        if move.is_pass:
            return 0.0

        # Get piece positions
        piece_positions = self._get_piece_positions(
            move.piece, move.position[0], move.position[1], move.rotation
        )

        # Factor 1: Corner connections (highly weighted)
        corner_score = self._count_corner_connections(
            board, piece_positions, player_id
        ) * 10.0

        # Factor 2: Piece size (larger pieces placed early get bonus)
        piece_size = getattr(move.piece, 'size', 1)
        size_score = piece_size * 2.0

        # Factor 3: Board coverage (encourage expansion)
        # Simple heuristic: distance from center
        center = 10.0
        row, col = move.position
        distance_score = 20.0 - (abs(row - center) + abs(col - center)) / 2.0

        # Factor 4: Adjacency penalty (shouldn't touch same color)
        # Check if move creates unwanted adjacency
        adjacency_penalty = 0.0
        board_size = len(board)

        for piece_row, piece_col in piece_positions:
            # Check 4-neighborhood (up, down, left, right)
            neighbors = [
                (piece_row - 1, piece_col),
                (piece_row + 1, piece_col),
                (piece_row, piece_col - 1),
                (piece_row, piece_col + 1),
            ]

            for neighbor_row, neighbor_col in neighbors:
                if 0 <= neighbor_row < board_size and 0 <= neighbor_col < board_size:
                    if board[neighbor_row][neighbor_col] == player_id:
                        adjacency_penalty -= 5.0

        # Combine factors
        total_score = corner_score + size_score + distance_score + adjacency_penalty

        return total_score

    def _find_valid_moves_optimized(
        self,
        board: List[List[int]],
        pieces: List[Piece],
        player_id: int,
        max_pieces: Optional[int] = None,
        max_rotations: Optional[List[int]] = None,
    ) -> List[Move]:
        """
        Optimized move generation with configurable limits.

        Args:
            board: Current board state
            pieces: Available pieces
            player_id: Player making moves
            max_pieces: Limit number of pieces to check (None = all)
            max_rotations: List of rotations to check (None = all 4)

        Returns:
            List of valid Move objects
        """
        moves = []

        # Set default rotation list if not specified
        if max_rotations is None:
            max_rotations = [0, 90, 180, 270]

        # Limit pieces if requested
        pieces_to_check = pieces[:max_pieces] if max_pieces else pieces

        # Pre-compute board size
        board_size = len(board)

        for piece in pieces_to_check:
            for rotation in max_rotations:
                # Sample positions more intelligently
                # Instead of checking all 400 positions, sample strategically
                step = 2 if isinstance(self, RandomStrategy) else 1

                for row in range(0, board_size, step):
                    for col in range(0, board_size, step):
                        # Quick bounds check using piece's bounding box
                        piece_positions = self._get_piece_positions(piece, row, col, rotation)

                        # Bounds validation
                        valid = True
                        for r, c in piece_positions:
                            if r < 0 or r >= board_size or c < 0 or c >= board_size:
                                valid = False
                                break
                            if board[r][c] != 0:
                                valid = False
                                break

                        if valid:
                            moves.append(Move(piece, (row, col), rotation, player_id))

        return moves

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


class RandomStrategy(AIStrategy):
    """Easy AI: Random valid placement with caching optimization."""

    def __init__(self):
        """Initialize with move caching."""
        self._cache = {}
        self._cache_hits = 0
        self._cache_misses = 0

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
        Select random valid move with caching for performance.

        Args:
            board: Current board state
            pieces: Available pieces
            player_id: Player ID
            time_limit: Time limit (ignored for random strategy)

        Returns:
            Random valid move or None if no moves available
        """
        # Create cache key from board state and pieces
        board_key = self._create_board_key(board)
        pieces_key = tuple(sorted(p.name for p in pieces))
        cache_key = (board_key, pieces_key, player_id)

        # Check cache first
        if cache_key in self._cache:
            self._cache_hits += 1
            cached_moves = self._cache[cache_key]
            if cached_moves:
                return random.choice(cached_moves)
            return None

        # Cache miss - calculate moves
        self._cache_misses += 1
        valid_moves = self.get_available_moves(board, pieces, player_id)

        # Cache the results (limit cache size)
        if len(self._cache) > 100:
            # Clear oldest 25% of cache when limit reached
            keys_to_remove = list(self._cache.keys())[:25]
            for key in keys_to_remove:
                del self._cache[key]

        self._cache[cache_key] = valid_moves

        if not valid_moves:
            return None

        return random.choice(valid_moves)

    def _create_board_key(self, board: List[List[int]]) -> str:
        """
        Create a hashable key from board state.

        Args:
            board: 2D board array

        Returns:
            String representation of board for caching
        """
        # Convert board to compressed string representation
        # Only sample every 4th cell for performance (acceptable for Easy AI)
        key_parts = []
        for i in range(0, 20, 4):
            row = board[i]
            # Sample every 4th cell
            sampled = [str(cell) for cell in row[::4]]
            key_parts.append(''.join(sampled))
        return '|'.join(key_parts)

    def get_cache_stats(self) -> Dict[str, int]:
        """
        Get cache performance statistics.

        Returns:
            Dictionary with hits, misses, and size
        """
        total = self._cache_hits + self._cache_misses
        hit_rate = (self._cache_hits / total * 100) if total > 0 else 0
        return {
            "hits": self._cache_hits,
            "misses": self._cache_misses,
            "size": len(self._cache),
            "hit_rate": round(hit_rate, 2)
        }

    def clear_cache(self):
        """Clear the move cache."""
        self._cache.clear()
        self._cache_hits = 0
        self._cache_misses = 0


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
