"""
Contract test for score calculation accuracy.

This test verifies that the ScoringSystem accurately calculates scores
according to Blokus rules:
- +1 point per square placed on the board
- -1 point for each remaining square not placed
- +15 points bonus for placing all pieces
"""

from blokus_game.config.pieces import PIECE_DEFINITIONS
from blokus_game.game.scoring import ScoringSystem
from blokus_game.models.player import Player


class TestScoreCalculation:
    """Test suite for score calculation accuracy."""

    def test_calculate_score_with_no_pieces_placed(self):
        """
        Test score calculation when no pieces are placed.

        Expected: Score should be 0 (no placed squares, no unplaced penalty)
        """
        player = Player(player_id=1, name="Test Player")
        # Don't place any pieces

        breakdown = ScoringSystem.get_score_breakdown(player)

        assert breakdown["placed_squares"] == 0
        assert breakdown["unplaced_squares"] == 89  # Total squares in all pieces
        assert breakdown["base_score"] == -89
        assert breakdown["all_pieces_bonus"] == 0
        assert breakdown["final_score"] == -89

    def test_calculate_score_with_all_pieces_placed(self):
        """
        Test score calculation when all pieces are placed.

        Expected: Score should be 89 + 15 = 104
        (89 squares + 15 bonus for placing all pieces)
        """
        player = Player(player_id=1, name="Test Player")

        # Place all 21 pieces (total 89 squares)
        piece_names = list(PIECE_DEFINITIONS.keys())
        for piece_name in piece_names:
            piece = player.get_piece(piece_name)
            piece.place_at(0, 0)

        breakdown = ScoringSystem.get_score_breakdown(player)

        assert breakdown["placed_squares"] == 89
        assert breakdown["unplaced_squares"] == 0
        assert breakdown["base_score"] == 89
        assert breakdown["all_pieces_bonus"] == 15
        assert breakdown["final_score"] == 104

    def test_calculate_score_with_partial_pieces(self):
        """
        Test score calculation with some pieces placed.

        Expected: Score should be (placed - unplaced) with no bonus
        """
        player = Player(player_id=1, name="Test Player")

        # Place only first few pieces
        piece_names = list(PIECE_DEFINITIONS.keys())[:5]
        for piece_name in piece_names:
            piece = player.get_piece(piece_name)
            piece.place_at(0, 0)

        placed_count = sum(
            len(coords) for name, coords in list(PIECE_DEFINITIONS.items())[:5]
        )
        unplaced_count = 89 - placed_count

        breakdown = ScoringSystem.get_score_breakdown(player)

        assert breakdown["placed_squares"] == placed_count
        assert breakdown["unplaced_squares"] == unplaced_count
        assert breakdown["base_score"] == placed_count - unplaced_count
        assert breakdown["all_pieces_bonus"] == 0
        assert breakdown["final_score"] == placed_count - unplaced_count

    def test_calculate_squares_placed(self):
        """Test calculation of total squares placed."""
        player = Player(player_id=1, name="Test Player")

        # Initially no pieces placed
        assert ScoringSystem.calculate_squares_placed(player) == 0

        # Place a few pieces
        piece1 = player.get_piece("I2")
        piece1.place_at(0, 0)  # 2 squares
        piece2 = player.get_piece("I3")
        piece2.place_at(0, 0)  # 3 squares

        assert ScoringSystem.calculate_squares_placed(player) == 5

    def test_calculate_squares_remaining(self):
        """Test calculation of total squares remaining."""
        player = Player(player_id=1, name="Test Player")

        # Initially all squares remaining
        assert ScoringSystem.calculate_squares_remaining(player) == 89

        # Place a few pieces
        piece1 = player.get_piece("I2")
        piece1.place_at(0, 0)  # 2 squares
        piece2 = player.get_piece("I3")
        piece2.place_at(0, 0)  # 3 squares

        assert ScoringSystem.calculate_squares_remaining(player) == 84

    def test_score_calculation_matches_breakdown(self):
        """Test that update_player_score produces same result as get_score_breakdown."""
        player = Player(player_id=1, name="Test Player")

        # Place some pieces
        piece_names = list(PIECE_DEFINITIONS.keys())[:10]
        for piece_name in piece_names:
            piece = player.get_piece(piece_name)
            piece.place_at(0, 0)

        # Get breakdown
        breakdown = ScoringSystem.get_score_breakdown(player)
        expected_score = breakdown["final_score"]

        # Update score using update_player_score
        ScoringSystem.update_player_score(player)

        # Player's score should match breakdown
        assert player.score == expected_score

    def test_calculate_final_scores_consistency(self):
        """
        Test that calculate_final_scores is consistent with individual player scores.
        """
        from blokus_game.models.game_state import GameState

        player = Player(player_id=1, name="Test Player")

        # Place some pieces
        piece_names = list(PIECE_DEFINITIONS.keys())[:7]
        for piece_name in piece_names:
            piece = player.get_piece(piece_name)
            piece.place_at(0, 0)

        # Get individual score
        individual_score = ScoringSystem._calculate_player_score(player)

        # Get score from final scores dict
        game_state = GameState()
        game_state.players = [player]
        final_scores = ScoringSystem.calculate_final_scores(game_state)
        dict_score = final_scores[1]

        # They should match
        assert individual_score == dict_score

    def test_ranking_players_by_score(self):
        """Test ranking of players by final scores."""
        from blokus_game.models.game_state import GameState

        # Create 3 players
        player1 = Player(player_id=1, name="Player 1")
        player2 = Player(player_id=2, name="Player 2")
        player3 = Player(player_id=3, name="Player 3")

        piece_names = list(PIECE_DEFINITIONS.keys())

        # Player 1: highest score (places all pieces)
        for piece_name in piece_names:
            piece = player1.get_piece(piece_name)
            piece.place_at(0, 0)

        # Player 2: medium score (places half)
        for piece_name in piece_names[:10]:
            piece = player2.get_piece(piece_name)
            piece.place_at(0, 0)

        # Player 3: low score (places few)
        for piece_name in piece_names[:3]:
            piece = player3.get_piece(piece_name)
            piece.place_at(0, 0)

        game_state = GameState()
        game_state.players = [player1, player2, player3]

        # Rank players
        ranked = ScoringSystem.rank_players(game_state)

        # Should have 3 players
        assert len(ranked) == 3

        # Player 1 should be rank 1
        rank1_player = next((r for r in ranked if r[0] == 1), None)
        assert rank1_player is not None
        assert rank1_player[1] == 1

        # Player 3 should be rank 3
        rank3_player = next((r for r in ranked if r[0] == 3), None)
        assert rank3_player is not None
        assert rank3_player[1] == 3

    def test_determine_winner_single(self):
        """Test winner determination when there's a clear winner."""
        from blokus_game.models.game_state import GameState

        player1 = Player(player_id=1, name="Winner")
        player2 = Player(player_id=2, name="Loser")

        piece_names = list(PIECE_DEFINITIONS.keys())

        # Player 1 places more pieces
        for piece_name in piece_names[:10]:
            piece = player1.get_piece(piece_name)
            piece.place_at(0, 0)
        for piece_name in piece_names[:5]:
            piece = player2.get_piece(piece_name)
            piece.place_at(0, 0)

        game_state = GameState()
        game_state.players = [player1, player2]

        winners = ScoringSystem.determine_winner(game_state)

        assert len(winners) == 1
        assert winners[0].player_id == 1
