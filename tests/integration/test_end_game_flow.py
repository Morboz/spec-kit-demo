"""
Integration test for complete end game flow.

This module contains integration tests that verify the complete flow from
game play through game end detection, score calculation, and winner determination.
"""

from blokus_game.game.scoring import ScoringSystem
from blokus_game.models.game_state import GamePhase, GameState
from blokus_game.models.player import Player


class TestEndGameFlow:
    """Integration tests for complete end game flow."""

    def test_complete_game_flow_all_pieces_placed(self):
        """Test full game flow when all players place all pieces."""
        # Setup: Create game with 2 players
        game_state = GameState()
        player1 = Player(1, "Alice")
        player2 = Player(2, "Bob")
        game_state.add_player(player1)
        game_state.add_player(player2)
        game_state.start_game()

        # Simulate placing all pieces for player1, most for player2
        for piece in player1.get_all_pieces():
            piece.is_placed = True
        for piece in player2.get_all_pieces()[:-3]:  # Leave 3 pieces unplaced
            piece.is_placed = True

        # Player2 passes to end the game
        player2.pass_turn()
        player1.pass_turn()

        # Game should end when all active players have passed
        assert game_state.should_end_game()

        # End the game
        game_state.end_game()
        assert game_state.is_game_over()

        # Calculate final scores
        final_scores = ScoringSystem.calculate_final_scores(game_state)
        assert len(final_scores) == 2

        # Player1 should have bonus for placing all pieces
        breakdown1 = ScoringSystem.get_score_breakdown(player1)
        assert breakdown1["all_pieces_bonus"] == 15

        # Player2 should not have bonus
        breakdown2 = ScoringSystem.get_score_breakdown(player2)
        assert breakdown2["all_pieces_bonus"] == 0

        # Update player scores before determining winners
        ScoringSystem.update_player_score(player1)
        ScoringSystem.update_player_score(player2)

        # Determine winners - player1 should win
        winners = game_state.get_winners()
        assert len(winners) == 1  # One winner
        assert winners[0] == player1

    def test_complete_game_flow_all_players_pass(self):
        """Test full game flow when all players pass consecutively."""
        # Setup: Create game with 3 players
        game_state = GameState()
        player1 = Player(1, "Alice")
        player2 = Player(2, "Bob")
        player3 = Player(3, "Charlie")
        game_state.add_player(player1)
        game_state.add_player(player2)
        game_state.add_player(player3)
        game_state.start_game()

        # Simulate some moves, then all players pass
        # Place a few pieces
        for piece in player1.get_all_pieces()[:3]:
            piece.is_placed = True
        for piece in player2.get_all_pieces()[:5]:
            piece.is_placed = True
        for piece in player3.get_all_pieces()[:2]:
            piece.is_placed = True

        # All players pass
        player1.pass_turn()
        game_state.next_turn()
        player2.pass_turn()
        game_state.next_turn()
        player3.pass_turn()

        # Round should end
        assert game_state.should_end_round()

        # Start new round
        game_state.next_turn()
        assert game_state.get_round_number() == 2

        # All players pass again - this time game ends
        player1.pass_turn()
        game_state.next_turn()
        player2.pass_turn()
        game_state.next_turn()
        player3.pass_turn()

        # Game should end
        assert game_state.should_end_game()

        # End the game
        game_state.end_game()

        # Verify game over state
        assert game_state.is_game_over()
        assert game_state.phase == GamePhase.GAME_OVER

        # Calculate final scores
        final_scores = ScoringSystem.calculate_final_scores(game_state)
        assert len(final_scores) == 3

        # Determine winners
        winners = game_state.get_winners()
        assert len(winners) >= 1

    def test_complete_game_flow_mixed_pass_and_inactive(self):
        """Test game flow with mix of passes and inactive players."""
        # Setup: Create game with 4 players
        game_state = GameState()
        player1 = Player(1, "Alice")
        player2 = Player(2, "Bob")
        player3 = Player(3, "Charlie")
        player4 = Player(4, "Diana")
        game_state.add_player(player1)
        game_state.add_player(player2)
        game_state.add_player(player3)
        game_state.add_player(player4)
        game_state.start_game()

        # Some players place pieces, others become inactive
        for piece in player1.get_all_pieces():
            piece.is_placed = True
        for piece in player2.get_all_pieces()[:10]:
            piece.is_placed = True
        player3.set_inactive()
        for piece in player4.get_all_pieces()[:8]:
            piece.is_placed = True

        # Active players pass
        player1.pass_turn()
        game_state.next_turn()
        player2.pass_turn()
        game_state.next_turn()
        # player3 is inactive
        game_state.next_turn()
        player4.pass_turn()

        # Round ends
        assert game_state.should_end_round()

        # Next round, all remaining active players pass again
        game_state.next_turn()  # Round 2
        player1.pass_turn()
        game_state.next_turn()
        player2.pass_turn()
        game_state.next_turn()
        player4.pass_turn()

        # Game should end
        assert game_state.should_end_game()

        # End the game and verify
        game_state.end_game()
        assert game_state.is_game_over()

        # Calculate final scores and rankings
        final_scores = ScoringSystem.calculate_final_scores(game_state)
        ranked = ScoringSystem.rank_players(game_state)

        assert len(final_scores) == 4
        assert len(ranked) == 4
        assert ranked[0][0] == 1  # First place

    def test_score_calculation_consistency(self):
        """Test that score calculation is consistent across methods."""
        # Setup: Create game with 2 players
        game_state = GameState()
        player1 = Player(1, "Alice")
        player2 = Player(2, "Bob")
        game_state.add_player(player1)
        game_state.add_player(player2)
        game_state.start_game()

        # Place different numbers of pieces
        for piece in player1.get_all_pieces()[:7]:
            piece.is_placed = True
        for piece in player2.get_all_pieces()[:5]:
            piece.is_placed = True

        # End game
        game_state.end_game()

        # Update player scores from final calculation
        for player in [player1, player2]:
            ScoringSystem.update_player_score(player)

        # Calculate scores using different methods
        scores_dict = ScoringSystem.calculate_final_scores(game_state)
        winners = game_state.get_winners()
        breakdown1 = ScoringSystem.get_score_breakdown(player1)
        breakdown2 = ScoringSystem.get_score_breakdown(player2)

        # Verify consistency
        assert scores_dict[1] == breakdown1["final_score"]
        assert scores_dict[2] == breakdown2["final_score"]

        # Verify winners match highest score
        if winners:
            max_score = max(scores_dict.values())
            # Winners should have the calculated score, not their attribute
            for w in winners:
                assert scores_dict[w.player_id] == max_score

    def test_game_end_state_isolated_from_play_state(self):
        """Test that game end state is properly isolated from play state."""
        # Setup: Create game with 2 players
        game_state = GameState()
        player1 = Player(1, "Alice")
        player2 = Player(2, "Bob")
        game_state.add_player(player1)
        game_state.add_player(player2)
        game_state.start_game()

        # Play some pieces
        for piece in player1.get_all_pieces()[:5]:
            piece.is_placed = True

        # Verify playing phase
        assert game_state.is_playing_phase()
        assert not game_state.is_game_over()

        # All players pass to end game
        player1.pass_turn()
        game_state.next_turn()
        player2.pass_turn()

        # End game
        game_state.end_game()

        # Verify game over state
        assert game_state.is_game_over()
        assert not game_state.is_playing_phase()

        # Verify next_turn doesn't change game over state
        initial_phase = game_state.phase
        game_state.next_turn()
        assert game_state.phase == initial_phase

        # Verify move recording still works
        game_state.record_move(1, "I1", 10, 10)
        assert len(game_state.get_move_history()) > 0

    def test_multiple_game_scenarios(self):
        """Test multiple different game end scenarios."""
        scenarios = [
            {"players": 2, "active_after_round_1": 2, "winners_expected": 1},
            {"players": 3, "active_after_round_1": 3, "winners_expected": 1},
            {"players": 4, "active_after_round_1": 2, "winners_expected": 2},  # Tie
        ]

        for i, scenario in enumerate(scenarios):
            # Setup
            game_state = GameState()
            players = [
                Player(j + 1, f"Player{j + 1}") for j in range(scenario["players"])
            ]
            for player in players:
                game_state.add_player(player)
            game_state.start_game()

            # Place varying numbers of pieces
            for j, player in enumerate(players):
                pieces_to_place = j + 3  # Different amounts
                for piece in player.get_all_pieces()[:pieces_to_place]:
                    piece.is_placed = True

            # End game
            for player in players:
                player.pass_turn()
                game_state.next_turn()
            game_state.end_game()

            # Verify
            assert game_state.is_game_over()
            winners = game_state.get_winners()
            assert len(winners) >= 1
            assert len(winners) <= scenario["players"]

            # Verify score calculation works
            scores = ScoringSystem.calculate_final_scores(game_state)
            assert len(scores) == scenario["players"]

    def test_game_loop_integration(self):
        """Test integration with game state transitions."""
        # Setup
        game_state = GameState()
        player1 = Player(1, "Alice")
        player2 = Player(2, "Bob")
        game_state.add_player(player1)
        game_state.add_player(player2)
        game_state.start_game()

        # Initial state
        assert game_state.is_playing_phase()
        assert game_state.get_current_player() == player1

        # Simulate turn progression with passes
        player1.pass_turn()
        game_state.next_turn()
        assert game_state.get_current_player() == player2

        player2.pass_turn()
        game_state.next_turn()

        # New round
        assert game_state.get_round_number() == 2

        # Second round passes
        player1.pass_turn()
        game_state.next_turn()
        player2.pass_turn()

        # Game should end
        assert game_state.should_end_game()

        # End game
        game_state.end_game()

        # Verify final state
        assert game_state.is_game_over()
        assert game_state.phase == GamePhase.GAME_OVER

        # Verify winner determination works
        winners = game_state.get_winners()
        assert isinstance(winners, list)

        # Verify scores are calculated
        final_scores = ScoringSystem.calculate_final_scores(game_state)
        assert isinstance(final_scores, dict)
        assert len(final_scores) == 2
