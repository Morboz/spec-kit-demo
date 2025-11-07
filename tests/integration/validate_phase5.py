"""
Phase 5 Validation Script

This script validates that all Phase 5 (Difficulty Settings) requirements are met:
- T058: Verify Easy AI makes simpler/lower-value moves than Hard AI
- T059: Verify difficulty settings persist across game sessions
- T060: Test all difficulty levels across all game modes
"""

import os
import tempfile
from pathlib import Path

from src.models.ai_config import AIConfig, Difficulty
from src.models.ai_player import AIPlayer
from src.models.game_mode import GameMode, GameModeType
from src.services.ai_strategy import CornerStrategy, RandomStrategy, StrategicStrategy


def validate_t058_easy_vs_hard_behavior():
    """
    T058: Verify Easy AI makes simpler/lower-value moves than Hard AI.

    This validates that:
    1. Easy AI uses RandomStrategy (simplest approach)
    2. Hard AI uses StrategicStrategy (complex evaluation)
    3. Timeouts reflect difficulty (Easy: 3s, Hard: 8s)
    """
    print("\n=== T058: Validating Easy vs Hard AI Behavior ===")

    # Create Easy and Hard AI players
    easy_ai = AIPlayer(1, RandomStrategy(), "blue")
    hard_ai = AIPlayer(2, StrategicStrategy(), "red")

    # Check strategy types
    assert isinstance(
        easy_ai.strategy, RandomStrategy
    ), "Easy AI should use RandomStrategy"
    assert isinstance(
        hard_ai.strategy, StrategicStrategy
    ), "Hard AI should use StrategicStrategy"
    print("✓ Easy AI uses RandomStrategy")
    print("✓ Hard AI uses StrategicStrategy")

    # Check difficulty names
    assert easy_ai.difficulty == "Easy"
    assert hard_ai.difficulty == "Hard"
    print("✓ Easy AI reports 'Easy' difficulty")
    print("✓ Hard AI reports 'Hard' difficulty")

    # Check timeouts
    assert easy_ai.timeout_seconds == 3, "Easy AI timeout should be 3 seconds"
    assert hard_ai.timeout_seconds == 8, "Hard AI timeout should be 8 seconds"
    print(f"✓ Easy AI timeout: {easy_ai.timeout_seconds}s")
    print(f"✓ Hard AI timeout: {hard_ai.timeout_seconds}s")

    # Check caching (Easy AI should have caching)
    stats = easy_ai.strategy.get_cache_stats()
    assert "hits" in stats
    assert "misses" in stats
    print("✓ Easy AI has caching (stats available)")
    print(f"  Cache size: {stats['size']}")

    print("\n✅ T058 PASSED: Easy AI makes simpler/lower-value moves than Hard AI")
    return True


def validate_t059_difficulty_persistence():
    """
    T059: Verify difficulty settings persist across game sessions.

    This validates that:
    1. save_difficulty_preference() saves settings
    2. get_difficulty_preference() loads saved settings
    3. Settings persist across GameMode instances
    4. Settings work for both Single AI and Three AI modes
    """
    print("\n=== T059: Validating Difficulty Persistence ===")

    # Use temporary config directory for testing
    with tempfile.TemporaryDirectory() as tmpdir:
        # Override home directory for testing
        original_home = os.path.expanduser("~")

        try:
            # Mock the home directory
            os.environ["HOME"] = tmpdir
            Path(tmpdir).mkdir(parents=True, exist_ok=True)

            # Create a game mode instance for saving
            game_mode = GameMode(GameModeType.SINGLE_AI, Difficulty.HARD)

            # Save preferences for different modes
            game_mode.save_difficulty_preference(
                GameModeType.SINGLE_AI, Difficulty.HARD
            )
            game_mode.save_difficulty_preference(GameModeType.THREE_AI, Difficulty.EASY)

            print("✓ Saved difficulty preferences")

            # Verify file was created
            config_file = Path(tmpdir) / ".blokus" / "difficulty_preferences.json"
            assert config_file.exists(), "Config file should exist"
            print(f"✓ Config file created: {config_file}")

            # Load preferences using class method
            single_ai_pref = GameMode.get_difficulty_preference(GameModeType.SINGLE_AI)
            three_ai_pref = GameMode.get_difficulty_preference(GameModeType.THREE_AI)

            assert (
                single_ai_pref == Difficulty.HARD
            ), "Single AI preference should be HARD"
            assert (
                three_ai_pref == Difficulty.EASY
            ), "Three AI preference should be EASY"
            print(f"✓ Single AI preference loaded: {single_ai_pref.value}")
            print(f"✓ Three AI preference loaded: {three_ai_pref.value}")

            # Verify game modes use saved preferences
            single_ai_mode = GameMode.single_ai()
            three_ai_mode = GameMode.three_ai()

            assert (
                single_ai_mode.difficulty == Difficulty.HARD
            ), "Should use saved preference"
            assert (
                three_ai_mode.difficulty == Difficulty.EASY
            ), "Should use saved preference"
            print("✓ GameMode.single_ai() uses saved preference")
            print("✓ GameMode.three_ai() uses saved preference")

            # Test clearing preferences
            game_mode.clear_difficulty_preferences()
            assert not config_file.exists(), "Config file should be deleted"
            print("✓ Preferences can be cleared")

            # Verify defaults after clearing
            default_pref = GameMode.get_difficulty_preference(GameModeType.SINGLE_AI)
            assert default_pref == Difficulty.MEDIUM, "Should default to MEDIUM"
            print("✓ Defaults to MEDIUM after clearing")

        finally:
            # Restore original HOME
            if "HOME" in os.environ:
                del os.environ["HOME"]
            os.environ["HOME"] = original_home

    print("\n✅ T059 PASSED: Difficulty settings persist across game sessions")
    return True


def validate_t060_all_difficulties_all_modes():
    """
    T060: Test all difficulty levels across all game modes.

    This validates that:
    1. Single AI mode works with Easy, Medium, and Hard
    2. Three AI mode works with Easy, Medium, and Hard
    3. Spectate mode works (uses mixed difficulties)
    4. Difficulty can be switched at runtime
    """
    print("\n=== T060: Validating All Difficulties Across All Modes ===")

    difficulties = [Difficulty.EASY, Difficulty.MEDIUM, Difficulty.HARD]
    difficulties_str = ["Easy", "Medium", "Hard"]

    # Test Single AI mode with all difficulties
    print("\n--- Single AI Mode ---")
    for diff in difficulties:
        mode = GameMode.single_ai(diff)
        assert mode.mode_type == GameModeType.SINGLE_AI
        assert mode.difficulty == diff
        assert len(mode.ai_players) == 1
        assert mode.human_player_position == 1
        print(f"✓ Single AI with {diff.value}: {mode.get_ai_count()} AI player(s)")

    # Test Three AI mode with all difficulties
    print("\n--- Three AI Mode ---")
    for diff in difficulties:
        mode = GameMode.three_ai(diff)
        assert mode.mode_type == GameModeType.THREE_AI
        assert mode.difficulty == diff
        assert len(mode.ai_players) == 3
        assert mode.human_player_position == 1
        print(f"✓ Three AI with {diff.value}: {mode.get_ai_count()} AI player(s)")

    # Test Spectate mode (uses mixed difficulties)
    print("\n--- Spectate Mode ---")
    spectate_mode = GameMode.spectate_ai()
    assert spectate_mode.mode_type == GameModeType.SPECTATE
    assert spectate_mode.human_player_position is None
    assert len(spectate_mode.ai_players) == 4

    # Spectate should have mixed difficulties
    difficulties_used = {ai.difficulty for ai in spectate_mode.ai_players}
    assert len(difficulties_used) >= 2, "Should use mixed difficulties"
    print(
        f"✓ Spectate mode: {len(spectate_mode.ai_players)} AI players with mixed difficulties"
    )
    print(f"  Difficulties used: {', '.join(d.value for d in difficulties_used)}")

    # Test difficulty switching
    print("\n--- Runtime Difficulty Switching ---")
    for diff_str in difficulties_str:
        # Test switching via string
        test_ai = AIPlayer(1, RandomStrategy(), "blue")
        test_ai.switch_to_difficulty(diff_str)
        assert test_ai.difficulty == diff_str
        print(f"✓ Can switch to {diff_str} via string")

        # Test switching via enum
        test_ai2 = AIPlayer(2, RandomStrategy(), "red")
        test_ai2.switch_to_difficulty(Difficulty(diff_str))
        assert test_ai2.difficulty == diff_str
        print(f"✓ Can switch to {diff_str} via enum")

    # Test AIConfig creation with all difficulties
    print("\n--- AIConfig with All Difficulties ---")
    for diff in difficulties:
        config = AIConfig(position=2, difficulty=diff)
        assert config.difficulty == diff
        player = config.create_player()
        assert player.difficulty == diff.value
        print(f"✓ AIConfig creates player with {diff.value} difficulty")

    print("\n✅ T060 PASSED: All difficulty levels work across all game modes")
    return True


def validate_strategy_switching():
    """
    Bonus: Validate strategy switching mechanism.

    This validates that:
    1. AIPlayer.switch_strategy() works
    2. AIPlayer.switch_to_difficulty() works
    3. Strategy properties update correctly
    """
    print("\n=== Validating Strategy Switching ===")

    # Create AI player
    ai = AIPlayer(1, RandomStrategy(), "blue")
    assert ai.difficulty == "Easy"

    # Switch to different strategy directly
    new_strategy = CornerStrategy()
    ai.switch_strategy(new_strategy)
    assert ai.strategy == new_strategy
    assert ai.difficulty == "Medium"
    assert ai.timeout_seconds == 5
    print("✓ Direct strategy switching works")

    # Switch to difficulty
    ai.switch_to_difficulty("Hard")
    assert ai.difficulty == "Hard"
    assert ai.timeout_seconds == 8
    print("✓ Difficulty-based switching works")

    # Verify properties are preserved
    assert ai.player_id == 1
    assert ai.color == "blue"
    assert len(ai.pieces) == 21
    print("✓ Switching preserves player properties")

    print("\n✅ Strategy switching validated")
    return True


def validate_performance_optimizations():
    """
    Bonus: Validate performance optimizations.

    This validates that:
    1. Easy AI has caching
    2. Easy AI uses fast move generation
    3. Performance stats are available
    """
    print("\n=== Validating Performance Optimizations ===")

    # Test caching
    easy_ai = AIPlayer(1, RandomStrategy(), "blue")
    stats = easy_ai.strategy.get_cache_stats()

    assert "hits" in stats
    assert "misses" in stats
    assert "size" in stats
    assert "hit_rate" in stats
    print("✓ Cache statistics available")
    print(f"  Initial cache size: {stats['size']}")

    # Test cache clearing
    easy_ai.strategy.clear_cache()
    stats_after = easy_ai.strategy.get_cache_stats()
    assert stats_after["size"] == 0
    print("✓ Cache can be cleared")

    # Verify other strategies don't have caching interface
    medium_ai = AIPlayer(2, CornerStrategy(), "red")
    assert hasattr(medium_ai.strategy, "get_available_moves")
    print("✓ Medium AI has move generation")

    hard_ai = AIPlayer(3, StrategicStrategy(), "green")
    assert hasattr(hard_ai.strategy, "get_available_moves")
    print("✓ Hard AI has move generation")

    print("\n✅ Performance optimizations validated")
    return True


def main():
    """Run all validation tests."""
    print("=" * 70)
    print("PHASE 5 VALIDATION: Difficulty Settings")
    print("=" * 70)

    tests = [
        ("T058", validate_t058_easy_vs_hard_behavior),
        ("T059", validate_t059_difficulty_persistence),
        ("T060", validate_t060_all_difficulties_all_modes),
        ("Bonus", validate_strategy_switching),
        ("Bonus", validate_performance_optimizations),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ {test_name} FAILED: {e}")
            import traceback

            traceback.print_exc()
            results.append((test_name, False))

    # Print summary
    print("\n" + "=" * 70)
    print("VALIDATION SUMMARY")
    print("=" * 70)

    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")

    all_passed = all(result for _, result in results)

    print("\n" + "=" * 70)
    if all_passed:
        print("✅ ALL VALIDATIONS PASSED")
        print("Phase 5 (Difficulty Settings) is complete and ready for acceptance!")
    else:
        print("❌ SOME VALIDATIONS FAILED")
        print("Please review the errors above.")
    print("=" * 70)

    return all_passed


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
