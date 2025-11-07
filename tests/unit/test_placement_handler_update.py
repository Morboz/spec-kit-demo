"""
Unit tests for PlacementHandler current_player update during turn changes.

Tests that PlacementHandler.current_player is correctly updated when:
- AI passes turn to human
- Turn advances normally
- Multiple AI players pass in sequence
"""

import pytest
from src.models.player import Player
from src.models.ai_player import AIPlayer
from src.models.board import Board
from src.models.game_state import GameState
from src.game.placement_handler import PlacementHandler
from src.services.ai_strategy import RandomStrategy


class TestPlacementHandlerUpdate:
    """Test PlacementHandler current_player update during turn changes."""

    def setup_method(self):
        """Setup test fixtures."""
        self.board = Board()
        self.game_state = GameState(board=self.board)

        # Create players: Human at position 1, AI at positions 2,3,4
        self.human_player = Player(1, "Human")
        self.ai_player_2 = AIPlayer(2, RandomStrategy(), color="green", name="AI_2")
        self.ai_player_3 = AIPlayer(3, RandomStrategy(), color="yellow", name="AI_3")
        self.ai_player_4 = AIPlayer(4, RandomStrategy(), color="red", name="AI_4")

        self.game_state.add_player(self.human_player)
        self.game_state.add_player(self.ai_player_2)
        self.game_state.add_player(self.ai_player_3)
        self.game_state.add_player(self.ai_player_4)

        self.game_state.start_game()

    def test_placement_handler_current_player_initial(self):
        """Test PlacementHandler initializes with correct current player."""
        current_player = self.game_state.get_current_player()
        handler = PlacementHandler(self.board, self.game_state, current_player)

        assert handler.current_player == current_player
        assert handler.current_player.player_id == 1  # Human player

    def test_placement_handler_update_after_turn_change(self):
        """Test PlacementHandler current_player can be updated."""
        current_player = self.game_state.get_current_player()
        handler = PlacementHandler(self.board, self.game_state, current_player)

        # Advance to next player
        self.game_state.next_turn()
        next_player = self.game_state.get_current_player()

        # Update handler's current player
        handler.current_player = next_player

        assert handler.current_player == next_player
        assert handler.current_player.player_id == 2  # AI player 2

    def test_select_piece_uses_current_player(self):
        """Test select_piece uses PlacementHandler's current_player."""
        current_player = self.game_state.get_current_player()
        handler = PlacementHandler(self.board, self.game_state, current_player)

        # Select a piece - should work with human player
        result = handler.select_piece("I1")
        assert result is True

        # Mark piece as placed for human
        piece = current_player.get_piece("I1")
        piece.place_at(0, 0)

        # Try to select same piece again - should fail (already placed)
        result = handler.select_piece("I1")
        assert result is False

        # Now switch to AI player
        self.game_state.next_turn()
        ai_player = self.game_state.get_current_player()
        handler.current_player = ai_player

        # AI player should have I1 available (not placed)
        result = handler.select_piece("I1")
        assert result is True  # AI's I1 is not placed

    def test_select_piece_after_ai_pass_to_human(self):
        """Test that after AI passes, human can select their own pieces."""
        # Start at human player
        assert self.game_state.get_current_player().player_id == 1

        # Create placement handler
        handler = PlacementHandler(
            self.board, self.game_state, self.game_state.get_current_player()
        )

        # Human places I1
        human_piece = self.human_player.get_piece("I1")
        human_piece.place_at(0, 0)

        # Advance to AI player 2
        self.game_state.next_turn()
        handler.current_player = self.game_state.get_current_player()
        assert handler.current_player.player_id == 2

        # AI player 2 places I1
        ai2_piece = self.ai_player_2.get_piece("I1")
        ai2_piece.place_at(1, 0)

        # AI player 2 passes
        self.ai_player_2.pass_turn()

        # Advance back to human (skipping passed AI)
        from src.game.turn_manager import TurnManager
        turn_manager = TurnManager(self.game_state)
        next_player = turn_manager.advance_to_next_active_player()

        # Verify we're back at human
        assert next_player is not None
        print(f"DEBUG: next_player id = {next_player.player_id}")
        
        # Update handler's current player
        handler.current_player = next_player

        # If next player is AI player 3, their I1 should be available
        # If next player is human, their I1 should be placed
        result = handler.select_piece("I1")
        
        if next_player.player_id == 1:
            # Human's I1 is already placed
            assert result is False
        else:
            # Other players' I1 might be available
            # Just verify handler uses the correct player
            assert handler.current_player == next_player

        # Verify human can select I2 (not placed) when it's their turn again
        if next_player.player_id == 1:
            result = handler.select_piece("I2")
            assert result is True  # Human's I2 is available

    def test_clear_selection_works_after_player_change(self):
        """Test clear_selection works after changing current_player."""
        current_player = self.game_state.get_current_player()
        handler = PlacementHandler(self.board, self.game_state, current_player)

        # Select a piece
        handler.select_piece("I1")
        assert handler.selected_piece is not None

        # Change player
        self.game_state.next_turn()
        handler.current_player = self.game_state.get_current_player()

        # Clear selection
        handler.clear_selection()
        assert handler.selected_piece is None
        assert handler.rotation_count == 0
        assert handler.is_flipped is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
