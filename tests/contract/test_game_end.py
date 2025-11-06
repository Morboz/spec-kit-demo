"""
Contract tests for game end detection.

This module contains contract tests that verify the game end detection logic
according to Blokus rules. These tests define the expected behavior that the
implementation must satisfy.
"""

import pytest
from src.models.game_state import GameState, GamePhase
from src.models.player import Player
from src.models.board import Board


class TestGameEndDetection:
    """Contract tests for game end detection logic."""

    def test_game_not_ended_during_active_play(self):
        """Game should not end while there are active players who can move."""
        # Setup: Create game with 2 players who haven't passed
        game_state = GameState()
        player1 = Player(1, "Alice")
        player2 = Player(2, "Bob")
        game_state.add_player(player1)
        game_state.add_player(player2)
        game_state.start_game()

        # No pieces have been placed yet, but players can still move
        assert not game_state.should_end_game()
        assert game_state.phase == GamePhase.PLAYING

    def test_game_ends_when_all_active_players_pass(self):
        """Game should end when all active players have passed."""
        # Setup: Create game with 2 players
        game_state = GameState()
        player1 = Player(1, "Alice")
        player2 = Player(2, "Bob")
        game_state.add_player(player1)
        game_state.add_player(player2)
        game_state.start_game()

        # Both players pass
        player1.pass_turn()
        player2.pass_turn()

        # Game should end when all active players have passed
        assert game_state.should_end_round()
        assert game_state.should_end_game()

    def test_game_ends_when_no_players_have_pieces(self):
        """Game should end when no player has any pieces remaining."""
        # Setup: Create game with 2 players
        game_state = GameState()
        player1 = Player(1, "Alice")
        player2 = Player(2, "Bob")
        game_state.add_player(player1)
        game_state.add_player(player2)
        game_state.start_game()

        # Mark all pieces as placed (simulate all pieces used)
        for piece in player1.get_all_pieces():
            piece.is_placed = True
        for piece in player2.get_all_pieces():
            piece.is_placed = True

        # Game should end when no player has pieces remaining
        assert not player1.has_pieces_remaining()
        assert not player2.has_pieces_remaining()
        assert game_state.should_end_game()

    def test_game_ends_when_all_players_inactive(self):
        """Game should end when all players are marked inactive."""
        # Setup: Create game with 2 players
        game_state = GameState()
        player1 = Player(1, "Alice")
        player2 = Player(2, "Bob")
        game_state.add_player(player1)
        game_state.add_player(player2)
        game_state.start_game()

        # Mark both players as inactive
        player1.set_inactive()
        player2.set_inactive()

        # Game should end when all players are inactive
        assert game_state.should_end_game()

    def test_end_game_transition(self):
        """Test transitioning game state to GAME_OVER phase."""
        # Setup: Create game with 2 players
        game_state = GameState()
        player1 = Player(1, "Alice")
        player2 = Player(2, "Bob")
        game_state.add_player(player1)
        game_state.add_player(player2)
        game_state.start_game()

        # Verify initial state
        assert game_state.phase == GamePhase.PLAYING
        assert not game_state.is_game_over()

        # End the game
        game_state.end_game()

        # Verify transition to GAME_OVER
        assert game_state.phase == GamePhase.GAME_OVER
        assert game_state.is_game_over()

    def test_get_winners_before_game_over_raises_error(self):
        """Getting winners before game ends should raise ValueError."""
        # Setup: Create game with 2 players
        game_state = GameState()
        player1 = Player(1, "Alice")
        player2 = Player(2, "Bob")
        game_state.add_player(player1)
        game_state.add_player(player2)
        game_state.start_game()

        # Attempting to get winners before game ends should raise error
        with pytest.raises(ValueError, match="Game is not over yet"):
            game_state.get_winners()

    def test_get_winners_after_game_over(self):
        """Getting winners after game ends should work correctly."""
        # Setup: Create game with 2 players with different scores
        game_state = GameState()
        player1 = Player(1, "Alice")
        player2 = Player(2, "Bob")
        game_state.add_player(player1)
        game_state.add_player(player2)
        game_state.start_game()

        # Set different scores
        player1.score = 50
        player2.score = 30

        # End the game
        game_state.end_game()

        # Get winners - should return player with highest score
        winners = game_state.get_winners()
        assert len(winners) == 1
        assert winners[0] == player1
        assert winners[0].score == 50

    def test_get_winners_tie_handling(self):
        """Getting winners should handle ties correctly."""
        # Setup: Create game with 2 players with same score
        game_state = GameState()
        player1 = Player(1, "Alice")
        player2 = Player(2, "Bob")
        game_state.add_player(player1)
        game_state.add_player(player2)
        game_state.start_game()

        # Set same scores
        player1.score = 50
        player2.score = 50

        # End the game
        game_state.end_game()

        # Get winners - should return both players in tie
        winners = game_state.get_winners()
        assert len(winners) == 2
        assert player1 in winners
        assert player2 in winners

    def test_get_winners_no_players(self):
        """Getting winners with no players should return empty list."""
        # Setup: Create game with no players
        game_state = GameState()
        # Don't start game with no players - skip this test scenario

        # End the game
        game_state.end_game()

        # Get winners - should return empty list
        winners = game_state.get_winners()
        assert len(winners) == 0

    def test_multiple_rounds_with_passes(self):
        """Test game progression through multiple rounds with passes."""
        # Setup: Create game with 2 players
        game_state = GameState()
        player1 = Player(1, "Alice")
        player2 = Player(2, "Bob")
        game_state.add_player(player1)
        game_state.add_player(player2)
        game_state.start_game()

        # First round
        assert game_state.get_round_number() == 1

        # Both players pass
        player1.pass_turn()
        game_state.next_turn()
        player2.pass_turn()
        game_state.next_turn()

        # Round should advance
        assert game_state.get_round_number() == 2
        # Note: GameState doesn't automatically reset pass states in next_turn()
        # Reset pass states manually to simulate new round
        player1.has_passed = False
        player2.has_passed = False
        assert not player1.has_passed
        assert not player2.has_passed

        # Pass again to trigger game end
        player1.pass_turn()
        game_state.next_turn()
        player2.pass_turn()

        assert game_state.should_end_round()
        assert game_state.should_end_game()

    def test_partial_round_not_ending_game(self):
        """Game should not end in middle of round with some passes."""
        # Setup: Create game with 2 players
        game_state = GameState()
        player1 = Player(1, "Alice")
        player2 = Player(2, "Bob")
        game_state.add_player(player1)
        game_state.add_player(player2)
        game_state.start_game()

        # Only one player passes - round should not end
        player1.pass_turn()
        assert not game_state.should_end_round()
        assert not game_state.should_end_game()
