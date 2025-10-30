"""
Comprehensive integration test for complete end game flow.

This module tests the complete end-to-end integration of game end detection,
winner determination, and UI components working together.
"""

import pytest
from unittest.mock import Mock, patch
from src.models.game_state import GameState, GamePhase
from src.models.player import Player
from src.game.game_loop import GameLoop
from src.game.end_game_detector import EndGameDetector
from src.game.winner_determiner import WinnerDeterminer
from src.ui.game_results import GameResults


class TestCompleteEndGameFlow:
    """Comprehensive integration tests for complete game end flow."""

    def test_game_loop_integration_with_end_detection(self):
        """Test that GameLoop properly integrates end game detection."""
        # Setup
        game_state = GameState()
        player1 = Player(1, "Alice")
        player2 = Player(2, "Bob")
        game_state.add_player(player1)
        game_state.add_player(player2)
        game_state.start_game()

        # Create callback tracker
        callback_called = []
        def game_end_callback(gs):
            callback_called.append(gs)

        # Create game loop with callback
        game_loop = GameLoop(
            game_state,
            on_game_end=game_end_callback,
        )

        # Verify initial state
        assert not game_loop.should_end_game()
        assert game_state.is_playing_phase()

        # Simulate game progression - players place some pieces
        for piece in player1.get_all_pieces()[:5]:
            piece.is_placed = True
        for piece in player2.get_all_pieces()[:7]:
            piece.is_placed = True

        # Both players pass in round 1
        game_loop.pass_turn(player1.player_id)
        game_loop.next_turn()
        game_loop.pass_turn(player2.player_id)
        game_loop.next_turn()

        # Round 1 ended with passes, round 2 starts
        # Players pass again - now game should end
        game_loop.pass_turn(player1.player_id)
        game_loop.next_turn()
        game_loop.pass_turn(player2.player_id)

        # Now game should end (all passed in consecutive rounds)
        assert game_loop.should_end_game()

        # Check game end
        was_ended = game_loop.check_and_handle_game_end()
        assert was_ended
        assert game_state.is_game_over()
        assert len(callback_called) == 1
        assert callback_called[0] == game_state

    def test_end_game_detector_integration(self):
        """Test EndGameDetector integration with GameState."""
        # Setup
        game_state = GameState()
        player1 = Player(1, "Alice")
        player2 = Player(2, "Bob")
        game_state.add_player(player1)
        game_state.add_player(player2)
        game_state.start_game()

        # Create detector
        detector = EndGameDetector(game_state)

        # Test initial state
        assert not detector.should_end_game()
        assert detector.get_end_game_reason() is None
        assert not detector.is_game_over()

        # Simulate all players passing in round 1
        player1.pass_turn()
        player2.pass_turn()

        # Round ends
        assert detector.should_end_round()

        # New round starts after next_turn
        game_state.next_turn()
        # Round 2 starts - players have passed reset
        # They pass again
        player1.pass_turn()
        player2.pass_turn()

        # Now game should end (consecutive rounds with all passes)
        assert detector.should_end_game()
        reason = detector.get_end_game_reason()
        assert reason is not None
        # Check for either "passed" or "active players" in reason
        assert "passed" in reason.lower() or "active" in reason.lower()

        # End game
        detector.end_game()
        assert detector.is_game_over()

    def test_winner_determiner_integration(self):
        """Test WinnerDeterminer integration with ScoringSystem."""
        # Setup
        game_state = GameState()
        player1 = Player(1, "Alice")
        player2 = Player(2, "Bob")
        game_state.add_player(player1)
        game_state.add_player(player2)
        game_state.start_game()

        # Place different numbers of pieces
        for piece in player1.get_all_pieces()[:-5]:  # Leave 5
            piece.is_placed = True
        for piece in player2.get_all_pieces():  # All placed
            piece.is_placed = True

        # End game
        game_state.end_game()

        # Create determiner
        determiner = WinnerDeterminer(game_state)

        # Get scores
        scores = determiner.calculate_final_scores()
        assert len(scores) == 2
        assert scores[2] >= scores[1]  # Player2 placed more or equal

        # Get winners
        winners = determiner.get_winners()
        assert len(winners) >= 1
        assert len(winners) <= 2

        # Verify winners have the highest score (use calculated scores, not player.score)
        max_score = max(scores.values())
        for winner in winners:
            # Compare calculated score, not player's attribute
            assert scores[winner.player_id] == max_score

        # Get winner names
        winner_names = determiner.get_winner_names()
        assert len(winner_names) == len(winners)

        # Test score breakdown
        breakdown = determiner.get_score_breakdown(player2)
        assert "final_score" in breakdown
        # Player2 placed all pieces, should get bonus
        assert breakdown["all_pieces_bonus"] == 15

        # Test ranking
        ranked = determiner.rank_players()
        assert len(ranked) == 2
        assert ranked[0][1] in [1, 2]  # Player1 or Player2 is rank 1

        # Test tie detection (may or may not be tie depending on scores)
        if determiner.is_tie():
            assert len(winners) > 1

        # Test winning score
        winning_score = determiner.get_winning_score()
        assert winning_score == max_score

    def test_complete_flow_all_components(self):
        """Test complete flow using all components together."""
        # Setup
        game_state = GameState()
        player1 = Player(1, "Alice")
        player2 = Player(2, "Bob")
        player3 = Player(3, "Charlie")
        game_state.add_player(player1)
        game_state.add_player(player2)
        game_state.add_player(player3)
        game_state.start_game()

        # Create callback tracker
        callback_data = []
        def game_end_callback(gs):
            callback_data.append(gs)

        # Create game loop
        game_loop = GameLoop(game_state, on_game_end=game_end_callback)

        # Simulate realistic game
        # Round 1: Players place some pieces
        for piece in player1.get_all_pieces()[:8]:
            piece.is_placed = True
        game_loop.next_turn()

        for piece in player2.get_all_pieces()[:6]:
            piece.is_placed = True
        game_loop.next_turn()

        for piece in player3.get_all_pieces()[:10]:
            piece.is_placed = True
        game_loop.next_turn()

        # Round 1 end - all pass
        game_loop.pass_turn(player1.player_id)
        game_loop.next_turn()
        game_loop.pass_turn(player2.player_id)
        game_loop.next_turn()
        game_loop.pass_turn(player3.player_id)

        # Round 2: Continue playing
        for piece in player1.get_all_pieces()[8:12]:
            piece.is_placed = True
        game_loop.next_turn()

        for piece in player2.get_all_pieces()[6:15]:
            piece.is_placed = True
        game_loop.next_turn()

        for piece in player3.get_all_pieces()[10:15]:
            piece.is_placed = True
        game_loop.next_turn()

        # Game continues with passes in round 2
        game_loop.pass_turn(player1.player_id)
        game_loop.next_turn()
        game_loop.pass_turn(player2.player_id)
        game_loop.next_turn()
        game_loop.pass_turn(player3.player_id)

        # Round 3: One more round
        game_loop.next_turn()
        game_loop.pass_turn(player1.player_id)
        game_loop.next_turn()
        game_loop.pass_turn(player2.player_id)
        game_loop.next_turn()
        game_loop.pass_turn(player3.player_id)

        # At this point, all have passed twice - game should end
        assert game_loop.should_end_game()
        assert game_state.should_end_game()

        # End game via loop (callback should only be called once)
        was_ended = game_loop.check_and_handle_game_end()
        assert was_ended
        assert game_state.is_game_over()

        # Verify callback was called once
        assert len(callback_data) == 1

        # Verify winner determination works
        winners = game_loop.get_winners()
        assert len(winners) >= 1
        assert len(winners) <= 3

        # Verify scores calculated
        scores = game_loop.calculate_final_scores()
        assert len(scores) == 3
        assert all(score >= 0 for score in scores.values())

        # Verify update scores works
        game_loop.update_player_scores()
        for player in [player1, player2, player3]:
            assert player.get_score() >= 0

    @pytest.mark.skip(reason="UI integration requires tkinter mainloop")
    def test_game_results_ui_integration(self):
        """Test that GameResults UI can be created with game data."""
        # This test is skipped because it requires running tkinter mainloop
        # In a real integration, this would be tested separately with GUI tests
        pass

    def test_edge_case_no_players(self):
        """Test edge case: game with no players."""
        # Setup
        game_state = GameState()

        # Create loop
        game_loop = GameLoop(game_state)

        # With no players, game should end (no active players)
        assert game_loop.should_end_game()

        # Manual end should work
        game_loop.end_game()
        assert game_loop.is_game_over()

    def test_edge_case_all_inactive_players(self):
        """Test edge case: all players become inactive."""
        # Setup
        game_state = GameState()
        player1 = Player(1, "Alice")
        player2 = Player(2, "Bob")
        game_state.add_player(player1)
        game_state.add_player(player2)
        game_state.start_game()

        # Mark all players inactive
        player1.set_inactive()
        player2.set_inactive()

        # Create detector
        detector = EndGameDetector(game_state)

        # Game should end
        assert detector.should_end_game()
        assert "No active players" in detector.get_end_game_reason()

    def test_callback_functionality(self):
        """Test that game end callback is properly invoked."""
        # Setup
        game_state = GameState()
        player1 = Player(1, "Alice")
        player2 = Player(2, "Bob")
        game_state.add_player(player1)
        game_state.add_player(player2)
        game_state.start_game()

        # Track callback calls
        callback_calls = []

        def track_callback(gs):
            callback_calls.append(gs)

        # Create loop with callback
        game_loop = GameLoop(game_state, on_game_end=track_callback)

        # End game
        game_loop.end_game()

        # Callback should be called immediately (end_game triggers callback)
        assert len(callback_calls) == 1
        assert callback_calls[0] == game_state

    def test_multiple_game_end_checks(self):
        """Test that multiple game end checks don't cause issues."""
        # Setup
        game_state = GameState()
        player1 = Player(1, "Alice")
        player2 = Player(2, "Bob")
        game_state.add_player(player1)
        game_state.add_player(player2)
        game_state.start_game()

        # Create loop
        game_loop = GameLoop(game_state)

        # End game
        was_ended = game_loop.end_game()
        assert game_loop.is_game_over()

        # Check multiple times - should return False since already ended
        assert not game_loop.detect_and_end_game_if_necessary()
        assert not game_loop.detect_and_end_game_if_necessary()
        assert not game_loop.detect_and_end_game_if_necessary()

    def test_score_update_all_players(self):
        """Test updating scores for all players."""
        # Setup
        game_state = GameState()
        player1 = Player(1, "Alice")
        player2 = Player(2, "Bob")
        game_state.add_player(player1)
        game_state.add_player(player2)
        game_state.start_game()

        # Place pieces
        for piece in player1.get_all_pieces()[:10]:
            piece.is_placed = True
        for piece in player2.get_all_pieces()[:5]:
            piece.is_placed = True

        # End game
        game_state.end_game()

        # Create loop
        game_loop = GameLoop(game_state)

        # Initial scores should be 0
        assert player1.get_score() == 0
        assert player2.get_score() == 0

        # Update scores
        game_loop.update_player_scores()

        # Now scores should be calculated
        assert player1.get_score() != 0
        assert player2.get_score() != 0

        # Player1 should have higher score (placed more)
        assert player1.get_score() > player2.get_score()
