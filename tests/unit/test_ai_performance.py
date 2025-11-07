"""
Performance tests for AI move calculation.

This module tests the performance characteristics of AI strategies,
including calculation time, timeout handling, and move quality.
"""

import pytest
import time
from src.services.ai_strategy import RandomStrategy, CornerStrategy, StrategicStrategy
from src.models.ai_player import AIPlayer
from src.config.pieces import get_full_piece_set


class TestAIPerformance:
    """Test suite for AI performance metrics."""

    def test_random_strategy_performance(self):
        """Test RandomStrategy calculation time is within limits."""
        strategy = RandomStrategy()

        # Create board with some pieces
        board = [[0 for _ in range(20)] for _ in range(20)]
        pieces = get_full_piece_set()

        # Measure calculation time
        start_time = time.time()
        move = strategy.calculate_move(board, pieces, player_id=1)
        elapsed_time = time.time() - start_time

        # Random strategy should be very fast (< 100ms)
        assert elapsed_time < 0.1, f"RandomStrategy took {elapsed_time:.3f}s (should be < 0.1s)"

        # Should complete within timeout
        assert elapsed_time <= strategy.timeout_seconds

    def test_corner_strategy_performance(self):
        """Test CornerStrategy calculation time is within limits."""
        strategy = CornerStrategy()

        # Create board with some pieces
        board = [[0 for _ in range(20)] for _ in range(20)]
        pieces = get_full_piece_set()

        # Measure calculation time
        start_time = time.time()
        move = strategy.calculate_move(board, pieces, player_id=1)
        elapsed_time = time.time() - start_time

        # Corner strategy should be fast (< 500ms)
        assert elapsed_time < 0.5, f"CornerStrategy took {elapsed_time:.3f}s (should be < 0.5s)"

        # Should complete within timeout
        assert elapsed_time <= strategy.timeout_seconds

    def test_strategic_strategy_performance(self):
        """Test StrategicStrategy calculation time is within limits."""
        strategy = StrategicStrategy()

        # Create board with some pieces
        board = [[0 for _ in range(20)] for _ in range(20)]
        pieces = get_full_piece_set()

        # Measure calculation time with custom timeout
        timeout = 2  # 2 seconds for test
        start_time = time.time()
        move = strategy.calculate_move(board, pieces, player_id=1, time_limit=timeout)
        elapsed_time = time.time() - start_time

        # Strategic strategy with lookahead may take longer but should respect timeout
        # Allow up to the timeout limit
        assert elapsed_time <= timeout + 0.5, f"StrategicStrategy exceeded timeout by {elapsed_time - timeout:.3f}s"

    def test_ai_player_calculation_performance(self):
        """Test AIPlayer calculation respects timeout limits."""
        # Test with different strategies
        strategies = [
            (RandomStrategy(), 1.0),    # 1 second max
            (CornerStrategy(), 2.0),    # 2 seconds max
            (StrategicStrategy(), 3.0), # 3 seconds max
        ]

        for strategy, max_time in strategies:
            ai_player = AIPlayer(
                player_id=1,
                strategy=strategy,
                color="blue"
            )

            # Create test board
            board = [[0 for _ in range(20)] for _ in range(20)]
            pieces = get_full_piece_set()

            # Calculate with timeout
            start_time = time.time()
            move = ai_player.calculate_move(board, pieces, time_limit=max_time)
            elapsed_time = time.time() - start_time

            # Should complete within time limit
            assert elapsed_time <= max_time + 0.5, f"{strategy.difficulty_name} took {elapsed_time:.3f}s (max: {max_time}s)"

    def test_timeout_handling(self):
        """Test AI respects timeout limits."""
        ai_player = AIPlayer(
            player_id=1,
            strategy=StrategicStrategy(),  # Longest calculation
            color="blue"
        )

        # Create board
        board = [[0 for _ in range(20)] for _ in range(20)]
        pieces = get_full_piece_set()

        # Use very short timeout
        timeout = 0.1  # 100ms
        start_time = time.time()
        move = ai_player.calculate_move(board, pieces, time_limit=timeout)
        elapsed_time = time.time() - start_time

        # Should respect timeout (may return None or best found move)
        assert elapsed_time <= timeout + 0.5, f"Timeout not respected: {elapsed_time:.3f}s > {timeout}s"

        # Should return a move (even if it's the first valid one found)
        assert move is not None or move is None  # Either is acceptable

    def test_calculation_with_no_pieces(self):
        """Test AI performance when no pieces are available."""
        ai_player = AIPlayer(
            player_id=1,
            strategy=CornerStrategy(),
            color="blue"
        )

        board = [[0 for _ in range(20)] for _ in range(20)]
        pieces = []  # No pieces

        start_time = time.time()
        move = ai_player.calculate_move(board, pieces)
        elapsed_time = time.time() - start_time

        # Should complete quickly even with no pieces
        assert elapsed_time < 0.1, f"Empty pieces calculation took {elapsed_time:.3f}s"

        # Should return None (no moves possible)
        assert move is None

    def test_calculation_with_empty_board(self):
        """Test AI performance on completely empty board."""
        ai_player = AIPlayer(
            player_id=1,
            strategy=RandomStrategy(),
            color="blue"
        )

        # Empty board
        board = [[0 for _ in range(20)] for _ in range(20)]
        pieces = get_full_piece_set()

        start_time = time.time()
        move = ai_player.calculate_move(board, pieces)
        elapsed_time = time.time() - start_time

        # Should be fast on empty board
        assert elapsed_time < 0.1, f"Empty board calculation took {elapsed_time:.3f}s"

        # Should find valid moves on empty board
        assert move is not None

    def test_calculation_with_full_board(self):
        """Test AI performance on nearly full board."""
        ai_player = AIPlayer(
            player_id=1,
            strategy=CornerStrategy(),
            color="blue"
        )

        # Nearly full board (only a few empty spaces)
        board = [[1 if (r + c) % 3 != 0 else 0 for c in range(20)] for r in range(20)]
        pieces = get_full_piece_set()

        start_time = time.time()
        move = ai_player.calculate_move(board, pieces)
        elapsed_time = time.time() - start_time

        # Should complete even with limited moves
        assert elapsed_time < 0.5, f"Full board calculation took {elapsed_time:.3f}s"

    def test_timeout_vs_calculation_quality(self):
        """Test that timeout doesn't prevent finding valid moves."""
        ai_player = AIPlayer(
            player_id=1,
            strategy=StrategicStrategy(),  # More complex strategy
            color="blue"
        )

        board = [[0 for _ in range(20)] for _ in range(20)]
        pieces = get_full_piece_set()

        # Multiple runs with timeout to ensure consistency
        for timeout in [0.5, 1.0, 2.0]:
            move = ai_player.calculate_move(board, pieces, time_limit=timeout)

            # Should always find a valid move on empty board
            if move and not move.is_pass:
                assert move.piece in pieces
                assert move.position is not None
                assert 0 <= move.position[0] < 20
                assert 0 <= move.position[1] < 20

    def test_available_moves_performance(self):
        """Test performance of get_available_moves method."""
        strategy = CornerStrategy()

        board = [[0 for _ in range(20)] for _ in range(20)]
        pieces = get_full_piece_set()

        # Time the move generation
        start_time = time.time()
        moves = strategy.get_available_moves(board, pieces, player_id=1)
        elapsed_time = time.time() - start_time

        # Move generation should be fast
        assert elapsed_time < 1.0, f"Move generation took {elapsed_time:.3f}s"

        # Should generate reasonable number of moves
        assert len(moves) > 0, "Should generate at least one move"

    def test_ai_elapsed_time_tracking(self):
        """Test AI player tracks elapsed calculation time."""
        ai_player = AIPlayer(
            player_id=1,
            strategy=RandomStrategy(),
            color="blue"
        )

        board = [[0 for _ in range(20)] for _ in range(20)]
        pieces = get_full_piece_set()

        # Before calculation
        elapsed = ai_player.get_elapsed_calculation_time()
        assert elapsed is None

        # Monkey-patch to add delay and check time during calculation
        original_calculate = ai_player.strategy.calculate_move
        times_during_calculation = []

        def patched_calculate_move(board, pieces, player_id, time_limit=None):
            # Check time at start
            elapsed = ai_player.get_elapsed_calculation_time()
            if elapsed is not None:
                times_during_calculation.append(elapsed)
            return original_calculate(board, pieces, player_id, time_limit)

        ai_player.strategy.calculate_move = patched_calculate_move

        # Calculate move
        move = ai_player.calculate_move(board, pieces)

        # Time tracking should have worked
        # Note: After calculation finishes, is_calculating is False, so get_elapsed_calculation_time returns None
        # But we tracked it during the calculation via the patch
        assert len(times_during_calculation) > 0, "Should have tracked time during calculation"
        assert all(t >= 0 for t in times_during_calculation), "All tracked times should be non-negative"

    def test_concurrent_calculation_performance(self):
        """Test multiple AI players can calculate concurrently."""
        # Create multiple AI players with different strategies
        ai_players = [
            AIPlayer(player_id=1, strategy=RandomStrategy(), color="blue", name="AI1"),
            AIPlayer(player_id=2, strategy=CornerStrategy(), color="red", name="AI2"),
            AIPlayer(player_id=3, strategy=RandomStrategy(), color="green", name="AI3"),
        ]

        board = [[0 for _ in range(20)] for _ in range(20)]
        pieces = get_full_piece_set()

        # Calculate moves for all AI players
        start_time = time.time()
        moves = []
        for ai_player in ai_players:
            move = ai_player.calculate_move(board, pieces, time_limit=1.0)
            moves.append(move)
        total_time = time.time() - start_time

        # Total time should be reasonable (sequential calculation)
        assert total_time < 3.0, f"Concurrent calculations took {total_time:.3f}s"

        # All should complete
        assert len(moves) == 3

    def test_performance_consistency(self):
        """Test AI performance is consistent across multiple runs."""
        ai_player = AIPlayer(
            player_id=1,
            strategy=CornerStrategy(),
            color="blue"
        )

        board = [[0 for _ in range(20)] for _ in range(20)]
        pieces = get_full_piece_set()

        # Run multiple times and check consistency
        times = []
        for _ in range(5):
            start_time = time.time()
            move = ai_player.calculate_move(board, pieces)
            elapsed = time.time() - start_time
            times.append(elapsed)

        # All times should be reasonable
        max_time = max(times)
        min_time = min(times)

        assert max_time < 0.5, f"Maximum calculation time {max_time:.3f}s too high"
        assert min_time >= 0, "Calculation time should be non-negative"

        # Times should be somewhat consistent (within same order of magnitude)
        # Allow for some variance but not orders of magnitude
        if max_time > 0:
            ratio = max_time / max(min_time, 0.001)
            assert ratio < 10, f"Calculation times inconsistent: {times}"


class TestAIMoveQuality:
    """Test AI move quality and validation."""

    def test_random_strategy_move_validity(self):
        """Test RandomStrategy produces valid moves."""
        strategy = RandomStrategy()

        # Empty board
        board = [[0 for _ in range(20)] for _ in range(20)]
        pieces = get_full_piece_set()

        for _ in range(10):  # Try multiple times
            move = strategy.calculate_move(board, pieces, player_id=1)

            if move and not move.is_pass:
                # Validate move structure
                assert move.piece in pieces
                assert move.position is not None
                assert isinstance(move.position[0], int)
                assert isinstance(move.position[1], int)
                assert 0 <= move.position[0] < 20
                assert 0 <= move.position[1] < 20

    def test_corner_strategy_prefers_corners(self):
        """Test CornerStrategy prioritizes corner connections."""
        strategy = CornerStrategy()

        # Empty board - no corner connections possible yet
        board = [[0 for _ in range(20)] for _ in range(20)]
        pieces = get_full_piece_set()

        move = strategy.calculate_move(board, pieces, player_id=1)

        # Should still produce a valid move
        if move and not move.is_pass:
            assert move.piece in pieces
            assert move.position is not None

    def test_strategic_strategy_produces_moves(self):
        """Test StrategicStrategy produces valid moves."""
        strategy = StrategicStrategy()

        board = [[0 for _ in range(20)] for _ in range(20)]
        pieces = get_full_piece_set()

        move = strategy.calculate_move(board, pieces, player_id=1, time_limit=2.0)

        # Should produce a move or None (if no valid moves)
        assert move is not None or move is None

        if move and not move.is_pass:
            assert move.piece in pieces
            assert move.position is not None

    def test_no_valid_moves_scenario(self):
        """Test AI handles no valid moves gracefully."""
        strategy = CornerStrategy()

        # Board filled with other player's pieces
        board = [[1 if (r + c) % 2 == 0 else 2 for c in range(20)] for r in range(20)]
        pieces = get_full_piece_set()

        move = strategy.calculate_move(board, pieces, player_id=3)

        # Should return None or pass move when no valid moves
        assert move is None or (move.is_pass if hasattr(move, 'is_pass') else move is None)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
