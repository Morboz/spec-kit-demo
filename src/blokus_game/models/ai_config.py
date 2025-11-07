"""
AI Configuration Module

This module defines the AIConfig class for configuring individual AI players
and the Difficulty enum for AI difficulty levels.
"""

from enum import Enum

from blokus_game.services.ai_strategy import (
    AIStrategy,
    CornerStrategy,
    RandomStrategy,
    StrategicStrategy,
)


class Difficulty(Enum):
    """AI difficulty levels."""

    EASY = "Easy"
    MEDIUM = "Medium"
    HARD = "Hard"


class AIConfig:
    """
    Configuration for a single AI player.

    Attributes:
        position: Board position (1-4)
        difficulty: AI difficulty level
        name: Display name (optional)
        color: Display color (optional)
    """

    def __init__(
        self,
        position: int,
        difficulty: Difficulty,
        name: str | None = None,
        color: str | None = None,
    ):
        """
        Initialize AI player configuration.

        Args:
            position: Board position (1-4)
            difficulty: AI difficulty level
            name: Display name (optional, default: "AI Player {position}")
            color: Display color (optional, defaults to standard palette)

        Raises:
            ValueError: If position is not in valid range
            ValueError: If difficulty is not valid
        """
        if not 1 <= position <= 4:
            raise ValueError(f"Position must be 1-4, got {position}")

        if not isinstance(difficulty, Difficulty):
            raise ValueError(
                f"Difficulty must be a Difficulty enum, got {type(difficulty)}"
            )

        self.position = position
        self.difficulty = difficulty
        self.name = name or f"AI Player {position}"
        self.color = color or self._get_default_color(position)

    def _get_default_color(self, position: int) -> str:
        """
        Get default color for a board position.

        Args:
            position: Board position (1-4)

        Returns:
            Default color string
        """
        color_map = {
            1: "blue",  # Bottom-left
            2: "red",  # Bottom-right
            3: "green",  # Top-right
            4: "orange",  # Top-left
        }
        return color_map.get(position, "gray")

    def create_player(self, strategy: AIStrategy | None = None):
        """
        Create AIPlayer instance from configuration.

        Args:
            strategy: Strategy instance (optional, created from difficulty if None)

        Returns:
            Configured AIPlayer object

        Raises:
            ValueError: If strategy creation fails
            InvalidStrategyError: If strategy is not properly configured
        """
        from blokus_game.models.ai_player import AIPlayer

        # Create strategy if not provided
        if strategy is None:
            strategy = self._create_strategy()

        if not isinstance(strategy, AIStrategy):
            raise ValueError("Strategy must implement AIStrategy interface")

        return AIPlayer(
            player_id=self.position, strategy=strategy, color=self.color, name=self.name
        )

    def _create_strategy(self) -> AIStrategy:
        """
        Create strategy instance based on difficulty.

        Returns:
            AIStrategy implementation

        Raises:
            ValueError: If difficulty is not supported
        """
        if self.difficulty == Difficulty.EASY:
            return RandomStrategy()
        elif self.difficulty == Difficulty.MEDIUM:
            return CornerStrategy()
        elif self.difficulty == Difficulty.HARD:
            return StrategicStrategy()
        else:
            raise ValueError(f"Unsupported difficulty: {self.difficulty}")

    def set_difficulty(self, difficulty: Difficulty):
        """
        Set difficulty level.

        Args:
            difficulty: New difficulty level

        Raises:
            ValueError: If difficulty is not valid
        """
        if not isinstance(difficulty, Difficulty):
            raise ValueError(
                f"Difficulty must be a Difficulty enum, got {type(difficulty)}"
            )
        self.difficulty = difficulty

    def set_name(self, name: str):
        """
        Set display name.

        Args:
            name: New display name
        """
        self.name = name

    def set_color(self, color: str):
        """
        Set display color.

        Args:
            color: New display color
        """
        self.color = color

    def get_color(self) -> str:
        """
        Get display color.

        Returns:
            Display color
        """
        return self.color

    def get_difficulty(self) -> Difficulty:
        """
        Get difficulty level.

        Returns:
            Current difficulty
        """
        return self.difficulty

    def get_position(self) -> int:
        """
        Get board position.

        Returns:
            Position (1-4)
        """
        return self.position

    def get_name(self) -> str:
        """
        Get display name.

        Returns:
            Display name
        """
        return self.name

    def __repr__(self):
        """String representation of AI config."""
        return (
            f"AIConfig(position={self.position}, difficulty={self.difficulty.value}, "
            f"name='{self.name}')"
        )
