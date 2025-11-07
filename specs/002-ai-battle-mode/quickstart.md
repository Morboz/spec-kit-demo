# Quickstart Guide: AI Battle Mode

**Feature**: AI Battle Mode for Blokus
**Last Updated**: 2025-11-03

## Overview

This guide helps developers implement and test AI battle modes in the Blokus game. AI battle modes allow players to compete against computer-controlled opponents with configurable difficulty levels.

## Prerequisites

- Python 3.11+
- tkinter (included with Python)
- pytest for testing
- Existing Blokus game with:
  - 20x20 game board
  - BlokusPiece definitions
  - Move validation logic
  - Player management
  - Turn-based gameplay

## Implementation Steps

### Step 1: Understand the Architecture

The AI battle mode feature follows a modular architecture:

```
┌─────────────────────────────────────────┐
│           TurnController                │
│  (Extended with AI awareness)           │
└──────────────┬──────────────────────────┘
               │
               ├── AIPlayer (has strategy)
               │     │
               │     └── AIStrategy Interface
               │           ├── RandomStrategy (Easy)
               │           ├── CornerStrategy (Medium)
               │           └── StrategicStrategy (Hard)
               │
               └── GameMode Configuration
                     ├── Single AI
                     ├── Three AI
                     └── Spectate
```

**Key Principle**: AI players use the same validation rules as human players. No special cases.

### Step 2: Implement AI Strategy Base

Create `src/services/ai_strategy.py`:

```python
from abc import ABC, abstractmethod
from typing import List, Optional
import time

class AIStrategy(ABC):
    """Base class for AI strategies"""

    @property
    @abstractmethod
    def difficulty_name(self) -> str:
        """Return difficulty: Easy, Medium, or Hard"""

    @property
    @abstractmethod
    def timeout_seconds(self) -> int:
        """Return max calculation time"""

    @abstractmethod
    def calculate_move(self, board, pieces, player_id, time_limit=None):
        """Calculate best move for current state"""
        pass

    def get_available_moves(self, board, pieces, player_id):
        """Generate all valid moves (uses existing validator)"""
        moves = []
        for piece in pieces:
            for rotation in [0, 90, 180, 270]:
                for x in range(20):
                    for y in range(20):
                        if is_valid_move(board, piece, x, y, rotation, player_id):
                            moves.append(Move(piece, (x, y), rotation, player_id))
        return moves

    def evaluate_board(self, board, player_id):
        """Evaluate board position (simple implementation)"""
        return sum(1 for row in board for cell in row if cell == player_id)
```

**Test-First Development**: Write tests for AIStrategy before implementing concrete classes.

### Step 3: Implement Easy Strategy (Random)

```python
import random

class RandomStrategy(AIStrategy):
    """Easy AI: Random valid placement"""

    @property
    def difficulty_name(self):
        return "Easy"

    @property
    def timeout_seconds(self):
        return 3

    def calculate_move(self, board, pieces, player_id, time_limit=None):
        valid_moves = self.get_available_moves(board, pieces, player_id)
        return random.choice(valid_moves) if valid_moves else None
```

**Test**: Verify that random strategy returns valid moves and respects timeout.

### Step 4: Implement Medium Strategy (Corner-Focused)

```python
class CornerStrategy(AIStrategy):
    """Medium AI: Prioritizes corner connections"""

    @property
    def difficulty_name(self):
        return "Medium"

    @property
    def timeout_seconds(self):
        return 5

    def calculate_move(self, board, pieces, player_id, time_limit=None):
        valid_moves = self.get_available_moves(board, pieces, player_id)
        if not valid_moves:
            return None

        # Score moves by corner connections
        scored = []
        for move in valid_moves:
            score = self._score_corner_move(board, move, player_id)
            scored.append((score, move))

        # Return highest scoring move
        scored.sort(key=lambda x: x[0], reverse=True)
        return scored[0][1]

    def _score_corner_move(self, board, move, player_id):
        """Score based on corner strategy"""
        # Implementation: count corners touched
        # +10 per corner connection
        # +2 per piece size
        pass
```

**Test**: Verify corner strategy prefers moves that establish corner connections.

### Step 5: Implement AIPlayer

Create `src/models/ai_player.py`:

```python
class AIPlayer:
    """AI-controlled player"""

    def __init__(self, player_id, strategy, color, name=None):
        self.player_id = player_id
        self.strategy = strategy
        self.color = color
        self.name = name or f"AI Player {player_id}"
        self.pieces = get_full_piece_set()
        self.score = 0
        self.has_passed = False

    def calculate_move(self, board, pieces, time_limit=None):
        """Delegate to strategy with timeout handling"""
        try:
            start_time = time.time()
            move = self.strategy.calculate_move(board, pieces, self.player_id, time_limit)
            elapsed = time.time() - start_time

            if elapsed > (time_limit or self.strategy.timeout_seconds):
                # Log timeout warning
                pass

            return move
        except Exception as e:
            # On error, try simpler strategy or pass
            return None

    def pass_turn(self):
        """Mark player as passed"""
        self.has_passed = True
```

### Step 6: Create Game Mode Selection UI

Create `src/ui/game_mode_selector.py`:

```python
import tkinter as tk
from tkinter import ttk

class GameModeSelector:
    """UI for selecting AI battle mode"""

    def __init__(self, parent, callback):
        self.parent = parent
        self.callback = callback
        self.selected_mode = None
        self.selected_difficulty = "Medium"

    def show(self):
        """Display mode selection dialog"""
        dialog = tk.Toplevel(self.parent)
        dialog.title("Select Game Mode")

        # Mode selection
        ttk.Label(dialog, text="Game Mode:").pack(pady=5)
        modes = [
            ("Human vs Single AI", "single_ai"),
            ("Human vs Three AI", "three_ai"),
            ("Spectate AI vs AI", "spectate")
        ]

        self.selected_mode = tk.StringVar()
        for text, value in modes:
            ttk.Radiobutton(dialog, text=text, variable=self.selected_mode,
                           value=value).pack(anchor="w", padx=20)

        # Difficulty selection
        ttk.Label(dialog, text="Difficulty:").pack(pady=(15, 5))
        self.selected_difficulty = tk.StringVar(value="Medium")
        difficulties = [("Easy", "Easy"), ("Medium", "Medium"), ("Hard", "Hard")]
        for text, value in difficulties:
            ttk.Radiobutton(dialog, text=text, variable=self.selected_difficulty,
                           value=value).pack(anchor="w", padx=20)

        # Start button
        ttk.Button(dialog, text="Start Game",
                  command=self._on_start).pack(pady=20)

    def _on_start(self):
        """Handle start button click"""
        mode = self.selected_mode.get()
        difficulty = self.selected_difficulty.get()
        self.callback(mode, difficulty)
```

### Step 7: Extend Turn Controller

Modify existing TurnController to support AI:

```python
class TurnController:
    """Extended turn controller with AI support"""

    def __init__(self, game_mode):
        self.game_mode = game_mode
        self.current_player = 1
        self.state = "human_turn"  # or "ai_calculating"

    def start_turn(self):
        """Start turn for current player"""
        if self.game_mode.is_ai_turn(self.current_player):
            self.state = "ai_calculating"
            self._trigger_ai_turn()
        else:
            self.state = "human_turn"
            # Wait for human input

    def _trigger_ai_turn(self):
        """Trigger AI calculation"""
        ai_player = get_ai_player(self.current_player)
        move = ai_player.calculate_move(get_board(), ai_player.pieces)

        if move:
            self._place_ai_move(move)
        else:
            ai_player.pass_turn()

    def _place_ai_move(self, move):
        """Process AI move"""
        # Validate using existing rules
        if validate_move(get_board(), move):
            place_piece(move.piece, move.position, move.rotation)
            self.current_player = self.game_mode.get_next_player(self.current_player)
            self.start_turn()
```

### Step 8: Connect UI to Game Modes

In main menu or game initialization:

```python
def start_ai_mode(mode_type, difficulty):
    """Start AI battle mode"""
    if mode_type == "single_ai":
        game_mode = GameMode.single_ai(Difficulty(difficulty))
    elif mode_type == "three_ai":
        game_mode = GameMode.three_ai(Difficulty(difficulty))
    elif mode_type == "spectate":
        game_mode = GameMode.spectate_ai()

    # Initialize game with mode
    controller = TurnController(game_mode)
    controller.start_turn()

# Add to main menu
def show_main_menu():
    menu = tk.Tk()
    ttk.Button(menu, text="Single AI",
              command=lambda: start_ai_mode("single_ai", "Medium")).pack()
    ttk.Button(menu, text="Three AI",
              command=lambda: start_ai_mode("three_ai", "Medium")).pack()
    ttk.Button(menu, text="Spectate AI",
              command=lambda: start_ai_mode("spectate", "Medium")).pack()
```

## Testing Strategy

### Unit Tests

**Test AI Strategies**:

```python
# tests/unit/test_ai_strategies.py
import pytest

def test_random_strategy_returns_valid_move():
    board = create_empty_board()
    pieces = get_full_piece_set()
    strategy = RandomStrategy()

    move = strategy.calculate_move(board, pieces, 1)

    assert move is not None
    assert validate_move(board, move)

def test_corner_strategy_prefers_corners():
    board = create_board_with_corner_setup()
    pieces = get_full_piece_set()
    strategy = CornerStrategy()

    move = strategy.calculate_move(board, pieces, 1)

    # Verify move touches a corner
    assert move_touches_corner(board, move)
```

**Test AIPlayer**:

```python
# tests/unit/test_ai_player.py
def test_ai_player_calculates_move():
    ai = AIPlayer(1, RandomStrategy(), "blue")
    board = create_empty_board()
    pieces = ai.pieces

    move = ai.calculate_move(board, pieces)

    assert move is not None

def test_ai_player_respects_timeout():
    ai = AIPlayer(1, StrategicStrategy(), "red")
    start_time = time.time()
    ai.calculate_move(board, pieces, time_limit=1)
    elapsed = time.time() - start_time

    assert elapsed <= 1.5  # Allow some margin
```

### Integration Tests

**Test Game Modes**:

```python
# tests/integration/test_ai_battle_modes.py
def test_single_ai_mode():
    mode = GameMode.single_ai(Difficulty.MEDIUM)

    assert mode.human_player_position == 1
    assert len(mode.ai_players) == 1
    assert mode.ai_players[0].position == 3

def test_three_ai_mode():
    mode = GameMode.three_ai(Difficulty.EASY)

    assert mode.human_player_position == 1
    assert len(mode.ai_players) == 3
    assert all(p in [2, 3, 4] for p in [ai.position for ai in mode.ai_players])

def test_spectate_mode():
    mode = GameMode.spectate_ai()

    assert mode.human_player_position is None
    assert len(mode.ai_players) == 4
```

**Test Full Game Flow**:

```python
def test_single_ai_game_completion():
    mode = GameMode.single_ai(Difficulty.EASY)
    controller = TurnController(mode)

    # Play game automatically
    moves = 0
    while not controller.check_game_over() and moves < 100:
        controller.start_turn()
        moves += 1

    assert controller.check_game_over()
    assert moves > 0
```

## Running Tests

```bash
# Run all AI tests
cd src
pytest ../tests/unit/test_ai*.py -v

# Run integration tests
pytest ../tests/integration/test_ai_battle_modes.py -v

# Run with coverage
pytest --cov=. --cov-report=html
```

## Performance Testing

### AI Response Time

```python
def test_ai_performance():
    """Ensure AI completes within timeout"""
    for difficulty in [Difficulty.EASY, Difficulty.MEDIUM, Difficulty.HARD]:
        strategy = get_strategy_for_difficulty(difficulty)
        timeout = strategy.timeout_seconds

        start = time.time()
        move = strategy.calculate_move(board, pieces, player_id)
        elapsed = time.time() - start

        assert elapsed <= timeout + 0.5, f"{difficulty} exceeded timeout"
        assert move is not None or not get_available_moves(board, pieces, player_id)
```

### Game Flow Performance

```python
def test_game_flow_performance():
    """Ensure AI games complete in reasonable time"""
    mode = GameMode.single_ai(Difficulty.MEDIUM)
    controller = TurnController(mode)

    start = time.time()
    while not controller.check_game_over():
        controller.start_turn()

    elapsed = time.time() - start

    # Should complete in 15-30 minutes
    assert elapsed < 1800  # 30 minutes max
```

## Debugging Tips

### Enable AI Logging

```python
import logging

logging.basicConfig(level=logging.DEBUG)
ai_logger = logging.getLogger('ai_strategy')
ai_logger.setLevel(logging.DEBUG)

# Log AI decisions
def log_ai_move(strategy_name, move, evaluation_score):
    ai_logger.debug(f"{strategy_name} chose move: {move} (score: {evaluation_score})")
```

### Visualize AI Thinking

```python
# Show "AI is thinking..." indicator
def show_ai_thinking():
    label = tk.Label(root, text="AI is thinking...", font=("Arial", 14))
    label.pack()
    root.update()

    # Hide after move calculated
    label.destroy()
```

### Save Game States for Replay

```python
def save_game_state(controller, filename):
    """Save game state for debugging"""
    import json

    state = {
        'board': controller.board.tolist(),
        'current_player': controller.current_player,
        'player_pieces': {i: player.pieces for i, player in controller.players.items()},
        'turn_number': controller.turn_number
    }

    with open(filename, 'w') as f:
        json.dump(state, f)
```

## Common Issues

### Issue: AI Makes Invalid Moves

**Solution**: Verify AI uses existing validator
```python
# Wrong: AI has own validation
if ai_validate_move(board, move):
    place_piece(move)

# Right: AI uses same validation as humans
if validate_move(board, move):  # Same function!
    place_piece(move)
```

### Issue: UI Freezes During AI Calculation

**Solution**: Run AI in background thread
```python
import threading

def trigger_ai_turn():
    def calculate():
        move = ai_player.calculate_move(board, pieces)
        root.after(0, lambda: handle_ai_move(move))

    thread = threading.Thread(target=calculate)
    thread.daemon = True
    thread.start()
```

### Issue: AI Too Slow

**Solution**: Optimize move generation
```python
# Cache valid moves for Easy/Medium strategies
from functools import lru_cache

@lru_cache(maxsize=1000)
def get_cached_valid_moves(board_hash, pieces_tuple, player_id):
    # Only for strategies that don't need frequent recalculation
    pass
```

## Next Steps

After basic implementation:

1. **Add More Strategies**: Implement additional AI personalities
2. **Improve Evaluation**: Enhance strategic AI with better heuristics
3. **Visual Indicators**: Show AI difficulty and "thinking" state
4. **Game Replay**: Record and replay AI vs AI games
5. **Tournament Mode**: Multiple AI players compete
6. **Difficulty Learning**: AI adapts to player skill level

## Resources

- **Specification**: [spec.md](spec.md)
- **Data Model**: [data-model.md](data-model.md)
- **Contracts**: [contracts/](contracts/)
- **Research**: [research.md](research.md)
- **Implementation Plan**: [plan.md](plan.md)

## Support

For questions or issues:
1. Review contracts for interface requirements
2. Check test files for usage examples
3. Consult Blokus rules for validation logic
4. Verify timeout and performance requirements
