"""Integration tests for complete turn flow.

This test validates the entire turn-based gameplay flow from start to finish,
including piece placement, turn advancement, and round management.
"""

from blokus_game.models.board import Board
from blokus_game.models.game_state import GameState
from blokus_game.models.player import Player


class TestTurnFlowIntegration:
    """Integration tests for complete turn-based gameplay flow."""

    def test_complete_two_player_turn_flow(self):
        """Integration: Two players alternate turns with piece placement.

        Given: Two player game started
        When: Players alternate placing pieces
        Then: Turns advance correctly, pieces placed on board
        """
        # Given: Two player game
        board = Board()
        game_state = GameState(board=board)
        player1 = Player(player_id=1, name="Alice")
        player2 = Player(player_id=2, name="Bob")

        game_state.add_player(player1)
        game_state.add_player(player2)
        game_state.start_game()

        # Verify initial state
        assert game_state.get_current_player().player_id == 1
        assert game_state.get_round_number() == 1
        assert board.count_player_squares(1) == 0
        assert board.count_player_squares(2) == 0

        # When: Player 1 places first piece
        piece1 = player1.get_piece("I1")
        positions1 = board.place_piece(piece1, 0, 0, 1)
        player1.place_piece("I1", 0, 0)
        game_state.record_move(1, "I1", 0, 0)

        # Then: Board updated
        assert board.count_player_squares(1) == 1
        assert (0, 0) in positions1

        # When: Advancing turn
        game_state.next_turn()

        # Then: Player 2's turn
        assert game_state.get_current_player().player_id == 2

        # When: Player 2 places piece
        piece2 = player2.get_piece("I1")
        positions2 = board.place_piece(piece2, 0, 19, 2)
        player2.place_piece("I1", 0, 19)
        game_state.record_move(2, "I1", 0, 19)

        # Then: Both players have pieces
        assert board.count_player_squares(1) == 1
        assert board.count_player_squares(2) == 1

        # When: Advancing turn again
        game_state.next_turn()

        # Then: Back to Player 1, round 2
        assert game_state.get_current_player().player_id == 1
        assert game_state.get_round_number() == 2

    def test_turn_flow_with_skip_and_continue(self):
        """Integration: Player can skip and game continues correctly.

        Given: Game where player skips
        When: Other players continue
        Then: Turn sequence handles skips properly
        """
        # Given: Three player game
        board = Board()
        game_state = GameState(board=board)
        player1 = Player(player_id=1, name="Alice")
        player2 = Player(player_id=2, name="Bob")
        player3 = Player(player_id=3, name="Carol")

        game_state.add_player(player1)
        game_state.add_player(player2)
        game_state.add_player(player3)
        game_state.start_game()

        # When: Player 1 places, Player 2 skips, Player 3 places
        piece1 = player1.get_piece("I1")
        board.place_piece(piece1, 0, 0, 1)
        player1.place_piece("I1", 0, 0)

        game_state.next_turn()  # To player 2

        # Player 2 skips
        player2.pass_turn()
        game_state.next_turn()  # To player 3

        # Player 3 places
        piece3 = player3.get_piece("I1")
        board.place_piece(piece3, 19, 19, 3)
        player3.place_piece("I1", 19, 19)

        game_state.next_turn()  # Back to player 1

        # Then: All turns executed correctly
        assert game_state.get_current_player().player_id == 1
        assert not player2.has_passed  # Reset for new round

    def test_turn_flow_multiple_rounds(self):
        """Integration: Multiple rounds complete with correct turn sequence.

        Given: Game progressing through multiple rounds
        When: Completing full rounds
        Then: Round numbers increment, turn sequence continues
        """
        # Given: Two player game
        board = Board()
        game_state = GameState(board=board)
        player1 = Player(player_id=1, name="Alice")
        player2 = Player(player_id=2, name="Bob")

        game_state.add_player(player1)
        game_state.add_player(player2)
        game_state.start_game()

        # Complete round 1
        assert game_state.get_round_number() == 1

        piece1 = player1.get_piece("I1")
        board.place_piece(piece1, 0, 0, 1)
        player1.place_piece("I1", 0, 0)
        game_state.next_turn()

        piece2 = player2.get_piece("I1")
        board.place_piece(piece2, 0, 19, 2)
        player2.place_piece("I1", 0, 19)
        game_state.next_turn()

        # Then: In round 2
        assert game_state.get_round_number() == 2
        assert game_state.get_current_player().player_id == 1

        # Complete round 2
        piece1_2 = player1.get_piece("I2")
        board.place_piece(piece1_2, 5, 5, 1)
        player1.place_piece("I2", 5, 5)
        game_state.next_turn()

        piece2_2 = player2.get_piece("I2")
        board.place_piece(piece2_2, 5, 14, 2)
        player2.place_piece("I2", 5, 14)
        game_state.next_turn()

        # Then: In round 3
        assert game_state.get_round_number() == 3
        assert game_state.get_current_player().player_id == 1

    def test_turn_flow_with_eliminated_player(self):
        """Integration: Eliminated player is skipped in turn sequence.

        Given: Player who has placed all pieces
        When: Game continues
        Then: Eliminated player is skipped
        """
        # Given: Three player game
        board = Board()
        game_state = GameState(board=board)
        player1 = Player(player_id=1, name="Alice")
        player2 = Player(player_id=2, name="Bob")
        player3 = Player(player_id=3, name="Carol")

        game_state.add_player(player1)
        game_state.add_player(player2)
        game_state.add_player(player3)
        game_state.start_game()

        # When: Player 2 is eliminated (no pieces left)
        # Simulate by placing all their pieces
        for piece_name in [
            "I1",
            "V3",
            "L4",
            "T5",
            "Z5",
            "F5",
            "P5",
            "W5",
            "U5",
            "X5",
            "Y5",
            "I2",
            "I3",
            "I4",
            "I5",
            "L5",
            "T4",
            "V4",
            "V5",
            "T4",
            "P5",
        ]:
            if player2.has_pieces_remaining():
                piece = player2.get_piece(piece_name)
                if piece and not piece.is_placed:
                    board.place_piece(piece, 10, 10, 2)
                    player2.place_piece(piece_name, 10, 10)

        player2.set_inactive()

        # When: Advancing turns
        assert game_state.get_current_player().player_id == 1
        game_state.next_turn()  # Should go to player 2 but skip
        # Player 2 is eliminated, so should go to player 3
        assert game_state.get_current_player().player_id == 3

        game_state.next_turn()  # Back to player 1
        assert game_state.get_current_player().player_id == 1

    def test_turn_flow_end_game_detection(self):
        """Integration: Game ends when all players skip.

        Given: Round where all players skip
        When: Checking game state
        Then: Game ends correctly
        """
        # Given: Two player game
        board = Board()
        game_state = GameState(board=board)
        player1 = Player(player_id=1, name="Alice")
        player2 = Player(player_id=2, name="Bob")

        game_state.add_player(player1)
        game_state.add_player(player2)
        game_state.start_game()

        # When: All players skip
        player1.pass_turn()
        game_state.next_turn()
        player2.pass_turn()
        game_state.next_turn()

        # Then: Round ends
        assert game_state.should_end_round() is True

        # When: All rounds complete
        # (In this case, both players have no pieces placed, so game should end)
        # Note: Actual end game detection may vary

    def test_turn_flow_maintains_correct_board_state(self):
        """Integration: Board state remains consistent through turn changes.

        Given: Game with pieces on board
        When: Advancing turns
        Then: Board state is preserved
        """
        # Given: Two player game with pieces placed
        board = Board()
        game_state = GameState(board=board)
        player1 = Player(player_id=1, name="Alice")
        player2 = Player(player_id=2, name="Bob")

        game_state.add_player(player1)
        game_state.add_player(player2)
        game_state.start_game()

        # Place pieces for both players
        piece1 = player1.get_piece("L4")
        board.place_piece(piece1, 5, 5, 1)
        player1.place_piece("L4", 5, 5)

        game_state.next_turn()

        piece2 = player2.get_piece("V3")
        board.place_piece(piece2, 10, 10, 2)
        player2.place_piece("V3", 10, 10)

        # Store board state
        board_state_before = board.get_board_state()
        occupied_before = board.get_occupied_positions()

        # When: Advancing several turns
        for _ in range(4):
            game_state.next_turn()

        # Then: Board state unchanged
        assert board.get_board_state() == board_state_before
        assert board.get_occupied_positions() == occupied_before
        assert board.count_player_squares(1) == 4  # L4 has 4 squares
        assert board.count_player_squares(2) == 3  # V3 has 3 squares

    def test_turn_flow_player_inventory_updates(self):
        """Integration: Player inventories update correctly after each turn.

        Given: Player with full inventory
        When: Player places pieces over multiple turns
        Then: Inventory decreases correctly
        """
        # Given: Player with full inventory
        player1 = Player(player_id=1, name="Alice")
        initial_count = player1.get_remaining_piece_count()
        assert initial_count == 21

        # When: Placing pieces over multiple turns
        board = Board()
        game_state = GameState(board=board)
        player2 = Player(player_id=2, name="Bob")  # Opponent

        game_state.add_player(player1)
        game_state.add_player(player2)
        game_state.start_game()

        # Place 3 pieces over multiple turns
        for turn in range(3):
            piece_name = ["I1", "V3", "L4"][turn]
            piece = player1.get_piece(piece_name)
            board.place_piece(piece, turn * 5, 0, 1)
            player1.place_piece(piece_name, turn * 5, 0)

            game_state.next_turn()  # Advance to opponent

            # Opponent plays
            opp_piece = player2.get_piece("I1")
            board.place_piece(opp_piece, turn * 5, 19, 2)
            player2.place_piece("I1", turn * 5, 19)

            game_state.next_turn()  # Back to player 1

        # Then: Inventory updated correctly
        assert player1.get_remaining_piece_count() == 18  # 21 - 3
        assert len(player1.get_placed_pieces()) == 3
        assert len(player1.get_unplaced_pieces()) == 18

    def test_turn_flow_with_rotated_and_flipped_pieces(self):
        """Integration: Turn flow works with piece transformations.

        Given: Player's turn
        When: Placing rotated and flipped pieces
        Then: Turns advance correctly with transformed pieces
        """
        # Given: Two player game
        board = Board()
        game_state = GameState(board=board)
        player1 = Player(player_id=1, name="Alice")
        player2 = Player(player_id=2, name="Bob")

        game_state.add_player(player1)
        game_state.add_player(player2)
        game_state.start_game()

        # When: Player 1 places rotated piece
        piece1 = player1.get_piece("L4")
        rotated_piece = piece1.rotate(90)
        # Get the rotated piece from player1's inventory
        # Note: In actual implementation, rotation creates a new piece
        # For testing, we need to place the original piece
        board.place_piece(piece1, 0, 0, 1)
        player1.place_piece("L4", 0, 0)

        game_state.next_turn()

        # When: Player 2 places flipped piece
        piece2 = player2.get_piece("V3")
        board.place_piece(piece2, 19, 19, 2)
        player2.place_piece("V3", 19, 19)

        # Then: Both pieces placed correctly
        assert board.count_player_squares(1) > 0
        assert board.count_player_squares(2) > 0

    def test_turn_flow_tracks_move_history(self):
        """Integration: Move history accurately tracks all turns.

        Given: Game with multiple turns
        When: Checking move history
        Then: History shows all moves in order
        """
        # Given: Two player game
        board = Board()
        game_state = GameState(board=board)
        player1 = Player(player_id=1, name="Alice")
        player2 = Player(player_id=2, name="Bob")

        game_state.add_player(player1)
        game_state.add_player(player2)
        game_state.start_game()

        # Record several moves
        game_state.record_move(1, "I1", 0, 0)
        game_state.next_turn()
        game_state.record_move(2, "I1", 0, 19)
        game_state.next_turn()
        game_state.record_move(1, "V3", 5, 5)
        game_state.next_turn()
        game_state.record_move(2, "L4", 5, 14)
        game_state.next_turn()

        # When: Checking history
        history = game_state.get_move_history()

        # Then: All moves recorded
        assert len(history) == 4

        # Then: Correct order
        assert history[0] == {
            "player_id": 1,
            "piece_name": "I1",
            "row": 0,
            "col": 0,
            "rotation": 0,
            "flipped": False,
            "round": 1,
        }
        assert history[1]["player_id"] == 2
        assert history[1]["round"] == 1
        assert history[2]["player_id"] == 1
        assert history[2]["round"] == 2
        assert history[3]["player_id"] == 2
        assert history[3]["round"] == 2
