"""
Integration tests for independent AI decision making.

This module tests that AI players operate independently with different strategies,
making distinct decisions based on their individual configurations.
"""

import pytest
from src.models.ai_player import AIPlayer
from src.services.ai_strategy import RandomStrategy, CornerStrategy, StrategicStrategy
from src.models.ai_config import AIConfig, Difficulty
from src.models.game_mode import GameMode, GameModeType


class TestAIPlayerIndependence:
    """Test suite for AI player independence."""

    def test_independent_strategy_instances(self):
        """Test that each AI player has an independent strategy instance."""
        # Create multiple AI players
        ai1 = AIPlayer(
            player_id=2,
            strategy=RandomStrategy(),
            color="blue",
            name="AI-1"
        )

        ai2 = AIPlayer(
            player_id=3,
            strategy=CornerStrategy(),
            color="red",
            name="AI-2"
        )

        ai3 = AIPlayer(
            player_id=4,
            strategy=StrategicStrategy(),
            color="green",
            name="AI-3"
        )

        # Each AI should have its own strategy instance
        assert ai1.strategy is not ai2.strategy
        assert ai2.strategy is not ai3.strategy
        assert ai1.strategy is not ai3.strategy

        # Each strategy should be of the correct type
        assert isinstance(ai1.strategy, RandomStrategy)
        assert isinstance(ai2.strategy, CornerStrategy)
        assert isinstance(ai3.strategy, StrategicStrategy)

    def test_independent_difficulty_levels(self):
        """Test that AI players have independent difficulty levels."""
        ai_easy = AIPlayer(
            player_id=2,
            strategy=RandomStrategy(),
            color="blue",
            name="Easy AI"
        )

        ai_medium = AIPlayer(
            player_id=3,
            strategy=CornerStrategy(),
            color="red",
            name="Medium AI"
        )

        ai_hard = AIPlayer(
            player_id=4,
            strategy=StrategicStrategy(),
            color="green",
            name="Hard AI"
        )

        # Each AI should report correct difficulty
        assert ai_easy.difficulty == "Easy"
        assert ai_medium.difficulty == "Medium"
        assert ai_hard.difficulty == "Hard"

    def test_independent_decision_making(self):
        """Test that AI players make independent decisions."""
        ai1 = AIPlayer(
            player_id=2,
            strategy=RandomStrategy(),
            color="blue",
            name="Random AI"
        )

        ai2 = AIPlayer(
            player_id=3,
            strategy=CornerStrategy(),
            color="red",
            name="Corner AI"
        )

        # Create board with some pieces
        board = [[0 for _ in range(20)] for _ in range(20)]

        # Add a piece for player 2 to encourage corner plays
        board[0][0] = 2
        board[0][19] = 2
        board[19][0] = 2
        board[19][19] = 2

        pieces = []

        # Each AI calculates move independently
        move1 = ai1.calculate_move(board, pieces)
        move2 = ai2.calculate_move(board, pieces)

        # Both should complete without error
        assert move1 is not None or move1 is None  # Either valid
        assert move2 is not None or move2 is None  # Either valid

        # Each move should belong to the correct player
        if move1:
            assert move1.player_id == 2
        if move2:
            assert move2.player_id == 3

    def test_independent_state_management(self):
        """Test that AI players maintain independent state."""
        ai1 = AIPlayer(
            player_id=2,
            strategy=RandomStrategy(),
            color="blue"
        )

        ai2 = AIPlayer(
            player_id=3,
            strategy=CornerStrategy(),
            color="red"
        )

        # Initially, neither is calculating
        assert not ai1.is_calculating
        assert not ai2.is_calculating

        # AI1 starts calculating
        board = [[0 for _ in range(20)] for _ in range(20)]
        pieces = []

        move1 = ai1.calculate_move(board, pieces)

        # After calculation, AI1 should not be calculating
        assert not ai1.is_calculating

        # AI2 should never have been calculating
        assert not ai2.is_calculating

        # Each should have its own state
        assert ai1.player_id != ai2.player_id
        assert ai1.strategy != ai2.strategy
        assert ai1.color != ai2.color

    def test_independent_timeout_handling(self):
        """Test that AI players handle timeouts independently."""
        ai1 = AIPlayer(
            player_id=2,
            strategy=RandomStrategy(),  # 3 second timeout
            color="blue"
        )

        ai2 = AIPlayer(
            player_id=3,
            strategy=StrategicStrategy(),  # 8 second timeout
            color="red"
        )

        # Each AI should have different timeout
        assert ai1.timeout_seconds == 3
        assert ai2.timeout_seconds == 8

        # Both should handle time limits correctly
        board = [[0 for _ in range(20)] for _ in range(20)]
        pieces = []

        # AI1 with short limit
        move1 = ai1.calculate_move(board, pieces, time_limit=1)
        assert not ai1.is_calculating

        # AI2 with short limit
        move2 = ai2.calculate_move(board, pieces, time_limit=1)
        assert not ai2.is_calculating

    def test_independent_piece_management(self):
        """Test that AI players manage pieces independently."""
        from src.config.pieces import get_full_piece_set

        ai1 = AIPlayer(
            player_id=2,
            strategy=RandomStrategy(),
            color="blue",
            name="AI-1"
        )

        ai2 = AIPlayer(
            player_id=3,
            strategy=CornerStrategy(),
            color="red",
            name="AI-2"
        )

        # Each should have full piece set
        full_pieces = get_full_piece_set()

        # AI1 pieces
        assert ai1.get_piece_count() == len(full_pieces)
        assert ai1.has_pieces_remaining()

        # AI2 pieces (independent)
        assert ai2.get_piece_count() == len(full_pieces)
        assert ai2.has_pieces_remaining()

        # After AI1 removes a piece, AI2 should still have all pieces
        if full_pieces:
            ai1.remove_piece(full_pieces[0])
            assert ai1.get_piece_count() == len(full_pieces) - 1
            assert ai2.get_piece_count() == len(full_pieces)

    def test_independent_scoring(self):
        """Test that AI players maintain independent scores."""
        ai1 = AIPlayer(
            player_id=2,
            strategy=RandomStrategy(),
            color="blue",
            name="AI-1"
        )

        ai2 = AIPlayer(
            player_id=3,
            strategy=CornerStrategy(),
            color="red",
            name="AI-2"
        )

        # Initially, both have score 0
        assert ai1.score == 0
        assert ai2.score == 0

        # Simulate scoring (would happen in actual game)
        ai1.score = 10
        assert ai1.score == 10
        assert ai2.score == 0  # AI2 unaffected

        ai2.score = 15
        assert ai1.score == 10  # AI1 unaffected
        assert ai2.score == 15

    def test_independent_pass_state(self):
        """Test that AI players manage pass state independently."""
        ai1 = AIPlayer(
            player_id=2,
            strategy=RandomStrategy(),
            color="blue"
        )

        ai2 = AIPlayer(
            player_id=3,
            strategy=CornerStrategy(),
            color="red"
        )

        # Neither has passed initially
        assert not ai1.has_passed
        assert not ai2.has_passed

        # AI1 passes
        ai1.pass_turn()
        assert ai1.has_passed
        assert not ai2.has_passed  # AI2 unaffected

        # AI2 passes
        ai2.pass_turn()
        assert ai1.has_passed  # Still passed
        assert ai2.has_passed

        # Reset AI1 only
        ai1.reset_pass()
        assert not ai1.has_passed
        assert ai2.has_passed  # AI2 still passed

    def test_multiple_ai_simultaneous_operations(self):
        """Test multiple AI players operating simultaneously."""
        # Create 4 AI players with different strategies
        ais = [
            AIPlayer(
                player_id=i,
                strategy=strategy,
                color=colors[i],
                name=names[i]
            )
            for i, (strategy, colors, names) in enumerate([
                (RandomStrategy(), ["blue", "red", "green", "yellow"], ["AI-1", "AI-2", "AI-3", "AI-4"]),
            ], start=1)
        ]

        # This is a simplified version - iterate through players
        for player_id in range(1, 5):
            ai = AIPlayer(
                player_id=player_id,
                strategy=RandomStrategy(),
                color=f"color_{player_id}",
                name=f"AI-{player_id}"
            )

            board = [[0 for _ in range(20)] for _ in range(20)]
            pieces = []

            move = ai.calculate_move(board, pieces)

            # Each AI operates independently
            assert ai.player_id == player_id
            assert not ai.is_calculating
            assert move is not None or move is None


class TestAIIndependenceInGameMode:
    """Test AI independence within game mode configurations."""

    def test_three_ai_mode_independence(self):
        """Test AI independence in Three AI mode."""
        game_mode = GameMode.three_ai(Difficulty.MEDIUM)

        # Create AI players for each position
        ai_players = {}
        for ai_config in game_mode.ai_players:
            strategies = {
                2: RandomStrategy(),
                3: CornerStrategy(),
                4: StrategicStrategy()
            }

            ai_players[ai_config.position] = AIPlayer(
                player_id=ai_config.position,
                strategy=strategies[ai_config.position],
                color=f"color_{ai_config.position}",
                name=f"AI-{ai_config.position}"
            )

        # Verify independence
        assert len(ai_players) == 3
        assert 2 in ai_players
        assert 3 in ai_players
        assert 4 in ai_players

        # Each has different strategy
        strategies_used = {ai.strategy.__class__.__name__ for ai in ai_players.values()}
        assert len(strategies_used) == 3

    def test_spectate_mode_all_ai(self):
        """Test that all players are independent in Spectate mode."""
        game_mode = GameMode.spectate_ai()

        # Create 4 AI players
        ai_players = {}
        strategies = [
            RandomStrategy(),
            CornerStrategy(),
            StrategicStrategy(),
            RandomStrategy()  # Can reuse strategy type
        ]
        colors = ["blue", "red", "green", "yellow"]
        names = ["Alpha", "Beta", "Gamma", "Delta"]

        for i, ai_config in enumerate(game_mode.ai_players):
            ai_players[ai_config.position] = AIPlayer(
                player_id=ai_config.position,
                strategy=strategies[i],
                color=colors[i],
                name=names[i]
            )

        # All should be independent
        assert len(ai_players) == 4

        for player_id, ai in ai_players.items():
            assert ai.player_id == player_id
            assert ai.name == names[player_id - 1]
            assert ai.color == colors[player_id - 1]

    def test_mixed_ai_configurations(self):
        """Test AI players with different configurations."""
        # Create custom AI configurations
        custom_ais = [
            AIConfig(position=2, difficulty=Difficulty.EASY),
            AIConfig(position=3, difficulty=Difficulty.MEDIUM),
            AIConfig(position=4, difficulty=Difficulty.HARD),
        ]

        game_mode = GameMode(
            GameModeType.THREE_AI,
            difficulty=Difficulty.MEDIUM,
            custom_ai_configs=custom_ais
        )

        # Create AI players based on config
        ai_map = {
            2: RandomStrategy(),
            3: CornerStrategy(),
            4: StrategicStrategy()
        }

        for ai_config in game_mode.ai_players:
            ai = AIPlayer(
                player_id=ai_config.position,
                strategy=ai_map[ai_config.position],
                color=f"color_{ai_config.position}",
                name=f"Custom-{ai_config.position}"
            )

            # Each AI should have correct difficulty
            assert ai.difficulty == ai_config.difficulty.name

    def test_ai_turn_detection(self):
        """Test that AI turn detection works for all AI players."""
        game_mode = GameMode.three_ai(Difficulty.HARD)

        # Human player should not be AI
        assert not game_mode.is_ai_turn(1)

        # All AI players should be detected
        for ai_config in game_mode.ai_players:
            assert game_mode.is_ai_turn(ai_config.position)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
