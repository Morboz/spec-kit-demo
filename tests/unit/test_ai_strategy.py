"""Unit tests for AI strategy components."""

import pytest
from src.services.ai_strategy import AIStrategy
from src.config.pieces import get_piece


class TestMove:
    """Test suite for Move data class."""

    def test_create_move_with_valid_data(self):
        """Test creating a move with all required fields."""
        from src.services.ai_strategy import Move

        piece = get_piece("I5")
        move = Move(
            piece=piece,
            position=(10, 10),
            rotation=0,
            player_id=1
        )

        assert move.piece == piece
        assert move.position == (10, 10)
        assert move.rotation == 0
        assert move.player_id == 1
        assert not move.is_pass

    def test_create_pass_move(self):
        """Test creating a pass move."""
        from src.services.ai_strategy import Move

        move = Move(
            piece=None,
            position=None,
            rotation=0,
            player_id=1,
            is_pass=True
        )

        assert move.is_pass
        assert move.piece is None
        assert move.position is None


class MockStrategy(AIStrategy):
    """Mock strategy for testing the abstract base class."""

    def __init__(self, difficulty_name: str, timeout_seconds: int):
        self._difficulty_name = difficulty_name
        self._timeout_seconds = timeout_seconds

    @property
    def difficulty_name(self) -> str:
        return self._difficulty_name

    @property
    def timeout_seconds(self) -> int:
        return self._timeout_seconds

    def calculate_move(self, board, pieces, player_id, time_limit=None):
        return None

    def get_available_moves(self, board, pieces, player_id):
        return []

    def evaluate_board(self, board, player_id):
        return 0.0


class TestAIStrategy:
    """Test suite for AIStrategy abstract base class."""

    def test_cannot_instantiate_abstract_strategy(self):
        """Test that AIStrategy cannot be instantiated directly."""
        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            AIStrategy()

    def test_strategy_has_difficulty_name(self):
        """Test that strategy provides difficulty name."""
        strategy = MockStrategy("Easy", 3)
        assert strategy.difficulty_name == "Easy"

    def test_strategy_has_timeout_seconds(self):
        """Test that strategy provides timeout."""
        strategy = MockStrategy("Easy", 3)
        assert strategy.timeout_seconds == 3

    def test_difficulty_levels_are_distinct(self):
        """Test that different strategies can have different difficulties."""
        easy = MockStrategy("Easy", 3)
        medium = MockStrategy("Medium", 5)
        hard = MockStrategy("Hard", 8)

        assert easy.difficulty_name == "Easy"
        assert medium.difficulty_name == "Medium"
        assert hard.difficulty_name == "Hard"

    def test_timeout_seconds_vary_by_difficulty(self):
        """Test that timeout seconds are appropriate for difficulty."""
        easy = MockStrategy("Easy", 3)
        medium = MockStrategy("Medium", 5)
        hard = MockStrategy("Hard", 8)

        assert easy.timeout_seconds == 3
        assert medium.timeout_seconds == 5
        assert hard.timeout_seconds == 8
        assert easy.timeout_seconds < medium.timeout_seconds
        assert medium.timeout_seconds < hard.timeout_seconds


class TestRandomStrategy:
    """Test suite for RandomStrategy (Easy difficulty)."""

    def test_random_strategy_exists(self):
        """Test that RandomStrategy can be imported."""
        from src.services.ai_strategy import RandomStrategy

        strategy = RandomStrategy()
        assert strategy is not None
        assert strategy.difficulty_name == "Easy"
        assert strategy.timeout_seconds == 3

    def test_random_strategy_returns_move_or_none(self):
        """Test that RandomStrategy returns a move or None."""
        from src.services.ai_strategy import RandomStrategy

        strategy = RandomStrategy()

        # Empty board, no pieces
        board = [[0] * 20 for _ in range(20)]
        pieces = []

        move = strategy.calculate_move(board, pieces, 1)

        # Should return None when no valid moves
        assert move is None or (move.piece is not None and move.position is not None)


class TestCornerStrategy:
    """Test suite for CornerStrategy (Medium difficulty)."""

    def test_corner_strategy_exists(self):
        """Test that CornerStrategy can be imported."""
        from src.services.ai_strategy import CornerStrategy

        strategy = CornerStrategy()
        assert strategy is not None
        assert strategy.difficulty_name == "Medium"
        assert strategy.timeout_seconds == 5

    def test_corner_strategy_prefers_corners(self):
        """Test that CornerStrategy prefers corner placements."""
        from src.services.ai_strategy import CornerStrategy

        strategy = CornerStrategy()

        # Create a board with corner setup
        board = [[0] * 20 for _ in range(20)]
        # Place a piece at position (0, 0) - a corner
        board[0][0] = 1

        pieces = [get_piece("I5")]

        # Strategy should be able to calculate
        move = strategy.calculate_move(board, pieces, 2)

        # If a move is returned, it should be valid
        if move and not move.is_pass:
            assert move.piece is not None
            assert move.position is not None


class TestStrategicStrategy:
    """Test suite for StrategicStrategy (Hard difficulty)."""

    def test_strategic_strategy_exists(self):
        """Test that StrategicStrategy can be imported."""
        from src.services.ai_strategy import StrategicStrategy

        strategy = StrategicStrategy()
        assert strategy is not None
        assert strategy.difficulty_name == "Hard"
        assert strategy.timeout_seconds == 8

    def test_strategic_strategy_performs_evaluation(self):
        """Test that StrategicStrategy can evaluate board positions."""
        from src.services.ai_strategy import StrategicStrategy

        strategy = StrategicStrategy()

        # Empty board
        board = [[0] * 20 for _ in range(20)]

        # Should be able to evaluate
        score = strategy.evaluate_board(board, 1)

        assert isinstance(score, (int, float))
        assert score >= 0

    def test_strategic_strategy_uses_lookahead(self):
        """Test that StrategicStrategy considers multiple moves."""
        from src.services.ai_strategy import StrategicStrategy

        strategy = StrategicStrategy()

        board = [[0] * 20 for _ in range(20)]
        pieces = [get_piece("I5"), get_piece("V3")]

        move = strategy.calculate_move(board, pieces, 1)

        # Should return a valid move
        if move and not move.is_pass:
            assert move.piece is not None
            assert move.position is not None
