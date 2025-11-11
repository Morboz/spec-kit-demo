"""
Blokus Game Managers Package

This package contains specialized manager classes that handle different aspects
of the Blokus game application. These managers work together through the
BlokusApp coordinator class to provide a modular and maintainable architecture.

Managers:
- GameSetupManager: Handles game initialization and configuration
- AIManager: Manages AI players and their decision-making
- UIManager: Manages all user interface components
- GameFlowManager: Controls game flow and state transitions
- EventHandlerManager: Handles player interactions and events
"""

from .ai_manager import AIManager
from .event_handler_manager import EventHandlerManager
from .game_flow_manager import GameFlowManager
from .game_setup_manager import GameSetupManager
from .ui_manager import UIManager

__all__ = [
    "GameSetupManager",
    "AIManager",
    "UIManager",
    "GameFlowManager",
    "EventHandlerManager",
]
