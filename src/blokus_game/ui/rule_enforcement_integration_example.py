"""
Rule Enforcement Integration Example

This module demonstrates how to integrate rule enforcement with error display
and placement preview in a complete Blokus game UI.

It shows:
- Real-time validation feedback
- Clear error messages for invalid moves
- Visual preview of piece placement
"""

import tkinter as tk
from tkinter import ttk

from blokus_game.game.rules import BlokusRules
from blokus_game.models.board import Board
from blokus_game.models.game_state import GameState
from blokus_game.models.player import Player
from blokus_game.ui.current_player_indicator import CurrentPlayerIndicator
from blokus_game.ui.error_display import ErrorDisplay
from blokus_game.ui.placement_preview import PlacementPreview


class RuleEnforcementGameUI(ttk.Frame):
    """
    Complete game UI with integrated rule enforcement.

    This class provides a working example of how all rule enforcement
    components work together in a real game.
    """

    def __init__(self, parent):
        """
        Initialize the game UI.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.game_state = GameState()
        self.setup_game()
        self.setup_ui()
        self.setup_preview()

    def setup_game(self):
        """Set up a basic game state."""
        # Create board
        self.board = Board()
        self.game_state.board = self.board

        # Create players
        self.player1 = Player(player_id=1, name="Alice")
        self.player2 = Player(player_id=2, name="Bob")
        self.game_state.add_player(self.player1)
        self.game_state.add_player(self.player2)

        # Set current player
        self.current_player_id = 1
        self.selected_piece = None

    def setup_ui(self):
        """Set up the user interface."""
        # Create main frame with padding
        self.configure(padding=10)

        # Top section: Current player and error display
        top_frame = ttk.Frame(self)
        top_frame.pack(fill=tk.X, pady=(0, 10))

        # Current player indicator
        self.player_indicator = CurrentPlayerIndicator(top_frame)
        self.player_indicator.pack(side=tk.LEFT, padx=(0, 10))

        # Error display
        self.error_display = ErrorDisplay(top_frame)
        self.error_display.pack(side=tk.RIGHT)

        # Middle section: Game board
        self.board_frame = ttk.LabelFrame(self, text="Game Board", padding=10)
        self.board_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Create canvas for board
        self.board_canvas = tk.Canvas(
            self.board_frame,
            width=600,
            height=600,
            bg="white",
            borderwidth=2,
            relief="solid",
        )
        self.board_canvas.pack()

        # Draw board grid
        self.draw_board_grid()

        # Bottom section: Piece selection and controls
        bottom_frame = ttk.Frame(self)
        bottom_frame.pack(fill=tk.X)

        # Piece selector
        piece_frame = ttk.LabelFrame(bottom_frame, text="Select Piece", padding=10)
        piece_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        self.piece_buttons = []
        for piece_name in self.player1.get_piece_names()[:5]:  # Show first 5 pieces
            btn = ttk.Button(
                piece_frame,
                text=piece_name,
                command=lambda n=piece_name: self.select_piece(n),
            )
            btn.pack(side=tk.LEFT, padx=5)
            self.piece_buttons.append(btn)

        # Control buttons
        control_frame = ttk.Frame(bottom_frame)
        control_frame.pack(side=tk.RIGHT)

        ttk.Button(
            control_frame,
            text="Rotate Piece",
            command=self.rotate_selected_piece,
        ).pack(pady=2)

        ttk.Button(
            control_frame,
            text="Flip Piece",
            command=self.flip_selected_piece,
        ).pack(pady=2)

        ttk.Button(
            control_frame,
            text="Skip Turn",
            command=self.skip_turn,
        ).pack(pady=2)

        # Bind board click event
        self.board_canvas.bind("<Button-1>", self.on_board_click)

    def setup_preview(self):
        """Set up the placement preview system."""
        self.placement_preview = PlacementPreview(
            self.board_canvas,
            self.game_state,
            self.error_display,
        )

    def draw_board_grid(self):
        """Draw the game board grid."""
        cell_size = 25
        board_origin_x = 50
        board_origin_y = 50

        # Draw grid lines
        for i in range(21):  # 20x20 grid
            # Vertical lines
            x = board_origin_x + i * cell_size
            self.board_canvas.create_line(
                x, board_origin_y, x, board_origin_y + 20 * cell_size
            )

            # Horizontal lines
            y = board_origin_y + i * cell_size
            self.board_canvas.create_line(
                board_origin_x, y, board_origin_x + 20 * cell_size, y
            )

        # Mark starting corners
        corners = [
            (0, 0, "Player 1"),
            (0, 19, "Player 2"),
            (19, 19, "Player 3"),
            (19, 0, "Player 4"),
        ]

        for row, col, label in corners:
            x = board_origin_x + col * cell_size + cell_size // 2
            y = board_origin_y + row * cell_size + cell_size // 2
            self.board_canvas.create_text(
                x,
                y,
                text=label.split()[1],
                font=("TkDefaultFont", 8, "bold"),
            )

    def select_piece(self, piece_name: str):
        """
        Select a piece for placement.

        Args:
            piece_name: Name of the piece to select
        """
        # Clear previous selection
        for btn in self.piece_buttons:
            btn.state(["!pressed"])

        # Find and press the button
        for btn in self.piece_buttons:
            if btn.cget("text") == piece_name:
                btn.state(["pressed"])
                break

        # Get piece from current player
        player = self.get_current_player()
        piece = player.get_piece(piece_name)

        if piece and not piece.is_placed:
            self.selected_piece = piece
            self.error_display.show_info(
                f"Selected {piece_name}. Hover over board to preview."
            )

            # Activate placement preview
            self.placement_preview.activate(piece, self.current_player_id)
        else:
            self.error_display.show("Piece not available.")
            self.selected_piece = None

    def rotate_selected_piece(self):
        """Rotate the selected piece."""
        if not self.selected_piece:
            self.error_display.show("No piece selected.")
            return

        # Create rotated copy
        rotated = self.selected_piece.rotate(90)
        self.error_display.show_info(f"Rotated {rotated.name} 90°.")

        # Update preview with rotated piece
        self.placement_preview.activate(
            self.selected_piece, self.current_player_id, rotated
        )

    def flip_selected_piece(self):
        """Flip the selected piece."""
        if not self.selected_piece:
            self.error_display.show("No piece selected.")
            return

        # Create flipped copy
        flipped = self.selected_piece.flip()
        self.error_display.show_info(f"Flipped {flipped.name}.")

        # Update preview with flipped piece
        self.placement_preview.activate(
            self.selected_piece, self.current_player_id, flipped
        )

    def skip_turn(self):
        """Skip the current player's turn."""
        player = self.get_current_player()
        player.pass_turn()
        self.error_display.show_info(f"{player.name} skipped their turn.")

        # Switch to next player
        self.switch_to_next_player()

    def on_board_click(self, event):
        """
        Handle board click event.

        Args:
            event: Tkinter mouse event
        """
        if not self.selected_piece:
            self.error_display.show("Please select a piece first.")
            return

        # Get board position
        row, col = self.placement_preview.get_board_position(event.x, event.y)

        if row is None or col is None:
            return

        # Validate the move
        result = BlokusRules.validate_move(
            self.game_state, self.current_player_id, self.selected_piece, row, col
        )

        if result.is_valid:
            # Place the piece
            self.board.place_piece(
                self.selected_piece, row, col, self.current_player_id
            )
            self.selected_piece.place_at(row, col)

            self.error_display.show("Piece placed successfully!")

            # Clear selection
            self.selected_piece = None
            self.placement_preview.deactivate()

            # Switch to next player
            self.switch_to_next_player()

        else:
            # Show error message
            self.error_display.show_validation_error(
                result.reason, self.placement_preview._get_rule_type(result.reason)
            )

    def switch_to_next_player(self):
        """Switch to the next player."""
        # Deactivate current preview
        self.placement_preview.deactivate()

        # Clear selection
        for btn in self.piece_buttons:
            btn.state(["!pressed"])

        self.selected_piece = None

        # Switch player
        self.current_player_id = 2 if self.current_player_id == 1 else 1

        # Update player indicator
        self.player_indicator.update_player(
            self.current_player_id,
            self.get_current_player().name,
            self.get_current_player().get_color(),
        )

        self.error_display.show(f"Turn: {self.get_current_player().name}")

    def get_current_player(self) -> Player:
        """
        Get the current player object.

        Returns:
            Current player
        """
        return self.player1 if self.current_player_id == 1 else self.player2


def main():
    """Run the example application."""
    root = tk.Tk()
    root.title("Blokus - Rule Enforcement Example")
    root.geometry("800x900")

    app = RuleEnforcementGameUI(root)

    app.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    root.mainloop()


if __name__ == "__main__":
    main()
