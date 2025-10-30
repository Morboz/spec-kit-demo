"""
Game Results UI Component

This module provides the GameResults class which displays the final game results,
including winners, scores, and detailed score breakdown.
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional, List, Dict
from src.models.player import Player
from src.game.winner_determiner import WinnerDeterminer


class GameResults(tk.Toplevel):
    """UI window for displaying final game results."""

    def __init__(
        self,
        parent: tk.Widget,
        game_state,
        winner_determiner: WinnerDeterminer,
    ) -> None:
        """
        Initialize the game results window.

        Args:
            parent: Parent widget
            game_state: Game state (to get final scores)
            winner_determiner: Winner determiner with game results
        """
        super().__init__(parent)
        self.game_state = game_state
        self.winner_determiner = winner_determiner
        self.players = game_state.players

        # Configure window
        self.title("Game Over - Results")
        self.geometry("600x500")
        self.resizable(True, True)

        # Make modal
        self.transient(parent)
        self.grab_set()

        # Create widget
        self._create_widgets()

        # Display results
        self.display_results()

    def _create_widgets(self) -> None:
        """Create and arrange UI widgets."""
        # Main container with scrollbar
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Create canvas with scrollbar for results
        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")),
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Results container
        self.results_frame = ttk.Frame(scrollable_frame)
        self.results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Title
        self.title_label = ttk.Label(
            self.results_frame,
            text="Game Over!",
            font=("Arial", 18, "bold"),
        )
        self.title_label.pack(pady=(0, 20))

        # Winners section
        self.winners_frame = ttk.LabelFrame(
            self.results_frame,
            text="Winner(s)",
            padding=10,
        )
        self.winners_frame.pack(fill=tk.X, pady=(0, 15))

        # Detailed scores section
        self.scores_frame = ttk.LabelFrame(
            self.results_frame,
            text="Final Scores",
            padding=10,
        )
        self.scores_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

        # Create treeview for scores
        columns = ("Rank", "Player", "Score", "Squares Placed", "Squares Remaining", "Bonus")
        self.scores_tree = ttk.Treeview(
            self.scores_frame,
            columns=columns,
            show="headings",
            height=6,
        )

        # Define column headings
        self.scores_tree.heading("Rank", text="Rank")
        self.scores_tree.heading("Player", text="Player")
        self.scores_tree.heading("Score", text="Final Score")
        self.scores_tree.heading("Squares Placed", text="Squares Placed")
        self.scores_tree.heading("Squares Remaining", text="Squares Remaining")
        self.scores_tree.heading("Bonus", text="All Pieces Bonus")

        # Define column widths
        self.scores_tree.column("Rank", width=60)
        self.scores_tree.column("Player", width=120)
        self.scores_tree.column("Score", width=80)
        self.scores_tree.column("Squares Placed", width=120)
        self.scores_tree.column("Squares Remaining", width=130)
        self.scores_tree.column("Bonus", width=100)

        # Add scrollbar for treeview
        tree_scrollbar = ttk.Scrollbar(
            self.scores_frame,
            orient="vertical",
            command=self.scores_tree.yview,
        )
        self.scores_tree.configure(yscrollcommand=tree_scrollbar.set)

        # Pack treeview and scrollbar
        self.scores_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Buttons frame
        buttons_frame = ttk.Frame(self.results_frame)
        buttons_frame.pack(fill=tk.X, pady=(10, 0))

        # New Game button
        self.new_game_button = ttk.Button(
            buttons_frame,
            text="New Game",
            command=self._on_new_game,
        )
        self.new_game_button.pack(side=tk.LEFT, padx=(0, 10))

        # Close button
        self.close_button = ttk.Button(
            buttons_frame,
            text="Close",
            command=self._on_close,
        )
        self.close_button.pack(side=tk.LEFT)

        # Initialize callback
        self.new_game_callback: Optional[callable] = None

    def display_results(self) -> None:
        """Display the game results in the window."""
        try:
            # Display winners
            self._display_winners()

            # Display detailed scores
            self._display_detailed_scores()

        except Exception as e:
            # Show error if something goes wrong
            error_label = ttk.Label(
                self.results_frame,
                text=f"Error displaying results: {e}",
                foreground="red",
            )
            error_label.pack(pady=20)

    def _display_winners(self) -> None:
        """Display the winner(s) in the winners section."""
        # Clear previous winners
        for widget in self.winners_frame.winfo_children():
            widget.destroy()

        try:
            winners = self.winner_determiner.get_winners()
            winner_names = self.winner_determiner.get_winner_names()

            if len(winners) == 1:
                # Single winner
                winner_text = f"🏆 Winner: {winner_names[0]} 🏆"
                winner_color = "green"
            else:
                # Tie
                winner_text = f"🤝 It's a tie! Winners: {', '.join(winner_names)} 🤝"
                winner_color = "blue"

            winner_label = ttk.Label(
                self.winners_frame,
                text=winner_text,
                font=("Arial", 14, "bold"),
                foreground=winner_color,
            )
            winner_label.pack()

            # Add winning score
            try:
                winning_score = self.winner_determiner.get_winning_score()
                score_label = ttk.Label(
                    self.winners_frame,
                    text=f"Winning Score: {winning_score}",
                    font=("Arial", 12),
                )
                score_label.pack(pady=(10, 0))
            except ValueError:
                pass  # No scores available

        except ValueError:
            # Game not over yet
            error_label = ttk.Label(
                self.winners_frame,
                text="Game is not over yet",
                foreground="red",
            )
            error_label.pack()

    def _display_detailed_scores(self) -> None:
        """Display detailed score breakdown for all players."""
        # Clear existing items
        for item in self.scores_tree.get_children():
            self.scores_tree.delete(item)

        try:
            # Get ranked players
            ranked = self.winner_determiner.rank_players()

            # Display each player's results
            for rank, player_id, name in ranked:
                player = self.game_state.get_player_by_id(player_id)
                if not player:
                    continue

                # Get score breakdown
                breakdown = self.winner_determiner.get_score_breakdown(player)

                # Insert row
                self.scores_tree.insert(
                    "",
                    tk.END,
                    values=(
                        rank,
                        name,
                        breakdown["final_score"],
                        breakdown["placed_squares"],
                        breakdown["unplaced_squares"],
                        breakdown["all_pieces_bonus"],
                    ),
                )

        except Exception as e:
            # Show error in treeview
            self.scores_tree.insert(
                "",
                tk.END,
                values=("Error", str(e), "", "", "", ""),
            )

    def set_new_game_callback(self, callback: callable) -> None:
        """
        Set callback for new game button.

        Args:
            callback: Function to call when new game is requested
        """
        self.new_game_callback = callback

    def _on_new_game(self) -> None:
        """Handle new game button click."""
        if self.new_game_callback:
            self.new_game_callback()

    def _on_close(self) -> None:
        """Handle close button click."""
        self.destroy()
