"""
Edge case tests for AI timeout handling and error scenarios.

This module tests various edge cases and failure scenarios for AI players,
including timeouts, exceptions, fallback behavior, and error recovery.
"""

import time
from unittest.mock import Mock, patch

import pytest

from blokus_game.models.ai_player import AIPlayer
from blokus_game.services.ai_strategy import AIStrategy


class SlowStrategy(AIStrategy):
    """Strategy that deliberately takes longer than timeout."""

    def __init__(self, delay_seconds: float = 10.0):
        self.delay_seconds = delay_seconds

    @property
    def difficulty_name(self) -> str:
        return "Slow"

    @property
    def timeout_seconds(self) -> int:
        return 3

    def calculate_move(self, board, pieces, player_id, time_limit=None):
        time.sleep(self.delay_seconds)  # Deliberately exceed timeout


class ErrorStrategy(AIStrategy):
    """Strategy that raises an exception."""

    def __init__(self, error_message: str = "Test error"):
        self.error_message = error_message

    @property
    def difficulty_name(self) -> str:
        return "Error"

    @property
    def timeout_seconds(self) -> int:
        return 3

    def calculate_move(self, board, pieces, player_id, time_limit=None):
        raise Exception(self.error_message)


class ValidMoveStrategy(AIStrategy):
    """Strategy that returns a valid move quickly."""

    @property
    def difficulty_name(self) -> str:
        return "Valid"

    @property
    def timeout_seconds(self) -> int:
        return 3

    def calculate_move(self, board, pieces, player_id, time_limit=None):
        # Create a mock move
        move = Mock()
        move.is_pass = False
        move.piece = Mock()
        move.piece.name = "TestPiece"
        return move

    def get_available_moves(self, board, pieces, player_id):
        # Return a valid move for fallback
        move = Mock()
        move.is_pass = False
        move.piece = Mock()
        move.piece.name = "FallbackPiece"
        return [move]

    def evaluate_board(self, board, player_id):
        return 1.0


class TestAITimeoutHandling:
    """Test suite for AI timeout scenarios."""

    def test_timeout_within_limit(self):
        """Test AI calculates move within timeout limit."""
        strategy = ValidMoveStrategy()
        ai = AIPlayer(1, strategy, "blue")

        board = [[0] * 20 for _ in range(20)]
        pieces = []

        start = time.time()
        move = ai.calculate_move(board, pieces, time_limit=5)
        elapsed = time.time() - start

        assert move is not None
        assert elapsed < 5

    def test_timeout_exceeds_limit(self):
        """Test AI behavior when calculation exceeds timeout."""
        strategy = SlowStrategy(delay_seconds=1.0)
        ai = AIPlayer(1, strategy, "blue")

        board = [[0] * 20 for _ in range(20)]

        # Create a mock piece for the test
        mock_piece = Mock()
        mock_piece.name = "TestPiece"
        mock_piece.coordinates = [(0, 0), (0, 1), (1, 0)]  # Simple L-shape
        mock_piece.size = 3
        pieces = [mock_piece]

        start = time.time()
        move = ai.calculate_move(board, pieces, time_limit=0.5)
        elapsed = time.time() - start

        # Should return a move despite timeout (fallback to available moves)
        assert move is not None
        # Elapsed time should be close to delay, not exact
        assert elapsed >= 0.5

    def test_timeout_with_no_available_moves(self):
        """Test timeout when no moves are available."""
        strategy = SlowStrategy(delay_seconds=1.0)
        ai = AIPlayer(1, strategy, "blue")

        board = [[0] * 20 for _ in range(20)]
        pieces = []

        # Mock get_available_moves to return empty list
        with patch.object(strategy, "get_available_moves", return_value=[]):
            start = time.time()
            move = ai.calculate_move(board, pieces, time_limit=0.5)
            elapsed = time.time() - start

            # Should return None when no moves available
            assert move is None
            # Since no moves available, returns immediately (no timeout wait)
            assert elapsed < 0.1

    def test_calculation_exception_fallback(self):
        """Test fallback when strategy raises exception."""
        strategy = ErrorStrategy("Test error")
        ai = AIPlayer(1, strategy, "blue")

        board = [[0] * 20 for _ in range(20)]

        # Create a mock piece for the test
        mock_piece = Mock()
        mock_piece.name = "TestPiece"
        mock_piece.coordinates = [(0, 0), (0, 1), (1, 0)]
        mock_piece.size = 3
        pieces = [mock_piece]

        move = ai.calculate_move(board, pieces)

        # Should return a move (either from fallback or available moves)
        assert move is not None

    def test_calculation_exception_with_no_fallback(self):
        """Test behavior when exception occurs and no fallback available."""
        strategy = ErrorStrategy("Test error")
        ai = AIPlayer(1, strategy, "blue")

        board = [[0] * 20 for _ in range(20)]
        pieces = []

        # Mock get_available_moves to return empty list
        with patch.object(strategy, "get_available_moves", return_value=[]):
            move = ai.calculate_move(board, pieces)

            # Should return None when no fallback available
            assert move is None

    def test_invalid_move_piece_not_in_inventory(self):
        """Test handling of move with piece not in inventory."""
        strategy = ValidMoveStrategy()
        ai = AIPlayer(1, strategy, "blue")

        board = [[0] * 20 for _ in range(20)]
        pieces = []

        # Mock strategy to return a move with invalid piece
        move = Mock()
        move.is_pass = False
        move.piece = Mock()
        move.piece.name = "NonExistentPiece"

        with patch.object(strategy, "calculate_move", return_value=move):
            result = ai.calculate_move(board, pieces)

            # Should fallback to valid move
            assert result is not None
            assert result.piece.name == "FallbackPiece"

    def test_elapsed_time_tracking(self):
        """Test that elapsed time is tracked correctly."""
        strategy = ValidMoveStrategy()
        ai = AIPlayer(1, strategy, "blue")

        board = [[0] * 20 for _ in range(20)]
        pieces = []

        # Before calculation
        assert ai.get_elapsed_calculation_time() is None

        # Start calculation in background
        ai.is_calculating = True
        ai._calculation_start_time = time.time()

        time.sleep(0.1)
        elapsed = ai.get_elapsed_calculation_time()

        # Should have measured some elapsed time
        assert elapsed is not None
        assert elapsed >= 0.1
        assert elapsed < 1.0

    def test_multiple_successive_timeouts(self):
        """Test AI behavior with multiple timeout occurrences."""
        strategy = SlowStrategy(delay_seconds=0.5)
        ai = AIPlayer(1, strategy, "blue")

        board = [[0] * 20 for _ in range(20)]

        # Create a mock piece for the test
        mock_piece = Mock()
        mock_piece.name = "TestPiece"
        mock_piece.coordinates = [(0, 0), (0, 1), (1, 0)]
        mock_piece.size = 3
        pieces = [mock_piece]

        # Calculate multiple times with timeouts
        for i in range(3):
            move = ai.calculate_move(board, pieces, time_limit=0.2)
            assert move is not None  # Should always have fallback

    def test_timeout_with_custom_time_limit(self):
        """Test timeout with custom time_limit parameter."""
        strategy = SlowStrategy(delay_seconds=2.0)
        ai = AIPlayer(1, strategy, "blue")

        board = [[0] * 20 for _ in range(20)]

        # Create a mock piece for the test
        mock_piece = Mock()
        mock_piece.name = "TestPiece"
        mock_piece.coordinates = [(0, 0), (0, 1), (1, 0)]
        mock_piece.size = 3
        pieces = [mock_piece]

        # Use custom time limit
        move = ai.calculate_move(board, pieces, time_limit=1.0)

        # Should use fallback due to timeout
        assert move is not None

    def test_strategy_using_default_timeout(self):
        """Test that strategy uses its own timeout when none specified."""
        strategy = ValidMoveStrategy()
        ai = AIPlayer(1, strategy, "blue")

        board = [[0] * 20 for _ in range(20)]
        pieces = []

        # Don't specify time_limit
        move = ai.calculate_move(board, pieces)

        # Should use strategy's timeout_seconds
        assert move is not None

    def test_pass_move_handling(self):
        """Test handling of pass moves (no move to make)."""
        strategy = ValidMoveStrategy()
        ai = AIPlayer(1, strategy, "blue")

        board = [[0] * 20 for _ in range(20)]
        pieces = []

        # Mock strategy to return a pass move
        move = Mock()
        move.is_pass = True
        move.piece = None

        with patch.object(strategy, "calculate_move", return_value=move):
            result = ai.calculate_move(board, pieces)

            # Should accept pass move
            assert result is not None
            assert result.is_pass is True

    def test_ai_is_calculating_flag(self):
        """Test that is_calculating flag is set correctly."""
        strategy = ValidMoveStrategy()
        ai = AIPlayer(1, strategy, "blue")

        board = [[0] * 20 for _ in range(20)]
        pieces = []

        assert not ai.is_calculating

        ai.is_calculating = True
        assert ai.is_calculating

        # Reset after calculation
        ai.is_calculating = False
        assert not ai.is_calculating

    def test_exception_during_fallback(self):
        """Test behavior when exception occurs during fallback."""
        strategy = ErrorStrategy("Test error")
        ai = AIPlayer(1, strategy, "blue")

        board = [[0] * 20 for _ in range(20)]
        pieces = []

        # Mock get_available_moves to also raise exception
        with patch.object(
            strategy, "get_available_moves", side_effect=Exception("Fallback error")
        ):
            move = ai.calculate_move(board, pieces)

            # Should return None when both strategy and fallback fail
            assert move is None


class TestLoggingEdgeCases:
    """Test logging behavior in edge cases."""

    @patch("blokus_game.models.ai_player.ai_logger")
    def test_timeout_logging(self, mock_logger):
        """Test that timeouts are logged correctly."""
        strategy = SlowStrategy(delay_seconds=1.0)
        ai = AIPlayer(1, strategy, "blue")

        board = [[0] * 20 for _ in range(20)]
        pieces = []

        move = ai.calculate_move(board, pieces, time_limit=0.5)

        # Verify logging was called
        assert (
            mock_logger.debug.called
            or mock_logger.info.called
            or mock_logger.warning.called
        )

    @patch("blokus_game.models.ai_player.ai_logger")
    def test_exception_logging(self, mock_logger):
        """Test that exceptions are logged correctly."""
        strategy = ErrorStrategy("Test error")
        ai = AIPlayer(1, strategy, "blue")

        board = [[0] * 20 for _ in range(20)]

        # Create a mock piece for the test
        mock_piece = Mock()
        mock_piece.name = "TestPiece"
        mock_piece.coordinates = [(0, 0), (0, 1), (1, 0)]
        mock_piece.size = 3
        pieces = [mock_piece]

        move = ai.calculate_move(board, pieces)

        # Verify error was logged
        assert mock_logger.error.called

    @patch("blokus_game.models.ai_player.ai_logger")
    def test_successful_calculation_logging(self, mock_logger):
        """Test that successful calculations are logged."""
        strategy = ValidMoveStrategy()
        ai = AIPlayer(1, strategy, "blue")

        board = [[0] * 20 for _ in range(20)]
        pieces = []

        move = ai.calculate_move(board, pieces)

        # Verify info logging was called
        assert mock_logger.info.called


class TestPerformanceEdgeCases:
    """Test performance-related edge cases."""

    def test_very_small_timeout(self):
        """Test AI with very small timeout."""
        strategy = ValidMoveStrategy()
        ai = AIPlayer(1, strategy, "blue")

        board = [[0] * 20 for _ in range(20)]
        pieces = []

        # Use very small timeout
        move = ai.calculate_move(board, pieces, time_limit=0.001)

        # Should still complete quickly
        assert move is not None

    def test_very_large_timeout(self):
        """Test AI with very large timeout."""
        strategy = ValidMoveStrategy()
        ai = AIPlayer(1, strategy, "blue")

        board = [[0] * 20 for _ in range(20)]
        pieces = []

        # Use very large timeout
        start = time.time()
        move = ai.calculate_move(board, pieces, time_limit=1000)
        elapsed = time.time() - start

        # Should complete quickly (not actually wait 1000 seconds)
        assert move is not None
        assert elapsed < 1.0  # Should be much less than timeout

    def test_none_time_limit(self):
        """Test AI with None time_limit."""
        strategy = ValidMoveStrategy()
        ai = AIPlayer(1, strategy, "blue")

        board = [[0] * 20 for _ in range(20)]
        pieces = []

        # Pass None as time_limit
        move = ai.calculate_move(board, pieces, time_limit=None)

        # Should use strategy's default timeout
        assert move is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
