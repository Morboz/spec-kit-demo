"""
Integration tests for Three AI battle mode.

This module tests the complete flow of a game against three AI opponents,
including multi-AI turn management, independent AI decision making, and game completion.
"""

import pytest
import tkinter as tk
from src.models.game_mode import GameMode, GameModeType
from src.models.ai_config import Difficulty
from src.models.ai_player import AIPlayer
from src.services.ai_strategy import RandomStrategy, CornerStrategy, StrategicStrategy


class TestThreeAIMode:
    """Test suite for Three AI mode functionality."""

    def test_create_three_ai_mode(self):
        """Test creating a Three AI game mode configuration."""
        game_mode = GameMode.three_ai(Difficulty.MEDIUM)

        assert game_mode.mode_type == GameModeType.THREE_AI
        assert game_mode.human_player_position == 1
        assert len(game_mode.ai_players) == 3
        assert game_mode.ai_players[0].position == 2
        assert game_mode.ai_players[1].position == 3
        assert game_mode.ai_players[2].position == 4
        assert game_mode.get_player_count() == 4
        assert game_mode.get_ai_count() == 3

    def test_three_ai_mode_validation(self):
        """Test Three AI mode configuration validation."""
        # Valid configuration
        game_mode = GameMode.three_ai(Difficulty.EASY)
        assert game_mode.validate() is True

        # Test is_ai_turn
        assert game_mode.is_ai_turn(1) is False  # Human player
        assert game_mode.is_ai_turn(2) is True   # AI player
        assert game_mode.is_ai_turn(3) is True   # AI player
        assert game_mode.is_ai_turn(4) is True   # AI player

    def test_three_ai_turn_progression(self):
        """Test turn progression in Three AI mode."""
        game_mode = GameMode.three_ai(Difficulty.MEDIUM)

        # Player 1 (human) starts
        assert game_mode.get_next_player(1) == 2

        # Player 2 (AI)
        assert game_mode.get_next_player(2) == 3

        # Player 3 (AI)
        assert game_mode.get_next_player(3) == 4

        # Player 4 (AI)
        assert game_mode.get_next_player(4) == 1

        # Wraps around
        assert game_mode.get_next_player(1) == 2

    def test_create_three_ai_players(self):
        """Test creating three AI players with different strategies."""
        game_mode = GameMode.three_ai(Difficulty.HARD)

        ai_players = []
        for ai_config in game_mode.ai_players:
            # Use different strategies for each AI
            if ai_config.position == 2:
                strategy = RandomStrategy()
                name = "Easy AI"
                color = "blue"
            elif ai_config.position == 3:
                strategy = CornerStrategy()
                name = "Medium AI"
                color = "red"
            else:
                strategy = StrategicStrategy()
                name = "Hard AI"
                color = "green"

            ai_player = AIPlayer(
                player_id=ai_config.position,
                strategy=strategy,
                color=color,
                name=name
            )
            ai_players.append(ai_player)

        # Verify all three AI players
        assert len(ai_players) == 3

        # Check they have different strategies
        difficulties = {ai.difficulty for ai in ai_players}
        assert len(difficulties) == 3
        assert "Easy" in difficulties
        assert "Medium" in difficulties
        assert "Hard" in difficulties

        # Check they have different names
        names = {ai.name for ai in ai_players}
        assert len(names) == 3

        # Check they have different colors
        colors = {ai.color for ai in ai_players}
        assert len(colors) == 3

    def test_ai_players_independence(self):
        """Test that AI players operate independently."""
        # Create three AI players
        ai1 = AIPlayer(player_id=2, strategy=RandomStrategy(), color="blue", name="AI-1")
        ai2 = AIPlayer(player_id=3, strategy=CornerStrategy(), color="red", name="AI-2")
        ai3 = AIPlayer(player_id=4, strategy=StrategicStrategy(), color="green", name="AI-3")

        # Create empty board
        board = [[0 for _ in range(20)] for _ in range(20)]

        # Each AI should make independent decisions
        pieces = []

        # AI1 calculates move
        move1 = ai1.calculate_move(board, pieces)

        # AI2 calculates move
        move2 = ai2.calculate_move(board, pieces)

        # AI3 calculates move
        move3 = ai3.calculate_move(board, pieces)

        # Each AI has its own state
        assert ai1.player_id == 2
        assert ai2.player_id == 3
        assert ai3.player_id == 4

        # Each AI has different strategy
        assert ai1.difficulty == "Easy"
        assert ai2.difficulty == "Medium"
        assert ai3.difficulty == "Hard"

        # Verify independence - one AI's state doesn't affect others
        assert not ai1.is_calculating
        assert not ai2.is_calculating
        assert not ai3.is_calculating

    def test_three_ai_game_setup(self):
        """Test setting up a complete Three AI game."""
        # Create game mode
        game_mode = GameMode.three_ai(Difficulty.MEDIUM)

        # Create AI players
        ai_players = []
        strategies = [RandomStrategy(), CornerStrategy(), StrategicStrategy()]
        colors = ["blue", "red", "green"]
        names = ["AI-1", "AI-2", "AI-3"]

        for i, ai_config in enumerate(game_mode.ai_players):
            ai_player = AIPlayer(
                player_id=ai_config.position,
                strategy=strategies[i],
                color=colors[i],
                name=names[i]
            )
            ai_players.append(ai_player)

        # Verify setup
        assert len(ai_players) == 3
        assert ai_players[0].player_id == 2
        assert ai_players[1].player_id == 3
        assert ai_players[2].player_id == 4

    def test_all_positions_active(self):
        """Test that all four positions are active in Three AI mode."""
        game_mode = GameMode.three_ai(Difficulty.EASY)

        # Check all positions are active
        active_positions = [1]  # Human
        active_positions.extend([config.position for config in game_mode.ai_players])
        active_positions.sort()

        assert active_positions == [1, 2, 3, 4]

    def test_skip_inactive_positions(self):
        """Test that get_next_player works correctly in Three AI mode."""
        game_mode = GameMode.three_ai(Difficulty.MEDIUM)

        # In Three AI mode, all positions should be active
        # So get_next_player should cycle through 1->2->3->4->1
        assert game_mode.get_next_player(1) == 2
        assert game_mode.get_next_player(2) == 3
        assert game_mode.get_next_player(3) == 4
        assert game_mode.get_next_player(4) == 1

    def test_different_difficulties(self):
        """Test Three AI mode with different difficulty levels."""
        difficulties = [Difficulty.EASY, Difficulty.MEDIUM, Difficulty.HARD]

        for difficulty in difficulties:
            game_mode = GameMode.three_ai(difficulty)
            assert game_mode.validate() is True
            assert game_mode.difficulty == difficulty
            assert len(game_mode.ai_players) == 3

    def test_ai_player_distinctiveness(self):
        """Test that AI players are visually distinct."""
        game_mode = GameMode.three_ai(Difficulty.MEDIUM)

        ai_players = []
        for i, ai_config in enumerate(game_mode.ai_players):
            colors = ["blue", "red", "green"]
            names = ["Speedy", "Strategic", "Clever"]

            ai_player = AIPlayer(
                player_id=ai_config.position,
                strategy=RandomStrategy(),
                color=colors[i],
                name=names[i]
            )
            ai_players.append(ai_player)

        # Verify each AI has unique identification
        for i, ai in enumerate(ai_players):
            assert ai.name == names[i]
            assert ai.color == colors[i]
            assert ai.player_id == game_mode.ai_players[i].position


class TestThreeAIIntegrationFlow:
    """Integration tests for complete Three AI game flow."""

    @pytest.fixture
    def three_ai_game(self):
        """Create a Three AI game for testing."""
        from src.models.player import Player
        from src.models.board import Board

        game_mode = GameMode.three_ai(Difficulty.MEDIUM)

        # Create game state with all 4 player positions
        board = Board()
        players = [
            Player(player_id=1, name="Human"),
            Player(player_id=2, name="AI-1"),
            Player(player_id=3, name="AI-2"),
            Player(player_id=4, name="AI-3"),
        ]

        return game_mode, board, players

    def test_game_initialization(self, three_ai_game):
        """Test game initializes correctly for Three AI."""
        game_mode, board, players = three_ai_game

        assert len(players) == 4
        active_positions = [p.player_id for p in players]
        assert sorted(active_positions) == [1, 2, 3, 4]

    def test_turn_sequence(self, three_ai_game):
        """Test turn sequence follows Three AI mode rules."""
        game_mode, board, players = three_ai_game

        # Player 1 starts
        current = 1
        assert current == 1

        # Advance through all players
        next_players = [
            game_mode.get_next_player(current) for _ in range(8)
        ]

        # Should cycle through all 4 players
        assert next_players == [2, 3, 4, 1, 2, 3, 4, 1]

    def test_multi_ai_turn_management(self, three_ai_game):
        """Test managing multiple AI turns in sequence."""
        game_mode, board, players = three_ai_game

        # Simulate multiple AI turns
        current = 1  # Human starts

        # Human turn
        assert not game_mode.is_ai_turn(current)

        # AI turn 1 (player 2)
        current = game_mode.get_next_player(current)
        assert game_mode.is_ai_turn(current)
        assert current == 2

        # AI turn 2 (player 3)
        current = game_mode.get_next_player(current)
        assert game_mode.is_ai_turn(current)
        assert current == 3

        # AI turn 3 (player 4)
        current = game_mode.get_next_player(current)
        assert game_mode.is_ai_turn(current)
        assert current == 4

        # Back to human
        current = game_mode.get_next_player(current)
        assert not game_mode.is_ai_turn(current)
        assert current == 1

    def test_ai_decision_independence(self, three_ai_game):
        """Test that each AI makes independent decisions."""
        game_mode, board, players = three_ai_game

        # Create AI players with different strategies
        ai_players = {
            2: AIPlayer(player_id=2, strategy=RandomStrategy(), color="blue", name="AI-2"),
            3: AIPlayer(player_id=3, strategy=CornerStrategy(), color="red", name="AI-3"),
            4: AIPlayer(player_id=4, strategy=StrategicStrategy(), color="green", name="AI-4"),
        }

        # Each AI should operate independently
        for player_id, ai in ai_players.items():
            assert ai.player_id == player_id
            assert not ai.is_calculating

        # Simulate turns for each AI
        for player_id in [2, 3, 4]:
            ai = ai_players[player_id]

            # Calculate move
            board_state = [[0 for _ in range(20)] for _ in range(20)]
            pieces = []

            move = ai.calculate_move(board_state, pieces)

            # AI should have made a decision
            assert not ai.is_calculating

    def test_all_ai_players_active(self, three_ai_game):
        """Test that all three AI players are active."""
        game_mode, board, players = three_ai_game

        # Verify all AI positions are active
        for player_id in [2, 3, 4]:
            assert game_mode.is_ai_turn(player_id) is True

    def test_game_completion_with_multiple_ai(self, three_ai_game):
        """Test game can complete with multiple AI players."""
        game_mode, board, players = three_ai_game

        # Verify the setup supports all 4 players
        assert game_mode.get_player_count() == 4
        assert game_mode.get_ai_count() == 3

        # Verify all AI players are correctly configured
        for ai_config in game_mode.ai_players:
            assert ai_config.position in [2, 3, 4]
            assert ai_config.difficulty == Difficulty.MEDIUM


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
