"""
Game configuration module for Blokus.

This module contains all configurable options for the game,
allowing customization of:
- Player names and colors
- Game rules and constraints
- UI settings
- Performance options
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum


class GameMode(Enum):
    """Game mode enumeration."""
    LOCAL_MULTIPLAYER = "local_multiplayer"
    LOCAL_TWO_PLAYER = "local_two_player"


class Difficulty(Enum):
    """AI difficulty levels (for future AI implementation)."""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


@dataclass
class PlayerConfig:
    """Configuration for a single player."""
    player_id: int
    name: str
    color: str
    is_human: bool = True
    difficulty: Optional[Difficulty] = None


@dataclass
class GameConfig:
    """Complete game configuration."""

    # Game settings
    game_mode: GameMode = GameMode.LOCAL_MULTIPLAYER
    board_size: int = 20
    min_players: int = 2
    max_players: int = 4

    # Player configurations
    players: List[PlayerConfig] = field(default_factory=list)

    # UI settings
    window_width: int = 1200
    window_height: int = 800
    cell_size: int = 30
    show_grid_lines: bool = True
    show_coordinates: bool = False
    animation_speed: int = 100  # milliseconds

    # Game rules
    enforce_corner_rule: bool = True
    enforce_no_edge_contact: bool = True
    enforce_board_bounds: bool = True
    allow_overlap: bool = False  # Should always be False in Blokus

    # Scoring settings
    use_official_scoring: bool = True
    show_score_breakdown: bool = True
    show_score_history: bool = True

    # Color schemes
    color_schemes: Dict[str, Dict[str, str]] = field(
        default_factory=lambda: {
            "default": {
                "player1": "blue",
                "player2": "red",
                "player3": "green",
                "player4": "yellow",
            },
            "pastel": {
                "player1": "#A8D5E2",
                "player2": "#F7A8A8",
                "player3": "#B8E6B8",
                "player4": "#F9E2A8",
            },
            "vibrant": {
                "player1": "#0066CC",
                "player2": "#CC0000",
                "player3": "#00AA00",
                "player4": "#CC9900",
            },
            "high_contrast": {
                "player1": "#0000FF",
                "player2": "#FF0000",
                "player3": "#00FF00",
                "player4": "#FFFF00",
            },
        }
    )

    current_color_scheme: str = "default"

    # Performance settings
    enable_caching: bool = True
    max_valid_moves_cache: int = 1000
    render_optimization: bool = True

    # Debug settings
    debug_mode: bool = False
    show_valid_moves_preview: bool = False
    show_move_validation_messages: bool = True

    # Sound settings (for future implementation)
    sound_enabled: bool = False
    sound_volume: float = 0.5

    def __post_init__(self):
        """Validate configuration after initialization."""
        # Validate board size
        if self.board_size < 10 or self.board_size > 50:
            raise ValueError(f"Board size must be between 10 and 50, got {self.board_size}")

        # Validate window dimensions
        if self.window_width < 800:
            raise ValueError(f"Window width must be at least 800, got {self.window_width}")

        if self.window_height < 600:
            raise ValueError(f"Window height must be at least 600, got {self.window_height}")

        # Validate cell size
        if self.cell_size < 10 or self.cell_size > 50:
            raise ValueError(f"Cell size must be between 10 and 50, got {self.cell_size}")

        # Validate player count
        player_count = len(self.players)
        if player_count < self.min_players or player_count > self.max_players:
            raise ValueError(
                f"Player count must be between {self.min_players} and {self.max_players}, got {player_count}"
            )

        # Validate color scheme
        if self.current_color_scheme not in self.color_schemes:
            raise ValueError(f"Unknown color scheme: {self.current_color_scheme}")

        # Validate animation speed
        if self.animation_speed < 0 or self.animation_speed > 1000:
            raise ValueError(f"Animation speed must be between 0 and 1000, got {self.animation_speed}")

    def get_player_color(self, player_id: int) -> str:
        """Get the color for a specific player."""
        scheme = self.color_schemes[self.current_color_scheme]
        key = f"player{player_id}"
        return scheme.get(key, "gray")

    def set_player_name(self, player_id: int, name: str):
        """Set the name for a specific player."""
        for player in self.players:
            if player.player_id == player_id:
                player.name = name
                break

    def set_player_color(self, player_id: int, color: str):
        """Set the color for a specific player."""
        for player in self.players:
            if player.player_id == player_id:
                player.color = color
                break

    def add_player(self, player_id: int, name: str, color: str):
        """Add a new player to the configuration."""
        if len(self.players) >= self.max_players:
            raise ValueError(f"Maximum number of players ({self.max_players}) reached")

        player_config = PlayerConfig(
            player_id=player_id,
            name=name,
            color=color,
        )
        self.players.append(player_config)

    def remove_player(self, player_id: int):
        """Remove a player from the configuration."""
        if len(self.players) <= self.min_players:
            raise ValueError(f"Minimum number of players ({self.min_players}) required")

        self.players = [p for p in self.players if p.player_id != player_id]

    def validate(self) -> List[str]:
        """
        Validate the configuration and return a list of issues.

        Returns:
            List of validation error messages (empty if valid).
        """
        errors = []

        # Check player count
        if len(self.players) < self.min_players:
            errors.append(f"Need at least {self.min_players} players")
        elif len(self.players) > self.max_players:
            errors.append(f"Maximum {self.max_players} players allowed")

        # Check for duplicate player IDs
        player_ids = [p.player_id for p in self.players]
        if len(player_ids) != len(set(player_ids)):
            errors.append("Duplicate player IDs detected")

        # Check for empty player names
        for player in self.players:
            if not player.name.strip():
                errors.append(f"Player {player.player_id} has empty name")

        # Check color scheme
        if self.current_color_scheme not in self.color_schemes:
            errors.append(f"Invalid color scheme: {self.current_color_scheme}")

        return errors

    def to_dict(self) -> Dict:
        """Convert configuration to dictionary."""
        return {
            "game_mode": self.game_mode.value,
            "board_size": self.board_size,
            "min_players": self.min_players,
            "max_players": self.max_players,
            "window_width": self.window_width,
            "window_height": self.window_height,
            "cell_size": self.cell_size,
            "current_color_scheme": self.current_color_scheme,
            "players": [
                {
                    "player_id": p.player_id,
                    "name": p.name,
                    "color": p.color,
                    "is_human": p.is_human,
                }
                for p in self.players
            ],
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "GameConfig":
        """Create configuration from dictionary."""
        config = cls()

        config.game_mode = GameMode(data.get("game_mode", "local_multiplayer"))
        config.board_size = data.get("board_size", 20)
        config.min_players = data.get("min_players", 2)
        config.max_players = data.get("max_players", 4)
        config.window_width = data.get("window_width", 1200)
        config.window_height = data.get("window_height", 800)
        config.cell_size = data.get("cell_size", 30)
        config.current_color_scheme = data.get("current_color_scheme", "default")

        # Load players
        for p_data in data.get("players", []):
            player = PlayerConfig(
                player_id=p_data["player_id"],
                name=p_data["name"],
                color=p_data["color"],
                is_human=p_data.get("is_human", True),
            )
            config.players.append(player)

        return config

    @classmethod
    def create_default_two_player(cls) -> "GameConfig":
        """Create a default two-player configuration."""
        config = cls()
        config.game_mode = GameMode.LOCAL_TWO_PLAYER

        config.players = [
            PlayerConfig(player_id=1, name="Player 1", color="blue"),
            PlayerConfig(player_id=2, name="Player 2", color="red"),
        ]

        return config

    @classmethod
    def create_default_four_player(cls) -> "GameConfig":
        """Create a default four-player configuration."""
        config = cls()
        config.game_mode = GameMode.LOCAL_MULTIPLAYER

        config.players = [
            PlayerConfig(player_id=1, name="Player 1", color="blue"),
            PlayerConfig(player_id=2, name="Player 2", color="red"),
            PlayerConfig(player_id=3, name="Player 3", color="green"),
            PlayerConfig(player_id=4, name="Player 4", color="yellow"),
        ]

        return config


# Pre-defined configuration presets
CONFIG_PRESETS = {
    "casual": GameConfig(
        show_grid_lines=True,
        show_coordinates=False,
        animation_speed=200,
        debug_mode=False,
    ),
    "tournament": GameConfig(
        show_grid_lines=False,
        show_coordinates=False,
        animation_speed=0,  # No animations
        show_valid_moves_preview=True,
        debug_mode=False,
    ),
    "debug": GameConfig(
        show_grid_lines=True,
        show_coordinates=True,
        animation_speed=500,
        debug_mode=True,
        show_valid_moves_preview=True,
        show_move_validation_messages=True,
    ),
    "high_contrast": GameConfig(
        current_color_scheme="high_contrast",
        show_grid_lines=True,
        cell_size=35,  # Larger cells for accessibility
    ),
}


def create_config_from_preset(preset_name: str) -> GameConfig:
    """Create a configuration from a preset."""
    if preset_name not in CONFIG_PRESETS:
        raise ValueError(f"Unknown preset: {preset_name}. Available presets: {list(CONFIG_PRESETS.keys())}")

    # Return a copy of the preset
    preset = CONFIG_PRESETS[preset_name]

    # Create new instance with default players
    if preset_name == "tournament":
        return GameConfig.create_default_four_player()
    elif preset_name == "high_contrast":
        config = GameConfig.create_default_two_player()
        config.current_color_scheme = "high_contrast"
        config.show_grid_lines = True
        config.cell_size = 35
        return config
    else:
        return GameConfig.create_default_two_player()