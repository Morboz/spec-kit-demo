"""Pytest configuration and shared fixtures for the Blokus game test suite."""

import os
import sys

import pytest

# Add src to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


def _has_display() -> bool:
    """Check if a display is available for GUI operations."""
    return bool(os.environ.get('DISPLAY') or sys.platform == 'darwin')


def _can_use_tkinter() -> bool:
    """Check if tkinter can be initialized without errors."""
    if not _has_display():
        return False

    try:
        import tkinter
        # Try to create a test root window
        test_root = tkinter.Tk()
        test_root.withdraw()  # Hide it immediately
        test_root.destroy()
        return True
    except (ImportError, Exception):
        return False


@pytest.fixture(scope="session")
def has_gui() -> bool:
    """Return True if GUI components can be used in the current environment."""
    return _can_use_tkinter()


@pytest.fixture(scope="session")
def skip_if_no_gui(has_gui):
    """Pytest fixture to skip tests if GUI is not available."""
    if not has_gui:
        pytest.skip("GUI not available - test requires tkinter and display support")


@pytest.fixture
def tkinter_root(has_gui, monkeypatch):
    """Provide a tkinter root window for GUI tests."""
    if has_gui:
        import tkinter
        root = tkinter.Tk()
        root.withdraw()  # Hide the window by default
        yield root
        root.destroy()
    else:
        # When GUI is not available, skip the test
        pytest.skip("Cannot create tkinter root - no GUI support available")


@pytest.fixture
def gui_environment(request, has_gui):
    """Fixture to handle GUI test environment setup and cleanup."""
    if not has_gui:
        # Check if the test has been marked to skip when GUI is unavailable
        if request.node.get_closest_marker('skip_if_no_gui'):
            pytest.skip("GUI test skipped - no display available")

    # Set up environment variables if needed
    original_display = os.environ.get('DISPLAY')
    if not original_display and has_gui:
        # Try to set a default display for some systems
        if sys.platform.startswith('linux'):
            os.environ['DISPLAY'] = ':99'

    yield

    # Cleanup: restore original environment
    if original_display is None:
        os.environ.pop('DISPLAY', None)
    else:
        os.environ['DISPLAY'] = original_display


# Register marks for GUI tests
def pytest_configure(config):
    """Register custom marks for pytest."""
    config.addinivalue_line(
        "markers", "skip_if_no_gui: skip test if GUI is not available"
    )
    config.addinivalue_line(
        "markers", "gui_test: mark test as GUI-dependent"
    )


def pytest_collection_modifyitems(config, items):
    """Automatically add skip_if_no_gui mark to GUI-dependent tests."""
    gui_test_files = [
        'test_ui_updates.py',
        'test_complete_state_visibility.py',
        'test_score_updates.py',
        'test_complete_setup_flow.py',
        'test_spectate.py',
        'test_complete_game_flow.py',
        'test_complete_end_game_flow.py',
        'test_complete_score_system.py'
    ]

    for item in items:
        # Check if the test file is GUI-dependent
        if any(gui_file in str(item.fspath) for gui_file in gui_test_files):
            if not any(mark.name == 'skip_if_no_gui' for mark in item.iter_markers()):
                item.add_marker(pytest.mark.skip_if_no_gui)
            if not any(mark.name == 'gui_test' for mark in item.iter_markers()):
                item.add_marker(pytest.mark.gui_test)
