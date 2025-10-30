"""Unit tests for GameState model."""

import pytest
from src.models.game_state import GameState, GamePhase
from src.models.board import Board
from src.models.player import Player


class TestGameState:
    """Test suite for GameState model."""

    def test_create_empty_game_state(self):
        """Test creating an empty game state."""
        game = GameState()
        assert game.get_player_count() == 0
        assert game.get_current_player() is None
        assert game.get_round_number() == 1
        assert game.get_turn_number() == 0
        assert game.is_setup_phase()
        assert not game.is_playing_phase()
        assert not game.is_game_over()
        assert len(game.move_history) == 0
        assert game.last_move is None

    def test_create_game_state_with_board(self):
        """Test creating game state with custom board."""
        board = Board()
        game = GameState(board=board)
        assert game.board is board
        assert game.get_player_count() == 0

    def test_add_player(self):
        """Test adding a player to the game."""
        game = GameState()
        player1 = Player(1, "Alice")
        player2 = Player(2, "Bob")

        game.add_player(player1)
        assert game.get_player_count() == 1
        assert game.get_current_player() == player1

        game.add_player(player2)
        assert game.get_player_count() == 2

    def test_cannot_add_more_than_4_players(self):
        """Test that adding more than 4 players raises an error."""
        game = GameState()

        # Add 4 players
        for i in range(1, 5):
            game.add_player(Player(i, f"Player{i}"))

        # Try to add 5th player (player IDs must be 1-4, so use 1-4 but add 5th player)
        # We'll create a player with valid ID but the 5th player should fail at game state level
        with pytest.raises(ValueError, match="Maximum of 4 players"):
            game.add_player(Player(1, "Duplicate"))

    def test_cannot_add_duplicate_player_id(self):
        """Test that adding duplicate player ID raises an error."""
        game = GameState()
        player1 = Player(1, "Alice")
        game.add_player(player1)

        # Try to add another player with same ID
        player2 = Player(1, "Bob")
        with pytest.raises(ValueError, match="already in game"):
            game.add_player(player2)

    def test_get_player_by_id(self):
        """Test retrieving a player by ID."""
        game = GameState()
        player1 = Player(1, "Alice")
        player2 = Player(2, "Bob")

        game.add_player(player1)
        game.add_player(player2)

        assert game.get_player_by_id(1) == player1
        assert game.get_player_by_id(2) == player2
        assert game.get_player_by_id(3) is None

    def test_next_turn(self):
        """Test advancing to next turn."""
        game = GameState()
        for i in range(1, 4):
            game.add_player(Player(i, f"Player{i}"))

        # Start with player 0
        assert game.get_current_player().player_id == 1

        # Next turn
        game.next_turn()
        assert game.get_current_player().player_id == 2

        # Next turn
        game.next_turn()
        assert game.get_current_player().player_id == 3

        # Next turn - loops back to first player and increments round
        game.next_turn()
        assert game.get_current_player().player_id == 1
        assert game.get_round_number() == 2

    def test_previous_player(self):
        """Test going to previous player."""
        game = GameState()
        for i in range(1, 4):
            game.add_player(Player(i, f"Player{i}"))

        # Move to second player
        game.next_turn()
        assert game.get_current_player().player_id == 2

        # Go back to first player
        game.previous_player()
        assert game.get_current_player().player_id == 1

    def test_start_game(self):
        """Test transitioning to playing phase."""
        game = GameState()
        for i in range(1, 3):
            game.add_player(Player(i, f"Player{i}"))

        assert game.is_setup_phase()

        game.start_game()

        assert game.is_playing_phase()
        assert game.get_current_player().player_id == 1
        assert game.get_round_number() == 1

    def test_start_game_requires_at_least_2_players(self):
        """Test that starting game with fewer than 2 players raises error."""
        game = GameState()
        game.add_player(Player(1, "Solo"))

        with pytest.raises(ValueError, match="at least 2 players"):
            game.start_game()

    def test_end_game(self):
        """Test transitioning to game over phase."""
        game = GameState()
        for i in range(1, 3):
            game.add_player(Player(i, f"Player{i}"))

        game.start_game()
        assert not game.is_game_over()

        game.end_game()
        assert game.is_game_over()

    def test_record_move(self):
        """Test recording a move in history."""
        game = GameState()
        for i in range(1, 3):
            game.add_player(Player(i, f"Player{i}"))

        game.start_game()
        game.record_move(1, "I5", 5, 5, rotation=90, flipped=False)

        assert len(game.move_history) == 1
        assert game.last_move is not None
        assert game.last_move["player_id"] == 1
        assert game.last_move["piece_name"] == "I5"
        assert game.last_move["row"] == 5
        assert game.last_move["col"] == 5
        assert game.last_move["rotation"] == 90
        assert game.last_move["flipped"] is False
        assert game.last_move["round"] == 1

    def test_can_player_move(self):
        """Test checking if player can make a move."""
        game = GameState()
        player1 = Player(1, "Alice")
        game.add_player(player1)

        assert player1.has_pieces_remaining()
        assert game.can_player_move(1)

        # Player passes
        player1.pass_turn()
        assert not game.can_player_move(1)

        # Player becomes inactive
        player1.set_inactive()
        assert not game.can_player_move(1)

    def test_get_active_players(self):
        """Test getting list of active players."""
        game = GameState()
        player1 = Player(1, "Alice")
        player2 = Player(2, "Bob")
        player3 = Player(3, "Charlie")

        game.add_player(player1)
        game.add_player(player2)
        game.add_player(player3)

        # All players start active with pieces
        active = game.get_active_players()
        assert len(active) == 3

        # Player 2 runs out of pieces
        for piece_name in list(player2.pieces.keys()):
            player2.remove_piece(piece_name)

        active = game.get_active_players()
        assert len(active) == 2
        assert player1 in active
        assert player3 in active
        assert player2 not in active

    def test_get_eliminated_players(self):
        """Test getting list of eliminated players."""
        game = GameState()
        player1 = Player(1, "Alice")
        player2 = Player(2, "Bob")
        player3 = Player(3, "Charlie")

        game.add_player(player1)
        game.add_player(player2)
        game.add_player(player3)

        # No one eliminated initially
        eliminated = game.get_eliminated_players()
        assert len(eliminated) == 0

        # Player 2 runs out of pieces
        for piece_name in list(player2.pieces.keys()):
            player2.remove_piece(piece_name)

        eliminated = game.get_eliminated_players()
        assert len(eliminated) == 1
        assert player2 in eliminated

    def test_should_end_round(self):
        """Test checking if round should end."""
        game = GameState()
        player1 = Player(1, "Alice")
        player2 = Player(2, "Bob")

        game.add_player(player1)
        game.add_player(player2)
        game.start_game()

        # Round should not end yet
        assert not game.should_end_round()

        # All active players pass
        player1.pass_turn()
        player2.pass_turn()

        assert game.should_end_round()

    def test_should_end_game(self):
        """Test checking if game should end."""
        game = GameState()
        player1 = Player(1, "Alice")
        player2 = Player(2, "Bob")

        game.add_player(player1)
        game.add_player(player2)
        game.start_game()

        # Game should not end yet
        assert not game.should_end_game()

        # All active players pass
        player1.pass_turn()
        player2.pass_turn()

        assert game.should_end_game()

    def test_get_winners(self):
        """Test determining game winners."""
        game = GameState()
        player1 = Player(1, "Alice")
        player2 = Player(2, "Bob")
        player3 = Player(3, "Charlie")

        game.add_player(player1)
        game.add_player(player2)
        game.add_player(player3)

        # Add different scores - player 2 wins with highest score
        player1.add_points(50)
        player2.add_points(75)
        player3.add_points(25)

        game.end_game()

        winners = game.get_winners()
        assert len(winners) == 1
        assert player2 in winners
        assert player1 not in winners
        assert player3 not in winners

    def test_get_winners_raises_error_if_game_not_over(self):
        """Test that getting winners before game over raises error."""
        game = GameState()
        game.add_player(Player(1, "Alice"))

        with pytest.raises(ValueError, match="Game is not over yet"):
            game.get_winners()

    def test_get_move_history(self):
        """Test retrieving move history."""
        game = GameState()
        for i in range(1, 3):
            game.add_player(Player(i, f"Player{i}"))

        game.start_game()
        game.record_move(1, "I5", 5, 5)
        game.record_move(2, "L4", 10, 10)

        history = game.get_move_history()
        assert len(history) == 2
        assert history[0]["player_id"] == 1
        assert history[1]["player_id"] == 2

        # Verify it's a copy
        history.append({"fake": "move"})
        assert len(game.move_history) == 2

    def test_get_player_positions(self):
        """Test getting player positions on board."""
        game = GameState()
        player1 = Player(1, "Alice")
        player2 = Player(2, "Bob")

        game.add_player(player1)
        game.add_player(player2)
        game.start_game()

        # Place a piece
        from src.models.piece import Piece

        piece = player1.get_piece("I2")
        game.board.place_piece(piece, 5, 5, 1)

        positions = game.get_player_positions(1)
        assert (5, 5) in positions
        assert (6, 5) in positions

    def test_get_board_state(self):
        """Test getting current board state."""
        game = GameState()
        player1 = Player(1, "Alice")
        player2 = Player(2, "Bob")

        game.add_player(player1)
        game.add_player(player2)
        game.start_game()

        state = game.get_board_state()
        assert len(state) == 20
        assert len(state[0]) == 20
        assert all(cell is None for row in state for cell in row)

    def test_game_state_repr(self):
        """Test string representation of game state."""
        game = GameState()
        assert "GameState" in repr(game)
        assert "SETUP" in repr(game)

        for i in range(1, 3):
            game.add_player(Player(i, f"Player{i}"))

        assert "players=2" in repr(game)
