"""
Keyboard shortcuts module for Blokus.

This module provides keyboard shortcut handling for the game,
allowing users to:
- Rotate pieces
- Flip pieces
- Select pieces
- Skip turns
- Restart game
- Access help
"""

import tkinter as tk
from collections.abc import Callable
from typing import Any


class KeyboardShortcuts:
    """Manages keyboard shortcuts for the Blokus game."""

    # Default key bindings
    DEFAULT_BINDINGS = {
        # Piece manipulation
        "r": "rotate_clockwise",
        "R": "rotate_counterclockwise",
        "f": "flip_piece",
        "F": "flip_piece",
        # Piece selection
        "1": "select_piece_1",
        "2": "select_piece_2",
        "3": "select_piece_3",
        "4": "select_piece_4",
        "5": "select_piece_5",
        "6": "select_piece_6",
        "7": "select_piece_7",
        "8": "select_piece_8",
        "9": "select_piece_9",
        "0": "select_piece_0",
        # Game actions
        "space": "skip_turn",
        "Return": "place_piece",
        "Escape": "cancel_action",
        # Game control
        "n": "new_game",
        "q": "quit",
        "h": "show_help",
        "?": "show_help",
        # Navigation
        "Left": "move_cursor_left",
        "Right": "move_cursor_right",
        "Up": "move_cursor_up",
        "Down": "move_cursor_down",
        # Game mode selection (AI Battle Mode)
        "F1": "show_help_dialog",
        "F2": "select_single_ai_mode",
        "F3": "select_three_ai_mode",
        "F4": "select_spectate_mode",
    }

    def __init__(self, root: tk.Tk):
        """
        Initialize keyboard shortcuts handler.

        Args:
            root: The Tkinter root window
        """
        self.root = root
        self.bindings: dict[str, str] = self.DEFAULT_BINDINGS.copy()
        self.callbacks: dict[str, Callable] = {}
        self.enabled: bool = True

        # Store the widget that currently has focus
        self._focus_widget: tk.Widget | None = None

    def register_callback(self, action: str, callback: Callable[[], None]):
        """
        Register a callback for an action.

        Args:
            action: Action name (e.g., "rotate_clockwise")
            callback: Function to call when action is triggered
        """
        self.callbacks[action] = callback

    def bind_all(self):
        """Bind all keyboard shortcuts to the root window."""
        if not self.enabled:
            return

        for key, action in self.bindings.items():
            # Handle function keys (F1, F2, etc.) differently
            if key.startswith("F") and key[1:].isdigit():
                # For function keys, use the exact binding
                binding = f"<{key}>"
            else:
                # For regular keys, use Key-event
                binding = f"<Key-{key}>"

            # Bind to root window
            self.root.bind(binding, lambda e, a=action: self._handle_action(a))

            # Also bind to all common widgets
            for widget_class in [tk.Canvas, tk.Frame, tk.Toplevel]:
                pass  # Will be bound individually where needed

    def unbind_all(self):
        """Unbind all keyboard shortcuts."""
        for key in self.bindings.keys():
            self.root.unbind(f"<Key-{key}>")

    def enable(self):
        """Enable keyboard shortcuts."""
        self.enabled = True
        self.bind_all()

    def disable(self):
        """Disable keyboard shortcuts."""
        self.enabled = False
        self.unbind_all()

    def set_focus(self, widget: tk.Widget):
        """
        Set the focus widget for keyboard shortcuts.

        Args:
            widget: Widget that should receive keyboard events
        """
        self._focus_widget = widget
        widget.focus_set()

    def _handle_action(self, action: str):
        """
        Handle a keyboard action.

        Args:
            action: Action name to execute
        """
        if not self.enabled:
            return

        if action in self.callbacks:
            try:
                self.callbacks[action]()
            except Exception as e:
                print(f"Error executing action '{action}': {e}")

    def get_action_for_key(self, key: str) -> str | None:
        """
        Get the action associated with a key.

        Args:
            key: Key pressed

        Returns:
            Action name or None if not bound
        """
        return self.bindings.get(key)

    def add_binding(self, key: str, action: str):
        """
        Add a new key binding.

        Args:
            key: Key to bind (e.g., "c", "F1")
            action: Action to execute
        """
        self.bindings[key] = action
        if self.enabled:
            # Handle function keys differently
            if key.startswith("F") and key[1:].isdigit():
                binding = f"<{key}>"
            else:
                binding = f"<Key-{key}>"
            self.root.bind(binding, lambda e, a=action: self._handle_action(a))

    def remove_binding(self, key: str):
        """
        Remove a key binding.

        Args:
            key: Key to unbind
        """
        if key in self.bindings:
            # Handle function keys differently
            if key.startswith("F") and key[1:].isdigit():
                binding = f"<{key}>"
            else:
                binding = f"<Key-{key}>"
            self.root.unbind(binding)
            del self.bindings[key]

    def get_all_bindings(self) -> dict[str, str]:
        """Get all current key bindings."""
        return self.bindings.copy()

    def load_custom_bindings(self, bindings: dict[str, str]):
        """
        Load custom key bindings.

        Args:
            bindings: Dictionary of key -> action mappings
        """
        self.unbind_all()
        self.bindings.update(bindings)
        if self.enabled:
            self.bind_all()


class GameKeyboardHandler:
    """Handles keyboard shortcuts for the game."""

    def __init__(
        self,
        root: tk.Tk,
        game_state: Any,
        board: Any,
        piece_display: Any,
        on_rotate: Callable[[], None] | None = None,
        on_flip: Callable[[], None] | None = None,
        on_mode_select: Callable[[str], None] | None = None,
        on_show_help: Callable[[], None] | None = None,
    ):
        """
        Initialize game keyboard handler.

        Args:
            root: Tkinter root window
            game_state: Game state object
            board: Board object
            piece_display: Piece display component
            on_rotate: Callback for rotating piece
            on_flip: Callback for flipping piece
            on_mode_select: Callback for selecting game mode
            on_show_help: Callback for showing help dialog
        """
        self.root = root
        self.game_state = game_state
        self.board = board
        self.piece_display = piece_display
        self.on_rotate_callback = on_rotate
        self.on_flip_callback = on_flip
        self.on_mode_select_callback = on_mode_select
        self.on_show_help_callback = on_show_help
        self.keyboard = KeyboardShortcuts(root)

        # Setup callbacks
        self._setup_callbacks()

        # Bind to root
        self.keyboard.bind_all()

        # Bind to common events
        self.root.bind("<FocusIn>", self._on_focus_in)
        self.root.bind("<FocusOut>", self._on_focus_out)

    def _setup_callbacks(self):
        """Setup keyboard shortcut callbacks."""
        # Piece manipulation
        self.keyboard.register_callback("rotate_clockwise", self._rotate_clockwise)
        self.keyboard.register_callback(
            "rotate_counterclockwise", self._rotate_counterclockwise
        )
        self.keyboard.register_callback("flip_piece", self._flip_piece)

        # Piece selection
        for i in range(1, 10):
            self.keyboard.register_callback(
                f"select_piece_{i}", lambda i=i: self._select_piece(i - 1)
            )
        self.keyboard.register_callback("select_piece_0", lambda: self._select_piece(9))

        # Game actions
        self.keyboard.register_callback("skip_turn", self._skip_turn)
        self.keyboard.register_callback("place_piece", self._place_piece)
        self.keyboard.register_callback("cancel_action", self._cancel_action)

        # Game control
        self.keyboard.register_callback("new_game", self._new_game)
        self.keyboard.register_callback("quit", self._quit)
        self.keyboard.register_callback("show_help", self._show_help)

        # Navigation
        self.keyboard.register_callback("move_cursor_left", self._move_cursor_left)
        self.keyboard.register_callback("move_cursor_right", self._move_cursor_right)
        self.keyboard.register_callback("move_cursor_up", self._move_cursor_up)
        self.keyboard.register_callback("move_cursor_down", self._move_cursor_down)

        # Game mode selection (AI Battle Mode)
        self.keyboard.register_callback("show_help_dialog", self._show_help_dialog)
        self.keyboard.register_callback(
            "select_single_ai_mode", lambda: self._select_game_mode("single_ai")
        )
        self.keyboard.register_callback(
            "select_three_ai_mode", lambda: self._select_game_mode("three_ai")
        )
        self.keyboard.register_callback(
            "select_spectate_mode", lambda: self._select_game_mode("spectate")
        )

    def _rotate_clockwise(self):
        """Rotate current piece clockwise."""
        if self.on_rotate_callback:
            self.on_rotate_callback()
        elif self.piece_display:
            self.piece_display.rotate_piece(clockwise=True)

    def _rotate_counterclockwise(self):
        """Rotate current piece counterclockwise."""
        if self.on_rotate_callback:
            # For now, treat both R and Shift+R as the same rotation
            # If you want different behavior, you can add a separate callback
            self.on_rotate_callback()
        elif self.piece_display:
            self.piece_display.rotate_piece(clockwise=False)

    def _flip_piece(self):
        """Flip current piece."""
        if self.on_flip_callback:
            self.on_flip_callback()
        elif self.piece_display:
            self.piece_display.flip_piece()

    def _select_piece(self, index: int):
        """
        Select piece by index.

        Args:
            index: Index of piece to select (0-9)
        """
        if self.piece_display:
            self.piece_display.select_piece_by_index(index)

    def _skip_turn(self):
        """Skip current player's turn."""
        if hasattr(self.game_state, "skip_turn"):
            self.game_state.skip_turn()

    def _place_piece(self):
        """Place current piece on board."""
        # Implementation would depend on how piece placement is handled
        # This is a placeholder
        pass

    def _cancel_action(self):
        """Cancel current action."""
        if self.piece_display:
            self.piece_display.clear_selection()

    def _new_game(self):
        """Start a new game."""
        # Implementation would trigger new game
        pass

    def _quit(self):
        """Quit the game."""
        self.root.quit()

    def _show_help(self):
        """Show help dialog."""
        self._display_help()

    def _move_cursor_left(self):
        """Move cursor left."""
        # Implementation would move selection cursor
        pass

    def _move_cursor_right(self):
        """Move cursor right."""
        # Implementation would move selection cursor
        pass

    def _move_cursor_up(self):
        """Move cursor up."""
        # Implementation would move selection cursor
        pass

    def _move_cursor_down(self):
        """Move cursor down."""
        # Implementation would move selection cursor
        pass

    def _display_help(self):
        """Display keyboard shortcuts help."""
        help_window = tk.Toplevel(self.root)
        help_window.title("Keyboard Shortcuts")
        help_window.geometry("500x400")
        help_window.transient(self.root)
        help_window.grab_set()

        # Create help text
        help_text = self._get_help_text()

        # Create text widget with scrollbar
        text_frame = tk.Frame(help_window)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        text_widget = tk.Text(text_frame, wrap=tk.WORD)
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(text_frame, command=text_widget.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        text_widget.config(yscrollcommand=scrollbar.set)
        text_widget.insert(tk.END, help_text)
        text_widget.config(state=tk.DISABLED)

        # Close button
        close_button = tk.Button(help_window, text="Close", command=help_window.destroy)
        close_button.pack(pady=10)

        # Center window
        help_window.geometry(
            "+%d+%d" % (self.root.winfo_rootx() + 50, self.root.winfo_rooty() + 50)
        )

    def _show_help_dialog(self):
        """Show help dialog for AI battle mode."""
        if self.on_show_help_callback:
            self.on_show_help_callback()
        else:
            # Fallback to displaying keyboard shortcuts help
            self._display_help()

    def _select_game_mode(self, mode: str):
        """
        Select game mode via keyboard shortcut.

        Args:
            mode: Game mode to select ("single_ai", "three_ai", or "spectate")
        """
        if self.on_mode_select_callback:
            self.on_mode_select_callback(mode)
        else:
            print(f"Game mode selection callback not set: {mode}")

    def _get_help_text(self) -> str:
        """Get help text for keyboard shortcuts."""
        return """
BLOKUS KEYBOARD SHORTCUTS

PIECE MANIPULATION
------------------
R or r       : Rotate piece clockwise
Shift+R or R : Rotate piece counterclockwise
F or f       : Flip piece

PIECE SELECTION
---------------
1-9          : Select piece by number
0            : Select piece 10

GAME ACTIONS
------------
Space        : Skip turn
Enter        : Place piece
Esc          : Cancel current action

GAME CONTROL
------------
N or n       : New game
Q or q       : Quit game
H or h or ?  : Show this help

NAVIGATION
----------
Left Arrow   : Move cursor left
Right Arrow  : Move cursor right
Up Arrow     : Move cursor up
Down Arrow   : Move cursor down

AI BATTLE MODE (002)
--------------------
F1           : Show help dialog
F2           : Select Single AI mode
F3           : Select Three AI mode
F4           : Select Spectate AI mode

TIPS
----
• Use number keys to quickly select pieces
• Press R to rotate pieces before placing
• Press F to flip pieces
• Space bar skips your turn if you can't make a move
• Press H at any time to see this help
• In AI Battle mode, use F2, F3, F4 to quickly select game modes
• Press F1 to open comprehensive help for AI Battle features

For more information, see the game documentation.
        """.strip()

    def _on_focus_in(self, event):
        """Handle window focus in event."""
        self.keyboard.set_focus(event.widget)

    def _on_focus_out(self, event):
        """Handle window focus out event."""
        # Optionally disable shortcuts when window loses focus
        pass

    def enable(self):
        """Enable keyboard shortcuts."""
        self.keyboard.enable()

    def disable(self):
        """Disable keyboard shortcuts."""
        self.keyboard.disable()

    def destroy(self):
        """Clean up keyboard handlers."""
        self.keyboard.unbind_all()


class KeyboardShortcutConfig:
    """Configuration for keyboard shortcuts."""

    PRESETS = {
        "default": {
            "r": "rotate_clockwise",
            "R": "rotate_counterclockwise",
            "f": "flip_piece",
            "1": "select_piece_1",
            "space": "skip_turn",
            "Return": "place_piece",
            "Escape": "cancel_action",
        },
        "vim": {
            "h": "move_cursor_left",
            "j": "move_cursor_down",
            "k": "move_cursor_up",
            "l": "move_cursor_right",
            "r": "rotate_clockwise",
            "R": "rotate_counterclockwise",
            "f": "flip_piece",
        },
        "minimal": {
            "r": "rotate_clockwise",
            "f": "flip_piece",
            "space": "skip_turn",
        },
    }

    @classmethod
    def get_preset(cls, name: str) -> dict[str, str]:
        """Get a keyboard shortcut preset by name."""
        if name not in cls.PRESETS:
            raise ValueError(f"Unknown preset: {name}")
        return cls.PRESETS[name].copy()

    @classmethod
    def get_preset_names(cls) -> list:
        """Get names of all available presets."""
        return list(cls.PRESETS.keys())
