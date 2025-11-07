"""
Turn Validator Module

This module provides the TurnValidator class which validates whether
players can make moves and checks various turn-related conditions.
"""

from blokus_game.game.rules import BlokusRules
from blokus_game.models.game_state import GamePhase, GameState
from blokus_game.models.player import Player


class TurnValidator:
    """Validates turn-related conditions and player moves."""

    def __init__(self, game_state: GameState) -> None:
        """
        Initialize the TurnValidator.

        Args:
            game_state: Current game state
        """
        self.game_state = game_state

    def validate_player_can_move(self, player_id: int) -> tuple[bool, str | None]:
        """
        Validate if a player can make a move.

        Args:
            player_id: ID of the player to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        player = self.game_state.get_player_by_id(player_id)

        if player is None:
            return False, f"Player {player_id} not found in game"

        # Check if game is in playing phase
        if self.game_state.phase != GamePhase.PLAYING:
            return (
                False,
                f"Game is not in playing phase (current: {self.game_state.phase.name})",
            )

        # Check if player is active
        if not player.is_active:
            return False, f"Player {player_id} is not active"

        # Check if player has pieces remaining
        if not player.has_pieces_remaining():
            return False, f"Player {player_id} has no pieces remaining"

        # Check if player has already passed
        if player.has_passed:
            return False, f"Player {player_id} has already passed in this round"

        # Check if it's actually this player's turn
        current_player = self.game_state.get_current_player()
        if current_player is None or current_player.player_id != player_id:
            return False, f"It is not player {player_id}'s turn"

        # Check if player has any valid moves
        valid_moves_exist = self._player_has_valid_moves(player)

        if not valid_moves_exist:
            return False, f"Player {player_id} has no valid moves available"

        return True, None

    def get_player_valid_moves(
        self, player_id: int
    ) -> set[tuple[str, int, int, int, bool]]:
        """
        Get all valid moves available to a player.

        Args:
            player_id: ID of the player

        Returns:
            Set of valid moves as (piece_name, row, col, rotation, flipped)
        """
        player = self.game_state.get_player_by_id(player_id)

        if player is None or not player.has_pieces_remaining():
            return set()

        valid_moves = set()
        unplaced_pieces = player.get_unplaced_pieces()

        # Try each unplaced piece
        for piece in unplaced_pieces:
            piece_name = piece.name

            # Try different orientations
            for rotation in [0, 90, 180, 270]:
                for flipped in [False, True]:
                    # Create transformed piece
                    transformed_piece = piece
                    if rotation > 0:
                        transformed_piece = piece.rotate(rotation)
                    if flipped:
                        transformed_piece = transformed_piece.flip()

                    # Try placing at various board positions
                    for row in range(self.game_state.board.size):
                        for col in range(self.game_state.board.size):
                            # Validate move
                            result = BlokusRules.validate_move(
                                self.game_state, player_id, transformed_piece, row, col
                            )

                            if result.is_valid:
                                valid_moves.add(
                                    (piece_name, row, col, rotation, flipped)
                                )

        return valid_moves

    def player_has_any_valid_move(self, player_id: int) -> bool:
        """
        Check if player has any valid move available.

        Args:
            player_id: ID of the player

        Returns:
            True if player has at least one valid move, False otherwise
        """
        valid_moves = self.get_player_valid_moves(player_id)
        return len(valid_moves) > 0

    def validate_current_player_turn(self) -> tuple[bool, str | None]:
        """
        Validate that the current turn state is valid.

        Returns:
            Tuple of (is_valid, error_message)
        """
        current_player = self.game_state.get_current_player()

        if current_player is None:
            # Check if game has players
            if len(self.game_state.players) == 0:
                return False, "No players in game"
            # Game might be over
            if self.game_state.is_game_over():
                return True, None
            return False, "No current player but game not over"

        # Check if current player is eligible
        if not current_player.is_active:
            return False, f"Current player {current_player.player_id} is not active"

        if not current_player.has_pieces_remaining():
            return False, f"Current player {current_player.player_id} has no pieces"

        return True, None

    def validate_turn_sequence(self) -> tuple[bool, str | None]:
        """
        Validate that the turn sequence is correct.

        Returns:
            Tuple of (is_valid, error_message)
        """
        players = self.game_state.players

        if len(players) < 2:
            return False, "Game requires at least 2 players"

        # Check if all player IDs are unique and in valid range
        player_ids = [p.player_id for p in players]
        if len(set(player_ids)) != len(player_ids):
            return False, "Duplicate player IDs found"

        if not all(1 <= pid <= 4 for pid in player_ids):
            return False, "Player IDs must be in range 1-4"

        # Check current player index is valid
        if self.game_state.current_player_index < 0:
            return False, "Current player index is negative"

        if self.game_state.current_player_index >= len(players):
            return False, "Current player index exceeds number of players"

        return True, None

    def validate_pass_state(self) -> tuple[bool, str | None]:
        """
        Validate that pass states are consistent.

        Returns:
            Tuple of (is_valid, error_message)
        """
        for player in self.game_state.players:
            # If player is inactive, they should not have passed
            if not player.is_active and player.has_passed:
                return False, f"Inactive player {player.player_id} has passed"

            # If player has no pieces, they should not have passed
            if not player.has_pieces_remaining() and player.has_passed:
                return (
                    False,
                    f"Player {player.player_id} with no pieces has passed",
                )

        return True, None

    def get_turn_statistics(self) -> dict:
        """
        Get statistics about the current turn state.

        Returns:
            Dictionary with turn statistics
        """
        active_players = [
            p
            for p in self.game_state.players
            if p.is_active and p.has_pieces_remaining()
        ]
        passed_players = [p for p in self.game_state.players if p.has_passed]
        inactive_players = [p for p in self.game_state.players if not p.is_active]

        return {
            "total_players": len(self.game_state.players),
            "active_players": len(active_players),
            "passed_players": len(passed_players),
            "inactive_players": len(inactive_players),
            "current_round": self.game_state.get_round_number(),
            "current_turn": self.game_state.get_turn_number(),
            "current_player": (
                self.game_state.get_current_player().player_id
                if self.game_state.get_current_player()
                else None
            ),
            "game_phase": self.game_state.phase.name,
            "should_end_round": self._should_end_round(),
            "should_end_game": self._should_end_game(),
        }

    def suggest_skip_if_no_moves(self, player_id: int) -> bool:
        """
        Suggest that a player should skip if they have no valid moves.

        Args:
            player_id: ID of the player to check

        Returns:
            True if player should skip (no valid moves), False otherwise
        """
        has_valid_moves = self.player_has_any_valid_move(player_id)
        return not has_valid_moves

    def _player_has_valid_moves(self, player: Player) -> bool:
        """
        Internal method to check if player has valid moves.

        Args:
            player: Player to check

        Returns:
            True if player has valid moves, False otherwise
        """
        return self.player_has_any_valid_move(player.player_id)

    def _should_end_round(self) -> bool:
        """Check if round should end."""
        active_players = [
            p
            for p in self.game_state.players
            if p.is_active and p.has_pieces_remaining()
        ]

        if not active_players:
            return True

        return all(p.has_passed for p in active_players)

    def _should_end_game(self) -> bool:
        """Check if game should end."""
        # End round check
        if not self._should_end_round():
            return False

        # Check if any player has placed all their pieces
        for player in self.game_state.players:
            if not player.has_pieces_remaining():
                return True

        # If no active players remain
        active_players = [
            p
            for p in self.game_state.players
            if p.is_active and p.has_pieces_remaining()
        ]
        if len(active_players) == 0:
            return True

        return False
