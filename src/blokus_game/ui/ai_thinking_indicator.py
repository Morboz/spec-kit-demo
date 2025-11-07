"""
AI Thinking Indicator UI Component

This module provides enhanced visual feedback for AI thinking state,
including animated indicators, elapsed time display, and progress tracking.
"""

import time
import tkinter as tk
from collections.abc import Callable
from tkinter import ttk


class AIThinkingIndicator(ttk.Frame):
    """
    Enhanced visual indicator for AI thinking state.

    Features:
    - Animated thinking indicator (spinning or dots)
    - Elapsed time display
    - Configurable styling
    - Callback integration for timeouts
    - Progress estimation
    """

    def __init__(
        self,
        parent: tk.Widget,
        show_elapsed_time: bool = True,
        animation_style: str = "dots",  # "dots", "spinner", or "pulse"
        on_timeout: Callable[[], None] | None = None,
        **kwargs,
    ):
        """
        Initialize the AI thinking indicator.

        Args:
            parent: Parent widget
            show_elapsed_time: Whether to show elapsed calculation time
            animation_style: Style of animation ("dots", "spinner", or "pulse")
            on_timeout: Optional callback when timeout threshold reached
            **kwargs: Additional ttk.Frame arguments
        """
        super().__init__(parent, **kwargs)

        # Configuration
        self.show_elapsed_time = show_elapsed_time
        self.animation_style = animation_style
        self.on_timeout = on_timeout

        # State
        self._is_thinking = False
        self._start_time = None
        self._animation_job = None
        self._dots_count = 0
        self._timeout_threshold = 10.0  # seconds
        self._timeout_triggered = False

        # Create widgets
        self._create_widgets()

        # Apply styling
        self._apply_styling()

    def _create_widgets(self):
        """Create and arrange UI widgets."""
        # Main container with border
        self.configure(style="AIThinking.TFrame", padding="10")

        # Status label
        self.status_var = tk.StringVar(value="")
        self.status_label = ttk.Label(
            self,
            textvariable=self.status_var,
            font=("Arial", 12, "bold"),
            foreground="orange",
        )
        self.status_label.pack(pady=(0, 5))

        # Animation frame
        self.animation_frame = ttk.Frame(self)
        self.animation_frame.pack(pady=(0, 5))

        # Elapsed time label
        if self.show_elapsed_time:
            self.time_var = tk.StringVar(value="Elapsed: 0.0s")
            self.time_label = ttk.Label(
                self, textvariable=self.time_var, font=("Arial", 9), foreground="gray"
            )
            self.time_label.pack()

        # Progress bar (optional, shown when timeout threshold reached)
        self.progress = ttk.Progressbar(
            self, mode="indeterminate", style="AIThinking.Horizontal.TProgressbar"
        )
        self.progress.pack(fill=tk.X, pady=(5, 0))

        # Initially hidden
        self.progress.pack_forget()

    def _apply_styling(self):
        """Apply custom styling for thinking indicator."""
        style = ttk.Style()

        # Configure thinking frame style
        style.configure("AIThinking.TFrame", relief="groove", borderwidth=2)

        # Configure progress bar style
        style.configure(
            "AIThinking.Horizontal.TProgressbar",
            troughcolor="lightgray",
            background="orange",
        )

    def start_thinking(
        self,
        player_name: str,
        difficulty: str | None = None,
        estimated_time: float | None = None,
    ):
        """
        Start the thinking indicator animation.

        Args:
            player_name: Name of the AI player
            difficulty: AI difficulty level (optional)
            estimated_time: Estimated calculation time in seconds (optional)
        """
        if self._is_thinking:
            self.stop_thinking()

        self._is_thinking = True
        self._start_time = time.time()
        self._timeout_triggered = False

        # Set status text
        status_text = f"🤖 {player_name} is thinking"
        if difficulty:
            status_text += f" ({difficulty})"
        self.status_var.set(status_text)

        # Store estimated time
        if estimated_time:
            self._timeout_threshold = min(estimated_time * 2, 15.0)  # Max 15s timeout

        # Show animation
        self._start_animation()

        # Show progress bar if we have an estimate
        if estimated_time and estimated_time > 3.0:
            self.progress.pack(fill=tk.X, pady=(5, 0))
            self.progress.start(10)

        # Start timer update
        self._update_timer()

    def stop_thinking(self):
        """Stop the thinking indicator animation."""
        if not self._is_thinking:
            return

        self._is_thinking = False

        # Stop animation
        if self._animation_job:
            self.after_cancel(self._animation_job)
            self._animation_job = None

        # Stop progress bar
        self.progress.stop()
        self.progress.pack_forget()

        # Clear display
        self.status_var.set("")
        if self.show_elapsed_time:
            self.time_var.set("")

    def _start_animation(self):
        """Start the appropriate animation based on style."""
        if self.animation_style == "dots":
            self._animate_dots()
        elif self.animation_style == "spinner":
            self._animate_spinner()
        elif self.animation_style == "pulse":
            self._animate_pulse()

    def _animate_dots(self):
        """Animate dots indicating thinking."""
        if not self._is_thinking:
            return

        self._dots_count = (self._dots_count + 1) % 4
        dots = "." * self._dots_count

        base_text = self.status_var.get()
        # Remove existing dots
        base_text = base_text.rstrip(".")
        # Add new dots
        current_text = f"{base_text}{dots}"

        # Check for timeout
        if self._check_timeout():
            # Add warning icon
            current_text = "⚠️ " + current_text

        self.status_var.set(current_text)

        # Schedule next animation frame
        self._animation_job = self.after(500, self._animate_dots)

    def _animate_spinner(self):
        """Animate spinner character."""
        if not self._is_thinking:
            return

        spinner_chars = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        self._dots_count = (self._dots_count + 1) % len(spinner_chars)

        base_text = self.status_var.get()
        # Remove existing spinner
        base_text = base_text.rstrip("⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏")
        current_text = f"{base_text} {spinner_chars[self._dots_count]}"

        # Check for timeout
        if self._check_timeout():
            current_text = "⚠️ " + current_text

        self.status_var.set(current_text)

        # Schedule next animation frame
        self._animation_job = self.after(100, self._animate_spinner)

    def _animate_pulse(self):
        """Animate pulsing effect."""
        if not self._is_thinking:
            return

        self._dots_count = (self._dots_count + 1) % 10
        intensity = self._dots_count / 10.0

        # Change color based on intensity
        if intensity > 0.7:
            color = "red"
        elif intensity > 0.4:
            color = "orange"
        else:
            color = "green"

        self.status_label.config(foreground=color)

        # Schedule next animation frame
        self._animation_job = self.after(150, self._animate_pulse)

    def _update_timer(self):
        """Update elapsed time display."""
        if not self._is_thinking or not self.show_elapsed_time:
            return

        elapsed = time.time() - self._start_time
        self.time_var.set(f"Elapsed: {elapsed:.1f}s")

        # Schedule next update
        self.after(100, self._update_timer)

    def _check_timeout(self) -> bool:
        """Check if timeout threshold has been reached."""
        if self._timeout_triggered or not self._start_time:
            return False

        elapsed = time.time() - self._start_time

        if elapsed >= self._timeout_threshold and not self._timeout_triggered:
            self._timeout_triggered = True

            # Trigger timeout callback if provided
            if self.on_timeout:
                try:
                    self.on_timeout()
                except Exception as e:
                    print(f"Error in timeout callback: {e}")

            return True

        return False

    def is_thinking(self) -> bool:
        """
        Check if indicator is currently in thinking state.

        Returns:
            True if thinking animation is active
        """
        return self._is_thinking

    def set_timeout_threshold(self, seconds: float):
        """
        Set timeout threshold in seconds.

        Args:
            seconds: Timeout threshold
        """
        self._timeout_threshold = max(seconds, 1.0)

    def get_elapsed_time(self) -> float | None:
        """
        Get elapsed time since thinking started.

        Returns:
            Elapsed time in seconds, or None if not thinking
        """
        if not self._is_thinking or not self._start_time:
            return None
        return time.time() - self._start_time


class ThinkingIndicatorDialog(tk.Toplevel):
    """
    Modal dialog for displaying AI thinking indicator.

    This can be used when you want to block user interaction
    while AI is thinking.
    """

    def __init__(
        self,
        parent: tk.Widget,
        title: str = "AI Thinking",
        player_name: str = "AI Player",
        difficulty: str | None = None,
        estimated_time: float | None = None,
        **kwargs,
    ):
        """
        Initialize thinking indicator dialog.

        Args:
            parent: Parent widget
            title: Dialog title
            player_name: Name of AI player
            difficulty: AI difficulty level
            estimated_time: Estimated calculation time
            **kwargs: Additional arguments
        """
        super().__init__(parent, **kwargs)

        self.title(title)
        self.geometry("400x150")
        self.resizable(False, False)

        # Make modal
        self.transient(parent)
        self.grab_set()

        # Center on parent
        self.update_idletasks()
        x = (
            parent.winfo_rootx()
            + (parent.winfo_width() // 2)
            - (self.winfo_width() // 2)
        )
        y = (
            parent.winfo_rooty()
            + (parent.winfo_height() // 2)
            - (self.winfo_height() // 2)
        )
        self.geometry(f"+{x}+{y}")

        # Create indicator
        self.indicator = AIThinkingIndicator(
            self, show_elapsed_time=True, animation_style="dots"
        )
        self.indicator.pack(fill=tk.BOTH, expand=True)

        # Start thinking
        self.indicator.start_thinking(player_name, difficulty, estimated_time)

        # Auto-close when thinking stops
        self._check_closed()

    def _check_closed(self):
        """Check if thinking has stopped and close dialog."""
        if not self.indicator.is_thinking():
            self.destroy()
        else:
            self.after(100, self._check_closed)

    def stop_thinking(self):
        """Stop thinking and close dialog."""
        self.indicator.stop_thinking()
        self.destroy()


# Convenience functions
def show_thinking_indicator(
    parent: tk.Widget,
    player_name: str,
    difficulty: str | None = None,
    estimated_time: float | None = None,
) -> AIThinkingIndicator:
    """
    Create and show a thinking indicator.

    Args:
        parent: Parent widget
        player_name: Name of AI player
        difficulty: AI difficulty level
        estimated_time: Estimated calculation time

    Returns:
        AIThinkingIndicator instance
    """
    indicator = AIThinkingIndicator(
        parent, show_elapsed_time=True, animation_style="dots"
    )
    indicator.start_thinking(player_name, difficulty, estimated_time)
    return indicator


def show_thinking_dialog(
    parent: tk.Widget,
    title: str = "AI Thinking",
    player_name: str = "AI Player",
    difficulty: str | None = None,
    estimated_time: float | None = None,
) -> ThinkingIndicatorDialog:
    """
    Show a modal thinking dialog.

    Args:
        parent: Parent widget
        title: Dialog title
        player_name: Name of AI player
        difficulty: AI difficulty level
        estimated_time: Estimated calculation time

    Returns:
        ThinkingIndicatorDialog instance
    """
    dialog = ThinkingIndicatorDialog(
        parent,
        title=title,
        player_name=player_name,
        difficulty=difficulty,
        estimated_time=estimated_time,
    )
    return dialog


# Example usage
if __name__ == "__main__":
    root = tk.Tk()
    root.title("AI Thinking Indicator Test")
    root.geometry("600x400")

    # Create a test frame
    test_frame = ttk.Frame(root, padding="20")
    test_frame.pack(fill=tk.BOTH, expand=True)

    # Create indicator
    indicator = AIThinkingIndicator(
        test_frame, show_elapsed_time=True, animation_style="dots"
    )
    indicator.pack(fill=tk.X, pady=10)

    # Start button
    start_btn = ttk.Button(
        test_frame,
        text="Start AI Thinking (5s)",
        command=lambda: indicator.start_thinking("Player 1", "Medium", 5.0),
    )
    start_btn.pack(side=tk.LEFT, padx=(0, 10))

    # Stop button
    stop_btn = ttk.Button(test_frame, text="Stop", command=indicator.stop_thinking)
    stop_btn.pack(side=tk.LEFT)

    # Test dialog button
    dialog_btn = ttk.Button(
        test_frame,
        text="Show Dialog",
        command=lambda: show_thinking_dialog(
            root, "Calculating Move", "AI Player", "Hard", 3.0
        ),
    )
    dialog_btn.pack(side=tk.RIGHT)

    root.mainloop()
