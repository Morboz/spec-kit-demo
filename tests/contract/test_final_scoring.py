"""
Contract tests for final score calculation.

This module contains contract tests that verify the final score calculation
according to Blokus scoring rules:
- +1 point per square placed on the board
- -1 point per unplaced square
- +15 bonus for placing all pieces
"""

from src.game.scoring import ScoringSystem
from src.models.game_state import GameState
from src.models.player import Player


class TestFinalScoring:
    """Contract tests for final score calculation."""

    def test_calculate_final_scores_returns_dict(self):
        """Should return dictionary mapping player_id to score."""
        # Setup: Create game with 2 players
        game_state = GameState()
        player1 = Player(1, "Alice")
        player2 = Player(2, "Bob")
        game_state.add_player(player1)
        game_state.add_player(player2)
        game_state.start_game()

        # Calculate final scores
        scores = ScoringSystem.calculate_final_scores(game_state)

        # Verify structure
        assert isinstance(scores, dict)
        assert len(scores) == 2
        assert 1 in scores
        assert 2 in scores
        assert all(isinstance(score, int) for score in scores.values())

    def test_squares_placed_scoring(self):
        """Should award +1 point per square placed."""
        # Setup: Create game with 2 players, one with some pieces placed
        game_state = GameState()
        player1 = Player(1, "Alice")
        player2 = Player(2, "Bob")
        game_state.add_player(player1)
        game_state.add_player(player2)
        game_state.start_game()

        # Place 5 squares total
        # Place a piece with 5 squares (simulate)
        for piece in player1.get_all_pieces()[:1]:
            piece.is_placed = True

        # Calculate score
        score = ScoringSystem._calculate_player_score(player1)

        # Score should account for placed squares
        placed_squares = ScoringSystem.calculate_squares_placed(player1)
        assert placed_squares > 0

    def test_unplaced_squares_scoring(self):
        """Should subtract -1 point per unplaced square."""
        # Setup: Create game with 2 players
        game_state = GameState()
        player1 = Player(1, "Alice")
        player2 = Player(2, "Bob")
        game_state.add_player(player1)
        game_state.add_player(player2)
        game_state.start_game()

        # Keep all pieces unplaced
        unplaced_squares = ScoringSystem.calculate_squares_remaining(player1)

        # Calculate score
        score = ScoringSystem._calculate_player_score(player1)

        # Score should be negative due to unplaced squares
        # Starting with unplaced squares (21 pieces, varying sizes)
        assert unplaced_squares > 0
        # Score will be negative because placed_squares = 0
        assert score < 0

    def test_all_pieces_bonus(self):
        """Should award +15 bonus for placing all pieces."""
        # Setup: Create game with 2 players
        game_state = GameState()
        player1 = Player(1, "Alice")
        player2 = Player(2, "Bob")
        game_state.add_player(player1)
        game_state.add_player(player2)
        game_state.start_game()

        # Place all pieces
        for piece in player1.get_all_pieces():
            piece.is_placed = True

        # Verify bonus eligibility
        assert ScoringSystem.check_bonus_eligibility(player1)

        # Calculate score with bonus
        score = ScoringSystem._calculate_player_score(player1)
        breakdown = ScoringSystem.get_score_breakdown(player1)

        # Should have all_pieces_bonus of 15
        assert breakdown["all_pieces_bonus"] == 15
        assert score >= 15  # At least the bonus

    def test_partial_pieces_no_bonus(self):
        """Should not award bonus for partial pieces placed."""
        # Setup: Create game with 2 players
        game_state = GameState()
        player1 = Player(1, "Alice")
        player2 = Player(2, "Bob")
        game_state.add_player(player1)
        game_state.add_player(player2)
        game_state.start_game()

        # Place only some pieces
        pieces_to_place = player1.get_all_pieces()[:10]  # Place half
        for piece in pieces_to_place:
            piece.is_placed = True

        # Verify not eligible for bonus
        assert not ScoringSystem.check_bonus_eligibility(player1)

        # Calculate score without bonus
        breakdown = ScoringSystem.get_score_breakdown(player1)

        # Should have all_pieces_bonus of 0
        assert breakdown["all_pieces_bonus"] == 0

    def test_score_breakdown_structure(self):
        """Score breakdown should contain all score components."""
        # Setup: Create game with 2 players
        game_state = GameState()
        player1 = Player(1, "Alice")
        player2 = Player(2, "Bob")
        game_state.add_player(player1)
        game_state.add_player(player2)
        game_state.start_game()

        # Place some pieces
        for piece in player1.get_all_pieces()[:5]:
            piece.is_placed = True

        # Get score breakdown
        breakdown = ScoringSystem.get_score_breakdown(player1)

        # Verify all required keys present
        assert "placed_squares" in breakdown
        assert "unplaced_squares" in breakdown
        assert "base_score" in breakdown
        assert "all_pieces_bonus" in breakdown
        assert "final_score" in breakdown

        # Verify all values are integers
        assert all(isinstance(v, int) for v in breakdown.values())

        # Verify score calculation
        expected_base = breakdown["placed_squares"] - breakdown["unplaced_squares"]
        assert breakdown["base_score"] == expected_base

        expected_final = breakdown["base_score"] + breakdown["all_pieces_bonus"]
        assert breakdown["final_score"] == expected_final

    def test_determine_winner_single(self):
        """Should correctly identify single winner."""
        # Setup: Create game with 2 players with different placed pieces
        game_state = GameState()
        player1 = Player(1, "Alice")
        player2 = Player(2, "Bob")
        game_state.add_player(player1)
        game_state.add_player(player2)
        game_state.start_game()

        # Player1 places more pieces (will have higher score)
        for piece in player1.get_all_pieces():
            piece.is_placed = True
        for piece in player2.get_all_pieces()[:-5]:  # Leave 5 unplaced
            piece.is_placed = True

        # Determine winner using scoring system
        winners = ScoringSystem.determine_winner(game_state)

        # Should return single winner (player1 with all pieces)
        assert len(winners) == 1
        assert winners[0] == player1

    def test_determine_winner_tie(self):
        """Should correctly identify all winners in tie."""
        # Setup: Create game with 2 players with same scores
        game_state = GameState()
        player1 = Player(1, "Alice")
        player2 = Player(2, "Bob")
        game_state.add_player(player1)
        game_state.add_player(player2)
        game_state.start_game()

        # Set same scores
        player1.score = 50
        player2.score = 50

        # Determine winners
        winners = ScoringSystem.determine_winner(game_state)

        # Should return both players
        assert len(winners) == 2
        assert player1 in winners
        assert player2 in winners

    def test_determine_winner_no_players(self):
        """Should return empty list when no players."""
        # Setup: Create game with no players
        game_state = GameState()

        # Determine winners
        winners = ScoringSystem.determine_winner(game_state)

        # Should return empty list
        assert len(winners) == 0

    def test_rank_players_correct_order(self):
        """Should rank players correctly by score."""
        # Setup: Create game with 3 players with different placed pieces
        game_state = GameState()
        player1 = Player(1, "Alice")
        player2 = Player(2, "Bob")
        player3 = Player(3, "Charlie")
        game_state.add_player(player1)
        game_state.add_player(player2)
        game_state.add_player(player3)
        game_state.start_game()

        # Different numbers of pieces placed
        for piece in player1.get_all_pieces()[:5]:  # Fewest
            piece.is_placed = True
        for piece in player2.get_all_pieces():  # Most
            piece.is_placed = True
        for piece in player3.get_all_pieces()[:-2]:  # Medium
            piece.is_placed = True

        # Rank players
        ranked = ScoringSystem.rank_players(game_state)

        # Should be sorted by score (descending)
        assert len(ranked) == 3
        assert ranked[0] == (1, 2, "Bob")  # Highest (all pieces)
        assert ranked[1] == (2, 3, "Charlie")  # Second (almost all)
        assert ranked[2] == (3, 1, "Alice")  # Third (fewest)

    def test_rank_players_tie_handling(self):
        """Should handle ties in ranking correctly."""
        # Setup: Create game with 3 players where 2 tie
        game_state = GameState()
        player1 = Player(1, "Alice")
        player2 = Player(2, "Bob")
        player3 = Player(3, "Charlie")
        game_state.add_player(player1)
        game_state.add_player(player2)
        game_state.add_player(player3)
        game_state.start_game()

        # Two players place same number, third places fewer
        for piece in player1.get_all_pieces()[:-3]:  # Leave 3
            piece.is_placed = True
        for piece in player2.get_all_pieces()[:-3]:  # Leave 3 (same as player1)
            piece.is_placed = True
        for piece in player3.get_all_pieces()[:-8]:  # Leave 8 (fewer)
            piece.is_placed = True

        # Rank players
        ranked = ScoringSystem.rank_players(game_state)

        # Verify tie handling (both get rank 1)
        assert len(ranked) == 3
        # First two should have rank 1 (tied)
        assert ranked[0][0] == 1  # rank
        assert ranked[1][0] == 1  # rank
        assert ranked[2][0] == 3  # Charlie gets rank 3 (not 2)

    def test_calculate_squares_placed(self):
        """Should calculate total squares placed correctly."""
        # Setup: Create player
        player = Player(1, "Alice")

        # Place some pieces
        placed_count = 0
        for piece in player.get_all_pieces()[:3]:
            piece.is_placed = True
            placed_count += piece.size

        # Calculate squares placed
        squares = ScoringSystem.calculate_squares_placed(player)

        # Should match total size of placed pieces
        assert squares == placed_count

    def test_calculate_squares_remaining(self):
        """Should calculate total squares remaining correctly."""
        # Setup: Create player
        player = Player(1, "Alice")

        # Place some pieces
        for piece in player.get_all_pieces()[:5]:
            piece.is_placed = True

        # Calculate squares remaining
        remaining = ScoringSystem.calculate_squares_remaining(player)

        # Should match total size of unplaced pieces
        total_size = sum(piece.size for piece in player.get_all_pieces())
        placed_size = sum(piece.size for piece in player.get_placed_pieces())
        expected = total_size - placed_size

        assert remaining == expected

    def test_update_player_score(self):
        """Should update player's score attribute."""
        # Setup: Create game with 2 players
        game_state = GameState()
        player1 = Player(1, "Alice")
        player2 = Player(2, "Bob")
        game_state.add_player(player1)
        game_state.add_player(player2)
        game_state.start_game()

        # Place some pieces
        for piece in player1.get_all_pieces()[:3]:
            piece.is_placed = True

        # Update score
        ScoringSystem.update_player_score(player1)

        # Player's score should be updated
        assert player1.get_score() == ScoringSystem._calculate_player_score(player1)

    def test_final_score_calculation_complete_game(self):
        """Test complete score calculation for full game scenario."""
        # Setup: Create game with 2 players
        game_state = GameState()
        player1 = Player(1, "Alice")
        player2 = Player(2, "Bob")
        game_state.add_player(player1)
        game_state.add_player(player2)
        game_state.start_game()

        # Player 1: Place all pieces
        for piece in player1.get_all_pieces():
            piece.is_placed = True

        # Player 2: Place half pieces
        for piece in player2.get_all_pieces()[:10]:
            piece.is_placed = True

        # Calculate final scores
        scores = ScoringSystem.calculate_final_scores(game_state)

        # Player 1 should have bonus for all pieces
        breakdown1 = ScoringSystem.get_score_breakdown(player1)
        assert breakdown1["all_pieces_bonus"] == 15
        assert scores[1] > 0  # Should be positive with bonus

        # Player 2 should not have bonus
        breakdown2 = ScoringSystem.get_score_breakdown(player2)
        assert breakdown2["all_pieces_bonus"] == 0
