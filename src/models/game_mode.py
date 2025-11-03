"""
Game Mode Module

This module defines the GameMode class for configuring different AI battle modes
and the Difficulty enum for AI difficulty levels.
"""

from enum import Enum
from typing import List, Optional
from src.models.ai_config import AIConfig, Difficulty


class GameModeType(Enum):
    """Supported game mode types."""
    SINGLE_AI = "single_ai"
    THREE_AI = "three_ai"
    SPECTATE = "spectate"


class GameMode:
    """
    Configuration for Blokus game mode with AI players.

    Attributes:
        mode_type: Type of game mode
        difficulty: Default difficulty for AI players
        human_player_position: Position of human player (1-4) or None
        ai_players: List of AI player configurations
    """

    def __init__(
        self,
        mode_type: GameModeType,
        difficulty: Difficulty = Difficulty.MEDIUM,
        custom_ai_configs: Optional[List[AIConfig]] = None,
    ):
        """
        Initialize game mode configuration.

        Args:
            mode_type: Type of game mode
            difficulty: Default difficulty for AI players
            custom_ai_configs: Custom AI configurations (optional)

        Raises:
            ValueError: If configuration is invalid
        """
        self.mode_type = mode_type
        self.difficulty = difficulty
        self.human_player_position = None
        self.ai_players: List[AIConfig] = []

        # Initialize based on mode type
        if custom_ai_configs:
            self.ai_players = custom_ai_configs
        else:
            self._initialize_default_config()

        # Validate configuration
        if not self.validate():
            raise ValueError(f"Invalid game mode configuration: {mode_type.value}")

    def _initialize_default_config(self):
        """Initialize default configuration based on mode type."""
        if self.mode_type == GameModeType.SINGLE_AI:
            self._init_single_ai()
        elif self.mode_type == GameModeType.THREE_AI:
            self._init_three_ai()
        elif self.mode_type == GameModeType.SPECTATE:
            self._init_spectate()

    def _init_single_ai(self):
        """Initialize single AI mode configuration."""
        self.human_player_position = 1
        self.ai_players = [
            AIConfig(position=3, difficulty=self.difficulty)
        ]

    def _init_three_ai(self):
        """Initialize three AI mode configuration."""
        self.human_player_position = 1
        self.ai_players = [
            AIConfig(position=2, difficulty=self.difficulty),
            AIConfig(position=3, difficulty=self.difficulty),
            AIConfig(position=4, difficulty=self.difficulty),
        ]

    def _init_spectate(self):
        """Initialize spectator mode configuration."""
        self.human_player_position = None
        # Mix of difficulties for interesting games
        self.ai_players = [
            AIConfig(position=1, difficulty=Difficulty.EASY),
            AIConfig(position=2, difficulty=Difficulty.MEDIUM),
            AIConfig(position=3, difficulty=Difficulty.HARD),
            AIConfig(position=4, difficulty=Difficulty.MEDIUM),
        ]

    def is_ai_turn(self, current_player: int) -> bool:
        """
        Check if current player is AI-controlled.

        Args:
            current_player: Current player ID (1-4)

        Returns:
            True if player is AI, False if human
        """
        if self.human_player_position == current_player:
            return False

        return any(config.position == current_player for config in self.ai_players)

    def get_next_player(self, current_player: int) -> int:
        """
        Get next player in turn order.

        Args:
            current_player: Current player ID (1-4)

        Returns:
            Next player ID (1-4)

        Note:
            Skips positions not used in this mode
        """
        # Determine active positions
        active_positions = [self.human_player_position] if self.human_player_position else []
        active_positions.extend([config.position for config in self.ai_players])
        active_positions.sort()

        # Find current player index
        try:
            current_index = active_positions.index(current_player)
        except ValueError:
            # Current player not in active positions, return first
            return active_positions[0]

        # Get next position (wrap around)
        next_index = (current_index + 1) % len(active_positions)
        return active_positions[next_index]

    def validate(self) -> bool:
        """
        Validate game mode configuration.

        Returns:
            True if configuration is valid
        """
        # Check mode type is valid
        if not isinstance(self.mode_type, GameModeType):
            return False

        # Collect all positions
        positions = set()
        if self.human_player_position:
            if not 1 <= self.human_player_position <= 4:
                return False
            positions.add(self.human_player_position)

        # Check AI player positions
        for config in self.ai_players:
            if not 1 <= config.position <= 4:
                return False
            if config.position in positions:
                return False
            positions.add(config.position)

        # Check mode-specific rules
        if self.mode_type == GameModeType.SINGLE_AI:
            return self._validate_single_ai(positions)
        elif self.mode_type == GameModeType.THREE_AI:
            return self._validate_three_ai(positions)
        elif self.mode_type == GameModeType.SPECTATE:
            return self._validate_spectate(positions)

        return False

    def _validate_single_ai(self, positions: set) -> bool:
        """Validate single AI mode configuration."""
        # Exactly 2 players (1 human + 1 AI)
        return len(positions) == 2

    def _validate_three_ai(self, positions: set) -> bool:
        """Validate three AI mode configuration."""
        # Exactly 4 players (1 human + 3 AI)
        return len(positions) == 4

    def _validate_spectate(self, positions: set) -> bool:
        """Validate spectator mode configuration."""
        # Exactly 4 players, all AI
        return len(positions) == 4 and self.human_player_position is None

    @classmethod
    def single_ai(cls, difficulty: Difficulty = Difficulty.MEDIUM) -> "GameMode":
        """
        Create single AI mode configuration.

        Args:
            difficulty: AI difficulty level

        Returns:
            GameMode configured for human vs 1 AI
        """
        return cls(GameModeType.SINGLE_AI, difficulty)

    @classmethod
    def three_ai(cls, difficulty: Difficulty = Difficulty.MEDIUM) -> "GameMode":
        """
        Create three AI mode configuration.

        Args:
            difficulty: AI difficulty level

        Returns:
            GameMode configured for human vs 3 AI
        """
        return cls(GameModeType.THREE_AI, difficulty)

    @classmethod
    def spectate_ai(cls) -> "GameMode":
        """
        Create spectator mode configuration.

        Returns:
            GameMode configured for 4 AI players (no human)
        """
        return cls(GameModeType.SPECTATE)

    def get_player_count(self) -> int:
        """
        Get total number of players in this mode.

        Returns:
            Number of players (human + AI)
        """
        count = len(self.ai_players)
        if self.human_player_position:
            count += 1
        return count

    def get_ai_count(self) -> int:
        """
        Get number of AI players.

        Returns:
            Number of AI players
        """
        return len(self.ai_players)

    def __repr__(self):
        """String representation of game mode."""
        return f"GameMode(type={self.mode_type.value}, players={self.get_player_count()}, ai={self.get_ai_count()})"
