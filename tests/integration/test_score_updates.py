"""
Integration test for score updates during gameplay.

This test verifies that scores are properly updated throughout the game
as players place pieces, and that the UI reflects these updates correctly.
"""

from blokus_game.config.pieces import PIECE_DEFINITIONS
from blokus_game.game.scoring import ScoringSystem
from blokus_game.models.board import Board
from blokus_game.models.game_state import GameState
from blokus_game.models.piece import Piece
from blokus_game.models.player import Player
from blokus_game.ui.scoreboard import Scoreboard


class TestScoreUpdates:
    """Test suite for score updates during gameplay."""

    def test_score_updates_after_each_piece_placement(self):
        """
        Test that scores update correctly after each piece is placed.
        """
        player = Player(player_id=1, name="Test Player")

        # Track scores after each placement (scores start negative and increase toward 0)
        previous_score = -89  # All squares remaining = -89
        piece_names = list(PIECE_DEFINITIONS.keys())

        for i, piece_name in enumerate(piece_names[:10]):
            # Place piece
            player.place_piece(piece_name, 0, 0)

            # Update score
            ScoringSystem.update_player_score(player)

            # Score should be greater than previous (less negative)
            assert (
                player.score > previous_score
            ), f"Score should increase (be less negative) after placing piece {i+1}"

            previous_score = player.score

    def test_scoreboard_updates_after_placements(self, tkinter_root):
        """
        Test that scoreboard reflects score changes after placements.
        """
        root = tkinter_root  # Use the fixture-provided root

        player = Player(player_id=1, name="Test Player")
        board = Board()

        # Create scoreboard
        scoreboard = Scoreboard(root, board, [player])

        # Initially no pieces placed
        scoreboard.update_scores()
        items = scoreboard.tree.get_children()
        assert len(items) == 1
        initial_values = scoreboard.tree.item(items[0])["values"]
        assert initial_values[1] == 0  # No squares placed

        # Place some pieces
        piece_names = list(PIECE_DEFINITIONS.keys())
        for piece_name in piece_names[:5]:
            player.place_piece(piece_name, 10, 10)
            piece = Piece(piece_name)
            board.place_piece(piece, 10, 10, player.player_id)

        # Update scoreboard
        scoreboard.update_scores()

        # Check that squares placed updated
        items = scoreboard.tree.get_children()
        updated_values = scoreboard.tree.item(items[0])["values"]
        assert updated_values[1] == 25  # 5 pieces placed

        # Check pieces remaining updated
        assert updated_values[2] == 16  # 21 - 5 = 16 pieces remaining

    def test_score_updates_tracked_throughout_game(self):
        """
        Test that scores are properly tracked throughout the entire game.
        """
        player1 = Player(player_id=1, name="Player 1")
        player2 = Player(player_id=2, name="Player 2")

        game_state = GameState()
        game_state.players = [player1, player2]

        # Track score history (scores start at -89 with all squares remaining)
        player1_scores = [-89]
        player2_scores = [-89]
        piece_names = list(PIECE_DEFINITIONS.keys())

        # Simulate turns where players place pieces
        for i in range(20):
            if i % 2 == 0:  # Player 1's turn
                if i < 12:
                    piece_name = piece_names[i // 2]
                    player1.place_piece(piece_name, 0, 0)
                    ScoringSystem.update_player_score(player1)
                    player1_scores.append(player1.score)
            elif i < 14:
                piece_name = piece_names[(i + 1) // 2]
                player2.place_piece(piece_name, 0, 0)
                ScoringSystem.update_player_score(player2)
                player2_scores.append(player2.score)

        # Both players should have increasing scores
        for i in range(1, len(player1_scores)):
            assert (
                player1_scores[i] >= player1_scores[i - 1]
            ), f"Player 1's score should not decrease at turn {i}"

        for i in range(1, len(player2_scores)):
            assert (
                player2_scores[i] >= player2_scores[i - 1]
            ), f"Player 2's score should not decrease at turn {i}"

    def test_real_time_score_update_trigger(self):
        """
        Test that score updates are triggered correctly during game loop.
        """
        player = Player(player_id=1, name="Test Player")
        board = Board()
        piece_names = list(PIECE_DEFINITIONS.keys())

        # Place several pieces at well-spaced positions
        for i, piece_name in enumerate(piece_names[:8]):
            # Get the actual piece from player's inventory
            piece = player.get_piece(piece_name)

            # Place pieces in a grid pattern to avoid overlap
            row = (i // 4) * 10  # 0, 0, 0, 0, 10, 10, 10, 10
            col = (i % 4) * 5    # 0, 5, 10, 15, 0, 5, 10, 15

            # Simulate what game loop would do
            # Place on board
            board.place_piece(piece, row, col, player.player_id)

            # Note: player.place_piece() is not needed here because
            # placing on the board already marks the piece as used

            # Update score
            ScoringSystem.update_player_score(player)

            # Verify score is correct
            breakdown = ScoringSystem.get_score_breakdown(player)
            assert player.score == breakdown["final_score"]

    def test_score_consistency_across_calculations(self):
        """
        Test that all score calculation methods produce consistent results.
        """
        player = Player(player_id=1, name="Test Player")
        board = Board()
        piece_names = list(PIECE_DEFINITIONS.keys())

        # Place some pieces at well-spaced positions
        for i, piece_name in enumerate(piece_names[:7]):
            # Get the actual piece from player's inventory
            piece = player.get_piece(piece_name)
            # Place pieces in a grid pattern to avoid overlap
            row = (i // 4) * 10
            col = (i % 4) * 5
            board.place_piece(piece, row, col, player.player_id)

        # Update score
        ScoringSystem.update_player_score(player)

        # All calculation methods should agree
        breakdown = ScoringSystem.get_score_breakdown(player)
        expected_score = breakdown["final_score"]

        assert player.score == expected_score
        assert player.score == breakdown["final_score"]

        # Score should match placed squares - unplaced squares + bonus
        placed = ScoringSystem.calculate_squares_placed(player)
        unplaced = ScoringSystem.calculate_squares_remaining(player)
        bonus = 15 if ScoringSystem.check_bonus_eligibility(player) else 0

        calculated_score = placed - unplaced + bonus
        assert player.score == calculated_score

    def test_game_state_score_synchronization(self):
        """
        Test that game state maintains synchronized scores.
        """
        player1 = Player(player_id=1, name="Player 1")
        player2 = Player(player_id=2, name="Player 2")

        game_state = GameState()
        game_state.players = [player1, player2]

        # Update scores for all players
        for player in game_state.players:
            ScoringSystem.update_player_score(player)

        # Get scores from game state via ScoringSystem
        final_scores = ScoringSystem.calculate_final_scores(game_state)

        # Verify synchronization
        assert final_scores[1] == player1.score
        assert final_scores[2] == player2.score

        # Place more pieces for player 1
        piece_names = list(PIECE_DEFINITIONS.keys())
        for piece_name in piece_names[:6]:
            player1.place_piece(piece_name, 0, 0)

        # Update score
        ScoringSystem.update_player_score(player1)

        # Verify game state reflects the update
        final_scores = ScoringSystem.calculate_final_scores(game_state)
        assert final_scores[1] > player2.score
        assert final_scores[1] == player1.score

    def test_score_update_with_board_integration(self):
        """
        Test that score updates work correctly with board state.
        """
        player = Player(player_id=1, name="Test Player")
        board = Board()
        piece_names = list(PIECE_DEFINITIONS.keys())

        # Place pieces on board
        for i, piece_name in enumerate(piece_names[:5]):
            row = i // 4
            col = (i % 4) * 5
            player.place_piece(piece_name, 0, 0)
            piece = Piece(piece_name)

            # This would typically be done by game loop
            board.place_piece(piece, row, col, player.player_id)

            # Update score
            ScoringSystem.update_player_score(player)

            # Verify
            breakdown = ScoringSystem.get_score_breakdown(player)
            assert player.score == breakdown["final_score"]

            # Score from board should match
            board_squares = board.count_player_squares(player.player_id)
            placed_squares = ScoringSystem.calculate_squares_placed(player)
            assert board_squares == placed_squares

    def test_final_score_calculation_after_game_end(self):
        """
        Test that final scores are calculated correctly when game ends.
        """
        player1 = Player(player_id=1, name="Player 1")
        player2 = Player(player_id=2, name="Player 2")

        game_state = GameState()
        game_state.players = [player1, player2]

        piece_names = list(PIECE_DEFINITIONS.keys())

        # Player 1 places all pieces
        for piece_name in piece_names:
            player1.place_piece(piece_name, 0, 0)

        # Player 2 places partial
        for piece_name in piece_names[:12]:
            player2.place_piece(piece_name, 0, 0)

        # Calculate final scores
        final_scores = ScoringSystem.calculate_final_scores(game_state)
        winners = ScoringSystem.determine_winner(game_state)
        ranked = ScoringSystem.rank_players(game_state)

        # Verify final scores
        # Player 1 should have highest score (all pieces + bonus)
        assert final_scores[1] > final_scores[2]
        assert winners[0].player_id == 1

        # Verify ranking
        assert ranked[0][0] == 1  # Player 1 rank 1
        assert ranked[1][0] == 2  # Player 2 rank 2
