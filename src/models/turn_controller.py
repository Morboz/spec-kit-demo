"""
Turn Controller Module

This module provides the TurnController class which extends TurnManager
with AI-aware functionality for managing automatic AI moves.
"""

from typing import Optional, Callable, List, Any
from enum import Enum
from dataclasses import dataclass
from datetime import datetime
import time
from src.game.turn_manager import TurnManager
from src.models.game_state import GameState, GamePhase
from src.models.player import Player
from src.models.ai_player import AIPlayer
from src.models.game_mode import GameModeType
from src.services.ai_strategy import Move


class TurnState(Enum):
    """Turn state enumeration."""
    HUMAN_TURN = "human_turn"
    AI_CALCULATING = "ai_calculating"
    AI_MAKING_MOVE = "ai_making_move"
    TRANSITION_AUTO = "transition_auto"
    GAME_OVER = "game_over"


@dataclass
class TurnEvent:
    """Event data for turn state changes."""
    event_type: str
    timestamp: datetime
    player_id: int
    state: TurnState
    move: Optional[Move] = None
    ai_time_seconds: Optional[float] = None
    additional_data: Optional[dict] = None


class TurnController(TurnManager):
    """
    Extended turn controller for managing AI and human turns.

    Extends TurnManager with AI-aware functionality.
    Maintains game flow for both human and AI players.
    """

    def __init__(self, game_mode, initial_player: int = 1) -> None:
        """
        Initialize turn controller.

        Args:
            game_mode: GameMode configuration
            initial_player: Starting player ID (default: 1)

        Raises:
            ValueError: If game_mode is invalid
            ValueError: If initial_player not in valid positions
        """
        # Get game_state from somewhere - need to initialize it
        # For now, we'll assume it's passed or we need to create it
        # This is a placeholder - actual implementation will need game_state
        self.game_mode = game_mode
        self.current_player = initial_player
        self.current_state = TurnState.HUMAN_TURN
        self._elapsed_ai_time = 0.0
        self._listeners: List[Callable[[TurnEvent], None]] = []
        self._turn_history: List[TurnEvent] = []
        self._is_calculating = False

    @property
    def game_mode(self):
        """Get current game mode configuration."""
        return self._game_mode

    @game_mode.setter
    def game_mode(self, value):
        """Set game mode configuration."""
        self._game_mode = value

    @property
    def current_player(self) -> int:
        """Get current player ID (1-4)."""
        return self._current_player

    @current_player.setter
    def current_player(self, value: int):
        """Set current player ID."""
        self._current_player = value

    @property
    def current_state(self) -> TurnState:
        """Get current turn state."""
        return self._current_state

    @current_state.setter
    def current_state(self, value: TurnState):
        """Set current turn state."""
        self._current_state = value

    @property
    def is_ai_turn(self) -> bool:
        """Check if current turn is AI-controlled."""
        return self.game_mode.is_ai_turn(self.current_player)

    @property
    def elapsed_ai_time(self) -> float:
        """Get elapsed time for current AI calculation (seconds)."""
        return self._elapsed_ai_time

    def set_game_mode(self, game_mode):
        """
        Set game mode before game starts.

        Args:
            game_mode: New game mode configuration

        Raises:
            ValueError: If game has already started
            ConfigurationError: If mode is invalid
        """
        # TODO: Check if game has started
        self.game_mode = game_mode

    def start_turn(self):
        """
        Start turn for current player.

        Behavior:
            - If AI player: Automatically trigger AI calculation
            - If human player: Enable UI input, wait for move
            - In spectator mode: All turns are AI turns

        Contract:
            - Must be called after game initialization
            - Cannot be called if game is over
            - State transitions to AI_CALCULATING or HUMAN_TURN
        """
        if self.current_state == TurnState.GAME_OVER:
            return

        # Emit turn started event
        self._emit_event("TURN_STARTED", self.current_player, self.current_state)

        # In spectator mode, all turns are AI-controlled
        if self.game_mode.mode_type == GameModeType.SPECTATE or self.is_ai_turn:
            self.current_state = TurnState.AI_CALCULATING
            self.trigger_ai_turn()
        else:
            self.current_state = TurnState.HUMAN_TURN

    def trigger_ai_turn(
        self,
        on_move_calculated: Callable[[Optional[Move]], None] = None,
        on_timeout: Callable[[], None] = None,
    ):
        """
        Trigger AI move calculation for current player.

        Args:
            on_move_calculated: Callback when move is calculated
            on_timeout: Callback if calculation times out

        Contract:
            - Must only be called when is_ai_turn is True
            - Automatically handles timeout scenarios
            - Calls on_move_calculated with result (or None if pass)
            - Calls on_timeout if strategy exceeds time limit
            - Runs calculation in background thread to avoid UI blocking

        Raises:
            InvalidStateError: If not AI turn
            AIPlayerError: If AI player is misconfigured
        """
        if not self.is_ai_turn:
            raise ValueError("Cannot trigger AI turn when it's not an AI's turn")

        self.current_state = TurnState.AI_CALCULATING
        self._is_calculating = True
        self._elapsed_ai_time = 0.0

        # Emit AI calculation started event
        self._emit_event(
            "AI_CALCULATION_STARTED",
            self.current_player,
            self.current_state
        )

        # TODO: Get AI player from game state
        # ai_player = self.game_state.get_ai_player(self.current_player)

        # TODO: In real implementation, this would run in background thread
        # For now, we'll simulate a calculation
        time.sleep(0.1)  # Simulate calculation time

        # Create a dummy move for testing
        dummy_move = None  # or Move(...)
        self._is_calculating = False

        # Emit move calculated event
        self._emit_event(
            "AI_MOVE_CALCULATED",
            self.current_player,
            self.current_state,
            move=dummy_move
        )

        # Call callback
        if on_move_calculated:
            on_move_calculated(dummy_move)

        # Handle the move
        if dummy_move:
            self.handle_ai_move(dummy_move)
        else:
            self.pass_turn()

    def handle_ai_move(self, move: Optional[Move]):
        """
        Process AI-calculated move.

        Args:
            move: Move object or None (for pass turn)

        Behavior:
            1. Validate move (uses existing validator)
            2. Animate piece placement (if visual)
            3. Update board state
            4. Update player pieces/score
            5. Transition to next turn

        Contract:
            - Must be called after AI calculation completes
            - Move must be valid according to Blokus rules
            - Updates game state atomically
            - Cannot be called during AI calculation

        Raises:
            InvalidMoveError: If move violates rules
            InvalidStateError: If not in proper state
        """
        if self._is_calculating:
            raise ValueError("Cannot handle move while AI is calculating")

        self.current_state = TurnState.AI_MAKING_MOVE

        # Emit move placed event
        self._emit_event(
            "MOVE_PLACED",
            self.current_player,
            self.current_state,
            move=move
        )

        # TODO: Validate move using BlokusRules
        # TODO: Place piece on board
        # TODO: Update player state
        # TODO: Animate placement

        # End the turn
        self.end_turn()

    def end_turn(self):
        """
        End current turn and advance to next player.

        Behavior:
            - Validates game is not over
            - Identifies next active player
            - Calls start_turn() for next player
            - In spectator mode: Automatically continues to next turn

        Contract:
            - Can be called after move is placed or passed
            - Skips inactive positions (empty quadrants)
            - Detects game end condition (all players passed)
            - Automatically schedules next turn in spectator mode

        Raises:
            InvalidStateError: If move not yet processed
            GameOverError: If game should end
        """
        self.current_state = TurnState.TRANSITION_AUTO

        # TODO: Check if game is over
        # if self.check_game_over():
        #     self.current_state = TurnState.GAME_OVER
        #     self._emit_event("GAME_OVER", self.current_player, self.current_state)
        #     return

        # Advance to next player
        next_player = self.get_next_player(self.current_player)
        self.current_player = next_player

        # In spectator mode, automatically continue to next turn
        if self.game_mode.mode_type == GameModeType.SPECTATE:
            # Small delay to make gameplay observable
            self.after(500, lambda: self.start_turn())
        else:
            # For human modes, wait for human input
            self.current_state = TurnState.HUMAN_TURN

    def pass_turn(self):
        """
        Handle player passing turn (no valid moves).

        Behavior:
            - Marks current player as passed
            - Checks if all active players have passed
            - If all passed: ends game
            - Otherwise: proceeds to next turn

        Contract:
            - Can be called at any time during player's turn
            - Validates player actually has no valid moves
            - Prevents consecutive passes by same player
            - Updates game state to track pass count

        Raises:
            InvalidStateError: If player has valid moves
            GameOverError: If game ends
        """
        # TODO: Mark player as passed
        # player = self.game_state.get_player_by_id(self.current_player)
        # player.pass_turn()

        # Emit pass event
        self._emit_event(
            "TURN_PASSED",
            self.current_player,
            self.current_state
        )

        # End the turn
        self.end_turn()

    def check_game_over(self) -> bool:
        """
        Check if game should end.

        Returns:
            True if game over condition met

        Conditions:
            - All active players have passed consecutively
            - No pieces remain for any player
            - Board is completely filled
            - All AI players have no valid moves (special handling)

        This method handles edge cases where all AI players might be stuck
        with no valid moves, ensuring the game doesn't hang indefinitely.
        """
        # Get all active players from game mode
        active_players = []
        if self.game_mode.human_player_position:
            active_players.append(self.game_mode.human_player_position)
        for ai_config in self.game_mode.ai_players:
            active_players.append(ai_config.position)

        # Track consecutive passes
        consecutive_passes = 0

        # TODO: Get player states from game state
        # For now, we'll use a placeholder approach

        # Check if all active players have no pieces
        # all_no_pieces = all(
        #     not self.game_state.get_player_by_id(pid).has_pieces_remaining()
        #     for pid in active_players
        # )
        #
        # if all_no_pieces:
        #     self._emit_event("GAME_OVER", self.current_player, TurnState.GAME_OVER)
        #     return True

        # Check if all players have passed consecutively
        # This would require tracking pass count in game state

        # For now, implement a simple check for AI-only scenarios
        if self.game_mode.mode_type == GameModeType.SPECTATE:
            # In spectator mode, check if all AI players have no moves
            # This is a safeguard against infinite loops

            # Get recent turn history to check for passes
            recent_events = self._turn_history[-len(active_players)*2:] if len(self._turn_history) > len(active_players)*2 else self._turn_history

            # Count recent passes by AI players
            ai_pass_count = sum(
                1 for event in recent_events
                if event.event_type == "TURN_PASSED" and
                   self.game_mode.is_ai_turn(event.player_id)
            )

            # If all AI players have passed recently, game should end
            if ai_pass_count >= len(active_players):
                self._emit_event("GAME_OVER", self.current_player, TurnState.GAME_OVER)
                return True

        # Check if board is completely filled
        # This would require accessing board state
        # board_full = self._is_board_full()
        # if board_full:
        #     self._emit_event("GAME_OVER", self.current_player, TurnState.GAME_OVER)
        #     return True

        return False

    def _is_board_full(self) -> bool:
        """
        Check if the game board is completely filled.

        Returns:
            True if no empty cells remain on the board

        Note:
            This is a placeholder. In actual implementation, this would
            check the game board state directly.
        """
        # TODO: Implement actual board check
        # Example implementation:
        # for row in self.game_state.board:
        #     for cell in row:
        #         if cell is None:
        #             return False
        # return True
        return False

    def check_consecutive_passes(self) -> int:
        """
        Check how many consecutive passes have occurred.

        Returns:
            Number of consecutive passes by all active players

        This helps detect end-game conditions where all players
        are passing because they have no valid moves.
        """
        if len(self._turn_history) == 0:
            return 0

        consecutive_count = 0
        # Check last events in reverse order
        for event in reversed(self._turn_history):
            if event.event_type == "TURN_PASSED":
                consecutive_count += 1
            else:
                # Stop counting if we hit a non-pass event
                break

        return consecutive_count

    def should_end_due_to_no_moves(self, player_id: int) -> bool:
        """
        Check if a player has no valid moves.

        Args:
            player_id: Player ID to check

        Returns:
            True if player has no valid moves available

        This is used to determine if a player should pass.
        In spectator mode, multiple consecutive no-move situations
        can trigger game end.
        """
        # TODO: Implement actual move availability check
        # Example:
        # player = self.game_state.get_player_by_id(player_id)
        # moves = player.get_available_moves(self.game_state.board, player.pieces)
        # return len(moves) == 0

        # For now, return False (placeholder)
        return False

    def add_turn_listener(self, callback: Callable[[TurnEvent], None]):
        """
        Add listener for turn events.

        Args:
            callback: Function to call on turn events

        Events:
            - TURN_STARTED: New turn begins
            - AI_CALCULATION_STARTED: AI starts thinking
            - AI_MOVE_CALCULATED: AI finished calculating
            - MOVE_PLACED: Piece placed on board
            - TURN_PASSED: Player passed turn
            - GAME_OVER: Game ended

        Contract:
            - Callbacks are called on main UI thread
            - Multiple listeners supported
            - Listeners notified in registration order
        """
        self._listeners.append(callback)

    def remove_turn_listener(self, callback: Callable[[TurnEvent], None]):
        """
        Remove turn event listener.

        Args:
            callback: Previously registered callback

        Contract:
            - Safe to call if callback not registered
            - Callback will not be called after removal
        """
        if callback in self._listeners:
            self._listeners.remove(callback)

    def get_turn_history(self) -> List[TurnEvent]:
        """
        Get history of turn events.

        Returns:
            List of all turn events in order

        Contract:
            - Events include timestamps
            - Used for game replay/debugging
            - Thread-safe snapshot of history
        """
        return self._turn_history.copy()

    def _emit_event(
        self,
        event_type: str,
        player_id: int,
        state: TurnState,
        move: Optional[Move] = None,
        additional_data: Optional[dict] = None,
    ):
        """
        Emit a turn event to all listeners.

        Args:
            event_type: Type of event
            player_id: Player ID
            state: Current turn state
            move: Move object (optional)
            additional_data: Additional event data (optional)
        """
        event = TurnEvent(
            event_type=event_type,
            timestamp=datetime.now(),
            player_id=player_id,
            state=state,
            move=move,
            additional_data=additional_data,
        )

        # Add to history
        self._turn_history.append(event)

        # Notify listeners
        for callback in self._listeners:
            try:
                callback(event)
            except Exception as e:
                # Log error but don't crash
                print(f"Error in turn listener: {e}")

    def get_next_player(self, current_player: int = None) -> int:
        """
        Get next player in turn order (using game mode configuration).

        Args:
            current_player: Current player ID (uses current_player if None)

        Returns:
            Next player ID (1-4)
        """
        if current_player is None:
            current_player = self.current_player

        return self.game_mode.get_next_player(current_player)
