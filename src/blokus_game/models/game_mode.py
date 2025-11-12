"""
Game Mode Module

This module defines the GameMode class for configuring different AI battle modes
and the Difficulty enum for AI difficulty levels.
"""

import json
from enum import Enum
from pathlib import Path

from blokus_game.config.logger_config import get_logger
from blokus_game.models.ai_config import AIConfig, Difficulty

# Create logger for this module
logger = get_logger(__name__)


class GameModeType(Enum):
    """Supported game mode types."""

    SINGLE_AI = "single_ai"
    THREE_AI = "three_ai"
    SPECTATE = "spectate"
    PVP_LOCAL = "pvp_local"


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
        custom_ai_configs: list[AIConfig] | None = None,
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
        self.ai_players: list[AIConfig] = []

        # Initialize based on mode type
        if custom_ai_configs:
            self.ai_players = custom_ai_configs
            # Set human player position based on mode type when using custom configs
            if self.mode_type != GameModeType.SPECTATE:
                self._set_human_position_for_custom_config()
        else:
            self._initialize_default_config()

        # Validate configuration
        if not self.validate():
            raise ValueError(f"Invalid game mode configuration: {mode_type.value}")

    def _initialize_default_config(self) -> None:
        """Initialize default configuration based on mode type."""
        if self.mode_type == GameModeType.SINGLE_AI:
            self._init_single_ai()
        elif self.mode_type == GameModeType.THREE_AI:
            self._init_three_ai()
        elif self.mode_type == GameModeType.SPECTATE:
            self._init_spectate()
        elif self.mode_type == GameModeType.PVP_LOCAL:
            self._init_pvp_local()

    def _set_human_position_for_custom_config(self) -> None:
        """Set human player position when using custom AI configs."""
        # Find first available position not used by AI
        ai_positions = {config.position for config in self.ai_players}
        for pos in range(1, 5):
            if pos not in ai_positions:
                self.human_player_position = pos
                break

    def _init_single_ai(self) -> None:
        """Initialize single AI mode configuration."""
        self.human_player_position = 1
        self.ai_players = [AIConfig(position=3, difficulty=self.difficulty)]

    def _init_three_ai(self) -> None:
        """Initialize three AI mode configuration."""
        self.human_player_position = 1
        self.ai_players = [
            AIConfig(position=2, difficulty=self.difficulty),
            AIConfig(position=3, difficulty=self.difficulty),
            AIConfig(position=4, difficulty=self.difficulty),
        ]

    def _init_spectate(self) -> None:
        """Initialize spectator mode configuration."""
        self.human_player_position = None
        # Mix of difficulties for interesting games
        self.ai_players = [
            AIConfig(position=1, difficulty=Difficulty.EASY),
            AIConfig(position=2, difficulty=Difficulty.MEDIUM),
            AIConfig(position=3, difficulty=Difficulty.HARD),
            AIConfig(position=4, difficulty=Difficulty.MEDIUM),
        ]

    def _init_pvp_local(self, player_count: int = 2) -> None:
        """
        Initialize PvP local mode configuration.

        Args:
            player_count: Number of players (2-4)
        """
        self.human_player_position = None  # All players are human
        self.ai_players = []  # No AI players in PvP mode
        self.pvp_player_count = player_count  # Track PvP player count

    def is_ai_turn(self, current_player: int) -> bool:
        """
        Check if current player is AI-controlled.

        Args:
            current_player: Current player ID (1-4)

        Returns:
            True if player is AI, False if human
        """
        # PvP mode has no AI players
        if self.mode_type == GameModeType.PVP_LOCAL:
            return False

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
        active_positions = (
            [self.human_player_position] if self.human_player_position else []
        )
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
        elif self.mode_type == GameModeType.PVP_LOCAL:
            return self._validate_pvp_local(positions)

        return False

    def _validate_single_ai(self, positions: set[int]) -> bool:
        """Validate single AI mode configuration."""
        # Exactly 2 players (1 human + 1 AI)
        return len(positions) == 2

    def _validate_three_ai(self, positions: set[int]) -> bool:
        """Validate three AI mode configuration."""
        # Exactly 4 players (1 human + 3 AI)
        return len(positions) == 4

    def _validate_spectate(self, positions: set[int]) -> bool:
        """Validate spectator mode configuration."""
        # Exactly 4 players, all AI
        return len(positions) == 4 and self.human_player_position is None

    def _validate_pvp_local(self, positions: set[int]) -> bool:
        """Validate PvP local mode configuration."""
        # All players must be human (no AI players)
        if self.ai_players:
            return False

        # No human player position (all are equal)
        if self.human_player_position is not None:
            return False

        # For PvP mode, positions set will be empty because all players are human
        # and there's no special human player position. This is expected.
        # The actual player count is tracked separately.

        return True

    @classmethod
    def single_ai(cls, difficulty: Difficulty | None = None) -> "GameMode":
        """
        Create single AI mode configuration.

        Args:
            difficulty: AI difficulty level (None to use saved preference)

        Returns:
            GameMode configured for human vs 1 AI
        """
        if difficulty is None:
            difficulty = cls.get_difficulty_preference(GameModeType.SINGLE_AI)
        return cls(GameModeType.SINGLE_AI, difficulty)

    @classmethod
    def three_ai(cls, difficulty: Difficulty | None = None) -> "GameMode":
        """
        Create three AI mode configuration.

        Args:
            difficulty: AI difficulty level (None to use saved preference)

        Returns:
            GameMode configured for human vs 3 AI
        """
        if difficulty is None:
            difficulty = cls.get_difficulty_preference(GameModeType.THREE_AI)
        return cls(GameModeType.THREE_AI, difficulty)

    @classmethod
    def spectate_ai(cls) -> "GameMode":
        """
        Create spectator mode configuration.

        Returns:
            GameMode configured for 4 AI players (no human)
        """
        return cls(GameModeType.SPECTATE)

    @classmethod
    def pvp_local(cls, player_count: int = 2) -> "GameMode":
        """
        Create PvP local multiplayer configuration.

        Args:
            player_count: Number of players (2-4)

        Returns:
            GameMode configured for local PvP with specified player count

        Raises:
            ValueError: If player_count is not between 2 and 4
        """
        if not 2 <= player_count <= 4:
            raise ValueError(
                f"Player count must be between 2 and 4, got {player_count}"
            )

        game_mode = cls.__new__(cls)
        game_mode.mode_type = GameModeType.PVP_LOCAL
        game_mode.difficulty = Difficulty.MEDIUM
        game_mode.human_player_position = None
        game_mode.ai_players = []
        game_mode._init_pvp_local(player_count)

        if not game_mode.validate():
            raise ValueError(f"Invalid PvP game mode configuration")

        return game_mode

    def get_player_count(self) -> int:
        """
        Get total number of players in this mode.

        Returns:
            Number of players (human + AI)
        """
        # PvP mode has no AI players, all are human
        if self.mode_type == GameModeType.PVP_LOCAL:
            return getattr(self, "pvp_player_count", 2)

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
        return (
            f"GameMode(type={self.mode_type.value}, players={self.get_player_count()}, "
            f"ai={self.get_ai_count()})"
        )

    # Difficulty Persistence Methods

    @staticmethod
    def _get_config_dir() -> Path:
        """
        Get the configuration directory for storing game settings.

        Returns:
            Path to config directory
        """
        config_dir = Path.home() / ".blokus"
        config_dir.mkdir(exist_ok=True)
        return config_dir

    def save_difficulty_preference(
        self, mode_type: GameModeType, difficulty: Difficulty
    ) -> None:
        """
        Save difficulty preference for a game mode.

        Args:
            mode_type: Game mode type
            difficulty: Difficulty level to save
        """
        try:
            config_file = self._get_config_dir() / "difficulty_preferences.json"

            # Load existing preferences
            preferences = self._load_difficulty_preferences()

            # Update preference for this mode
            preferences[mode_type.value] = difficulty.value

            # Save to file
            with open(config_file, "w") as f:
                json.dump(preferences, f, indent=2)
        except Exception as e:
            # Log error but don't crash
            logger.warning(f"Failed to save difficulty preference: {e}")

    @staticmethod
    def _load_difficulty_preferences() -> dict[str, str]:
        """
        Load difficulty preferences from file.

        Returns:
            Dictionary mapping mode types to difficulty levels
        """
        config_file = Path.home() / ".blokus" / "difficulty_preferences.json"

        if not config_file.exists():
            return {}

        try:
            with open(config_file) as f:
                return json.load(f)
        except Exception:
            return {}

    @classmethod
    def get_difficulty_preference(cls, mode_type: GameModeType) -> Difficulty:
        """
        Get saved difficulty preference for a game mode.

        Args:
            mode_type: Game mode type

        Returns:
            Saved difficulty or MEDIUM as default
        """
        preferences = cls._load_difficulty_preferences()
        difficulty_str = preferences.get(mode_type.value, Difficulty.MEDIUM.value)

        try:
            return Difficulty(difficulty_str)
        except ValueError:
            return Difficulty.MEDIUM

    def clear_difficulty_preferences(self) -> None:
        """
        Clear all saved difficulty preferences.
        """
        try:
            config_file = self._get_config_dir() / "difficulty_preferences.json"
            if config_file.exists():
                config_file.unlink()
        except Exception as e:
            logger.warning(f"Failed to clear difficulty preferences: {e}")
