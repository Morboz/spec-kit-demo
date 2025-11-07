"""
Piece Inventory UI Component

This module provides the PieceInventory class which displays the
remaining pieces for all players with visual piece representations.
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional, List, Dict
from src.models.player import Player
from src.config.pieces import PIECE_DEFINITIONS


class PieceInventory(ttk.Frame):
    """UI component for displaying players' remaining pieces."""

    def __init__(
        self,
        parent: tk.Widget,
        players: Optional[List[Player]] = None,
    ) -> None:
        """
        Initialize the piece inventory.

        Args:
            parent: Parent widget
            players: List of players to display
        """
        super().__init__(parent)
        self.players = players or []
        self.selected_piece: Optional[str] = None
        self.on_piece_selected: Optional[callable] = None

        # Create widget
        self._create_widgets()

    def _create_widgets(self) -> None:
        """Create and arrange UI widgets."""
        # Title
        title_label = ttk.Label(
            self, text="Piece Inventory", font=("Arial", 12, "bold")
        )
        title_label.pack(pady=(0, 10))

        # Create notebook for tabbed view
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Dictionary to store player tabs
        self.player_tabs: Dict[int, ttk.Frame] = {}

        # Create initial tabs
        if self.players:
            self._create_player_tabs()

    def _create_player_tabs(self) -> None:
        """Create tab for each player."""
        for player in self.players:
            self._create_player_tab(player)

    def _create_player_tab(self, player: Player) -> None:
        """
        Create a tab for a specific player.

        Args:
            player: Player to create tab for
        """
        # Create frame for player tab
        tab_frame = ttk.Frame(self.notebook)
        self.notebook.add(tab_frame, text=f"P{player.player_id}: {player.name}")

        # Store reference
        self.player_tabs[player.player_id] = tab_frame

        # Create scrollable frame for pieces
        canvas = tk.Canvas(tab_frame, bg="white", highlightthickness=0)
        scrollbar = ttk.Scrollbar(tab_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        # Update scroll region when frame size changes
        def _on_frame_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
            # Force canvas to update
            canvas.update_idletasks()

        scrollable_frame.bind("<Configure>", _on_frame_configure)

        # Create window inside canvas
        canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        
        # Make the scrollable frame fill the canvas width
        def _on_canvas_configure(event):
            canvas.itemconfig(canvas_window, width=event.width)
        
        canvas.bind("<Configure>", _on_canvas_configure)
        canvas.configure(yscrollcommand=scrollbar.set)

        # Bind mouse wheel scrolling - only when mouse is over this canvas
        def _on_mousewheel(event):
            # macOS trackpad/mouse wheel
            if event.delta:
                canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            # Linux mouse wheel
            elif event.num == 4:
                canvas.yview_scroll(-1, "units")
            elif event.num == 5:
                canvas.yview_scroll(1, "units")

        # Bind mousewheel only when entering/leaving this canvas
        def _bind_mousewheel(event):
            canvas.bind_all("<MouseWheel>", _on_mousewheel)  # Windows/macOS
            canvas.bind_all("<Button-4>", _on_mousewheel)    # Linux scroll up
            canvas.bind_all("<Button-5>", _on_mousewheel)    # Linux scroll down

        def _unbind_mousewheel(event):
            canvas.unbind_all("<MouseWheel>")
            canvas.unbind_all("<Button-4>")
            canvas.unbind_all("<Button-5>")

        canvas.bind("<Enter>", _bind_mousewheel)
        canvas.bind("<Leave>", _unbind_mousewheel)

        # Pack canvas and scrollbar
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        # Display player's pieces
        self._display_player_pieces(scrollable_frame, player)
        
        # Force initial scroll region update
        tab_frame.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox("all"))

    def _display_player_pieces(self, parent: ttk.Frame, player: Player) -> None:
        """
        Display all pieces for a player with visual representations.

        Args:
            parent: Parent frame
            player: Player whose pieces to display
        """
        # Get all piece names sorted by size
        all_pieces = self._get_all_piece_names_sorted_by_size()

        # Track which pieces are placed vs remaining
        placed_pieces = set()
        remaining_pieces = []

        for piece_name in all_pieces:
            piece = player.get_piece(piece_name)
            if piece and piece.is_placed:
                placed_pieces.add(piece_name)
            elif piece:
                remaining_pieces.append(piece_name)

        # Display remaining pieces
        if remaining_pieces:
            remaining_label = ttk.Label(
                parent,
                text=f"Remaining Pieces ({len(remaining_pieces)})",
                font=("Arial", 10, "bold"),
                foreground="green",
            )
            remaining_label.pack(pady=(5, 2))

            # Group by size for better organization
            current_size = None
            for piece_name in remaining_pieces:
                piece_size = len(PIECE_DEFINITIONS[piece_name])
                
                # Add size separator
                if current_size != piece_size:
                    if current_size is not None:
                        ttk.Separator(parent, orient='horizontal').pack(fill=tk.X, pady=5)
                    current_size = piece_size
                
                # Create piece frame with visual representation
                piece_frame = ttk.Frame(parent)
                piece_frame.pack(fill=tk.X, pady=3, padx=5)

                # Create clickable canvas for piece visualization
                canvas = tk.Canvas(
                    piece_frame,
                    width=100,
                    height=100,
                    bg="white",
                    highlightthickness=1,
                    highlightbackground="gray",
                    cursor="hand2"
                )
                canvas.pack(side=tk.LEFT, padx=(0, 10))
                
                # Draw the piece
                self._draw_piece_on_canvas(canvas, piece_name, player)
                
                # Make canvas clickable
                canvas.bind("<Button-1>", lambda e, pn=piece_name: self._on_piece_click(pn))
                
                # Info label
                info_frame = ttk.Frame(piece_frame)
                info_frame.pack(side=tk.LEFT, fill=tk.Y)
                
                name_label = ttk.Label(
                    info_frame,
                    text=piece_name,
                    font=("Arial", 11, "bold")
                )
                name_label.pack(anchor=tk.W)
                
                size_label = ttk.Label(
                    info_frame,
                    text=f"{piece_size} square{'s' if piece_size > 1 else ''}",
                    font=("Arial", 9),
                    foreground="gray"
                )
                size_label.pack(anchor=tk.W)

        # Display placed pieces (simplified)
        if placed_pieces:
            placed_label = ttk.Label(
                parent,
                text=f"Placed Pieces ({len(placed_pieces)})",
                font=("Arial", 10, "bold"),
                foreground="red",
            )
            placed_label.pack(pady=(15, 2))

            # Show placed pieces as a compact list
            placed_text = ", ".join(sorted(placed_pieces))
            placed_info = ttk.Label(
                parent,
                text=placed_text,
                font=("Arial", 9),
                foreground="gray",
                wraplength=250
            )
            placed_info.pack(pady=(0, 5), padx=10)

    def _get_all_piece_names_sorted_by_size(self) -> List[str]:
        """
        Get list of all piece names sorted by size (number of squares).

        Returns:
            List of piece names sorted by size (ascending)
        """
        # Get all pieces from PIECE_DEFINITIONS and sort by size
        pieces = []
        for name, coords in PIECE_DEFINITIONS.items():
            pieces.append((name, len(coords)))
        
        # Sort by size, then by name
        pieces.sort(key=lambda x: (x[1], x[0]))
        
        return [name for name, _ in pieces]
    
    def _draw_piece_on_canvas(
        self, 
        canvas: tk.Canvas, 
        piece_name: str, 
        player: Player
    ) -> None:
        """
        Draw a visual representation of a piece on canvas.

        Args:
            canvas: Canvas to draw on
            piece_name: Name of the piece
            player: Player object for color
        """
        if piece_name not in PIECE_DEFINITIONS:
            return
        
        coords = PIECE_DEFINITIONS[piece_name]
        
        # Calculate bounds
        rows = [r for r, c in coords]
        cols = [c for r, c in coords]
        min_row, max_row = min(rows), max(rows)
        min_col, max_col = min(cols), max(cols)
        
        piece_height = max_row - min_row + 1
        piece_width = max_col - min_col + 1
        
        # Calculate cell size to fit in canvas (with padding)
        canvas_width = 100
        canvas_height = 100
        padding = 10
        
        cell_size = min(
            (canvas_width - 2 * padding) // max(piece_width, 1),
            (canvas_height - 2 * padding) // max(piece_height, 1)
        )
        cell_size = min(cell_size, 25)  # Max cell size
        
        # Calculate offset to center the piece
        total_width = piece_width * cell_size
        total_height = piece_height * cell_size
        offset_x = (canvas_width - total_width) // 2
        offset_y = (canvas_height - total_height) // 2
        
        # Get player color from player object
        color = player.color
        
        # Draw each square
        for row, col in coords:
            x = offset_x + (col - min_col) * cell_size
            y = offset_y + (row - min_row) * cell_size
            
            # Draw filled rectangle
            canvas.create_rectangle(
                x, y,
                x + cell_size, y + cell_size,
                fill=color,
                outline="black",
                width=2
            )
        
        # Draw piece name below
        canvas.create_text(
            canvas_width // 2,
            canvas_height - 5,
            text=piece_name,
            font=("Arial", 8, "bold"),
            fill="black"
        )

    def _on_piece_click(self, piece_name: str) -> None:
        """
        Handle piece selection.

        Args:
            piece_name: Name of selected piece
        """
        self.selected_piece = piece_name
        if self.on_piece_selected:
            self.on_piece_selected(piece_name)

    def set_players(self, players: List[Player]) -> None:
        """
        Set the players to display.

        Args:
            players: List of players
        """
        self.players = players
        self._refresh_tabs()

    def _refresh_tabs(self) -> None:
        """Refresh all player tabs."""
        # Clear existing tabs
        for tab in self.player_tabs.values():
            tab.destroy()
        self.player_tabs.clear()

        # Recreate tabs
        if self.players:
            self._create_player_tabs()

    def update_inventory(self, player_id: int) -> None:
        """
        Update inventory for a specific player.

        Args:
            player_id: ID of player to update
        """
        # Refresh the specific player's tab
        if player_id in self.player_tabs and self.players:
            for player in self.players:
                if player.player_id == player_id:
                    self._refresh_tabs()
                    break

    def select_player_tab(self, player_id: int) -> None:
        """
        Select the tab for a specific player.

        Args:
            player_id: ID of player to select
        """
        # Find tab index
        for i, (pid, _) in enumerate(self.player_tabs.items()):
            if pid == player_id:
                self.notebook.select(i)
                break

    def get_selected_piece(self) -> Optional[str]:
        """
        Get the currently selected piece.

        Returns:
            Name of selected piece or None
        """
        return self.selected_piece

    def set_piece_selected_callback(self, callback: callable) -> None:
        """
        Set callback for piece selection.

        Args:
            callback: Function to call when piece is selected
        """
        self.on_piece_selected = callback

    def clear(self) -> None:
        """Clear the inventory display."""
        for tab in self.player_tabs.values():
            tab.destroy()
        self.player_tabs.clear()
        self.players = []
        self.selected_piece = None
