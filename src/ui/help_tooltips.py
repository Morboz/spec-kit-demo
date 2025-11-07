"""
Help Tooltips and Documentation System

This module provides contextual help, tooltips, and documentation
for AI battle mode features and game modes.
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional, Dict, Any, Callable
import webbrowser


class Tooltip:
    """
    Tooltip widget for displaying helpful text on hover.

    Creates a popup window with helpful information when
    hovering over a widget.
    """

    def __init__(
        self,
        widget: tk.Widget,
        text: str,
        delay: int = 500,
        wraplength: int = 300,
        **kwargs
    ):
        """
        Initialize the tooltip.

        Args:
            widget: Widget to attach tooltip to
            text: Text to display
            delay: Delay in milliseconds before showing tooltip
            wraplength: Maximum line length for text wrapping
            **kwargs: Additional configuration options
        """
        self.widget = widget
        self.text = text
        self.delay = delay
        self.wraplength = wraplength

        # Configuration
        self.x = 0
        self.y = 0
        self.tw = None
        self._id = None

        # Bind events
        self.widget.bind("<Enter>", self.on_enter)
        self.widget.bind("<Leave>", self.on_leave)
        self.widget.bind("<ButtonPress>", self.on_leave)

    def on_enter(self, event):
        """Handle mouse enter event."""
        self._schedule_tooltip()

    def on_leave(self, event):
        """Handle mouse leave event."""
        self._unschedule_tooltip()
        self._hide_tooltip()

    def _schedule_tooltip(self):
        """Schedule tooltip to be shown after delay."""
        self._unschedule_tooltip()
        self._id = self.widget.after(self.delay, self._show_tooltip)

    def _unschedule_tooltip(self):
        """Cancel scheduled tooltip."""
        if self._id:
            self.widget.after_cancel(self._id)
            self._id = None

    def _show_tooltip(self):
        """Display the tooltip window."""
        if self.tw:
            return

        # Get widget position
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5

        # Create tooltip window
        self.tw = tk.Toplevel(self.widget)
        self.tw.wm_overrideredirect(True)
        self.tw.wm_geometry(f"+{x}+{y}")

        # Create label with text
        label = ttk.Label(
            self.tw,
            text=self.text,
            justify=tk.LEFT,
            background="#ffffe0",
            relief=tk.SOLID,
            borderwidth=1,
            font=("Arial", 9),
            wraplength=self.wraplength
        )
        label.pack()

        # Handle click outside to close
        self.tw.bind("<ButtonPress>", lambda e: self._hide_tooltip())

    def _hide_tooltip(self):
        """Hide and destroy the tooltip window."""
        if self.tw:
            self.tw.destroy()
            self.tw = None


class HelpDialog:
    """
    Dialog window for displaying comprehensive help documentation.
    """

    def __init__(
        self,
        parent: tk.Widget,
        title: str = "Help",
        content: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize the help dialog.

        Args:
            parent: Parent widget
            title: Dialog title
            content: Help content (optional)
            **kwargs: Additional dialog arguments
        """
        self.parent = parent
        self.dialog = None

        # Predefined help content
        self.help_content = content or self._get_default_content()

        # Create dialog
        self._create_dialog(title)

    def _create_dialog(self, title: str):
        """Create the help dialog window."""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title(title)
        self.dialog.geometry("600x500")
        self.dialog.resizable(True, True)

        # Make modal
        self.dialog.transient(self.parent)
        self.dialog.grab_set()

        # Main frame
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Create notebook for tabbed help
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)

        # Game Modes tab
        modes_frame = ttk.Frame(notebook, padding="10")
        notebook.add(modes_frame, text="Game Modes")
        self._create_modes_content(modes_frame)

        # Difficulty Levels tab
        difficulty_frame = ttk.Frame(notebook, padding="10")
        notebook.add(difficulty_frame, text="Difficulty Levels")
        self._create_difficulty_content(difficulty_frame)

        # Controls tab
        controls_frame = ttk.Frame(notebook, padding="10")
        notebook.add(controls_frame, text="Controls")
        self._create_controls_content(controls_frame)

        # Spectator Mode tab
        spectator_frame = ttk.Frame(notebook, padding="10")
        notebook.add(spectator_frame, text="Spectator Mode")
        self._create_spectator_content(spectator_frame)

        # Close button
        close_btn = ttk.Button(
            main_frame,
            text="Close",
            command=self.close
        )
        close_btn.pack(pady=(10, 0))

    def _create_modes_content(self, parent):
        """Create game modes help content."""
        content = ttk.Frame(parent)
        content.pack(fill=tk.BOTH, expand=True)

        # Scrollable text
        text_widget = tk.Text(
            content,
            wrap=tk.WORD,
            font=("Arial", 10),
            state=tk.DISABLED
        )
        scrollbar = ttk.Scrollbar(content, orient="vertical", command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)

        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Insert content
        text_widget.configure(state=tk.NORMAL)
        text_widget.insert(tk.END, self._get_game_modes_help())
        text_widget.configure(state=tk.DISABLED)

    def _create_difficulty_content(self, parent):
        """Create difficulty levels help content."""
        content = ttk.Frame(parent)
        content.pack(fill=tk.BOTH, expand=True)

        text_widget = tk.Text(
            content,
            wrap=tk.WORD,
            font=("Arial", 10),
            state=tk.DISABLED
        )
        scrollbar = ttk.Scrollbar(content, orient="vertical", command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)

        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        text_widget.configure(state=tk.NORMAL)
        text_widget.insert(tk.END, self._get_difficulty_help())
        text_widget.configure(state=tk.DISABLED)

    def _create_controls_content(self, parent):
        """Create controls help content."""
        content = ttk.Frame(parent)
        content.pack(fill=tk.BOTH, expand=True)

        text_widget = tk.Text(
            content,
            wrap=tk.WORD,
            font=("Arial", 10),
            state=tk.DISABLED
        )
        scrollbar = ttk.Scrollbar(content, orient="vertical", command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)

        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        text_widget.configure(state=tk.NORMAL)
        text_widget.insert(tk.END, self._get_controls_help())
        text_widget.configure(state=tk.DISABLED)

    def _create_spectator_content(self, parent):
        """Create spectator mode help content."""
        content = ttk.Frame(parent)
        content.pack(fill=tk.BOTH, expand=True)

        text_widget = tk.Text(
            content,
            wrap=tk.WORD,
            font=("Arial", 10),
            state=tk.DISABLED
        )
        scrollbar = ttk.Scrollbar(content, orient="vertical", command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)

        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        text_widget.configure(state=tk.NORMAL)
        text_widget.insert(tk.END, self._get_spectator_help())
        text_widget.configure(state=tk.DISABLED)

    def _get_default_content(self) -> str:
        """Get default help content."""
        return self._get_game_modes_help()

    def _get_game_modes_help(self) -> str:
        """Get game modes help text."""
        return """Game Modes

Blokus AI Battle Mode offers several game modes to suit different play styles:

1. Single AI Mode
   - Play against one AI opponent
   - 2-player game (you + AI)
   - AI controls position 3 (bottom-left quadrant)
   - Your pieces are blue, AI pieces are red
   - Great for learning the game or casual play

2. Three AI Mode
   - Compete against three AI opponents
   - 4-player game (you + 3 AI players)
   - AI controls positions 2, 3, and 4
   - Your pieces are blue, AI pieces are red, green, and yellow
   - More challenging and strategic gameplay
   - Each AI has independent strategy

3. Spectate Mode
   - Watch AI vs AI vs AI vs AI
   - All 4 players are AI-controlled
   - Mixed difficulty levels (Easy, Medium, Hard)
   - No human input required - fully automated
   - Great for entertainment or learning AI strategies
   - Includes statistics tracking and final score display

How to Start:
1. Click "New Game" from the main menu
2. Select your desired game mode
3. Configure difficulty (if applicable)
4. Click "Start Game"

Tips:
- Watch how different AI difficulty levels play
- Easy AI makes simpler, more random moves
- Hard AI uses advanced strategic evaluation
- Spectator mode lets you see AI vs AI battles
"""

    def _get_difficulty_help(self) -> str:
        """Get difficulty levels help text."""
        return """AI Difficulty Levels

Each AI player has a difficulty setting that affects their gameplay:

Easy (Random Strategy)
- Uses simple random placement
- Faster move calculation (1-2 seconds)
- Good for beginners
- Focuses on valid moves rather than strategy
- Lower challenge level
- Recommended for learning

Medium (Corner Strategy)
- Balanced corner-focused placement
- Moderate move calculation time (3-5 seconds)
- Good for intermediate players
- Considers corner connections
- Balances speed and strategy
- Recommended for most players

Hard (Strategic Strategy)
- Advanced strategic evaluation with lookahead
- Slower move calculation (5-8 seconds)
- Challenging gameplay
- Considers multiple factors:
  * Corner connections
  * Board position
  * Future mobility
  * Area control
- Recommended for expert players

Difficulty Persistence
- Your difficulty preference is saved
- Next game uses last selected difficulty
- You can change difficulty anytime before starting

Performance Impact
- Easy: Fastest gameplay
- Medium: Balanced
- Hard: Slower but more strategic

Choose difficulty based on:
- Your experience level
- Desired challenge
- Available time
- Learning goals
"""

    def _get_controls_help(self) -> str:
        """Get controls help text."""
        return """Game Controls

Mouse Controls:
- Left Click: Select piece from inventory
- Left Click: Place selected piece on board
- Right Click: Rotate selected piece
- Scroll Wheel: Navigate through pieces (when inventory is focused)

Keyboard Shortcuts (Future Feature):
- 1-9: Quick-select pieces from inventory
- R: Rotate selected piece
- Space: Pass turn (when no valid moves)
- Esc: Cancel current action
- F1: Open help dialog
- Ctrl+N: New game
- Ctrl+Q: Quit game

UI Elements:
- Game Board: 20x20 grid for piece placement
- Piece Inventory: Shows available pieces (unplaced)
- Current Player Indicator: Shows whose turn it is
- Score Display: Current scores for all players
- Turn Counter: Number of completed turns
- AI Difficulty Indicator: Shows AI difficulty levels

Game Actions:
- Place Piece: Click on piece, then click on board
- Rotate Piece: Right-click on selected piece or press R
- Pass Turn: Click "Pass" button (when you have no valid moves)
- Restart: Click "Restart" button to start new game
- Cancel: Press Esc to cancel current selection

Visual Indicators:
- Blue highlighting: Valid placement positions
- Red highlighting: Invalid placement positions
- Orange text: "AI is thinking..." during AI turns
- Colored borders: Distinguish player quadrants

Tips:
- Hover over UI elements to see helpful tooltips
- Watch the current player indicator to track turns
- AI difficulty is shown for each AI player
- Scores update after each turn
"""

    def _get_spectator_help(self) -> str:
        """Get spectator mode help text."""
        return """Spectator Mode

Watch AI vs AI battles in fully automated games!

What is Spectator Mode?
- All 4 players are AI-controlled
- No human input required
- You watch the game unfold automatically
- Games play themselves from start to finish
- Great for entertainment and learning

Features:
✓ Mixed AI Difficulty Levels
  - Easy, Medium, and Hard AI opponents
  - Each AI has unique strategy and playstyle
  - Watch different strategies compete

✓ Real-Time Visual Indicators
  - Current AI player highlighted
  - Turn counter and game timer
  - "AI is thinking..." status
  - Automatic gameplay status

✓ Game Statistics
  - Track all moves and passes
  - AI calculation times
  - Final scores for each player
  - Winner announcement

✓ Smooth Gameplay
  - 500ms delay between turns
  - Easy to follow and observe
  - Automatic game progression
  - No interaction needed

How to Use:
1. Click "New Game" from main menu
2. Select "Spectate AI" mode
3. Click "Start Game"
4. Sit back and enjoy the show!

Statistics Available:
- Total turns in game
- Duration (time to complete)
- Each player's moves and passes
- AI calculation performance
- Final scores and winner
- Performance metrics per AI

Educational Value:
- Learn Blokus strategies from AI
- Observe different difficulty levels
- See how AI evaluates positions
- Understand optimal play patterns
- Compare AI strategies

Entertainment:
- Relaxing to watch
- Like a sport or competition
- See unexpected outcomes
- Root for your favorite AI!

Game Completion:
- Games end automatically when all players pass
- Statistics dialog displays results
- Option to view detailed performance data
- Can start new spectator game immediately
"""

    def show(self):
        """Show the help dialog."""
        if self.dialog:
            self.dialog.lift()
            self.dialog.focus_set()

    def close(self):
        """Close the help dialog."""
        if self.dialog:
            self.dialog.destroy()
            self.dialog = None


# Utility functions
def add_tooltip(widget: tk.Widget, text: str, delay: int = 500):
    """
    Add a tooltip to a widget.

    Args:
        widget: Widget to add tooltip to
        text: Tooltip text
        delay: Delay in milliseconds before showing
    """
    return Tooltip(widget, text, delay)


def show_help_dialog(parent: tk.Widget, title: str = "Game Help"):
    """
    Show a help dialog.

    Args:
        parent: Parent widget
        title: Dialog title

    Returns:
        HelpDialog instance
    """
    dialog = HelpDialog(parent, title)
    dialog.show()
    return dialog


# Predefined tooltip texts
TOOLTIP_TEXT = {
    "single_ai": "Play against one AI opponent. You control position 1 (blue), AI controls position 3 (red).\nShortcut: Press F2",
    "three_ai": "Compete against three AI opponents. You control position 1 (blue), AI controls positions 2, 3, and 4.\nShortcut: Press F3",
    "spectate": "Watch AI vs AI battle. All 4 players are AI-controlled with mixed difficulty levels. No input required.\nShortcut: Press F4",
    "easy": "Easy AI uses random placement. Faster moves, simpler strategy. Good for beginners.",
    "medium": "Medium AI uses corner strategy. Balanced moves with moderate calculation time. Good for most players.",
    "hard": "Hard AI uses strategic evaluation. Slower but more challenging. Best for expert players.",
    "ai_thinking": "AI is calculating the best move. Please wait...",
    "turn": "Current turn number. Shows how many turns have been completed.",
    "score": "Current score. Points are awarded for each square placed on the board.",
    "pass": "Pass your turn if you have no valid moves. Game continues with next player.",
    "restart": "Start a new game. Current game will be lost.",
    "piece_inventory": "Your remaining pieces. Click to select, then click on board to place.",
    "help": "Open help dialog with detailed information about game modes and controls.\nShortcut: Press F1 or H",
    "keyboard_shortcuts": "Keyboard shortcuts help:\n• F1: Help dialog\n• F2: Single AI mode\n• F3: Three AI mode\n• F4: Spectate mode\n• R: Rotate piece\n• H: Show shortcuts",
}


# Example usage
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Help Tooltips Test")
    root.geometry("500x300")

    frame = ttk.Frame(root, padding="20")
    frame.pack(fill=tk.BOTH, expand=True)

    # Add buttons with tooltips
    single_btn = ttk.Button(frame, text="Single AI Mode")
    single_btn.pack(pady=5)
    add_tooltip(single_btn, TOOLTIP_TEXT["single_ai"])

    three_ai_btn = ttk.Button(frame, text="Three AI Mode")
    three_ai_btn.pack(pady=5)
    add_tooltip(three_ai_btn, TOOLTIP_TEXT["three_ai"])

    spectate_btn = ttk.Button(frame, text="Spectate Mode")
    spectate_btn.pack(pady=5)
    add_tooltip(spectate_btn, TOOLTIP_TEXT["spectate"])

    help_btn = ttk.Button(
        frame,
        text="Show Help",
        command=lambda: show_help_dialog(root)
    )
    help_btn.pack(pady=(20, 5))

    # Add button to test dialog
    test_btn = ttk.Button(
        frame,
        text="Show Help Dialog",
        command=lambda: show_help_dialog(root, "AI Battle Mode Help")
    )
    test_btn.pack(pady=5)

    root.mainloop()
