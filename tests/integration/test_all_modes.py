"""
End-to-end integration tests for all AI Battle modes.

This module provides comprehensive testing across Single AI, Three AI,
and Spectate modes, ensuring all game modes work correctly together
and can be seamlessly switched between during gameplay.
"""

import time

import pytest

from blokus_game.models.ai_config import Difficulty
from blokus_game.models.ai_player import AIPlayer
from blokus_game.models.game_mode import GameMode, GameModeType
from blokus_game.models.game_state import GameState
from blokus_game.models.player import Player
from blokus_game.services.ai_strategy import (
    CornerStrategy,
    RandomStrategy,
    StrategicStrategy,
)


class TestAllGameModes:
    """Comprehensive test suite for all AI Battle game modes."""

    def test_all_modes_initialization(self):
        """Test that all game modes can be initialized correctly."""
        # Single AI mode
        single_ai = GameMode.single_ai(Difficulty.EASY)
        assert single_ai.mode_type == GameModeType.SINGLE_AI
        assert single_ai.get_player_count() == 2
        assert single_ai.get_ai_count() == 1

        # Three AI mode
        three_ai = GameMode.three_ai(Difficulty.MEDIUM)
        assert three_ai.mode_type == GameModeType.THREE_AI
        assert three_ai.get_player_count() == 4
        assert three_ai.get_ai_count() == 3

        # Spectate mode
        spectate = GameMode.spectate_ai()
        assert spectate.mode_type == GameModeType.SPECTATE
        assert spectate.get_player_count() == 4
        assert spectate.get_ai_count() == 4

    def test_mode_switching_simulation(self):
        """Test switching between different game modes during a session."""
        # Start with Single AI
        mode1 = GameMode.single_ai(Difficulty.EASY)
        assert mode1.mode_type == GameModeType.SINGLE_AI
        assert mode1.human_player_position == 1

        # Switch to Three AI
        mode2 = GameMode.three_ai(Difficulty.HARD)
        assert mode2.mode_type == GameModeType.THREE_AI
        assert mode2.human_player_position == 1

        # Switch to Spectate
        mode3 = GameMode.spectate_ai()
        assert mode3.mode_type == GameModeType.SPECTATE
        assert mode3.human_player_position is None

        # Verify player configurations remain independent
        assert mode1.get_ai_count() == 1
        assert mode2.get_ai_count() == 3
        assert mode3.get_ai_count() == 4

    def test_all_difficulties_work_across_modes(self):
        """Test that all difficulty levels work in all applicable modes."""
        difficulties = [Difficulty.EASY, Difficulty.MEDIUM, Difficulty.HARD]

        for difficulty in difficulties:
            # Single AI
            single = GameMode.single_ai(difficulty)
            assert single.ai_players[0].difficulty == difficulty

            # Three AI (all AIs use same difficulty)
            three = GameMode.three_ai(difficulty)
            for ai in three.ai_players:
                assert ai.difficulty == difficulty

    def test_turn_progression_all_modes(self):
        """Test turn progression works correctly in all modes."""
        # Single AI: Player 1 -> Player 3 -> Player 1
        single = GameMode.single_ai(Difficulty.MEDIUM)
        assert single.get_next_player(1) == 3
        assert single.get_next_player(3) == 1

        # Three AI: Player 1 -> Player 2 -> Player 3 -> Player 4 -> Player 1
        three = GameMode.three_ai(Difficulty.MEDIUM)
        assert three.get_next_player(1) == 2
        assert three.get_next_player(2) == 3
        assert three.get_next_player(3) == 4
        assert three.get_next_player(4) == 1

        # Spectate: Player 1 -> Player 2 -> Player 3 -> Player 4 -> Player 1
        spectate = GameMode.spectate_ai()
        assert spectate.get_next_player(1) == 2
        assert spectate.get_next_player(2) == 3
        assert spectate.get_next_player(3) == 4
        assert spectate.get_next_player(4) == 1

    def test_ai_player_independence_all_modes(self):
        """Test that AI players in all modes make independent decisions."""
        # Create AI players with different strategies
        ai1 = AIPlayer(1, RandomStrategy(), "#FF0000", "Random AI")
        ai2 = AIPlayer(2, CornerStrategy(), "#00FF00", "Corner AI")
        ai3 = AIPlayer(3, StrategicStrategy(), "#0000FF", "Strategic AI")

        # Verify each AI has different strategy type
        assert isinstance(ai1.strategy, RandomStrategy)
        assert isinstance(ai2.strategy, CornerStrategy)
        assert isinstance(ai3.strategy, StrategicStrategy)

        # Verify they have different difficulty names
        assert ai1.difficulty == "Easy"
        assert ai2.difficulty == "Medium"
        assert ai3.difficulty == "Hard"

    def test_game_state_isolation_between_modes(self):
        """Test that game states don't interfere between different modes."""
        # Create separate game states for each mode
        state1 = GameState()
        # Add players for Single AI (Player 1 human, Player 3 AI)
        human1 = Player(1, "Human")
        state1.add_player(human1)
        ai1 = AIPlayer(3, RandomStrategy(), "#FF0000", "AI")
        state1.add_player(ai1)
        state1.start_game()

        state2 = GameState()
        # Add players for Three AI (Player 1 human, Players 2,3,4 AI)
        human2 = Player(1, "Human")
        state2.add_player(human2)
        for pos in [2, 3, 4]:
            ai2 = AIPlayer(pos, RandomStrategy(), f"#{pos:02x}0000", f"AI {pos}")
            state2.add_player(ai2)
        state2.start_game()

        state3 = GameState()
        # Add players for Spectate (All 4 AI)
        for pos in [1, 2, 3, 4]:
            ai3 = AIPlayer(pos, RandomStrategy(), f"#{pos:02x}0000", f"AI {pos}")
            state3.add_player(ai3)
        state3.start_game()

        # Verify initial states are independent
        assert state1.get_current_player().player_id == 1
        assert state2.get_current_player().player_id == 1
        assert state3.get_current_player().player_id == 1

        # Modify state1
        state1.next_turn()
        assert state1.get_current_player().player_id == 3

        # Verify state2 and state3 remain unchanged
        assert state2.get_current_player().player_id == 1
        assert state3.get_current_player().player_id == 1

    def test_complete_single_ai_game_flow(self):
        """Test a complete game flow in Single AI mode (abbreviated)."""
        game_mode = GameMode.single_ai(Difficulty.EASY)
        game_state = GameState()

        # Add players for Single AI (Player 1 human, Player 3 AI)
        human = Player(1, "Human")
        game_state.add_player(human)
        ai = AIPlayer(3, RandomStrategy(), "#FF0000", "AI")
        game_state.add_player(ai)
        game_state.start_game()

        # Simulate a few turns
        turns_to_simulate = 5

        for turn in range(turns_to_simulate):
            current_player = game_state.get_current_player()

            if game_mode.is_ai_turn(current_player.player_id):
                # Simulate AI move
                assert current_player.player_id in [2, 3, 4]  # AI players are 2, 3, 4
                # In Single AI, only player 3 is active
                if game_mode.mode_type == GameModeType.SINGLE_AI:
                    assert current_player.player_id == 3
            else:
                # Human player turn
                assert current_player.player_id == 1

            game_state.next_turn()

        # Verify game progressed
        assert game_state.get_round_number() >= 1

    def test_complete_three_ai_game_flow(self):
        """Test a complete game flow in Three AI mode (abbreviated)."""
        game_mode = GameMode.three_ai(Difficulty.MEDIUM)
        game_state = GameState()

        # Add players for Three AI (Player 1 human, Players 2,3,4 AI)
        human = Player(1, "Human")
        game_state.add_player(human)
        for pos in [2, 3, 4]:
            ai = AIPlayer(pos, RandomStrategy(), f"#{pos:02x}0000", f"AI {pos}")
            game_state.add_player(ai)
        game_state.start_game()

        # Simulate a few turns cycling through all players
        turns_to_simulate = 8

        for turn in range(turns_to_simulate):
            current_player = game_state.get_current_player()

            # In Three AI mode, players 1 (human), 2, 3, 4 (AI) are all active
            assert current_player.player_id in [1, 2, 3, 4]

            if current_player.player_id == 1:
                assert not game_mode.is_ai_turn(current_player.player_id)
            else:
                assert game_mode.is_ai_turn(current_player.player_id)

            game_state.next_turn()

        # Verify all players got turns
        assert game_state.get_round_number() >= 1

    def test_spectate_mode_fully_autonomous(self):
        """Test that Spectate mode runs without human input."""
        game_mode = GameMode.spectate_ai()
        game_state = GameState()

        # Add players for Spectate (All 4 AI)
        for pos in [1, 2, 3, 4]:
            ai = AIPlayer(pos, RandomStrategy(), f"#{pos:02x}0000", f"AI {pos}")
            game_state.add_player(ai)
        game_state.start_game()

        # In spectate mode, all players should be AI
        for player_id in [1, 2, 3, 4]:
            assert game_mode.is_ai_turn(player_id) is True

        # Simulate autonomous turns
        turns_to_simulate = 12

        for turn in range(turns_to_simulate):
            current_player = game_state.get_current_player()

            # All turns should be AI-controlled
            assert game_mode.is_ai_turn(current_player.player_id) is True

            game_state.next_turn()

        # Verify autonomous progression
        assert game_state.get_round_number() >= 1

    def test_difficulty_persistence_across_modes(self):
        """Test that difficulty settings persist when switching modes."""
        # Set difficulty preference
        preferred_difficulty = Difficulty.HARD

        # Use in Single AI
        single = GameMode.single_ai(preferred_difficulty)
        assert single.ai_players[0].difficulty == Difficulty.HARD

        # Use in Three AI
        three = GameMode.three_ai(preferred_difficulty)
        for ai in three.ai_players:
            assert ai.difficulty == Difficulty.HARD

        # Change preference
        preferred_difficulty = Difficulty.EASY

        # Use in Single AI with new preference
        single2 = GameMode.single_ai(preferred_difficulty)
        assert single2.ai_players[0].difficulty == Difficulty.EASY

        # Previous mode should remain unchanged
        single_unchanged = GameMode.single_ai(Difficulty.HARD)
        assert single_unchanged.ai_players[0].difficulty == Difficulty.HARD

    def test_concurrent_mode_safety(self):
        """Test that multiple modes can coexist without conflicts."""
        modes = [
            GameMode.single_ai(Difficulty.EASY),
            GameMode.three_ai(Difficulty.MEDIUM),
            GameMode.spectate_ai(),
        ]

        # Each mode should have independent state
        for i, mode in enumerate(modes):
            assert mode is not None
            if i == 0:
                assert mode.mode_type == GameModeType.SINGLE_AI
            elif i == 1:
                assert mode.mode_type == GameModeType.THREE_AI
            else:
                assert mode.mode_type == GameModeType.SPECTATE

        # Verify no cross-contamination
        assert modes[0].get_ai_count() == 1
        assert modes[1].get_ai_count() == 3
        assert modes[2].get_ai_count() == 4

    def test_all_modes_validate_correctly(self):
        """Test that all game modes pass validation."""
        modes = [
            GameMode.single_ai(Difficulty.EASY),
            GameMode.single_ai(Difficulty.MEDIUM),
            GameMode.single_ai(Difficulty.HARD),
            GameMode.three_ai(Difficulty.EASY),
            GameMode.three_ai(Difficulty.MEDIUM),
            GameMode.three_ai(Difficulty.HARD),
            GameMode.spectate_ai(),
        ]

        for mode in modes:
            assert mode.validate() is True

    def test_player_configuration_all_modes(self):
        """Test player configuration is correct for all modes."""
        # Single AI: Human + 1 AI
        single = GameMode.single_ai(Difficulty.MEDIUM)
        human_positions = [single.human_player_position] if single.human_player_position else []
        ai_positions = [config.position for config in single.ai_players]

        assert human_positions == [1]
        assert ai_positions == [3]

        # Three AI: Human + 3 AI
        three = GameMode.three_ai(Difficulty.MEDIUM)
        human_positions = [three.human_player_position] if three.human_player_position else []
        ai_positions = [config.position for config in three.ai_players]

        assert human_positions == [1]
        assert set(ai_positions) == {2, 3, 4}

        # Spectate: 4 AI, no human
        spectate = GameMode.spectate_ai()
        human_positions = [spectate.human_player_position] if spectate.human_player_position else []
        ai_positions = [config.position for config in spectate.ai_players]

        assert human_positions == []
        assert set(ai_positions) == {1, 2, 3, 4}

    def test_ai_strategy_isolation(self):
        """Test that AI strategies don't interfere between modes."""
        # Create modes with specific strategies
        single_random = GameMode.single_ai(Difficulty.EASY)
        single_strategic = GameMode.single_ai(Difficulty.HARD)

        # Get AI configurations
        ai1_config = single_random.ai_players[0]
        ai2_config = single_strategic.ai_players[0]

        # Verify different difficulties
        assert ai1_config.difficulty != ai2_config.difficulty
        assert ai1_config.difficulty == Difficulty.EASY
        assert ai2_config.difficulty == Difficulty.HARD

        # Verify isolation - configurations are independent
        # Create actual AI players to test isolation
        from blokus_game.services.ai_strategy import RandomStrategy, StrategicStrategy

        ai1_player = ai1_config.create_player(RandomStrategy())
        ai2_player = ai2_config.create_player(StrategicStrategy())

        # Players should have different strategies
        assert ai1_player.difficulty != ai2_player.difficulty

    def test_mode_creation_performance(self):
        """Test that mode creation is efficient."""
        # Measure creation time for each mode
        start = time.time()
        for _ in range(100):
            GameMode.single_ai(Difficulty.EASY)
        single_time = time.time() - start

        start = time.time()
        for _ in range(100):
            GameMode.three_ai(Difficulty.MEDIUM)
        three_time = time.time() - start

        start = time.time()
        for _ in range(100):
            GameMode.spectate_ai()
        spectate_time = time.time() - start

        # All modes should be creatable within reasonable time
        assert single_time < 1.0  # Less than 1 second for 100 creations
        assert three_time < 1.0
        assert spectate_time < 1.0

    def test_error_handling_across_modes(self):
        """Test error handling works consistently across modes."""
        # Test invalid difficulty
        with pytest.raises(ValueError):
            GameMode.single_ai("Invalid")

        with pytest.raises(ValueError):
            GameMode.three_ai("Invalid")

        # Test mode-specific validation
        single = GameMode.single_ai(Difficulty.EASY)
        assert single.validate() is True

        three = GameMode.three_ai(Difficulty.EASY)
        assert three.validate() is True

        spectate = GameMode.spectate_ai()
        assert spectate.validate() is True
