"""Integration tests for basic AI functionality."""

from blokus_game.models.ai_config import AIConfig
from blokus_game.models.ai_player import AIPlayer
from blokus_game.models.game_mode import Difficulty, GameMode, GameModeType
from blokus_game.models.turn_controller import TurnController, TurnState
from blokus_game.services.ai_strategy import (
    CornerStrategy,
    RandomStrategy,
    StrategicStrategy,
)
from blokus_game.ui.game_mode_selector import GameModeSelector


class TestAIGameModeIntegration:
    """Integration tests for AI game mode configuration."""

    def test_create_single_ai_mode(self):
        """Test creating and configuring single AI mode."""
        game_mode = GameMode.single_ai(Difficulty.MEDIUM)

        assert game_mode.mode_type == GameModeType.SINGLE_AI
        assert game_mode.difficulty == Difficulty.MEDIUM
        assert game_mode.human_player_position == 1
        assert len(game_mode.ai_players) == 1
        assert game_mode.ai_players[0].position == 3
        assert game_mode.get_player_count() == 2
        assert game_mode.get_ai_count() == 1

    def test_create_three_ai_mode(self):
        """Test creating and configuring three AI mode."""
        game_mode = GameMode.three_ai(Difficulty.EASY)

        assert game_mode.mode_type == GameModeType.THREE_AI
        assert game_mode.difficulty == Difficulty.EASY
        assert game_mode.human_player_position == 1
        assert len(game_mode.ai_players) == 3
        assert game_mode.get_player_count() == 4
        assert game_mode.get_ai_count() == 3

    def test_create_spectate_mode(self):
        """Test creating and configuring spectator mode."""
        game_mode = GameMode.spectate_ai()

        assert game_mode.mode_type == GameModeType.SPECTATE
        assert game_mode.human_player_position is None
        assert len(game_mode.ai_players) == 4
        assert game_mode.get_player_count() == 4
        assert game_mode.get_ai_count() == 4

    def test_game_mode_selector_integration(self):
        """Test game mode selector creates valid modes."""
        # Single AI
        mode = GameModeSelector.create_game_mode("single_ai", "Hard")
        assert isinstance(mode, GameMode)
        assert mode.mode_type == GameModeType.SINGLE_AI

        # Three AI
        mode = GameModeSelector.create_game_mode("three_ai", "Easy")
        assert isinstance(mode, GameMode)
        assert mode.mode_type == GameModeType.THREE_AI

        # Spectate
        mode = GameModeSelector.create_game_mode("spectate", None)
        assert isinstance(mode, GameMode)
        assert mode.mode_type == GameModeType.SPECTATE

    def test_ai_turn_detection(self):
        """Test detecting AI turns in different modes."""
        # Single AI mode
        mode = GameMode.single_ai(Difficulty.MEDIUM)
        assert not mode.is_ai_turn(1)  # Human player
        assert mode.is_ai_turn(3)  # AI player

        # Three AI mode
        mode = GameMode.three_ai(Difficulty.MEDIUM)
        assert not mode.is_ai_turn(1)  # Human player
        assert mode.is_ai_turn(2)  # AI player
        assert mode.is_ai_turn(3)  # AI player
        assert mode.is_ai_turn(4)  # AI player

        # Spectate mode
        mode = GameMode.spectate_ai()
        assert mode.is_ai_turn(1)  # All AI
        assert mode.is_ai_turn(2)  # All AI
        assert mode.is_ai_turn(3)  # All AI
        assert mode.is_ai_turn(4)  # All AI

    def test_next_player_advancement(self):
        """Test advancing to next player in different modes."""
        # Single AI mode (only positions 1 and 3 active)
        mode = GameMode.single_ai(Difficulty.MEDIUM)
        assert mode.get_next_player(1) == 3
        assert mode.get_next_player(3) == 1

        # Three AI mode (all positions active)
        mode = GameMode.three_ai(Difficulty.MEDIUM)
        assert mode.get_next_player(1) == 2
        assert mode.get_next_player(2) == 3
        assert mode.get_next_player(3) == 4
        assert mode.get_next_player(4) == 1

        # Spectate mode (all positions active)
        mode = GameMode.spectate_ai()
        assert mode.get_next_player(1) == 2
        assert mode.get_next_player(4) == 1


class TestAIPlayerIntegration:
    """Integration tests for AI player creation and configuration."""

    def test_create_ai_player_from_config(self):
        """Test creating AI player from configuration."""
        config = AIConfig(position=2, difficulty=Difficulty.EASY)
        ai_player = config.create_player()

        assert isinstance(ai_player, AIPlayer)
        assert ai_player.player_id == 2
        assert ai_player.difficulty == "Easy"
        assert ai_player.name == "AI Player 2"
        assert ai_player.color == config.color

    def test_ai_players_with_different_strategies(self):
        """Test AI players with different strategies."""
        strategies = [
            (Difficulty.EASY, RandomStrategy),
            (Difficulty.MEDIUM, CornerStrategy),
            (Difficulty.HARD, StrategicStrategy),
        ]

        for difficulty, expected_strategy_class in strategies:
            config = AIConfig(position=1, difficulty=difficulty)
            ai_player = config.create_player()

            assert isinstance(ai_player.strategy, expected_strategy_class)
            assert ai_player.difficulty == difficulty.value

    def test_ai_player_calculation(self):
        """Test AI player move calculation."""
        strategy = RandomStrategy()
        ai_player = AIPlayer(1, strategy, "blue", "Test AI")

        # Empty board
        board = [[0] * 20 for _ in range(20)]
        pieces = [ai_player.pieces[0]]  # Use first piece

        move = ai_player.calculate_move(board, pieces)

        # Should either return a move or None
        assert move is None or (move.piece is not None and move.position is not None)

    def test_multiple_ai_players_independence(self):
        """Test that multiple AI players operate independently."""
        strategies = [
            RandomStrategy(),
            CornerStrategy(),
            StrategicStrategy(),
        ]

        ai_players = []
        for i, strategy in enumerate(strategies, 2):
            config = AIConfig(position=i, difficulty=Difficulty.MEDIUM)
            ai_player = config.create_player(strategy)
            ai_players.append(ai_player)

        # Each AI should have independent strategy
        assert ai_players[0].strategy != ai_players[1].strategy
        assert ai_players[1].strategy != ai_players[2].strategy

        # Each AI should have its own strategy's difficulty (not the config's difficulty when strategy is overridden)
        expected_difficulties = ["Easy", "Medium", "Hard"]  # Based on strategy types
        actual_difficulties = [ai.difficulty for ai in ai_players]
        assert actual_difficulties == expected_difficulties


class TestTurnControllerIntegration:
    """Integration tests for TurnController with AI."""

    def test_turn_controller_initialization(self):
        """Test TurnController initialization with game mode."""
        game_mode = GameMode.single_ai(Difficulty.MEDIUM)
        controller = TurnController(game_mode)

        assert controller.game_mode == game_mode
        assert controller.current_player == 1
        assert controller.current_state == TurnState.HUMAN_TURN
        assert not controller.is_ai_turn

    def test_turn_controller_ai_turn_detection(self):
        """Test TurnController detects AI turns correctly."""
        game_mode = GameMode.single_ai(Difficulty.MEDIUM)
        controller = TurnController(game_mode)

        # Initially player 1 (human)
        assert not controller.is_ai_turn

        # Switch to player 3 (AI)
        controller.current_player = 3
        assert controller.is_ai_turn

    def test_turn_controller_event_listeners(self):
        """Test TurnController event listener system."""
        game_mode = GameMode.single_ai(Difficulty.MEDIUM)
        controller = TurnController(game_mode)

        events_received = []

        def event_listener(event):
            events_received.append(event)

        controller.add_turn_listener(event_listener)

        # Trigger a turn
        controller.start_turn()

        # Check that events were received
        assert len(events_received) > 0
        assert any(event.event_type == "TURN_STARTED" for event in events_received)

    def test_turn_controller_next_player(self):
        """Test TurnController advances to next player correctly."""
        game_mode = GameMode.single_ai(Difficulty.MEDIUM)
        controller = TurnController(game_mode)

        # Player 1 (human)
        controller.current_player = 1
        assert not controller.is_ai_turn

        # Next should be player 3 (AI)
        next_player = controller.get_next_player()
        assert next_player == 3
        assert game_mode.is_ai_turn(next_player)


class TestEndToEndAIWorkflow:
    """End-to-end integration tests for complete AI workflows."""

    def test_single_ai_game_setup_workflow(self):
        """Test complete workflow for setting up a single AI game."""
        # 1. Create game mode
        game_mode = GameMode.single_ai(Difficulty.MEDIUM)
        assert game_mode.mode_type == GameModeType.SINGLE_AI

        # 2. Create AI player from config
        ai_config = game_mode.ai_players[0]
        ai_player = ai_config.create_player()
        assert isinstance(ai_player, AIPlayer)

        # 3. Create TurnController
        controller = TurnController(game_mode)
        assert game_mode.is_ai_turn(3)

        # 4. Verify turn advancement
        assert controller.get_next_player(1) == 3
        assert controller.get_next_player(3) == 1

    def test_three_ai_game_setup_workflow(self):
        """Test complete workflow for setting up a three AI game."""
        # 1. Create game mode
        game_mode = GameMode.three_ai(Difficulty.HARD)
        assert game_mode.mode_type == GameModeType.THREE_AI

        # 2. Create all AI players
        ai_players = [config.create_player() for config in game_mode.ai_players]
        assert len(ai_players) == 3

        # 3. Verify each AI has correct difficulty
        for ai_player in ai_players:
            assert ai_player.difficulty == "Hard"

        # 4. Create TurnController
        controller = TurnController(game_mode)
        assert game_mode.is_ai_turn(2)
        assert game_mode.is_ai_turn(3)
        assert game_mode.is_ai_turn(4)

    def test_spectate_mode_workflow(self):
        """Test complete workflow for spectator mode."""
        # 1. Create game mode
        game_mode = GameMode.spectate_ai()
        assert game_mode.mode_type == GameModeType.SPECTATE
        assert game_mode.human_player_position is None

        # 2. Create all AI players
        ai_players = [config.create_player() for config in game_mode.ai_players]
        assert len(ai_players) == 4

        # 3. Verify mixed difficulties
        difficulties = {ai.difficulty for ai in ai_players}
        assert (
            "Easy" in difficulties or "Medium" in difficulties or "Hard" in difficulties
        )

        # 4. All turns are AI turns
        controller = TurnController(game_mode)
        for player_id in [1, 2, 3, 4]:
            assert game_mode.is_ai_turn(player_id)

    def test_strategy_instantiation_workflow(self):
        """Test that strategies are properly instantiated."""
        # Test Easy strategy
        config = AIConfig(position=1, difficulty=Difficulty.EASY)
        strategy = config._create_strategy()
        assert isinstance(strategy, RandomStrategy)
        assert strategy.difficulty_name == "Easy"
        assert strategy.timeout_seconds == 3

        # Test Medium strategy
        config = AIConfig(position=2, difficulty=Difficulty.MEDIUM)
        strategy = config._create_strategy()
        assert isinstance(strategy, CornerStrategy)
        assert strategy.difficulty_name == "Medium"
        assert strategy.timeout_seconds == 5

        # Test Hard strategy
        config = AIConfig(position=3, difficulty=Difficulty.HARD)
        strategy = config._create_strategy()
        assert isinstance(strategy, StrategicStrategy)
        assert strategy.difficulty_name == "Hard"
        assert strategy.timeout_seconds == 8
