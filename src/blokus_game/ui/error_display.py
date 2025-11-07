"""
Error Display UI Component

This module provides a user-friendly error message display for the Blokus game.
It shows validation errors with clear, actionable messages to help players
understand why their moves are invalid.
"""

import tkinter as tk
from tkinter import ttk


class ErrorDisplay(ttk.Frame):
    """Displays error messages to the player."""

    def __init__(self, parent):
        """
        Initialize the error display.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.error_message_var = tk.StringVar(value="")
        self._setup_ui()

    def _setup_ui(self):
        """Set up the UI components."""
        # Error label with red text
        self.error_label = ttk.Label(
            self,
            textvariable=self.error_message_var,
            foreground="#CC0000",  # Dark red
            font=("TkDefaultFont", 10, "bold"),
            wraplength=400,
        )
        self.error_label.pack(pady=5)

        # Hide by default
        self.hide()

    def show(self, message: str):
        """
        Display an error message.

        Args:
            message: The error message to display
        """
        self.error_message_var.set(message)
        self.pack(fill=tk.X, padx=10, pady=5)
        self.error_label.update_idletasks()

    def hide(self):
        """Hide the error message."""
        self.pack_forget()

    def clear(self):
        """Clear the error message."""
        self.error_message_var.set("")
        self.hide()

    def show_validation_error(self, reason: str, rule_type: str | None = None):
        """
        Show a formatted validation error.

        Args:
            reason: The raw reason from ValidationResult
            rule_type: Optional type of rule (e.g., "corner", "bounds", "overlap")
        """
        # Format the message based on rule type
        if rule_type == "corner":
            message = f"Invalid move: {reason}"
        elif rule_type == "bounds":
            message = f"Invalid move: {reason}"
        elif rule_type == "overlap":
            message = f"Invalid move: {reason}"
        elif rule_type == "adjacency":
            message = f"Invalid move: {reason}"
        else:
            message = f"Invalid move: {reason}"

        self.show(message)

    def show_warning(self, message: str):
        """
        Show a warning message (non-error).

        Args:
            message: The warning message
        """
        self.error_message_var.set(message)
        self.error_label.config(foreground="#FF8800")  # Orange
        self.pack(fill=tk.X, padx=10, pady=5)
        self.error_label.update_idletasks()

    def show_info(self, message: str):
        """
        Show an informational message.

        Args:
            message: The info message
        """
        self.error_message_var.set(message)
        self.error_label.config(foreground="#0066CC")  # Blue
        self.pack(fill=tk.X, padx=10, pady=5)
        self.error_label.update_idletasks()

    def reset_style(self):
        """Reset label style to default error styling."""
        self.error_label.config(foreground="#CC0000")
