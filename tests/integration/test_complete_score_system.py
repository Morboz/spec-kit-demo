"""
Integration test for complete score tracking and display system.

This test verifies that the entire score tracking system works together:
- Scoring calculations
- Score history tracking
- UI display components
- Game loop integration
"""

import tkinter as tk

from blokus_game.config.pieces import PIECE_DEFINITIONS
from blokus_game.game.game_loop import GameLoop
from blokus_game.game.score_history import ScoreHistory
from blokus_game.game.scoring import ScoringSystem
from blokus_game.models.board import Board
from blokus_game.models.game_state import GameState
from blokus_game.models.player import Player
from blokus_game.ui.score_breakdown import ScoreBreakdown
from blokus_game.ui.scoreboard import Scoreboard


class TestCompleteScoreSystem:
    """Test suite for complete score tracking and display system."""

    def test_score_tracking_through_game_lifecycle(self):
        """
        Test that scores are tracked correctly throughout the entire game.
        """
        # Create game state with 2 players
        player1 = Player(player_id=1, name="Player 1")
        player2 = Player(player_id=2, name="Player 2")

        game_state = GameState()
        game_state.players = [player1, player2]

        # Create score history tracker
        history = ScoreHistory(game_state)

        # Create game loop
        game_loop = GameLoop(game_state)

        piece_names = list(PIECE_DEFINITIONS.keys())

        # Simulate game play
        turn_number = 0
        for i, piece_name in enumerate(piece_names):
            # Determine current player
            current_player = player1 if i % 2 == 0 else player2

            # Place piece
            current_player.place_piece(piece_name, 0, 0)

            # Update score
            ScoringSystem.update_player_score(current_player)

            # Record in history (every 3 turns)
            if i % 3 == 0:
                turn_number += 1
                history.record_current_scores(turn_number, 1)

        # Verify history was recorded
        assert len(history.entries) > 0

        # Verify final scores match ScoringSystem calculation
        for player in game_state.players:
            breakdown = ScoringSystem.get_score_breakdown(player)
            assert player.score == breakdown["final_score"]

    def test_score_history_tracking(self):
        """
        Test that score history correctly tracks all score changes.
        """
        # Create game state
        player1 = Player(player_id=1, name="Player 1")
        player2 = Player(player_id=2, name="Player 2")

        game_state = GameState()
        game_state.players = [player1, player2]

        # Create score history
        history = ScoreHistory(game_state)

        # Record initial scores
        history.record_current_scores(0, 0)

        piece_names = list(PIECE_DEFINITIONS.keys())

        # Player 1 places pieces
        for i in range(5):
            player1.place_piece(piece_names[i], 0, 0)
            ScoringSystem.update_player_score(player1)
            history.record_current_scores(i + 1, 1)

        # Player 2 places pieces
        for i in range(5, 10):
            player2.place_piece(piece_names[i], 0, 0)
            ScoringSystem.update_player_score(player2)
            history.record_current_scores(i + 1, 1)

        # Verify history contains entries for both players
        histories = history.get_all_histories()
        assert 1 in histories
        assert 2 in histories

        # Verify player 1 has more entries (placed first)
        assert len(histories[1]) >= len(histories[2])

        # Verify score changes
        changes = history.get_score_changes()
        assert len(changes) > 0

        # All changes should be positive (scores increase)
        for change in changes:
            assert change["change"] >= 0

    def test_scoreboard_and_breakdown_integration(self):
        """
        Test that scoreboard and score breakdown work together.
        """
        root = tk.Tk()
        root.withdraw()  # Hide window

        try:
            # Create game components
            player = Player(player_id=1, name="Test Player")
            board = Board()

            # Create scoreboard
            scoreboard = Scoreboard(root, board, [player])

            # Place some pieces
            piece_names = list(PIECE_DEFINITIONS.keys())
            for piece_name in piece_names[:8]:
                player.place_piece(piece_name, 10, 10)
                board.place_piece(player.player_id, piece_name, 10, 10)

            # Update score
            ScoringSystem.update_player_score(player)

            # Update scoreboard
            scoreboard.update_scores()

            # Get detailed info
            detailed_info = scoreboard.get_player_detailed_info(1)
            assert detailed_info is not None
            assert detailed_info["score"] == player.score
            assert detailed_info["squares_placed"] > 0

            # Get score breakdown (UI component)
            breakdown = ScoreBreakdown(root, player)
            breakdown.update_breakdown()

            # Verify breakdown matches player score
            breakdown_data = breakdown.get_current_breakdown()
            assert breakdown_data is not None
            assert breakdown_data["final_score"] == player.score

        finally:
            root.destroy()

    def test_game_loop_score_updates(self):
        """
        Test that game loop properly updates scores.
        """
        # Create game state
        player1 = Player(player_id=1, name="Player 1")
        game_state = GameState()
        game_state.players = [player1]

        # Create game loop
        game_loop = GameLoop(game_state)

        # Initially no score update
        initial_score = player1.score
        assert initial_score == 0

        # Place a piece
        piece_names = list(PIECE_DEFINITIONS.keys())
        player1.place_piece(piece_names[0], 0, 0)

        # Update current player score via game loop
        game_loop.update_current_player_score()

        # Score should be updated
        assert player1.score != initial_score
        assert player1.score < 0  # Should be negative until more pieces placed

        # Update all active player scores
        game_loop.update_all_active_player_scores()
        assert player1.score < 0

    def test_final_score_calculation(self):
        """
        Test that final scores are correctly calculated at game end.
        """
        # Create game state
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

        # Update scores
        ScoringSystem.update_player_score(player1)
        ScoringSystem.update_player_score(player2)

        # Calculate final scores
        final_scores = ScoringSystem.calculate_final_scores(game_state)

        # Verify player 1 has higher score (all pieces + bonus)
        assert final_scores[1] > final_scores[2]
        assert final_scores[1] == 103  # 88 + 15 bonus

        # Verify rankings
        ranked = ScoringSystem.rank_players(game_state)
        assert ranked[0][1] == 1  # Player 1 is rank 1
        assert ranked[1][1] == 2  # Player 2 is rank 2

        # Verify winners
        winners = ScoringSystem.determine_winner(game_state)
        assert len(winners) == 1
        assert winners[0].player_id == 1

    def test_score_consistency_across_system(self):
        """
        Test that scores are consistent across all system components.
        """
        # Create game state
        player = Player(player_id=1, name="Test Player")
        board = Board()

        game_state = GameState()
        game_state.players = [player]

        piece_names = list(PIECE_DEFINITIONS.keys())

        # Place pieces gradually
        for i in range(10):
            piece_name = piece_names[i]
            player.place_piece(piece_name, i, i)
            board.place_piece(player.player_id, piece_name, i, i)

            # Update score via ScoringSystem
            ScoringSystem.update_player_score(player)

            # Get breakdown
            breakdown = ScoringSystem.get_score_breakdown(player)

            # All should match
            assert player.score == breakdown["final_score"]
            assert (
                player.score == breakdown["base_score"] + breakdown["all_pieces_bonus"]
            )
            assert breakdown["placed_squares"] + breakdown["unplaced_squares"] == 88

            # Board squares should match placed squares
            board_squares = board.count_player_squares(player.player_id)
            assert board_squares == breakdown["placed_squares"]

    def test_score_history_export_import(self):
        """
        Test that score history can be exported and imported.
        """
        # Create game state
        player1 = Player(player_id=1, name="Player 1")

        game_state = GameState()
        game_state.players = [player1]

        # Create history and record some data
        history = ScoreHistory(game_state)

        piece_names = list(PIECE_DEFINITIONS.keys())
        for i in range(5):
            player1.place_piece(piece_names[i], 0, 0)
            ScoringSystem.update_player_score(player1)
            history.record_current_scores(i + 1, 1)

        # Export to dict
        exported_data = history.export_to_dict()

        # Create new history and import
        new_history = ScoreHistory()
        new_history.import_from_dict(exported_data)

        # Verify data matches
        assert len(new_history.entries) == len(history.entries)

        # Verify summary
        original_summary = history.get_summary()
        imported_summary = new_history.get_summary()
        assert original_summary["total_entries"] == imported_summary["total_entries"]
        assert (
            original_summary["players_tracked"] == imported_summary["players_tracked"]
        )
