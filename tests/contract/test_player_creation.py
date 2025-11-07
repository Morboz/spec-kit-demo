"""Contract tests for Player creation in game setup flow.

This test validates that Players can be properly created during game setup,
ensuring each player has all necessary components for gameplay.
"""

from src.models.player import Player


class TestPlayerCreationContract:
    """Contract tests for Player creation during game setup."""

    def test_player_created_with_all_21_pieces(self):
        """Contract: Each player must receive all 21 Blokus pieces.

        Given: A new game setup is initiated
        When: A player is created
        Then: Player must have exactly 21 unique pieces available
        """
        player = Player(player_id=1, name="Player 1")

        # Verify player has all 21 pieces
        all_pieces = player.get_all_pieces()
        assert len(all_pieces) == 21, "Player must have exactly 21 pieces"

        # Verify all pieces are unplaced initially
        unplaced_pieces = player.get_unplaced_pieces()
        assert len(unplaced_pieces) == 21, "All pieces must be unplaced initially"

        # Verify no pieces are placed
        placed_pieces = player.get_placed_pieces()
        assert len(placed_pieces) == 0, "No pieces should be placed initially"

    def test_player_has_valid_starting_corner(self):
        """Contract: Each player must be assigned a valid board corner.

        Given: A new game setup is initiated
        When: A player is created
        Then: Player must be assigned a valid starting corner position
        """
        # Test corners for different player IDs
        corners = {
            1: (0, 0),  # Top-left
            2: (0, 19),  # Top-right
            3: (19, 19),  # Bottom-right
            4: (19, 0),  # Bottom-left
        }

        for player_id, expected_corner in corners.items():
            player = Player(player_id=player_id, name=f"Player {player_id}")
            assert (
                player.get_starting_corner() == expected_corner
            ), f"Player {player_id} must have corner {expected_corner}"

    def test_player_is_ready_for_gameplay(self):
        """Contract: Player must have all attributes needed for gameplay.

        Given: A new game setup is initiated
        When: A player is created
        Then: Player must have valid ID, name, color, score, and state
        """
        player = Player(player_id=1, name="Alice")

        # Verify required attributes exist and are valid
        assert player.player_id == 1
        assert player.name == "Alice"
        assert player.get_color() is not None, "Player must have a color"
        assert player.get_color().startswith("#"), "Color must be hex format"
        assert player.score == 0, "Initial score must be 0"
        assert player.is_active is True, "Player must be active initially"

        # Verify player can report state
        assert player.get_remaining_piece_count() == 21
        # Total squares in all 21 pieces is 88 (not all pieces are size 1)
        assert player.get_remaining_squares() > 0
        assert player.has_pieces_remaining() is True

    def test_multiple_players_have_unique_identifiers(self):
        """Contract: Each player must have unique ID and starting position.

        Given: A new game setup with multiple players
        When: Players are created
        Then: Each player must have unique ID and corner
        """
        players = [
            Player(player_id=1, name="Player 1"),
            Player(player_id=2, name="Player 2"),
            Player(player_id=3, name="Player 3"),
            Player(player_id=4, name="Player 4"),
        ]

        # Verify all player IDs are unique
        player_ids = [p.player_id for p in players]
        assert len(player_ids) == len(set(player_ids)), "Player IDs must be unique"

        # Verify all starting corners are unique
        corners = [p.get_starting_corner() for p in players]
        assert len(corners) == len(set(corners)), "Starting corners must be unique"

        # Verify all corners are valid board positions
        for corner in corners:
            row, col = corner
            assert 0 <= row < 20, f"Corner row {row} must be on board"
            assert 0 <= col < 20, f"Corner col {col} must be on board"
