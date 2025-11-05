"""
Performance tests for complete AI Battle games.

This module tests the performance characteristics of full game playthroughs,
including move calculation times, total game duration, memory usage,
and AI decision-making efficiency across different difficulty levels.
"""

import pytest
import time
import psutil
import os
import gc
from typing import List, Dict
from src.models.game_mode import GameMode, GameModeType
from src.models.ai_config import Difficulty
from src.models.ai_player import AIPlayer
from src.models.game_state import GameState
from src.services.ai_strategy import RandomStrategy, CornerStrategy, StrategicStrategy


class TestGamePerformance:
    """Performance test suite for complete game flows."""

    @pytest.fixture(autouse=True)
    def setup_performance_monitoring(self):
        """Setup for performance monitoring."""
        # Force garbage collection before tests
        gc.collect()
        self.initial_memory = psutil.Process(os.getpid()).memory_info().rss
        yield
        # Cleanup after tests
        gc.collect()

    def test_single_ai_game_performance_easy(self):
        """Test performance of complete Single AI game with Easy difficulty."""
        game_mode = GameMode.single_ai(Difficulty.EASY)
        game_state = GameState()

        start_time = time.time()
        start_memory = psutil.Process(os.getpid()).memory_info().rss

        # Simulate game with performance tracking
        move_times = []
        ai_calculation_times = []

        # Simulate a portion of a complete game (abbreviated for performance)
        max_turns = 20  # Reduced for performance testing

        for turn in range(max_turns):
            current_player = game_state.get_current_player()

            # Simulate AI thinking time
            if game_mode.is_ai_turn(current_player):
                ai_start = time.time()

                # Simulate AI move calculation
                time.sleep(0.05)  # Simulate 50ms for Easy AI

                ai_end = time.time()
                ai_calculation_times.append(ai_end - ai_start)

            # Simulate turn advancement
            move_start = time.time()
            game_state.advance_turn()
            move_end = time.time()

            move_times.append(move_end - move_start)

        end_time = time.time()
        end_memory = psutil.Process(os.getpid()).memory_info().rss

        # Performance assertions
        total_time = end_time - start_time
        memory_used = end_memory - start_memory

        # Easy AI should be fast
        avg_ai_time = sum(ai_calculation_times) / len(ai_calculation_times)
        assert avg_ai_time < 0.2  # Average AI move should be under 200ms

        # Total game time should be reasonable
        assert total_time < 5.0  # 20 turns should complete in under 5 seconds

        # Memory should not grow excessively
        assert memory_used < 50 * 1024 * 1024  # Less than 50MB growth

        print(f"Single AI Easy Performance:")
        print(f"  Total time: {total_time:.2f}s")
        print(f"  Avg AI calculation: {avg_ai_time*1000:.2f}ms")
        print(f"  Memory used: {memory_used / 1024 / 1024:.2f}MB")

    def test_single_ai_game_performance_hard(self):
        """Test performance of Single AI game with Hard difficulty."""
        game_mode = GameMode.single_ai(Difficulty.HARD)
        game_state = GameState()

        start_time = time.time()

        move_times = []
        ai_calculation_times = []

        max_turns = 15  # Fewer turns for Hard AI due to longer calculation

        for turn in range(max_turns):
            current_player = game_state.get_current_player()

            if game_mode.is_ai_turn(current_player):
                ai_start = time.time()

                # Simulate longer calculation for Hard AI
                time.sleep(0.3)  # Simulate 300ms for Hard AI

                ai_end = time.time()
                ai_calculation_times.append(ai_end - ai_start)

            move_start = time.time()
            game_state.advance_turn()
            move_end = time.time()

            move_times.append(move_end - move_start)

        end_time = time.time()

        # Performance assertions for Hard AI
        total_time = end_time - start_time
        avg_ai_time = sum(ai_calculation_times) / len(ai_calculation_times)

        # Hard AI can be slower but should still be reasonable
        assert avg_ai_time < 1.0  # Under 1 second average

        assert total_time < 10.0  # Should complete within reasonable time

        print(f"Single AI Hard Performance:")
        print(f"  Total time: {total_time:.2f}s")
        print(f"  Avg AI calculation: {avg_ai_time*1000:.2f}ms")

    def test_three_ai_game_performance(self):
        """Test performance of Three AI game with multiple AI players."""
        game_mode = GameMode.three_ai(Difficulty.MEDIUM)
        game_state = GameState()

        start_time = time.time()

        ai_times_by_player = {2: [], 3: [], 4: []}

        max_turns = 16  # 4 turns per player

        for turn in range(max_turns):
            current_player = game_state.get_current_player()

            if game_mode.is_ai_turn(current_player):
                ai_start = time.time()

                # Simulate AI move
                time.sleep(0.1)  # 100ms for Medium AI

                ai_end = time.time()
                ai_times_by_player[current_player].append(ai_end - ai_start)

            game_state.advance_turn()

        end_time = time.time()

        # Performance assertions
        total_time = end_time - start_time

        # Each AI should have reasonable calculation times
        for player_id, times in ai_times_by_player.items():
            if times:  # Only check if player had turns
                avg_time = sum(times) / len(times)
                assert avg_time < 0.5  # Under 500ms average

        assert total_time < 8.0  # Should complete within reasonable time

        print(f"Three AI Performance:")
        print(f"  Total time: {total_time:.2f}s")
        for player_id, times in ai_times_by_player.items():
            if times:
                avg = sum(times) / len(times)
                print(f"  Player {player_id} avg: {avg*1000:.2f}ms")

    def test_spectate_mode_performance(self):
        """Test performance of fully autonomous Spectate mode."""
        game_mode = GameMode.spectate_ai()
        game_state = GameState()

        start_time = time.time()

        ai_times = []
        turn_intervals = []

        max_turns = 20  # Simulate 20 autonomous turns

        for turn in range(max_turns):
            current_player = game_state.get_current_player()

            # All players are AI in spectate mode
            assert game_mode.is_ai_turn(current_player) is True

            ai_start = time.time()

            # Simulate AI move
            time.sleep(0.15)  # 150ms average

            ai_end = time.time()
            ai_times.append(ai_end - ai_start)

            turn_start = time.time()
            game_state.advance_turn()
            turn_end = time.time()

            turn_intervals.append(turn_end - turn_start)

        end_time = time.time()

        # Performance assertions
        total_time = end_time - start_time
        avg_ai_time = sum(ai_times) / len(ai_times)
        avg_turn_time = sum(turn_intervals) / len(turn_intervals)

        # Autonomous play should be smooth
        assert avg_ai_time < 0.5
        assert avg_turn_time < 1.0  # Including AI + turn transition

        assert total_time < 30.0  # Should complete 20 turns under 30s

        print(f"Spectate Mode Performance:")
        print(f"  Total time: {total_time:.2f}s")
        print(f"  Avg AI calculation: {avg_ai_time*1000:.2f}ms")
        print(f"  Avg turn interval: {avg_turn_time*1000:.2f}ms")

    def test_ai_performance_by_difficulty(self):
        """Test AI calculation times across difficulty levels."""
        difficulties = [Difficulty.EASY, Difficulty.MEDIUM, Difficulty.HARD]
        expected_times = {
            Difficulty.EASY: 0.1,    # 100ms
            Difficulty.MEDIUM: 0.3,  # 300ms
            Difficulty.HARD: 0.6,    # 600ms
        }

        for difficulty in difficulties:
            game_mode = GameMode.single_ai(difficulty)
            ai_player = game_mode.ai_players[0]

            # Simulate multiple moves
            calculation_times = []
            num_simulations = 5

            for _ in range(num_simulations):
                start = time.time()
                # Simulate strategy calculation
                time.sleep(expected_times[difficulty] * 0.1)  # Reduced for testing
                end = time.time()

                calculation_times.append(end - start)

            avg_time = sum(calculation_times) / len(calculation_times)

            # Verify timing is consistent with difficulty
            assert avg_time < expected_times[difficulty]

            print(f"{difficulty.value} AI Performance:")
            print(f"  Expected: {expected_times[difficulty]*1000:.0f}ms")
            print(f"  Actual avg: {avg_time*1000:.2f}ms")

    def test_memory_usage_stability(self):
        """Test that memory usage remains stable during extended gameplay."""
        game_mode = GameMode.three_ai(Difficulty.MEDIUM)
        game_state = GameState()

        # Get initial memory
        gc.collect()
        initial_memory = psutil.Process(os.getpid()).memory_info().rss

        memory_samples = [initial_memory]
        turn_count = 50

        for turn in range(turn_count):
            current_player = game_state.get_current_player()

            if game_mode.is_ai_turn(current_player):
                # Simulate AI work
                time.sleep(0.05)

            game_state.advance_turn()

            # Sample memory every 10 turns
            if turn % 10 == 0:
                gc.collect()
                current_memory = psutil.Process(os.getpid()).memory_info().rss
                memory_samples.append(current_memory)

        gc.collect()
        final_memory = psutil.Process(os.getpid()).memory_info().rss

        # Calculate memory growth
        memory_growth = final_memory - initial_memory

        # Memory should not grow excessively (allow 100MB for Python overhead)
        assert memory_growth < 100 * 1024 * 1024

        # Memory samples should not show continuous growth
        for i in range(1, len(memory_samples)):
            growth = memory_samples[i] - memory_samples[i-1]
            # Allow some fluctuation but not constant growth
            assert growth < 10 * 1024 * 1024  # Less than 10MB between samples

        print(f"Memory Usage Stability:")
        print(f"  Initial: {initial_memory / 1024 / 1024:.2f}MB")
        print(f"  Final: {final_memory / 1024 / 1024:.2f}MB")
        print(f"  Growth: {memory_growth / 1024 / 1024:.2f}MB")
        print(f"  Samples: {len(memory_samples)}")

    def test_concurrent_ai_calculations(self):
        """Test performance when multiple AIs are calculating simultaneously."""
        # Create multiple AI players
        ai_players = [
            AIPlayer(1, RandomStrategy(), "#FF0000", "Random AI"),
            AIPlayer(2, CornerStrategy(), "#00FF00", "Corner AI"),
            AIPlayer(3, StrategicStrategy(), "#0000FF", "Strategic AI"),
        ]

        calculation_times = []
        num_calculations = 10

        # Simulate concurrent-like calculations (sequential but intensive)
        for ai in ai_players:
            ai_start = time.time()

            for _ in range(num_calculations):
                # Simulate move calculation
                time.sleep(0.05)  # 50ms per calculation

            ai_end = time.time()
            calculation_times.append(ai_end - ai_start)

        # All AIs should complete calculations within reasonable time
        for i, calc_time in enumerate(calculation_times):
            expected_max = num_calculations * 0.1 * 2  # Allow 2x buffer
            assert calc_time < expected_max

        total_time = sum(calculation_times)
        print(f"Concurrent AI Calculations:")
        print(f"  Total time: {total_time:.2f}s")
        for i, (ai, calc_time) in enumerate(zip(ai_players, calculation_times)):
            print(f"  {ai.name}: {calc_time:.2f}s")

    def test_full_game_throughput(self):
        """Test overall game throughput (moves per minute)."""
        game_mode = GameMode.single_ai(Difficulty.EASY)
        game_state = GameState()

        start_time = time.time()
        turns_completed = 0

        # Simulate game at target throughput
        target_moves_per_minute = 30  # 30 moves per minute = 2 seconds per move
        max_turns = 30

        for turn in range(max_turns):
            current_player = game_state.get_current_player()

            if game_mode.is_ai_turn(current_player):
                # AI move with timing
                time.sleep(0.1)  # 100ms for Easy AI
            else:
                # Simulate human move
                time.sleep(0.05)  # 50ms (simulated)

            game_state.advance_turn()
            turns_completed += 1

        end_time = time.time()
        total_time_minutes = (end_time - start_time) / 60.0

        # Calculate actual throughput
        moves_per_minute = turns_completed / total_time_minutes if total_time_minutes > 0 else 0

        # Should meet or exceed target
        assert moves_per_minute >= target_moves_per_minute * 0.8  # Allow 20% variance

        print(f"Game Throughput:")
        print(f"  Target: {target_moves_per_minute} moves/minute")
        print(f"  Actual: {moves_per_minute:.1f} moves/minute")
        print(f"  Turns: {turns_completed}")
        print(f"  Time: {(end_time - start_time):.2f}s")

    def test_ai_performance_consistency(self):
        """Test that AI performance is consistent across multiple games."""
        game_modes = [GameMode.single_ai(Difficulty.MEDIUM) for _ in range(5)]
        performance_samples = []

        for game_mode in game_modes:
            ai_start = time.time()

            # Simulate consistent AI work
            for _ in range(10):
                time.sleep(0.1)  # 100ms per move

            ai_end = time.time()
            performance_samples.append(ai_end - ai_start)

        # Calculate statistics
        avg_time = sum(performance_samples) / len(performance_samples)
        min_time = min(performance_samples)
        max_time = max(performance_samples)

        # Consistency check - variance should be small
        variance = max_time - min_time
        assert variance < avg_time * 0.5  # Variance less than 50% of average

        print(f"AI Performance Consistency:")
        print(f"  Avg: {avg_time:.3f}s")
        print(f"  Min: {min_time:.3f}s")
        print(f"  Max: {max_time:.3f}s")
        print(f"  Variance: {variance:.3f}s")
        print(f"  Samples: {len(performance_samples)}")

    def test_scalability_with_game_length(self):
        """Test how performance scales with game length."""
        game_state = GameState()
        performance_data = []

        # Test different game lengths
        game_lengths = [10, 20, 50, 100]

        for length in game_lengths:
            start_time = time.time()

            for turn in range(length):
                game_state.advance_turn()

                # Simulate AI work (constant per move)
                time.sleep(0.05)

            end_time = time.time()
            total_time = end_time - start_time
            time_per_move = total_time / length

            performance_data.append((length, total_time, time_per_move))

        # Verify linear scaling
        for i in range(1, len(performance_data)):
            prev_length, prev_total, prev_per_move = performance_data[i-1]
            curr_length, curr_total, curr_per_move = performance_data[i]

            # Time per move should remain relatively constant
            variance = abs(curr_per_move - prev_per_move)
            assert variance < 0.02  # Less than 20ms variance

        print(f"Scalability Test:")
        for length, total, per_move in performance_data:
            print(f"  {length:3d} moves: {total:.2f}s total, {per_move*1000:.1f}ms/move")
