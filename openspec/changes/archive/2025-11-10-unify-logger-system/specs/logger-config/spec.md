# Logger Configuration Specification

## Overview
Define a centralized logger configuration system for the Blokus game project with standardized formatting, levels, and usage patterns.

## ADDED Requirements

### Requirement: Central Logger Configuration Module
The project MUST have a centralized logger configuration module that provides consistent logging across the application.

**Location:** `src/blokus_game/config/logger_config.py`

**Details:**
- Create a new module `blokus_game.config.logger_config`
- Provide a `get_logger(name: str) -> logging.Logger` function
- Configure logger with consistent format and handlers
- Support both console and optional file logging

**Implementation:**
```python
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DEFAULT_LEVEL = logging.INFO
CONSOLE_LEVEL = logging.INFO
FILE_LEVEL = logging.DEBUG
```

#### Scenario: Logger Creation
When calling `get_logger("blokus_game.game.rules")`, the function returns a logger with:
- Name: "blokus_game.game.rules"
- Level: INFO
- Console handler with formatted output
- No duplicate handlers

### Requirement: Standardized Log Levels
The project MUST use standardized logging levels throughout the codebase for consistency and proper log filtering.

**Details:**
- DEBUG: Detailed information for debugging (development only)
- INFO: General game events, state changes
- WARNING: Non-critical issues, recoverable errors
- ERROR: Serious problems affecting game functionality
- CRITICAL: Fatal errors, game cannot continue

#### Scenario: Log Level Usage
When logging piece placement, use INFO level
When logging AI decisions, use DEBUG level (configurable)
When logging errors from user actions, use WARNING level
When logging system errors, use ERROR level
When logging unrecoverable errors, use CRITICAL level

### Requirement: Logger Naming Convention
The project MUST use hierarchical logger names for proper log organization and filtering.

**Details:**
- Use hierarchical logger names: `blokus_game.game`, `blokus_game.ui`, etc.
- Module-level logger: `logger = get_logger(__name__)`
- No duplicate handler creation

#### Scenario: Module Logger Initialization
When creating logger in `blokus_game.game.rules`, use name "blokus_game.game.rules"
When creating logger in `blokus_game.ui.board_renderer`, use name "blokus_game.ui.board_renderer"
When creating logger in `blokus_game.models.player`, use name "blokus_game.models.player"
