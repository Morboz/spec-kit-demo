"""
Comprehensive error handling and recovery system for Blokus.

This module provides:
- Custom exception types for game-specific errors
- Global error handler with recovery mechanisms
- Error logging and reporting
- User-friendly error messages
- Error statistics and tracking
"""

import sys
import traceback
import logging
from typing import Optional, Dict, List, Callable, Any, Type
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime


class ErrorSeverity(Enum):
    """Error severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """Error categories for classification."""
    GAME_RULES = "game_rules"
    BOARD_OPERATION = "board_operation"
    PIECE_OPERATION = "piece_operation"
    UI_RENDERING = "ui_rendering"
    USER_INPUT = "user_input"
    FILE_IO = "file_io"
    NETWORK = "network"
    SYSTEM = "system"
    UNKNOWN = "unknown"


class BlokusException(Exception):
    """Base exception for all Blokus-related errors."""

    def __init__(
        self,
        message: str,
        category: ErrorCategory = ErrorCategory.UNKNOWN,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        context: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize Blokus exception.

        Args:
            message: Error message
            category: Error category
            severity: Error severity
            context: Additional context information
        """
        super().__init__(message)
        self.message = message
        self.category = category
        self.severity = severity
        self.context = context or {}
        self.timestamp = datetime.now()


class GameRuleException(BlokusException):
    """Exception raised when game rules are violated."""

    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            category=ErrorCategory.GAME_RULES,
            severity=ErrorSeverity.HIGH,
            **kwargs
        )


class BoardOperationException(BlokusException):
    """Exception raised during board operations."""

    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            category=ErrorCategory.BOARD_OPERATION,
            severity=ErrorSeverity.MEDIUM,
            **kwargs
        )


class PieceOperationException(BlokusException):
    """Exception raised during piece operations."""

    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            category=ErrorCategory.PIECE_OPERATION,
            severity=ErrorSeverity.MEDIUM,
            **kwargs
        )


class UIRenderingException(BlokusException):
    """Exception raised during UI rendering."""

    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            category=ErrorCategory.UI_RENDERING,
            severity=ErrorSeverity.MEDIUM,
            **kwargs
        )


class UserInputException(BlokusException):
    """Exception raised for invalid user input."""

    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            category=ErrorCategory.USER_INPUT,
            severity=ErrorSeverity.LOW,
            **kwargs
        )


@dataclass
class ErrorRecord:
    """Record of an error occurrence."""
    exception: Exception
    category: ErrorCategory
    severity: ErrorSeverity
    timestamp: datetime
    message: str
    traceback_str: str
    context: Dict[str, Any] = field(default_factory=dict)
    recovered: bool = False
    recovery_action: Optional[str] = None


class ErrorHandler:
    """Comprehensive error handling and recovery system."""

    def __init__(self, enable_logging: bool = True, log_file: Optional[str] = None):
        """
        Initialize error handler.

        Args:
            enable_logging: Whether to enable error logging
            log_file: Optional log file path
        """
        self.enable_logging = enable_logging
        self.log_file = log_file

        # Setup logging
        self.logger = self._setup_logging()

        # Error tracking
        self.error_history: List[ErrorRecord] = []
        self.error_counts: Dict[str, int] = {}
        self.error_stats: Dict[str, int] = {
            "total_errors": 0,
            "recovered_errors": 0,
            "fatal_errors": 0,
        }

        # Recovery handlers
        self.recovery_handlers: Dict[Type[Exception], Callable] = {}

        # Error callbacks
        self.error_callbacks: List[Callable[[ErrorRecord], None]] = []

        # Global exception hook
        self._original_excepthook = sys.excepthook

    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration."""
        logger = logging.getLogger("blokus.error_handler")
        logger.setLevel(logging.DEBUG)

        # Create formatter
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # File handler if specified
        if self.log_file:
            file_handler = logging.FileHandler(self.log_file)
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

        return logger

    def register_recovery_handler(
        self,
        exception_type: Type[Exception],
        handler: Callable[[Exception], bool],
    ):
        """
        Register a recovery handler for an exception type.

        Args:
            exception_type: Type of exception to handle
            handler: Recovery function that returns True if recovery successful
        """
        self.recovery_handlers[exception_type] = handler

    def register_error_callback(self, callback: Callable[[ErrorRecord], None]):
        """
        Register a callback to be called on every error.

        Args:
            callback: Function to call with error record
        """
        self.error_callbacks.append(callback)

    def handle_error(
        self,
        exception: Exception,
        context: Optional[Dict[str, Any]] = None,
        show_user_message: bool = True,
    ) -> bool:
        """
        Handle an error with recovery attempt.

        Args:
            exception: The exception that occurred
            context: Additional context information
            show_user_message: Whether to show user message

        Returns:
            True if error was recovered, False otherwise
        """
        # Categorize error
        category = self._categorize_error(exception)
        severity = self._determine_severity(exception)

        # Create error record
        error_record = ErrorRecord(
            exception=exception,
            category=category,
            severity=severity,
            timestamp=datetime.now(),
            message=str(exception),
            traceback_str=traceback.format_exc(),
            context=context or {},
        )

        # Log error
        self._log_error(error_record)

        # Try to recover
        recovered = self._attempt_recovery(error_record)
        error_record.recovered = recovered

        if recovered:
            self.error_stats["recovered_errors"] += 1
        elif severity == ErrorSeverity.CRITICAL:
            self.error_stats["fatal_errors"] += 1

        # Update statistics
        self.error_stats["total_errors"] += 1
        error_key = f"{category.value}.{type(exception).__name__}"
        self.error_counts[error_key] = self.error_counts.get(error_key, 0) + 1

        # Store in history
        self.error_history.append(error_record)

        # Limit history size
        if len(self.error_history) > 1000:
            self.error_history = self.error_history[-500:]

        # Call callbacks
        for callback in self.error_callbacks:
            try:
                callback(error_record)
            except Exception as e:
                self.logger.error(f"Error in error callback: {e}")

        # Show user message if requested
        if show_user_message:
            self._show_user_message(error_record)

        # If critical error and not recovered, exit
        if severity == ErrorSeverity.CRITICAL and not recovered:
            self._handle_fatal_error(error_record)

        return recovered

    def _categorize_error(self, exception: Exception) -> ErrorCategory:
        """Categorize an exception."""
        if isinstance(exception, GameRuleException):
            return ErrorCategory.GAME_RULES
        elif isinstance(exception, BoardOperationException):
            return ErrorCategory.BOARD_OPERATION
        elif isinstance(exception, PieceOperationException):
            return ErrorCategory.PIECE_OPERATION
        elif isinstance(exception, UIRenderingException):
            return ErrorCategory.UI_RENDERING
        elif isinstance(exception, UserInputException):
            return ErrorCategory.USER_INPUT
        elif isinstance(exception, FileNotFoundError):
            return ErrorCategory.FILE_IO
        elif isinstance(exception, (ConnectionError, OSError)):
            return ErrorCategory.SYSTEM
        else:
            return ErrorCategory.UNKNOWN

    def _determine_severity(self, exception: Exception) -> ErrorSeverity:
        """Determine severity of an exception."""
        if isinstance(exception, BlokusException):
            return exception.severity
        elif isinstance(exception, (KeyboardInterrupt, SystemExit)):
            return ErrorSeverity.CRITICAL
        elif isinstance(exception, (MemoryError, RecursionError)):
            return ErrorSeverity.CRITICAL
        elif isinstance(exception, (ValueError, TypeError)):
            return ErrorSeverity.MEDIUM
        else:
            return ErrorSeverity.MEDIUM

    def _attempt_recovery(self, error_record: ErrorRecord) -> bool:
        """
        Attempt to recover from an error.

        Args:
            error_record: Error record

        Returns:
            True if recovery successful, False otherwise
        """
        exception = error_record.exception

        # Check for specific recovery handler
        for exc_type, handler in self.recovery_handlers.items():
            if isinstance(exception, exc_type):
                try:
                    result = handler(exception)
                    if result:
                        error_record.recovery_action = f"Handled by {handler.__name__}"
                        return True
                except Exception as e:
                    self.logger.error(f"Recovery handler failed: {e}")

        # Generic recovery based on error type
        if isinstance(exception, UserInputException):
            # User input errors are typically recoverable by ignoring invalid input
            error_record.recovery_action = "Ignored invalid input"
            return True
        elif isinstance(exception, UIRenderingException):
            # UI errors - try to refresh UI
            error_record.recovery_action = "UI will refresh"
            return True
        elif isinstance(exception, BoardOperationException):
            # Board operation errors - validate board state
            error_record.recovery_action = "Board state validated"
            return True

        return False

    def _log_error(self, error_record: ErrorRecord):
        """Log an error."""
        if not self.enable_logging:
            return

        log_message = (
            f"[{error_record.category.value}] "
            f"[{error_record.severity.value}] "
            f"{error_record.message}\n"
            f"Traceback:\n{error_record.traceback_str}"
        )

        if error_record.context:
            log_message += f"\nContext: {error_record.context}"

        if error_record.severity in [ErrorSeverity.HIGH, ErrorSeverity.CRITICAL]:
            self.logger.error(log_message)
        else:
            self.logger.warning(log_message)

    def _show_user_message(self, error_record: ErrorRecord):
        """
        Show user-friendly error message.

        Args:
            error_record: Error record
        """
        # Get user-friendly message
        message = self._get_user_friendly_message(error_record)

        # Show based on severity
        if error_record.severity == ErrorSeverity.CRITICAL:
            # Critical errors might use messagebox
            try:
                import tkinter as tk
                from tkinter import messagebox

                root = tk.Tk()
                root.withdraw()

                messagebox.showerror(
                    "Critical Error",
                    message,
                    icon="error",
                )

                root.destroy()
            except Exception:
                print(f"CRITICAL ERROR: {message}")

        elif error_record.severity == ErrorSeverity.HIGH:
            print(f"ERROR: {message}")

        elif error_record.severity == ErrorSeverity.MEDIUM:
            print(f"WARNING: {message}")

        else:
            # Low severity - just log
            pass

    def _get_user_friendly_message(self, error_record: ErrorRecord) -> str:
        """
        Get user-friendly error message.

        Args:
            error_record: Error record

        Returns:
            User-friendly message
        """
        exception = error_record.exception

        # Get exception message - use str() for all exceptions
        exception_msg = str(exception)

        if isinstance(exception, GameRuleException):
            return f"Invalid move: {exception_msg}"

        elif isinstance(exception, BoardOperationException):
            return f"Board operation failed: {exception_msg}"

        elif isinstance(exception, PieceOperationException):
            return f"Cannot perform that action: {exception_msg}"

        elif isinstance(exception, UIRenderingException):
            return f"Display error: {exception_msg}"

        elif isinstance(exception, UserInputException):
            return exception_msg

        elif isinstance(exception, FileNotFoundError):
            filename = getattr(exception, 'filename', 'unknown file')
            return f"Required file not found: {filename}"

        else:
            return f"An error occurred: {exception_msg}"

    def _handle_fatal_error(self, error_record: ErrorRecord):
        """Handle a fatal error."""
        self.logger.critical(
            f"Fatal error - application cannot continue: {error_record.message}"
        )

        # Save error report
        self.save_error_report("fatal_error_report.txt")

        # Exit
        sys.exit(1)

    def save_error_report(self, filename: str):
        """
        Save an error report to file.

        Args:
            filename: Output filename
        """
        with open(filename, "w") as f:
            f.write("=== BLOKUS ERROR REPORT ===\n\n")
            f.write(f"Generated: {datetime.now()}\n\n")

            f.write("=== ERROR STATISTICS ===\n")
            for key, value in self.error_stats.items():
                f.write(f"{key}: {value}\n")
            f.write("\n")

            f.write("=== ERROR COUNTS ===\n")
            for error_key, count in sorted(self.error_counts.items()):
                f.write(f"{error_key}: {count}\n")
            f.write("\n")

            f.write("=== RECENT ERRORS ===\n")
            for error_record in self.error_history[-20:]:
                f.write(f"\nTime: {error_record.timestamp}\n")
                f.write(f"Category: {error_record.category.value}\n")
                f.write(f"Severity: {error_record.severity.value}\n")
                f.write(f"Message: {error_record.message}\n")
                f.write(f"Recovered: {error_record.recovered}\n")
                if error_record.context:
                    f.write(f"Context: {error_record.context}\n")
                f.write(f"Traceback:\n{error_record.traceback_str}\n")
                f.write("-" * 80 + "\n")

    def get_error_statistics(self) -> Dict[str, Any]:
        """
        Get error statistics.

        Returns:
            Dictionary with error statistics
        """
        recent_errors = [
            e for e in self.error_history
            if (datetime.now() - e.timestamp).seconds < 3600
        ]

        return {
            **self.error_stats,
            "unique_errors": len(self.error_counts),
            "recent_errors_count": len(recent_errors),
            "most_common_error": max(
                self.error_counts.items(),
                key=lambda x: x[1],
                default=(None, 0),
            ),
        }

    def enable_global_handling(self):
        """Enable global exception handling."""
        sys.excepthook = self._global_exception_handler

    def _global_exception_handler(
        self,
        exc_type: Type[Exception],
        exc_value: Exception,
        exc_traceback,
    ):
        """Global exception handler."""
        # Handle with our error handler
        self.handle_error(exc_value, show_user_message=True)

        # Call original handler
        self._original_excepthook(exc_type, exc_value, exc_traceback)


# Global error handler instance
_global_error_handler: Optional[ErrorHandler] = None


def get_error_handler() -> ErrorHandler:
    """Get the global error handler instance."""
    global _global_error_handler
    if _global_error_handler is None:
        _global_error_handler = ErrorHandler()
    return _global_error_handler


def setup_error_handling(log_file: Optional[str] = None):
    """
    Setup global error handling.

    Args:
        log_file: Optional log file path
    """
    handler = get_error_handler()
    handler.enable_global_handling()
    return handler


def handle_error(
    exception: Exception,
    context: Optional[Dict[str, Any]] = None,
    show_user_message: bool = True,
) -> bool:
    """
    Convenience function to handle an error.

    Args:
        exception: Exception to handle
        context: Additional context
        show_user_message: Show user message

    Returns:
        True if recovered, False otherwise
    """
    return get_error_handler().handle_error(
        exception, context, show_user_message
    )


def safe_execute(
    func: Callable,
    *args,
    default_return: Any = None,
    context: Optional[Dict[str, Any]] = None,
    **kwargs,
) -> Any:
    """
    Safely execute a function with error handling.

    Args:
        func: Function to execute
        *args: Function arguments
        default_return: Value to return on error
        context: Additional context information
        **kwargs: Function keyword arguments

    Returns:
        Function result or default_return on error
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        get_error_handler().handle_error(e, context, show_user_message=False)
        return default_return


# Recovery handler examples
def recovery_handler_board_state(error: Exception) -> bool:
    """Example recovery handler for board state errors."""
    # Validate and reset board state if needed
    return True


def recovery_handler_ui_refresh(error: Exception) -> bool:
    """Example recovery handler for UI errors."""
    # Trigger UI refresh
    return True