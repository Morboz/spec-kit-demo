"""
Tests for Game Mode Selector UI functionality.
"""

import tkinter as tk
import unittest
from unittest.mock import Mock, patch

from blokus_game.models.ai_config import Difficulty
from blokus_game.ui.game_mode_selector import GameModeSelector


class TestGameModeSelector(unittest.TestCase):
    """Test cases for GameModeSelector UI."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a real Tkinter root window for testing
        try:
            self.root = tk.Tk()
            self.root.withdraw()  # Hide the window
        except Exception:
            # On systems without display (CI/CD), skip Tk initialization
            import pytest

            pytest.skip("Tkinter not available in this environment")

        # Use real Tk window as parent
        self.parent = self.root

        # Mock callback
        self.callback = Mock()

    def tearDown(self):
        """Clean up test fixtures."""
        # Destroy the root window after each test
        try:
            self.root.destroy()
        except Exception:
            pass

    def test_initialization(self):
        """Test that selector initializes correctly."""
        selector = GameModeSelector(self.parent, self.callback)

        # Check initial values
        self.assertEqual(selector.selected_mode_var.get(), "single_ai")
        self.assertIsNotNone(selector.selected_difficulty_var.get())
        self.assertEqual(selector.parent, self.parent)
        self.assertEqual(selector.callback, self.callback)
        self.assertIsNone(selector.result)

    @patch("blokus_game.models.game_mode.GameMode.get_difficulty_preference")
    def test_loads_saved_difficulty(self, mock_get_pref):
        """Test that saved difficulty preference is loaded."""
        # Setup mock to return Hard difficulty
        mock_get_pref.return_value = Difficulty.HARD

        selector = GameModeSelector(self.parent, self.callback)

        # Should load saved difficulty
        self.assertEqual(selector.selected_difficulty_var.get(), "Hard")

    def test_fallback_to_default_on_error(self):
        """Test fallback to default difficulty if loading fails."""
        with patch(
            "blokus_game.models.game_mode.GameMode.get_difficulty_preference"
        ) as mock_get_pref:
            # Simulate exception during loading
            mock_get_pref.side_effect = Exception("File not found")

            selector = GameModeSelector(self.parent, self.callback)

            # Should fallback to default
            self.assertEqual(selector.selected_difficulty_var.get(), "Medium")

    def test_save_difficulty_preference_on_start(self):
        """Test that difficulty preference is saved when starting game."""
        selector = GameModeSelector(self.parent, self.callback)

        # Set the mode variables
        selector.selected_mode_var.set("single_ai")
        selector.selected_difficulty_var.set("Hard")

        # Simulate dialog and widgets
        selector.dialog = Mock()
        selector.dialog.destroy = Mock()

        # Patch the imports that happen inside _on_start_clicked method
        with patch("blokus_game.models.game_mode.GameMode") as mock_game_mode_class:
            mock_save = Mock()
            mock_game_mode_instance = Mock()
            mock_game_mode_instance.save_difficulty_preference = mock_save
            mock_game_mode_class.return_value = mock_game_mode_instance

            # Call _on_start_clicked
            selector._on_start_clicked()

            # Verify save was called twice (once for SINGLE_AI, once for THREE_AI)
            self.assertEqual(mock_save.call_count, 2)

    @patch("blokus_game.ui.game_mode_selector.GameMode")
    def test_no_save_for_spectate_mode(self, mock_game_mode_class):
        """Test that difficulty is not saved for spectate mode."""
        mock_save = Mock()
        mock_game_mode_instance = Mock()
        mock_game_mode_instance.save_difficulty_preference = mock_save
        mock_game_mode_class.return_value = mock_game_mode_instance

        selector = GameModeSelector(self.parent, self.callback)

        # Set variables for spectate mode
        selector.selected_mode_var.set("spectate")
        selector.selected_difficulty_var.set("Hard")

        selector.dialog = Mock()
        selector.dialog.destroy = Mock()

        # Call _on_start_clicked
        selector._on_start_clicked()

        # Verify save was NOT called for spectate mode
        self.assertFalse(mock_save.called)

    def test_on_start_clicks_creates_correct_config(self):
        """Test that correct configuration is created for each mode."""
        test_cases = [
            (
                "single_ai",
                "Hard",
                {
                    "mode_type": "single_ai",
                    "difficulty": "Hard",
                    "description": "Human vs Hard AI",
                },
            ),
            (
                "three_ai",
                "Easy",
                {
                    "mode_type": "three_ai",
                    "difficulty": "Easy",
                    "description": "Human vs Easy AI",
                },
            ),
            (
                "spectate",
                None,
                {
                    "mode_type": "spectate",
                    "difficulty": None,
                    "description": "Spectate AI vs AI match",
                },
            ),
        ]

        for mode, difficulty, expected_config in test_cases:
            with self.subTest(mode=mode):
                selector = GameModeSelector(self.parent, self.callback)

                # Set variables
                selector.selected_mode_var.set(mode)
                if difficulty:
                    selector.selected_difficulty_var.set(difficulty)

                selector.dialog = Mock()
                selector.dialog.destroy = Mock()

                selector._on_start_clicked()

                # Verify result
                self.assertEqual(selector.result, expected_config)
                selector.dialog.destroy.assert_called_once()

    def test_on_mode_selected_disables_difficulty_for_spectate(self):
        """Test that difficulty selection is disabled in spectate mode."""
        selector = GameModeSelector(self.parent, self.callback)

        # Create the dialog to initialize widgets
        selector._create_dialog()

        # Set to spectate mode
        selector.selected_mode_var.set("spectate")
        selector._on_mode_selected()

        # Verify difficulty frame widgets are disabled
        # Check a sample widget (radiobutton)
        for widget in selector.difficulty_frame.winfo_children():
            if isinstance(widget, tk.Radiobutton):
                self.assertEqual(str(widget.cget("state")), "disabled")

        self.assertIn("mixed difficulty", selector.hint_label.cget("text"))

        # Clean up
        selector.dialog.destroy()

    def test_on_mode_selected_enables_difficulty_for_play_modes(self):
        """Test that difficulty selection is enabled in play modes."""
        selector = GameModeSelector(self.parent, self.callback)

        # Create the dialog to initialize widgets
        selector._create_dialog()

        # Set to single_ai mode
        selector.selected_mode_var.set("single_ai")
        selector._on_mode_selected()

        # Verify difficulty frame widgets are enabled
        for widget in selector.difficulty_frame.winfo_children():
            if isinstance(widget, tk.Radiobutton):
                self.assertEqual(str(widget.cget("state")), "normal")

        self.assertIn("Choose AI difficulty", selector.hint_label.cget("text"))

        # Clean up
        selector.dialog.destroy()

    def test_on_cancel_clicked(self):
        """Test that cancel button works correctly."""
        selector = GameModeSelector(self.parent, self.callback)
        selector.dialog = Mock()

        selector._on_cancel_clicked()

        # Verify result is None and dialog is destroyed
        self.assertIsNone(selector.result)
        selector.dialog.destroy.assert_called_once()

    @patch("blokus_game.ui.game_mode_selector.messagebox")
    def test_callback_invoked_on_start(self, mock_messagebox):
        """Test that callback is invoked when starting game."""
        selector = GameModeSelector(self.parent, self.callback)

        # Mock variables
        selector.selected_mode_var.set("single_ai")
        selector.selected_difficulty_var.set("Hard")

        selector.dialog = Mock()
        selector.dialog.destroy = Mock()

        # Call _on_start_clicked
        selector._on_start_clicked()

        # Verify callback was called
        self.callback.assert_called_once_with("single_ai", "Hard")

    def test_callback_error_handling(self):
        """Test that exceptions in callback are handled gracefully."""
        # Mock callback to raise exception
        bad_callback = Mock(side_effect=Exception("Callback failed"))
        selector = GameModeSelector(self.parent, bad_callback)

        # Mock variables
        selector.selected_mode_var = tk.StringVar(value="single_ai")
        selector.selected_difficulty_var = tk.StringVar(value="Hard")

        selector.dialog = Mock()
        selector.dialog.destroy = Mock()

        # Patch messagebox to avoid popup
        with patch("blokus_game.ui.game_mode_selector.messagebox") as mock_messagebox:
            # Call _on_start_clicked - should not raise exception
            selector._on_start_clicked()

            # Verify error message was shown
            mock_messagebox.showerror.assert_called_once()

    def test_create_game_mode_factory_method(self):
        """Test the static factory method for creating game modes."""
        # Test single_ai
        with patch("blokus_game.ui.game_mode_selector.GameMode") as mock_game_mode:
            mock_instance = Mock()
            mock_game_mode.single_ai.return_value = mock_instance

            GameModeSelector.create_game_mode("single_ai", "Hard")

            # Verify GameMode.single_ai was called with correct difficulty
            mock_game_mode.single_ai.assert_called_once()
            args = mock_game_mode.single_ai.call_args[0]
            self.assertEqual(args[0], Difficulty.HARD)

    def test_show_function(self):
        """Test the convenience show_game_mode_selector function."""
        from blokus_game.ui.game_mode_selector import show_game_mode_selector

        with patch(
            "blokus_game.ui.game_mode_selector.GameModeSelector"
        ) as mock_selector_class:
            mock_instance = Mock()
            mock_selector_class.return_value = mock_instance
            mock_instance.show.return_value = {"mode_type": "single_ai"}

            result = show_game_mode_selector(self.parent, self.callback)

            # Verify selector was created and shown
            mock_selector_class.assert_called_once_with(self.parent, self.callback)
            mock_instance.show.assert_called_once()
            self.assertEqual(result, {"mode_type": "single_ai"})


if __name__ == "__main__":
    unittest.main()
