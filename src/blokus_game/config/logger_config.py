"""
Centralized Logger Configuration for Blokus Game

This module provides a unified logging system with consistent formatting,
levels, and configuration across the entire application.
"""

import logging
import sys
from typing import TextIO


# Standard log format
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Default log levels
DEFAULT_LEVEL = logging.DEBUG
CONSOLE_LEVEL = logging.DEBUG
FILE_LEVEL = logging.DEBUG

# Global logger cache to avoid duplicate handlers
_loggers = {}

# Create console handler formatter
_formatter = logging.Formatter(LOG_FORMAT)


class UnbufferedStreamHandler(logging.StreamHandler):
    """
    A StreamHandler that automatically flushes after each emit.

    This ensures log messages are written to stdout immediately without buffering,
    providing real-time log output for better debugging experience.
    """

    def __init__(self, stream: TextIO | None = None):
        """Initialize with immediate flush capability."""
        super().__init__(stream)

    def emit(self, record):
        """Emit a log record and immediately flush the stream."""
        super().emit(record)
        self.flush()


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with unified configuration.

    This function provides a centralized logger that:
    - Uses a consistent format across all modules
    - Prevents duplicate handlers
    - Supports hierarchical logging (e.g., 'blokus_game.game', 'blokus_game.ui')
    - Configures appropriate log levels

    Args:
        name: Logger name, typically __name__ from the calling module

    Returns:
        A configured logger instance

    Example:
        >>> from blokus_game.config.logger_config import get_logger
        >>> logger = get_logger(__name__)
        >>> logger.info("This is an info message")
        >>> logger.error("This is an error message")
    """
    if name in _loggers:
        return _loggers[name]

    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(DEFAULT_LEVEL)

    # Add console handler if not already present
    if not logger.handlers:
        # Use unbuffered stream handler for immediate output
        console_handler = UnbufferedStreamHandler(sys.stdout)
        console_handler.setLevel(CONSOLE_LEVEL)
        console_handler.setFormatter(_formatter)
        logger.addHandler(console_handler)

    # Prevent propagation to root logger to avoid duplicate output
    logger.propagate = False

    # Cache the logger
    _loggers[name] = logger

    return logger
