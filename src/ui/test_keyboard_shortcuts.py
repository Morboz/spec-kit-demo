"""
Test script for keyboard shortcuts functionality.
This script demonstrates the new game mode selection keyboard shortcuts.
"""

import tkinter as tk
from tkinter import ttk
from src.ui.keyboard_shortcuts import GameKeyboardHandler
from src.ui.help_tooltips import show_help_dialog, add_tooltip, TOOLTIP_TEXT


def test_keyboard_shortcuts():
    """Test keyboard shortcuts for AI battle mode."""
    root = tk.Tk()
    root.title("Keyboard Shortcuts Test - AI Battle Mode")
    root.geometry("700x500")

    # State tracking
    selected_mode = tk.StringVar(value="No mode selected")
    mode_history = []

    def on_mode_select(mode: str):
        """Handle game mode selection."""
        mode_names = {
            "single_ai": "Single AI Mode",
            "three_ai": "Three AI Mode",
            "spectate": "Spectate AI Mode"
        }
        mode_name = mode_names.get(mode, mode)
        selected_mode.set(f"Selected: {mode_name}")
        mode_history.append(mode_name)

        # Update history display
        history_text.delete(1.0, tk.END)
        for i, m in enumerate(mode_history[-10:], 1):  # Show last 10
            history_text.insert(tk.END, f"{i}. {m}\n")

    def on_show_help():
        """Handle help dialog request."""
        show_help_dialog(root, "AI Battle Mode Help")

    # Create keyboard handler with callbacks
    keyboard_handler = GameKeyboardHandler(
        root=root,
        game_state=None,
        board=None,
        piece_display=None,
        on_mode_select=on_mode_select,
        on_show_help=on_show_help
    )

    # Create UI
    main_frame = ttk.Frame(root, padding="20")
    main_frame.pack(fill=tk.BOTH, expand=True)

    # Title
    title_label = ttk.Label(
        main_frame,
        text="AI Battle Mode - Keyboard Shortcuts Test",
        font=("Arial", 16, "bold")
    )
    title_label.pack(pady=(0, 20))

    # Instructions
    instructions = ttk.Label(
        main_frame,
        text="Test the keyboard shortcuts:",
        font=("Arial", 12)
    )
    instructions.pack(pady=(0, 10))

    # Buttons for testing
    buttons_frame = ttk.Frame(main_frame)
    buttons_frame.pack(pady=10)

    # Test buttons
    single_btn = ttk.Button(
        buttons_frame,
        text="Single AI Mode (F2)",
        command=lambda: on_mode_select("single_ai")
    )
    single_btn.pack(side=tk.LEFT, padx=5)
    add_tooltip(single_btn, TOOLTIP_TEXT["single_ai"])

    three_ai_btn = ttk.Button(
        buttons_frame,
        text="Three AI Mode (F3)",
        command=lambda: on_mode_select("three_ai")
    )
    three_ai_btn.pack(side=tk.LEFT, padx=5)
    add_tooltip(three_ai_btn, TOOLTIP_TEXT["three_ai"])

    spectate_btn = ttk.Button(
        buttons_frame,
        text="Spectate AI Mode (F4)",
        command=lambda: on_mode_select("spectate")
    )
    spectate_btn.pack(side=tk.LEFT, padx=5)
    add_tooltip(spectate_btn, TOOLTIP_TEXT["spectate"])

    help_btn = ttk.Button(
        buttons_frame,
        text="Help (F1)",
        command=on_show_help
    )
    help_btn.pack(side=tk.LEFT, padx=5)
    add_tooltip(help_btn, TOOLTIP_TEXT["help"])

    # Selection display
    selection_frame = ttk.LabelFrame(main_frame, text="Current Selection", padding="10")
    selection_frame.pack(fill=tk.X, pady=20)

    selection_label = ttk.Label(
        selection_frame,
        textvariable=selected_mode,
        font=("Arial", 14, "bold"),
        foreground="blue"
    )
    selection_label.pack()

    # Mode history
    history_frame = ttk.LabelFrame(main_frame, text="Mode Selection History (last 10)", padding="10")
    history_frame.pack(fill=tk.BOTH, expand=True, pady=10)

    history_text = tk.Text(history_frame, height=8, font=("Courier", 10))
    history_text.pack(fill=tk.BOTH, expand=True)

    # Shortcuts reference
    shortcuts_frame = ttk.LabelFrame(main_frame, text="Keyboard Shortcuts Reference", padding="10")
    shortcuts_frame.pack(fill=tk.X, pady=10)

    shortcuts_text = ttk.Label(
        shortcuts_frame,
        text=(
            "F1: Help Dialog    F2: Single AI Mode    F3: Three AI Mode    F4: Spectate AI Mode\n"
            "R: Rotate Piece    H: Show Shortcuts Help    Esc: Cancel Action"
        ),
        font=("Arial", 10),
        foreground="gray"
    )
    shortcuts_text.pack()

    # Info label
    info_label = ttk.Label(
        main_frame,
        text="Click buttons or use keyboard shortcuts!",
        font=("Arial", 10, "italic"),
        foreground="green"
    )
    info_label.pack(pady=(20, 0))

    # Test button to show shortcuts help
    ttk.Button(
        main_frame,
        text="Show Keyboard Shortcuts Help (H)",
        command=lambda: keyboard_handler._display_help()
    ).pack(pady=10)

    print("\n=== Keyboard Shortcuts Test Started ===")
    print("Available shortcuts:")
    print("  F1 - Help Dialog")
    print("  F2 - Single AI Mode")
    print("  F3 - Three AI Mode")
    print("  F4 - Spectate AI Mode")
    print("  H  - Show this help")
    print("  Esc - Cancel")
    print("\nClick buttons or press keyboard shortcuts!")
    print("=" * 45)

    root.mainloop()


if __name__ == "__main__":
    test_keyboard_shortcuts()
