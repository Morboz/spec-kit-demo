"""
Test AI Pass Turn and Piece Inventory Switching

This module tests the scenario where AI players pass their turn
and verifies that the piece inventory correctly switches to the
next player (especially from AI to human player).
"""

import pytest

from blokus_game.game.turn_manager import TurnManager
from blokus_game.models.ai_config import Difficulty
from blokus_game.models.board import Board
from blokus_game.models.game_mode import GameMode, GameModeType
from blokus_game.models.game_state import GameState
from blokus_game.models.player import Player


class TestAIPassTurnInventory:
    """Test AI pass turn behavior and inventory switching."""

    def test_three_ai_mode_configuration(self):
        """Test that Three AI mode is correctly configured."""
        # Given: Three AI mode
        game_mode = GameMode.three_ai(Difficulty.MEDIUM)

        # Then: Configuration is correct
        assert game_mode.mode_type == GameModeType.THREE_AI
        assert game_mode.human_player_position == 1
        assert len(game_mode.ai_players) == 3
        assert game_mode.ai_players[0].position == 2
        assert game_mode.ai_players[1].position == 3
        assert game_mode.ai_players[2].position == 4

    def test_ai_pass_advances_to_next_player(self):
        """Test that when AI passes, turn advances to next player."""
        # Given: Game state with multiple players
        board = Board()
        game_state = GameState(board=board)

        player1 = Player(player_id=1, name="Human")
        player2 = Player(player_id=2, name="AI1")
        player3 = Player(player_id=3, name="AI2")
        player4 = Player(player_id=4, name="AI3")

        game_state.add_player(player1)
        game_state.add_player(player2)
        game_state.add_player(player3)
        game_state.add_player(player4)
        game_state.start_game()

        # Set current player to AI (player 2)
        game_state.current_player_index = 1  # Player 2

        # When: AI player passes turn
        current_player = game_state.get_current_player()
        assert current_player.player_id == 2
        current_player.pass_turn()

        turn_manager = TurnManager(game_state)
        next_player = turn_manager.advance_to_next_active_player()

        # Then: Turn advances to player 3
        assert next_player is not None
        assert next_player.player_id == 3

    def test_ai_pass_skips_already_passed_players(self):
        """Test that advance_to_next_active_player skips players who already passed."""
        # Given: Game state where some players have already passed
        board = Board()
        game_state = GameState(board=board)

        player1 = Player(player_id=1, name="Human")
        player2 = Player(player_id=2, name="AI1")
        player3 = Player(player_id=3, name="AI2")
        player4 = Player(player_id=4, name="AI3")

        game_state.add_player(player1)
        game_state.add_player(player2)
        game_state.add_player(player3)
        game_state.add_player(player4)
        game_state.start_game()

        # Player 3 and 4 have already passed
        player3.pass_turn()
        player4.pass_turn()

        # Current player is AI (player 2)
        game_state.current_player_index = 1  # Player 2
        current_player = game_state.get_current_player()
        assert current_player.player_id == 2
        current_player.pass_turn()

        # When: Advance to next active player
        turn_manager = TurnManager(game_state)
        next_player = turn_manager.advance_to_next_active_player()

        # Then: Should skip player 3 and 4 (already passed) and go to player 1
        assert next_player is not None
        assert next_player.player_id == 1
        assert not next_player.has_passed

    def test_ai_pass_to_human_player(self):
        """Test specific scenario: AI pass → Human player (Three AI mode)."""
        # Given: Three AI mode game state
        board = Board()
        game_state = GameState(board=board)

        player1 = Player(player_id=1, name="Human")
        player2 = Player(player_id=2, name="AI1")
        player3 = Player(player_id=3, name="AI2")
        player4 = Player(player_id=4, name="AI3")

        game_state.add_player(player1)
        game_state.add_player(player2)
        game_state.add_player(player3)
        game_state.add_player(player4)
        game_state.start_game()

        game_mode = GameMode.three_ai(Difficulty.MEDIUM)

        # AI players 2, 3, 4 have all passed
        player2.pass_turn()
        player3.pass_turn()
        player4.pass_turn()

        # Current player is AI (player 4)
        game_state.current_player_index = 3  # Player 4

        # When: Advance to next player
        turn_manager = TurnManager(game_state)
        next_player = turn_manager.advance_to_next_active_player()

        # Then: Should advance to human player (player 1)
        assert next_player is not None
        assert next_player.player_id == 1
        assert not game_mode.is_ai_turn(next_player.player_id)
        assert not next_player.has_passed

    def test_turn_manager_is_player_eligible_checks_passed_status(self):
        """Test that _is_player_eligible correctly checks has_passed status."""
        # Given: Game state with players
        board = Board()
        game_state = GameState(board=board)

        player1 = Player(player_id=1, name="Player1")
        player2 = Player(player_id=2, name="Player2")

        game_state.add_player(player1)
        game_state.add_player(player2)
        game_state.start_game()

        turn_manager = TurnManager(game_state)

        # When: Player has not passed
        assert turn_manager._is_player_eligible(player1) is True

        # When: Player has passed
        player1.pass_turn()
        assert turn_manager._is_player_eligible(player1) is False

        # When: Player has no pieces remaining
        # Remove all pieces manually
        for piece in player2.pieces.values():
            piece.is_placed = True
        assert turn_manager._is_player_eligible(player2) is False

    def test_consecutive_ai_passes_reach_human(self):
        """Test that multiple consecutive AI passes eventually reach human player."""
        # Given: Three AI mode with all AIs having no moves
        board = Board()
        game_state = GameState(board=board)

        player1 = Player(player_id=1, name="Human")
        player2 = Player(player_id=2, name="AI1")
        player3 = Player(player_id=3, name="AI2")
        player4 = Player(player_id=4, name="AI3")

        game_state.add_player(player1)
        game_state.add_player(player2)
        game_state.add_player(player3)
        game_state.add_player(player4)
        game_state.start_game()

        # Start from AI player 2
        game_state.current_player_index = 1  # Player 2

        turn_manager = TurnManager(game_state)

        # Simulate AI 2 passes
        player2.pass_turn()
        next_player = turn_manager.advance_to_next_active_player()
        assert next_player.player_id == 3

        # Simulate AI 3 passes
        player3.pass_turn()
        next_player = turn_manager.advance_to_next_active_player()
        assert next_player.player_id == 4

        # Simulate AI 4 passes
        player4.pass_turn()
        next_player = turn_manager.advance_to_next_active_player()

        # Should reach human player 1
        assert next_player.player_id == 1
        assert not next_player.has_passed

    def test_get_eligible_players_excludes_passed_players(self):
        """Test that get_eligible_players excludes players who have passed."""
        # Given: Game state with some passed players
        board = Board()
        game_state = GameState(board=board)

        player1 = Player(player_id=1, name="Player1")
        player2 = Player(player_id=2, name="Player2")
        player3 = Player(player_id=3, name="Player3")

        game_state.add_player(player1)
        game_state.add_player(player2)
        game_state.add_player(player3)
        game_state.start_game()

        turn_manager = TurnManager(game_state)

        # When: No one has passed
        eligible = turn_manager.get_eligible_players()
        assert len(eligible) == 3

        # When: One player passes
        player2.pass_turn()
        eligible = turn_manager.get_eligible_players()
        assert len(eligible) == 2
        assert player2 not in eligible

        # When: All players pass
        player1.pass_turn()
        player3.pass_turn()
        eligible = turn_manager.get_eligible_players()
        assert len(eligible) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
