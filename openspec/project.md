# Project Context

## Purpose
Blokus AI Battle Mode is a local multiplayer Blokus board game implementation featuring intelligent AI opponents across multiple game modes. The project enables players to:
- Play against single AI opponents (2-player mode)
- Compete against three AI opponents simultaneously
- Watch fully autonomous AI vs AI battles (Spectate mode)
- Experience three difficulty levels: Easy (Random), Medium (Corner), and Hard (Strategic)

The project focuses on educational and entertainment value, demonstrating AI strategy patterns in board game contexts.

## Tech Stack
- **Core Language**: Python 3.11+
- **GUI Framework**: tkinter (Python standard library)
- **Testing Framework**: pytest >= 8.4.2
- **Test Coverage**: pytest-cov >= 7.0.0
- **Code Formatting**: black >= 25.9.0 (88 character line length)
- **Linting**: flake8 >= 7.3.0 (E203, W503 ignored)
- **Type Checking**: mypy >= 1.18.2 (strict mode enabled)
- **Build Tool**: uv (optional, for dependency management)

**Runtime Dependencies**: None (uses only Python standard library)
**Dev Dependencies**: black, flake8, mypy, pytest, pytest-cov (for development only)

## Project Conventions

### Code Style
- **Line Length**: 88 characters (Black default)
- **Python Version**: 3.11+ (minimum version check enforced)
- **Formatting**: Black for automatic formatting
- **Linting**: flake8 with max-line-length=88, ignoring E203 and W503
- **Type Hints**: Strict mypy enforcement with:
  - `disallow_untyped_defs = true`
  - `disallow_incomplete_defs = true`
  - `disallow_untyped_decorators = true`
  - `no_implicit_optional = true`
  - `strict_equality = true`
- **Naming**: Standard Python conventions (snake_case for functions/variables, PascalCase for classes)
- **Imports**: Standard library organized by PEP 8 (tkinter imports explicitly allowed to fail)

### Architecture Patterns

#### Project Structure
```
src/
├── models/          # Data models and game state
│   ├── ai_player.py
│   ├── ai_config.py
│   ├── game_mode.py
│   ├── game_state.py
│   └── turn_controller.py
├── services/        # Business logic layer
│   └── ai_strategy.py
├── ui/              # User interface components
│   ├── game_mode_selector.py
│   ├── keyboard_shortcuts.py
│   ├── ai_thinking_indicator.py
│   ├── ai_difficulty_indicator.py
│   └── help_tooltips.py
└── config/          # Configuration files
```

#### Architectural Patterns
1. **Strategy Pattern**: AI implementations use strategy pattern with base `AIStrategy` interface and three implementations:
   - `RandomStrategy` (Easy difficulty)
   - `CornerStrategy` (Medium difficulty)
   - `StrategicStrategy` (Hard difficulty)

2. **Model-View-Service**: Separation of concerns:
   - Models: Game state, player data, AI configuration
   - Services: Business logic (AI strategies, move validation)
   - UI: tkinter-based interface with modular components

3. **Game Mode Configuration**: Abstract base `GameMode` class with concrete implementations for:
   - Single AI mode (1 human + 1 AI)
   - Three AI mode (1 human + 3 AI)
   - Spectate mode (4 AI players)

### Testing Strategy

#### Test Organization
```
tests/
├── unit/           # Unit tests for individual components
│   ├── test_ai_strategy.py
│   ├── test_ai_player.py
│   ├── test_game_mode.py
│   └── test_ai_edge_cases.py
└── integration/    # End-to-end and mode-specific tests
    ├── test_single_ai.py
    ├── test_three_ai.py
    ├── test_spectate.py
    ├── test_all_modes.py       # Comprehensive E2E tests
    ├── test_game_performance.py # Performance benchmarks
    └── test_ai_stress.py       # Stress/concurrency tests
```

#### Testing Approach
- **TDD**: Test-driven development for new features
- **Test Markers**:
  - `unit`: Unit tests
  - `integration`: Integration tests
  - `contract`: Contract tests (API validation)
  - `slow`: Slow-running tests
- **Coverage**: Minimum 80% branch coverage enforced
- **Performance Tests**: Dedicated tests for AI calculation times and timeout handling
- **Stress Tests**: Concurrent game handling and memory usage
- **pytest Options**: `-ra -q --strict-markers --strict-config`

#### Running Tests
```bash
# All tests
uv pytest

# Specific test types
uv pytest tests/unit/
uv pytest tests/integration/

# Performance-specific
uv pytest tests/integration/test_game_performance.py
uv pytest tests/integration/test_ai_stress.py

# Coverage report
uv pytest --cov=src --cov-report=html
```

### Git Workflow

#### Branch Naming Convention
- Feature branches: `<ticket>/<short-description>` (e.g., `003-fix-ai-player`)
- Hotfix branches: `hotfix/<description>`
- Release branches: `release/<version>`

#### Commit Message Convention
Format: `<emoji> <type>: <short description>`

Common types:
- `feat`: New feature
- `fix`: Bug fix
- `refactor`: Code refactoring
- `test`: Test additions/modifications
- `docs`: Documentation updates
- `ui`: UI-related changes
- `ai`: AI-related changes

Examples from history:
- `🎮 feat: Complete AI Player Strategy Implementation (003-fix-ai-player)`
- `🚀 feat: Phase 7 Progress: Error Handling & Performance Optimization Complete`

#### Development Workflow
1. Create feature branch from main
2. Write tests first (TDD approach)
3. Implement feature with passing tests
4. Run full test suite with coverage
5. Commit with conventional format
6. Create pull request for review
7. Merge after approval

## Domain Context

### Blokus Game Rules
- **Board**: 20x20 grid divided into 4 quadrants (one per player)
- **Pieces**: Each player has 21 unique polyomino pieces of varying shapes
- **Placement Rules**:
  - Pieces cannot overlap opponents' pieces
  - First piece must touch own corner (no edge-to-edge adjacency)
  - Subsequent pieces must connect to own pieces at corners only
  - No edge-to-edge adjacency with own pieces
- **Turn Flow**: Players take turns placing one piece
- **Game End**: When all players pass consecutively
- **Scoring**: Points for placed squares + bonuses for:
  - Keeping at least one piece
  - Having a piece in opponent's starting corner
  - Most squares placed

### AI Strategy Context
- **Random Strategy (Easy)**: Simple random valid move selection, 1-2 second calculation
- **Corner Strategy (Medium)**: Corner-focused placement, considers corner connections, 3-5 seconds
- **Strategic Strategy (Hard)**: Multi-factor evaluation (corners, mobility, area control, lookahead), 5-8 seconds

### Performance Considerations
- **Move Calculation Timeout**: Graceful fallbacks if AI exceeds time limits
- **Move Caching**: LRU caching for 2-5x speed improvement on repeated calculations
- **Concurrent Games**: Support for multiple simultaneous AI games
- **UI Responsiveness**: Async patterns to prevent UI freezing during AI thinking

## Important Constraints

### Technical Constraints
- **Python Version**: Must be >= 3.11 (checked via `requires-python = ">=3.11"`)
- **GUI Library**: tkinter only (standard library, no external dependencies)
- **Runtime Dependencies**: None (pure standard library for production)
- **Development Dependencies**: Only for dev tools (pytest, black, flake8, mypy)
- **File Structure**: Source code must be in `src/` directory
- **Test Directory**: Tests must be in `tests/` directory

### Game Constraints
- **Players**: 2-4 players maximum
- **Board Size**: Fixed 20x20 grid
- **Pieces**: Standard 21 Blokus pieces per player
- **Turn Timeout**: AI moves must complete or timeout gracefully
- **UI Responsiveness**: UI must remain responsive during AI calculations

### Performance Constraints
- **AI Calculation Time**:
  - Easy: < 2 seconds
  - Medium: < 5 seconds
  - Hard: < 8 seconds (with timeout fallback)
- **Memory Usage**: No explicit limit, but must handle concurrent games
- **Frame Rate**: Not applicable (turn-based game)

## External Dependencies

### Runtime Dependencies
- **None** - All functionality uses Python standard library only
- tkinter: GUI framework (standard library, may require separate installation on some Linux distributions)
- No database, no web services, no external APIs

### Development Dependencies (Optional)
- **pytest**: Testing framework
- **pytest-cov**: Coverage reporting
- **black**: Code formatting
- **flake8**: Linting
- **mypy**: Static type checking
- **uv**: Modern Python package manager (optional, pip can be used alternatively)

### Build/Development Tools
- **uv**: Recommended for dependency management (included in pyproject.toml)
- Can alternatively use pip/venv for traditional Python development
- pytest configured for test discovery in `tests/` directory
- Coverage reporting via pytest-cov with HTML output

### Documentation References
- Feature specifications: `specs/002-ai-battle-mode/spec.md`
- Implementation plans: `specs/002-ai-battle-mode/plan.md`
- Task breakdowns: `specs/002-ai-battle-mode/tasks.md`
- API documentation: `docs/ai_api.md`
- User guide: `README.md`
- Test documentation: `TESTING.md`
