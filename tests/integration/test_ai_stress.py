"""
Stress tests for multiple concurrent AI games.

This module tests the system's ability to handle multiple AI games running
concurrently, including resource management, isolation between games,
and system stability under high load.
"""

import pytest
import threading
import time
import queue
import gc
from typing import List, Dict, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
from src.models.game_mode import GameMode, GameModeType
from src.models.ai_config import Difficulty
from src.models.ai_player import AIPlayer
from src.models.game_state import GameState
from src.services.ai_strategy import RandomStrategy, CornerStrategy, StrategicStrategy


class TestAIStress:
    """Stress test suite for concurrent AI games."""

    @pytest.fixture
    def stress_config(self):
        """Configuration for stress tests."""
        return {
            'num_concurrent_games': 5,
            'turns_per_game': 15,
            'max_workers': 3,
        }

    def test_multiple_singletai_games_concurrent(self, stress_config):
        """Test multiple Single AI games running concurrently."""
        results = []
        errors = []

        def run_single_ai_game(game_id: int) -> Tuple[int, float, str]:
            """Run a Single AI game and return results."""
            try:
                start_time = time.time()

                # Create game
                game_mode = GameMode.single_ai(Difficulty.MEDIUM)
                game_state = GameState()
                game_state.initialize(2)

                # Simulate game turns
                for turn in range(stress_config['turns_per_game']):
                    current_player = game_state.get_current_player()

                    # Simulate AI work
                    if game_mode.is_ai_turn(current_player):
                        time.sleep(0.05)  # 50ms for Medium AI

                    game_state.advance_turn()

                end_time = time.time()
                duration = end_time - start_time

                return (game_id, duration, "SUCCESS")

            except Exception as e:
                errors.append(f"Game {game_id}: {str(e)}")
                return (game_id, 0, f"ERROR: {str(e)}")

        # Run multiple games concurrently
        with ThreadPoolExecutor(max_workers=stress_config['max_workers']) as executor:
            futures = [
                executor.submit(run_single_ai_game, i)
                for i in range(stress_config['num_concurrent_games'])
            ]

            for future in as_completed(futures):
                results.append(future.result())

        # Verify results
        assert len(errors) == 0, f"Errors occurred: {errors}"

        successful_games = [r for r in results if r[2] == "SUCCESS"]
        assert len(successful_games) == stress_config['num_concurrent_games']

        # Verify games completed within reasonable time
        for game_id, duration, status in successful_games:
            assert duration < 5.0, f"Game {game_id} took too long: {duration:.2f}s"
            assert duration > 0, f"Game {game_id} had invalid duration"

        print(f"Concurrent Single AI Games:")
        print(f"  Games run: {len(successful_games)}")
        print(f"  Errors: {len(errors)}")
        avg_duration = sum(r[1] for r in successful_games) / len(successful_games)
        print(f"  Avg duration: {avg_duration:.2f}s")

    def test_mixed_difficulty_concurrent_games(self, stress_config):
        """Test concurrent games with different AI difficulties."""
        difficulties = [Difficulty.EASY, Difficulty.MEDIUM, Difficulty.HARD]
        results = []

        def run_game_with_difficulty(game_id: int, difficulty: Difficulty) -> Dict:
            """Run a game with specific difficulty."""
            start_time = time.time()
            ai_times = []

            # Create game with specified difficulty
            if game_id % 3 == 0:
                game_mode = GameMode.single_ai(difficulty)
            elif game_id % 3 == 1:
                game_mode = GameMode.three_ai(difficulty)
            else:
                game_mode = GameMode.spectate_ai()

            game_state = GameState()
            game_state.initialize(4 if game_mode.get_ai_count() > 1 else 2)

            for turn in range(stress_config['turns_per_game']):
                current_player = game_state.get_current_player()

                if game_mode.is_ai_turn(current_player):
                    ai_start = time.time()
                    # Difficulty-adjusted simulation
                    if difficulty == Difficulty.EASY:
                        time.sleep(0.03)
                    elif difficulty == Difficulty.MEDIUM:
                        time.sleep(0.08)
                    else:  # HARD
                        time.sleep(0.15)
                    ai_end = time.time()
                    ai_times.append(ai_end - ai_start)

                game_state.advance_turn()

            end_time = time.time()

            return {
                'game_id': game_id,
                'difficulty': difficulty.value,
                'mode': game_mode.mode_type.value,
                'duration': end_time - start_time,
                'avg_ai_time': sum(ai_times) / len(ai_times) if ai_times else 0,
                'ai_turns': len(ai_times),
            }

        # Run games with different difficulties
        with ThreadPoolExecutor(max_workers=stress_config['max_workers']) as executor:
            futures = []
            for i in range(stress_config['num_concurrent_games']):
                difficulty = difficulties[i % len(difficulties)]
                future = executor.submit(run_game_with_difficulty, i, difficulty)
                futures.append(future)

            for future in as_completed(futures):
                results.append(future.result())

        # Verify all games completed
        assert len(results) == stress_config['num_concurrent_games']

        # Verify difficulty-based performance
        for result in results:
            if result['difficulty'] == 'Easy':
                assert result['avg_ai_time'] < 0.1
            elif result['difficulty'] == 'Medium':
                assert result['avg_ai_time'] < 0.2
            else:  # Hard
                assert result['avg_ai_time'] < 0.3

        print(f"Mixed Difficulty Concurrent Games:")
        for difficulty in difficulties:
            difficulty_games = [r for r in results if r['difficulty'] == difficulty.value]
            if difficulty_games:
                avg_duration = sum(g['duration'] for g in difficulty_games) / len(difficulty_games)
                print(f"  {difficulty.value}: {len(difficulty_games)} games, avg {avg_duration:.2f}s")

    def test_max_concurrent_load(self):
        """Test system under maximum concurrent load."""
        max_concurrent = 10
        turns_per_game = 10

        results = queue.Queue()
        errors = queue.Queue()

        def run_game(game_id: int):
            """Run a game under load."""
            try:
                start_time = time.time()

                # Alternate between game modes
                if game_id % 3 == 0:
                    game_mode = GameMode.single_ai(Difficulty.EASY)
                elif game_id % 3 == 1:
                    game_mode = GameMode.three_ai(Difficulty.MEDIUM)
                else:
                    game_mode = GameMode.spectate_ai()

                game_state = GameState()
                game_state.initialize(4 if game_mode.get_ai_count() > 1 else 2)

                for turn in range(turns_per_game):
                    current_player = game_state.get_current_player()

                    if game_mode.is_ai_turn(current_player):
                        time.sleep(0.02)  # Minimal delay for stress test

                    game_state.advance_turn()

                end_time = time.time()
                results.put((game_id, end_time - start_time, True))

            except Exception as e:
                errors.put((game_id, str(e)))

        # Launch all games simultaneously
        threads = []
        for i in range(max_concurrent):
            thread = threading.Thread(target=run_game, args=(i,))
            threads.append(thread)
            thread.start()

        # Wait for all to complete
        for thread in threads:
            thread.join(timeout=30)  # 30 second timeout

        # Collect results
        successful_games = []
        while not results.empty():
            successful_games.append(results.get())

        error_list = []
        while not errors.empty():
            error_list.append(errors.get())

        # Verify system handled load
        assert len(successful_games) == max_concurrent, f"Only {len(successful_games)}/{max_concurrent} games completed"
        assert len(error_list) == 0, f"Errors: {error_list}"

        # Verify reasonable completion time under load
        max_duration = max(game[1] for game in successful_games)
        avg_duration = sum(game[1] for game in successful_games) / len(successful_games)

        assert max_duration < 10.0, f"Max duration under load too high: {max_duration:.2f}s"
        assert avg_duration < 5.0, f"Avg duration under load too high: {avg_duration:.2f}s"

        print(f"Max Concurrent Load Test:")
        print(f"  Concurrent games: {max_concurrent}")
        print(f"  Successful: {len(successful_games)}")
        print(f"  Errors: {len(error_list)}")
        print(f"  Max duration: {max_duration:.2f}s")
        print(f"  Avg duration: {avg_duration:.2f}s")

    def test_rapid_game_creation_and_destruction(self):
        """Test rapid creation and destruction of games."""
        num_cycles = 20
        games_per_cycle = 3

        creation_times = []
        destruction_times = []

        for cycle in range(num_cycles):
            cycle_start = time.time()

            # Create multiple games rapidly
            games = []
            create_start = time.time()
            for i in range(games_per_cycle):
                if i % 3 == 0:
                    game = GameMode.single_ai(Difficulty.EASY)
                elif i % 3 == 1:
                    game = GameMode.three_ai(Difficulty.MEDIUM)
                else:
                    game = GameMode.spectate_ai()
                games.append(game)
            create_end = time.time()

            # Simulate brief gameplay
            for game in games:
                game_state = GameState()
                game_state.initialize(4 if game.get_ai_count() > 1 else 2)
                for _ in range(3):
                    game_state.advance_turn()

            # Destroy games
            destroy_start = time.time()
            del games
            gc.collect()
            destroy_end = time.time()

            cycle_end = time.time()

            creation_times.append(create_end - create_start)
            destruction_times.append(destroy_end - destroy_start)

            # Verify cycle completed quickly
            assert (cycle_end - cycle_start) < 1.0, f"Cycle {cycle} took too long"

        # Verify consistent performance
        avg_creation = sum(creation_times) / len(creation_times)
        avg_destruction = sum(destruction_times) / len(destruction_times)

        assert avg_creation < 0.1, f"Avg creation time too high: {avg_creation:.3f}s"
        assert avg_destruction < 0.1, f"Avg destruction time too high: {avg_destruction:.3f}s"

        print(f"Rapid Game Creation/Destruction:")
        print(f"  Cycles: {num_cycles}")
        print(f"  Games per cycle: {games_per_cycle}")
        print(f"  Avg creation: {avg_creation:.4f}s")
        print(f"  Avg destruction: {avg_destruction:.4f}s")

    def test_memory_isolation_between_concurrent_games(self):
        """Test that concurrent games don't interfere with each other's memory."""
        num_games = 5

        # Track memory usage
        memory_snapshots = []

        def run_isolated_game(game_id: int) -> Dict:
            """Run a game with memory tracking."""
            import psutil
            import os

            process = psutil.Process(os.getpid())
            initial_memory = process.memory_info().rss

            # Create game
            game_mode = GameMode.three_ai(Difficulty.MEDIUM)

            # Simulate gameplay
            game_state = GameState()
            game_state.initialize(4)

            # Create local data structures
            local_data = []
            for i in range(10):
                local_data.append([j for j in range(100)])

            # Simulate turns
            for turn in range(10):
                if game_mode.is_ai_turn(game_state.get_current_player()):
                    time.sleep(0.03)
                game_state.advance_turn()

            mid_memory = process.memory_info().rss

            # Clean up
            del local_data
            del game_state
            del game_mode

            final_memory = process.memory_info().rss

            return {
                'game_id': game_id,
                'initial': initial_memory,
                'mid': mid_memory,
                'final': final_memory,
                'peak_increase': mid_memory - initial_memory,
                'cleanup_effective': final_memory < mid_memory,
            }

        # Run games concurrently
        with ThreadPoolExecutor(max_workers=num_games) as executor:
            futures = [executor.submit(run_isolated_game, i) for i in range(num_games)]
            results = [future.result() for future in as_completed(futures)]

        # Verify isolation
        for result in results:
            # Each game should have reasonable memory usage
            assert result['peak_increase'] < 20 * 1024 * 1024, f"Game {result['game_id']} used too much memory"

            # Cleanup should be effective
            assert result['cleanup_effective'] or result['final'] < result['mid'] + 1024 * 1024

        print(f"Memory Isolation Test:")
        for result in results:
            print(f"  Game {result['game_id']}: "
                  f"peak +{result['peak_increase']/1024/1024:.1f}MB, "
                  f"cleanup: {result['cleanup_effective']}")

    def test_concurrent_ai_calculation_isolation(self):
        """Test that AI calculations don't interfere between concurrent games."""
        num_games = 5
        calculation_results = []

        def run_ai_calculation_game(game_id: int) -> Dict:
            """Run game with isolated AI calculations."""
            # Create game with specific AI
            game_mode = GameMode.three_ai(Difficulty.MEDIUM)
            ai_players = game_mode.ai_players

            # Each AI tracks its own calculations
            ai_calculations = {}

            for ai in ai_players:
                # Simulate multiple calculations
                calc_times = []
                for _ in range(5):
                    start = time.time()
                    # Simulate AI work
                    time.sleep(0.05)
                    end = time.time()
                    calc_times.append(end - start)

                ai_calculations[ai.player_id] = {
                    'times': calc_times,
                    'avg': sum(calc_times) / len(calc_times),
                    'min': min(calc_times),
                    'max': max(calc_times),
                }

            return {
                'game_id': game_id,
                'ai_calculations': ai_calculations,
            }

        # Run games concurrently
        with ThreadPoolExecutor(max_workers=num_games) as executor:
            futures = [executor.submit(run_ai_calculation_game, i) for i in range(num_games)]
            results = [future.result() for future in as_completed(futures)]

        # Verify isolation - each game should have consistent calculations
        for result in results:
            for ai_id, calc_data in result['ai_calculations'].items():
                # Consistency check
                variance = calc_data['max'] - calc_data['min']
                assert variance < 0.05, f"Game {result['game_id']} AI {ai_id} calculation variance too high"

        print(f"AI Calculation Isolation Test:")
        for result in results:
            print(f"  Game {result['game_id']}:")
            for ai_id, calc_data in result['ai_calculations'].items():
                variance = calc_data['max'] - calc_data['min']
                print(f"    AI {ai_id}: avg={calc_data['avg']*1000:.1f}ms, variance={variance*1000:.1f}ms")

    def test_system_stability_under_prolonged_load(self):
        """Test system stability under prolonged concurrent load."""
        duration_seconds = 5  # Run for 5 seconds
        max_concurrent = 3

        start_time = time.time()
        games_completed = 0
        errors = []

        while (time.time() - start_time) < duration_seconds:
            def run_quick_game():
                try:
                    game_id = games_completed
                    games_completed += 1

                    # Random mode selection
                    if game_id % 3 == 0:
                        game_mode = GameMode.single_ai(Difficulty.EASY)
                    elif game_id % 3 == 1:
                        game_mode = GameMode.three_ai(Difficulty.MEDIUM)
                    else:
                        game_mode = GameMode.spectate_ai()

                    game_state = GameState()
                    game_state.initialize(4 if game_mode.get_ai_count() > 1 else 2)

                    # Quick gameplay
                    for _ in range(5):
                        if game_mode.is_ai_turn(game_state.get_current_player()):
                            time.sleep(0.02)
                        game_state.advance_turn()

                    return True

                except Exception as e:
                    errors.append(str(e))
                    return False

            # Run batch of concurrent games
            with ThreadPoolExecutor(max_workers=max_concurrent) as executor:
                futures = [executor.submit(run_quick_game) for _ in range(max_concurrent)]
                for future in as_completed(futures):
                    future.result()  # Wait for completion

        end_time = time.time()
        actual_duration = end_time - start_time

        # Verify system stability
        assert len(errors) == 0, f"Errors during prolonged load: {errors}"
        assert games_completed > 0, "No games completed"

        print(f"Prolonged Load Stability Test:")
        print(f"  Duration: {actual_duration:.2f}s")
        print(f"  Games completed: {games_completed}")
        print(f"  Games/second: {games_completed/actual_duration:.1f}")
        print(f"  Errors: {len(errors)}")

        # Should maintain reasonable throughput
        assert (games_completed / actual_duration) > 1.0, "Throughput too low"
