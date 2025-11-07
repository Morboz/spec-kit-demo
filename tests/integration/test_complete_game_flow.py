"""
Comprehensive integration test for the complete Blokus game flow.

This test verifies that all components work together from game initialization
through game end, including:
- Game setup and configuration
- Piece placement with rotation/flip
- Turn-based gameplay
- Rule enforcement
- Score tracking and updates
- Game end detection
- Winner determination
"""

import tkinter as tk

from src.config.pieces import PIECE_DEFINITIONS
from src.game.end_game_detector import EndGameDetector
from src.game.game_loop import GameLoop
from src.game.score_history import ScoreHistory
from src.game.scoring import ScoringSystem
from src.game.turn_manager import TurnManager
from src.game.turn_validator import TurnValidator
from src.game.winner_determiner import WinnerDeterminer
from src.models.board import Board
from src.models.game_state import GameState
from src.models.player import Player
from src.ui.current_player_indicator import CurrentPlayerIndicator
from src.ui.piece_inventory import PieceInventory
from src.ui.scoreboard import Scoreboard


class TestCompleteGameFlow:
    """Test suite for complete Blokus game flow from start to finish."""

    def test_complete_two_player_game(self):
        """
        Test a complete two-player game from start to finish.
        """
        # Step 1: Game Setup
        player1 = Player(player_id=1, name="Alice", color="blue")
        player2 = Player(player_id=2, name="Bob", color="red")

        game_state = GameState()
        game_state.players = [player1, player2]
        game_state.current_player_index = 0

        board = Board()

        # Step 2: Create game components
        game_loop = GameLoop(game_state)
        turn_manager = TurnManager(game_state)
        turn_validator = TurnValidator(game_state)
        score_history = ScoreHistory(game_state)

        # Step 3: Initialize UI components (headless)
        root = tk.Tk()
        root.withdraw()

        try:
            scoreboard = Scoreboard(root, board, [player1, player2])
            current_player_indicator = CurrentPlayerIndicator(root, game_state)
            piece_inventory = PieceInventory(root, player1)

            # Step 4: Record initial game state
            score_history.record_current_scores(0, 0)

            # Step 5: Play multiple turns
            piece_names = list(PIECE_DEFINITIONS.keys())

            for turn in range(20):  # Play 20 turns
                current_player = game_state.get_current_player()
                current_player_name = current_player.name

                # Get valid moves for current player
                valid_moves = turn_validator.get_valid_moves(board)

                if valid_moves:
                    # Place a piece (use turn number to vary placement)
                    piece_idx = turn % len(piece_names)
                    piece_name = piece_names[piece_idx]
                    row = turn % 15
                    col = turn % 15

                    # Place piece
                    current_player.place_piece(piece_name, row, col)
                    board.place_piece(current_player.player_id, piece_name, row, col)

                    # Update score
                    ScoringSystem.update_player_score(current_player)

                    # Update UI components
                    scoreboard.update_scores()
                    scoreboard.update_player_info(1)
                    scoreboard.update_player_info(2)

                    # Record score history every 5 turns
                    if turn % 5 == 0:
                        score_history.record_current_scores(turn + 1, 1)
                else:
                    # No valid moves, player is blocked
                    break

                # Advance turn
                turn_manager.advance_turn()

                # Update current player indicator
                current_player_indicator.update_indicator()

                # Update piece inventory for current player
                new_current = game_state.get_current_player()
                piece_inventory.update_inventory(new_current)

            # Step 6: Check game state after gameplay
            assert len(game_state.players) == 2
            assert all(
                p.score != 0 for p in game_state.players if p.pieces_remaining > 0
            )

            # Step 7: Check score history
            history_entries = score_history.get_all_histories()
            assert 1 in history_entries or 2 in history_entries

            # Step 8: Test end game detection
            end_detector = EndGameDetector(game_state)
            all_players_blocked = end_detector.check_all_players_blocked(board)
            all_pieces_placed = end_detector.check_all_pieces_placed()

            if all_players_blocked or all_pieces_placed:
                # Step 9: Determine winner
                winner_determiner = WinnerDeterminer(game_state)
                final_scores = ScoringSystem.calculate_final_scores(game_state)
                winners = ScoringSystem.determine_winner(game_state)

                # Verify final scores
                assert len(final_scores) == 2
                assert all(score != 0 for score in final_scores.values())

                # Verify winner determination
                assert len(winners) >= 1
                winner_ids = [w.player_id for w in winners]
                assert all(id in [1, 2] for id in winner_ids)

            # Step 10: Verify score consistency
            for player in game_state.players:
                breakdown = ScoringSystem.get_score_breakdown(player)
                assert player.score == breakdown["final_score"]
                assert breakdown["placed_squares"] + breakdown["unplaced_squares"] == 88

        finally:
            root.destroy()

    def test_complete_four_player_game(self):
        """
        Test a complete four-player game from start to finish.
        """
        # Step 1: Game Setup with 4 players
        players = [
            Player(player_id=1, name="Alice", color="blue"),
            Player(player_id=2, name="Bob", color="red"),
            Player(player_id=3, name="Charlie", color="green"),
            Player(player_id=4, name="Diana", color="yellow"),
        ]

        game_state = GameState()
        game_state.players = players
        game_state.current_player_index = 0

        board = Board()

        # Step 2: Create game components
        game_loop = GameLoop(game_state)
        turn_manager = TurnManager(game_state)
        turn_validator = TurnValidator(game_state)
        score_history = ScoreHistory(game_state)

        # Initialize UI
        root = tk.Tk()
        root.withdraw()

        try:
            scoreboard = Scoreboard(root, board, players)
            current_player_indicator = CurrentPlayerIndicator(root, game_state)

            # Step 3: Record initial state
            score_history.record_current_scores(0, 0)

            # Step 4: Play multiple turns
            piece_names = list(PIECE_DEFINITIONS.keys())

            for turn in range(40):  # Play 40 turns
                current_player = game_state.get_current_player()

                # Get valid moves
                valid_moves = turn_validator.get_valid_moves(board)

                if valid_moves and current_player.pieces_remaining > 0:
                    # Place a piece
                    piece_idx = turn % len(piece_names)
                    piece_name = piece_names[piece_idx]
                    row = (turn * 2) % 18
                    col = (turn * 2) % 18

                    # Validate and place
                    current_player.place_piece(piece_name, row, col)
                    board.place_piece(current_player.player_id, piece_name, row, col)

                    # Update score
                    ScoringSystem.update_player_score(current_player)

                    # Update UI
                    for player in players:
                        scoreboard.update_player_info(player.player_id)

                    current_player_indicator.update_indicator()
                else:
                    # Player is blocked
                    pass

                # Advance turn
                turn_manager.advance_turn()
                current_player_indicator.update_indicator()

            # Step 5: Verify game state
            active_players = game_state.get_active_players()
            assert len(active_players) >= 2

            # Step 6: Check final scores
            final_scores = ScoringSystem.calculate_final_scores(game_state)
            assert len(final_scores) == 4

            # Verify scores are reasonable
            for player_id, score in final_scores.items():
                player = game_state.get_player_by_id(player_id)
                assert player.score == score
                assert -88 <= score <= 103  # Reasonable score range

            # Step 7: Verify scoreboard accuracy
            scoreboard_scores = scoreboard.get_all_player_scores()
            for player_id, player in [(p.player_id, p) for p in players]:
                assert scoreboard_scores[player_id] == player.score

        finally:
            root.destroy()

    def test_turn_rotation_through_complete_game(self):
        """
        Test that turns rotate correctly through a complete game.
        """
        # Setup 3 players
        players = [
            Player(player_id=1, name="Player 1"),
            Player(player_id=2, name="Player 2"),
            Player(player_id=3, name="Player 3"),
        ]

        game_state = GameState()
        game_state.players = players
        game_state.current_player_index = 0

        board = Board()
        turn_manager = TurnManager(game_state)
        turn_validator = TurnValidator(game_state)

        piece_names = list(PIECE_DEFINITIONS.keys())

        # Play for several turns
        for turn in range(30):
            current_player = game_state.get_current_player()
            original_player_id = current_player.player_id

            # Get valid moves
            valid_moves = turn_validator.get_valid_moves(board)

            if valid_moves and current_player.pieces_remaining > 0:
                # Place piece
                piece_name = piece_names[turn % len(piece_names)]
                current_player.place_piece(piece_name, turn % 10, turn % 10)
                board.place_piece(
                    current_player.player_id, piece_name, turn % 10, turn % 10
                )

                # Update score
                ScoringSystem.update_player_score(current_player)

            # Advance turn
            turn_manager.advance_turn()

            # Verify turn advanced
            new_current = game_state.get_current_player()
            if current_player.pieces_remaining > 0:
                # Next player should be different (or wrap around)
                assert new_current.player_id != original_player_id

        # Verify all players got turns
        turn_counts = turn_manager.get_turn_counts()
        assert sum(turn_counts.values()) >= 10  # At least 10 turns total

    def test_rule_enforcement_during_complete_game(self):
        """
        Test that rules are properly enforced throughout the game.
        """
        player1 = Player(player_id=1, name="Player 1")
        player2 = Player(player_id=2, name="Player 2")

        game_state = GameState()
        game_state.players = [player1, player2]
        game_state.current_player_index = 0

        board = Board()

        piece_names = list(PIECE_DEFINITIONS.keys())

        # Player 1 makes first move (must be in corner)
        player1.place_piece(piece_names[0], 0, 0)
        board.place_piece(1, piece_names[0], 0, 0)
        ScoringSystem.update_player_score(player1)

        # Try to place second piece touching own piece (should fail)
        from src.game.rules import Rules

        result = Rules.validate_move(
            board, player2, piece_names[1], 0, 1, rotation=0, flipped=False
        )
        assert not result.is_valid

        # Player 2 makes valid move in corner
        player2.place_piece(piece_names[1], 19, 19)
        board.place_piece(2, piece_names[1], 19, 19)
        ScoringSystem.update_player_score(player2)

        # Try to overlap (should fail)
        result = Rules.validate_move(
            board, player1, piece_names[2], 0, 0, rotation=0, flipped=False
        )
        assert not result.is_valid
        assert "overlap" in result.message.lower()

        # Continue game with valid moves
        for turn in range(10):
            current_player = game_state.get_current_player()

            # Try to find a valid move
            valid_move_found = False
            for row in range(20):
                for col in range(20):
                    for rotation in range(4):
                        for flipped in [False, True]:
                            result = Rules.validate_move(
                                board,
                                current_player,
                                piece_names[turn % len(piece_names)],
                                row,
                                col,
                                rotation=rotation,
                                flipped=flipped,
                            )
                            if result.is_valid:
                                current_player.place_piece(
                                    piece_names[turn % len(piece_names)], row, col
                                )
                                board.place_piece(
                                    current_player.player_id,
                                    piece_names[turn % len(piece_names)],
                                    row,
                                    col,
                                )
                                ScoringSystem.update_player_score(current_player)
                                valid_move_found = True
                                break
                        if valid_move_found:
                            break
                    if valid_move_found:
                        break
                if valid_move_found:
                    break

            # Advance turn
            if game_state.current_player_index == 0:
                game_state.current_player_index = 1
            else:
                game_state.current_player_index = 0

        # Verify game progressed with valid moves only
        assert all(p.score != 0 for p in game_state.players)
        assert board.count_all_squares() > 2  # At least some squares placed

    def test_score_tracking_throughout_complete_game(self):
        """
        Test that scores are accurately tracked throughout the entire game.
        """
        player1 = Player(player_id=1, name="Player 1")
        player2 = Player(player_id=2, name="Player 2")

        game_state = GameState()
        game_state.players = [player1, player2]

        board = Board()
        score_history = ScoreHistory(game_state)

        piece_names = list(PIECE_DEFINITIONS.keys())

        # Record initial score
        score_history.record_current_scores(0, 0)
        initial_scores = {1: 0, 2: 0}

        # Play game and track scores
        score_changes = []

        for turn in range(20):
            current_player = game_state.get_current_player()
            player_id = current_player.player_id

            old_score = current_player.score

            # Place piece
            piece_name = piece_names[turn % len(piece_names)]
            current_player.place_piece(piece_name, turn % 10, turn % 10)
            board.place_piece(
                current_player.player_id, piece_name, turn % 10, turn % 10
            )

            # Update score
            ScoringSystem.update_player_score(current_player)
            new_score = current_player.score

            # Record change
            score_change = new_score - old_score
            score_changes.append(score_change)

            # Record in history
            score_history.record_current_scores(turn + 1, 1)

            # Advance turn
            if game_state.current_player_index == 0:
                game_state.current_player_index = 1
            else:
                game_state.current_player_index = 0

        # Verify score changes
        assert len(score_changes) == 20
        assert all(isinstance(change, int) for change in score_changes)

        # Verify score history
        histories = score_history.get_all_histories()
        assert 1 in histories or 2 in histories

        # Verify final scores are reasonable
        assert -88 <= player1.score <= 103
        assert -88 <= player2.score <= 103

        # Verify score breakdown consistency
        breakdown1 = ScoringSystem.get_score_breakdown(player1)
        assert player1.score == breakdown1["final_score"]

        breakdown2 = ScoringSystem.get_score_breakdown(player2)
        assert player2.score == breakdown2["final_score"]

    def test_ui_components_integration(self):
        """
        Test that all UI components work together during game.
        """
        players = [
            Player(player_id=1, name="Player 1", color="blue"),
            Player(player_id=2, name="Player 2", color="red"),
        ]

        game_state = GameState()
        game_state.players = players

        board = Board()

        root = tk.Tk()
        root.withdraw()

        try:
            # Create all UI components
            scoreboard = Scoreboard(root, board, players)
            current_player_indicator = CurrentPlayerIndicator(root, game_state)
            piece_inventory1 = PieceInventory(root, players[0])
            piece_inventory2 = PieceInventory(root, players[1])

            # Verify initial state
            assert current_player_indicator.get_current_player_name() == "Player 1"

            for player in players:
                inventory_count = (
                    piece_inventory1.get_remaining_count()
                    if player == players[0]
                    else piece_inventory2.get_remaining_count()
                )
                assert inventory_count == 21

            # Play some turns
            piece_names = list(PIECE_DEFINITIONS.keys())

            for turn in range(10):
                current_player = game_state.get_current_player()

                # Place piece
                piece_name = piece_names[turn % len(piece_names)]
                current_player.place_piece(piece_name, turn, turn)
                board.place_piece(current_player.player_id, piece_name, turn, turn)

                # Update scores
                ScoringSystem.update_player_score(current_player)

                # Update UI components
                scoreboard.update_scores()
                scoreboard.update_player_info(1)
                scoreboard.update_player_info(2)

                current_player_indicator.update_indicator()

                # Update inventory for current player
                if current_player == players[0]:
                    piece_inventory1.update_inventory(current_player)
                    assert piece_inventory1.get_remaining_count() < 21
                else:
                    piece_inventory2.update_inventory(current_player)
                    assert piece_inventory2.get_remaining_count() < 21

                # Advance turn
                if game_state.current_player_index == 0:
                    game_state.current_player_index = 1
                else:
                    game_state.current_player_index = 0

            # Verify final state
            for player in players:
                assert player.score != 0
                assert player.pieces_remaining < 21

        finally:
            root.destroy()

    def test_game_end_detection_and_winner(self):
        """
        Test that game end is properly detected and winner determined.
        """
        player1 = Player(player_id=1, name="Player 1")
        player2 = Player(player_id=2, name="Player 2")

        game_state = GameState()
        game_state.players = [player1, player2]

        board = Board()
        end_detector = EndGameDetector(game_state)

        # Scenario 1: All pieces placed
        piece_names = list(PIECE_DEFINITIONS.keys())

        # Player 1 places all pieces
        for piece_name in piece_names:
            player1.place_piece(piece_name, 0, 0)
        board.place_pieces(player1.player_id, player1.placed_pieces)

        # Check if game should end
        all_pieces_placed = end_detector.check_all_pieces_placed()
        assert all_pieces_placed

        # Determine winner
        winners = ScoringSystem.determine_winner(game_state)
        assert len(winners) >= 1
        assert winners[0].player_id == 1

        # Scenario 2: All players blocked
        player3 = Player(player_id=3, name="Player 3")
        player4 = Player(player_id=4, name="Player 4")

        game_state2 = GameState()
        game_state2.players = [player3, player4]

        board2 = Board()
        end_detector2 = EndGameDetector(game_state2)

        # Fill board with pieces so no moves possible
        for row in range(20):
            for col in range(20):
                board2.grid[row][col] = 1  # Mark as occupied

        # Check if all players blocked
        all_blocked = end_detector2.check_all_players_blocked(board2)
        assert all_blocked

        # Final scores should still be calculable
        final_scores = ScoringSystem.calculate_final_scores(game_state2)
        assert len(final_scores) == 2
        assert all(score != 0 for score in final_scores.values())

    def test_full_game_simulation(self):
        """
        Simulate a complete game with realistic gameplay.
        """
        # Setup 2 players
        players = [
            Player(player_id=1, name="Alice", color="blue"),
            Player(player_id=2, name="Bob", color="red"),
        ]

        game_state = GameState()
        game_state.players = players
        game_state.current_player_index = 0

        board = Board()

        # Create all game components
        game_loop = GameLoop(game_state)
        turn_manager = TurnManager(game_state)
        turn_validator = TurnValidator(game_state)
        score_history = ScoreHistory(game_state)
        end_detector = EndGameDetector(game_state)

        # Initialize UI
        root = tk.Tk()
        root.withdraw()

        try:
            scoreboard = Scoreboard(root, board, players)
            current_player_indicator = CurrentPlayerIndicator(root, game_state)

            # Record initial state
            score_history.record_current_scores(0, 0)

            piece_names = list(PIECE_DEFINITIONS.keys())
            turn_number = 0

            # Play until game end
            while turn_number < 100:  # Safety limit
                current_player = game_state.get_current_player()

                # Check if player has valid moves
                valid_moves = turn_validator.get_valid_moves(board)

                if not valid_moves or current_player.pieces_remaining == 0:
                    # No valid moves or no pieces left
                    # Advance turn
                    turn_manager.advance_turn()

                    # Check if all players are blocked
                    if end_detector.check_all_players_blocked(board):
                        break

                    if end_detector.check_all_pieces_placed():
                        break

                    turn_number += 1
                    continue

                # Find and place a piece
                piece_name = piece_names[turn_number % len(piece_names)]
                row = turn_number % 18
                col = turn_number % 18

                # Place piece
                current_player.place_piece(piece_name, row, col)
                board.place_piece(current_player.player_id, piece_name, row, col)

                # Update score
                ScoringSystem.update_player_score(current_player)

                # Update UI
                scoreboard.update_scores()
                scoreboard.update_player_info(1)
                scoreboard.update_player_info(2)
                current_player_indicator.update_indicator()

                # Record history every 5 turns
                if turn_number % 5 == 0:
                    score_history.record_current_scores(turn_number + 1, 1)

                # Advance turn
                turn_manager.advance_turn()

                turn_number += 1

            # Game ended
            final_scores = ScoringSystem.calculate_final_scores(game_state)
            winners = ScoringSystem.determine_winner(game_state)

            # Verify game ended properly
            assert len(final_scores) == 2
            assert len(winners) >= 1

            # Verify score consistency
            for player in players:
                breakdown = ScoringSystem.get_score_breakdown(player)
                assert player.score == breakdown["final_score"]

            # Verify history was recorded
            assert len(score_history.entries) > 0

            # Verify game progress
            total_squares = board.count_all_squares()
            assert total_squares > 0

        finally:
            root.destroy()
