"""
Game Setup Orchestrator

This module provides the GameSetup class which orchestrates the process
of setting up a new Blokus game, including creating players, board,
and game state.
"""

from typing import List, Optional
from src.models.board import Board
from src.models.player import Player
from src.models.game_state import GameState


class GameSetup:
    """Orchestrates the game setup process."""

    def __init__(self) -> None:
        """Initialize the game setup orchestrator."""
        self.board: Optional[Board] = None
        self.game_state: Optional[GameState] = None
        self.players: List[Player] = []

    def setup_game(self, num_players: int, player_names: List[str]) -> GameState:
        """
        Set up a new game with the specified configuration.

        Args:
            num_players: Number of players (2-4)
            player_names: List of player names

        Returns:
            Configured GameState ready for gameplay

        Raises:
            ValueError: If configuration is invalid
        """
        # Validate inputs
        self._validate_setup_config(num_players, player_names)

        # Create board
        self.board = Board()

        # Create players
        self.players = []
        for i in range(num_players):
            player = Player(player_id=i + 1, name=player_names[i])
            self.players.append(player)

        # Create game state
        self.game_state = GameState(board=self.board, players=self.players)
        
        # Start the game (transition to PLAYING phase)
        self.game_state.start_game()

        return self.game_state

    def _validate_setup_config(self, num_players: int, player_names: List[str]) -> None:
        """
        Validate the game setup configuration.

        Args:
            num_players: Number of players
            player_names: List of player names

        Raises:
            ValueError: If configuration is invalid

        Validates:
            - Player count is between 2 and 4
            - All player names are provided
            - No player names are empty or whitespace only
            - All player names are unique
            - No player names exceed reasonable length
        """
        # Check player count
        if num_players < 2 or num_players > 4:
            raise ValueError(
                f"Number of players must be between 2 and 4, got {num_players}"
            )

        # Check player names list length
        if len(player_names) != num_players:
            raise ValueError(
                f"Number of player names ({len(player_names)}) must match "
                f"number of players ({num_players})"
            )

        # Check each name
        seen_names = set()
        for i, name in enumerate(player_names):
            # Check if name is provided
            if not name or not name.strip():
                raise ValueError(f"Player {i+1} name cannot be empty")

            # Strip whitespace for checking
            clean_name = name.strip()

            # Check name length
            if len(clean_name) > 20:
                raise ValueError(f"Player {i+1} name is too long (max 20 characters)")

            # Check for duplicate names
            if clean_name in seen_names:
                raise ValueError(
                    f"Duplicate player name: '{clean_name}'. "
                    "All player names must be unique"
                )

            seen_names.add(clean_name)

        # Additional validation: check for valid characters
        for i, name in enumerate(player_names):
            clean_name = name.strip()
            if not all(c.isalnum() or c in " _-'" for c in clean_name):
                raise ValueError(
                    f"Player {i+1} name contains invalid characters. "
                    "Only letters, numbers, spaces, underscores, hyphens, "
                    "and apostrophes are allowed"
                )

    def get_game_state(self) -> Optional[GameState]:
        """
        Get the configured game state.

        Returns:
            GameState instance or None if not setup yet
        """
        return self.game_state

    def get_board(self) -> Optional[Board]:
        """
        Get the configured board.

        Returns:
            Board instance or None if not setup yet
        """
        return self.board

    def get_players(self) -> List[Player]:
        """
        Get the list of players.

        Returns:
            List of Player instances (empty if not setup yet)
        """
        return self.players

    def is_setup_complete(self) -> bool:
        """
        Check if game setup is complete.

        Returns:
            True if game is configured and ready to play
        """
        return (
            self.board is not None
            and self.game_state is not None
            and len(self.players) >= 2
        )
