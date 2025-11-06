"""
AI Player Module

This module defines the AIPlayer class which represents an AI-controlled
player in the Blokus game with configurable strategy.
"""

from typing import Optional, List, Dict
import time
import logging
from src.services.ai_strategy import AIStrategy, Move
from src.models.piece import Piece
from src.config.pieces import get_full_piece_set

# Configure logger for AI players
ai_logger = logging.getLogger('ai_player')
ai_logger.setLevel(logging.DEBUG)

# Create console handler if not already present
if not ai_logger.handlers:
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    ai_logger.addHandler(handler)


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
        is_active: Whether player is still active in the game
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
        self.is_active = True  # Compatibility with Player class
        self.is_calculating = False
        self._calculation_start_time = None

        # Performance metrics tracking
        self._calculation_times: List[float] = []
        self._move_count = 0
        self._pass_count = 0
        self._timeout_count = 0
        self._fallback_count = 0
        self._total_calculation_time = 0.0

    @property
    def difficulty(self) -> str:
        """
        Get AI difficulty level.

        Returns:
            Difficulty name from strategy
        """
        return self.strategy.difficulty_name

    @property
    def timeout_seconds(self) -> int:
        """
        Get AI timeout in seconds.

        Returns:
            Timeout limit from strategy
        """
        return self.strategy.timeout_seconds

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

        Behavior:
            - Gracefully handles timeout scenarios
            - Falls back to simpler strategies if timeout occurs
            - Logs all significant events for debugging
            - Returns None only if absolutely no moves are available
        """
        self.is_calculating = True
        self._calculation_start_time = time.time()

        # Determine effective time limit
        effective_limit = time_limit or self.timeout_seconds
        ai_logger.debug(
            f"AI Player {self.player_id} starting move calculation "
            f"(strategy={self.strategy.difficulty_name}, time_limit={effective_limit}s)"
        )

        try:
            # Track elapsed time
            start_time = time.time()

            # Get all available moves first for fallback
            available_moves = self.get_available_moves(board, pieces)

            if not available_moves:
                ai_logger.info(f"AI Player {self.player_id}: No valid moves available")
                # Record pass (no moves available)
                elapsed = time.time() - start_time
                self._record_calculation_time(elapsed, timed_out=False, used_fallback=False)
                self._pass_count += 1
                return None

            ai_logger.debug(f"AI Player {self.player_id}: Found {len(available_moves)} valid moves")

            # Calculate move with timeout
            move = self.strategy.calculate_move(
                board, pieces, self.player_id, effective_limit
            )

            elapsed = time.time() - start_time
            timed_out = elapsed > effective_limit
            used_fallback = False

            # Check timeout
            if timed_out:
                ai_logger.warning(
                    f"AI Player {self.player_id}: Calculation exceeded time limit "
                    f"({elapsed:.2f}s > {effective_limit}s)"
                )

                # If we got a move anyway, use it with warning
                if move:
                    ai_logger.warning(
                        f"AI Player {self.player_id}: Using move despite timeout "
                        f"(elapsed={elapsed:.2f}s)"
                    )
                else:
                    # Timeout with no move - try fallback to first available move
                    ai_logger.info(
                        f"AI Player {self.player_id}: Timeout, falling back to simple move"
                    )
                    # For timeout, just return first available move (simplest valid move)
                    move = available_moves[0] if available_moves else None
                    used_fallback = True

            # Validate move
            if move and not move.is_pass:
                if move.piece not in self.pieces:
                    ai_logger.error(
                        f"AI Player {self.player_id}: Invalid move - piece not in inventory"
                    )
                    # Fall back to a valid move
                    move = available_moves[0] if available_moves else None
                    used_fallback = True

            # Record performance metrics
            self._record_calculation_time(elapsed, timed_out=timed_out, used_fallback=used_fallback)

            # Update counters
            if move:
                if move.is_pass:
                    self._pass_count += 1
                    ai_logger.info(
                        f"AI Player {self.player_id}: Passed turn "
                        f"(elapsed={elapsed:.2f}s)"
                    )
                else:
                    self._move_count += 1
                    ai_logger.info(
                        f"AI Player {self.player_id}: Calculated move in {elapsed:.2f}s "
                        f"(piece={move.piece.name if move.piece else 'PASS'})"
                    )
            else:
                ai_logger.info(
                    f"AI Player {self.player_id}: No move calculated "
                    f"(elapsed={elapsed:.2f}s)"
                )

            return move

        except Exception as e:
            elapsed = time.time() - self._calculation_start_time
            ai_logger.error(
                f"AI Player {self.player_id}: Calculation error after {elapsed:.2f}s: {e}",
                exc_info=True
            )

            # Record the error calculation
            self._record_calculation_time(elapsed, timed_out=False, used_fallback=True)

            # Try to fall back to a simple valid move
            try:
                available_moves = self.get_available_moves(board, pieces)
                if available_moves:
                    ai_logger.info(
                        f"AI Player {self.player_id}: Falling back to first available move"
                    )
                    self._fallback_count += 1
                    return available_moves[0]
            except Exception as fallback_error:
                ai_logger.error(
                    f"AI Player {self.player_id}: Fallback also failed: {fallback_error}"
                )

            return None
        finally:
            self.is_calculating = False
            final_elapsed = time.time() - self._calculation_start_time
            ai_logger.debug(
                f"AI Player {self.player_id}: Calculation finished (total time={final_elapsed:.2f}s)"
            )

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

    def set_active(self):
        """Mark the player as active (compatibility with Player class)."""
        self.is_active = True

    def set_inactive(self):
        """Mark the player as inactive (compatibility with Player class)."""
        self.is_active = False

    def has_pieces_remaining(self) -> bool:
        """
        Check if player has any pieces remaining.

        Returns:
            True if player has unplaced pieces
        """
        return len(self.pieces) > 0


    # Compatibility methods to match Player interface
    def get_all_pieces(self) -> List[Piece]:
        """Return all Piece instances for this AI player."""
        return list(self.pieces)

    def get_unplaced_pieces(self) -> List[Piece]:
        """Return pieces that have not been placed yet."""
        return [p for p in self.pieces if not getattr(p, "is_placed", False)]

    def get_placed_pieces(self) -> List[Piece]:
        """Return pieces that have been placed."""
        return [p for p in self.pieces if getattr(p, "is_placed", False)]

    def get_remaining_piece_count(self) -> int:
        """Return count of unplaced pieces (compat with Player)."""
        return len(self.get_unplaced_pieces())

    def get_remaining_squares(self) -> int:
        """Return total squares remaining in unplaced pieces."""
        return sum(getattr(p, "size", 0) for p in self.get_unplaced_pieces())

    def get_color(self) -> str:
        """Return color string for this player (compat with Player)."""
        return self.color

    def get_starting_corner(self) -> tuple:
        """Return starting corner for this player's id."""
        from src.config.pieces import get_starting_corner

        return get_starting_corner(self.player_id)

    def get_score(self) -> int:
        """Return current score (compatibility with Player class)."""
        return self.score

    def add_points(self, points: int) -> None:
        """Add points to the player's score (compatibility with Player class)."""
        self.score += points

    def subtract_points(self, points: int) -> None:
        """Subtract points from the player's score (compatibility with Player class)."""
        self.score -= points

    def get_piece_names(self) -> List[str]:
        """Return sorted list of piece names."""
        return sorted(p.name for p in self.pieces)

    def get_piece(self, piece_name: str) -> Optional[Piece]:
        """Return a Piece by name, or None if not found (compat with Player)."""
        return next((p for p in self.pieces if p.name == piece_name), None)

    def remove_piece(self, piece):
        """Remove a piece by Piece instance or by name.

        Args:
            piece: Piece instance or piece name string
        """
        # If name provided, remove by matching name
        if isinstance(piece, str):
            to_remove = next((p for p in self.pieces if p.name == piece), None)
            if not to_remove:
                raise ValueError(f"Attempted to remove piece {piece} not in inventory")
            self.pieces.remove(to_remove)
            return to_remove

        # Otherwise assume Piece instance
        if piece not in self.pieces:
            raise ValueError(f"Attempted to remove piece {getattr(piece, 'name', piece)} not in inventory")
        self.pieces.remove(piece)
        return piece

    def get_elapsed_calculation_time(self) -> Optional[float]:
        """
        Get elapsed time for current calculation.

        Returns:
            Seconds elapsed since calculation started, or None if not calculating
        """
        if not self.is_calculating or self._calculation_start_time is None:
            return None
        return time.time() - self._calculation_start_time

    def get_performance_metrics(self) -> Dict[str, float]:
        """
        Get comprehensive performance metrics for this AI player.

        Returns:
            Dictionary with performance statistics
        """
        total_calculations = len(self._calculation_times)
        avg_time = (
            self._total_calculation_time / total_calculations
            if total_calculations > 0
            else 0.0
        )

        max_time = max(self._calculation_times) if self._calculation_times else 0.0
        min_time = min(self._calculation_times) if self._calculation_times else 0.0

        timeout_rate = (
            (self._timeout_count / total_calculations * 100)
            if total_calculations > 0
            else 0.0
        )

        fallback_rate = (
            (self._fallback_count / total_calculations * 100)
            if total_calculations > 0
            else 0.0
        )

        return {
            "total_calculations": total_calculations,
            "moves_made": self._move_count,
            "passes_made": self._pass_count,
            "average_calculation_time": round(avg_time, 4),
            "min_calculation_time": round(min_time, 4),
            "max_calculation_time": round(max_time, 4),
            "total_calculation_time": round(self._total_calculation_time, 4),
            "timeout_count": self._timeout_count,
            "fallback_count": self._fallback_count,
            "timeout_rate_percent": round(timeout_rate, 2),
            "fallback_rate_percent": round(fallback_rate, 2),
        }

    def log_performance_summary(self):
        """Log performance summary for debugging and analysis."""
        metrics = self.get_performance_metrics()

        ai_logger.info(
            f"AI Player {self.player_id} Performance Summary:\n"
            f"  Total Calculations: {metrics['total_calculations']}\n"
            f"  Moves Made: {metrics['moves_made']}, Passes: {metrics['passes_made']}\n"
            f"  Avg Time: {metrics['average_calculation_time']}s "
            f"(min: {metrics['min_calculation_time']}s, "
            f"max: {metrics['max_calculation_time']}s)\n"
            f"  Total Time: {metrics['total_calculation_time']}s\n"
            f"  Timeouts: {metrics['timeout_count']} ({metrics['timeout_rate_percent']}%)\n"
            f"  Fallbacks: {metrics['fallback_count']} ({metrics['fallback_rate_percent']}%)"
        )

    def reset_performance_metrics(self):
        """Reset all performance tracking counters."""
        self._calculation_times.clear()
        self._move_count = 0
        self._pass_count = 0
        self._timeout_count = 0
        self._fallback_count = 0
        self._total_calculation_time = 0.0

        ai_logger.debug(f"AI Player {self.player_id}: Performance metrics reset")

    def _record_calculation_time(self, elapsed_time: float, timed_out: bool = False, used_fallback: bool = False):
        """
        Record calculation time and update counters.

        Args:
            elapsed_time: Time taken for calculation
            timed_out: Whether timeout occurred
            used_fallback: Whether fallback was used
        """
        self._calculation_times.append(elapsed_time)
        self._total_calculation_time += elapsed_time

        # Keep only last 100 calculation times for memory efficiency
        if len(self._calculation_times) > 100:
            self._calculation_times.pop(0)

        if timed_out:
            self._timeout_count += 1

        if used_fallback:
            self._fallback_count += 1

    def get_piece_count(self) -> int:
        """
        Get number of pieces remaining.

        Returns:
            Count of unplaced pieces
        """
        return len(self.pieces)

    def place_piece(self, piece_name: str, row: int, col: int) -> None:
        """
        Mark a piece as placed at given position.

        Args:
            piece_name: Name of the piece
            row: Row where piece was placed
            col: Column where piece was placed

        Raises:
            ValueError: If piece is not found or already placed
        """
        piece = self.get_piece(piece_name)
        if piece is None:
            raise ValueError(f"AI Player does not have piece: {piece_name}")
        if piece.is_placed:
            raise ValueError(f"Piece {piece_name} is already placed")

        piece.place_at(row, col)

    def switch_strategy(self, new_strategy: AIStrategy):
        """
        Switch the AI player's strategy at runtime.

        Args:
            new_strategy: New strategy to use

        Raises:
            ValueError: If strategy is not valid
        """
        if not isinstance(new_strategy, AIStrategy):
            raise ValueError("Strategy must implement AIStrategy interface")

        self.strategy = new_strategy

    def switch_to_difficulty(self, difficulty: str):
        """
        Switch to a strategy based on difficulty level.

        Args:
            difficulty: Difficulty level ("Easy", "Medium", "Hard")

        Raises:
            ValueError: If difficulty is not supported
        """
        from src.models.ai_config import Difficulty as AIDifficulty

        # Convert string to enum
        if isinstance(difficulty, str):
            try:
                diff_enum = AIDifficulty(difficulty)
            except ValueError:
                raise ValueError(f"Invalid difficulty: {difficulty}. Must be Easy, Medium, or Hard")
        else:
            diff_enum = difficulty

        # Create new strategy based on difficulty
        from src.services.ai_strategy import RandomStrategy, CornerStrategy, StrategicStrategy

        if diff_enum == AIDifficulty.EASY:
            self.strategy = RandomStrategy()
        elif diff_enum == AIDifficulty.MEDIUM:
            self.strategy = CornerStrategy()
        elif diff_enum == AIDifficulty.HARD:
            self.strategy = StrategicStrategy()
        else:
            raise ValueError(f"Unsupported difficulty: {diff_enum}")

    def __repr__(self):
        """String representation of AI player."""
        return f"AIPlayer(id={self.player_id}, name='{self.name}', difficulty='{self.difficulty}')"
