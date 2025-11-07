<!-- OPENSPEC:START -->
# OpenSpec Instructions

These instructions are for AI assistants working in this project.

Always open `@/openspec/AGENTS.md` when the request:
- Mentions planning or proposals (words like proposal, spec, change, plan)
- Introduces new capabilities, breaking changes, architecture shifts, or big performance/security work
- Sounds ambiguous and you need the authoritative spec before coding

Use `@/openspec/AGENTS.md` to learn:
- How to create and apply change proposals
- Spec format and conventions
- Project structure and guidelines

Keep this managed block so 'openspec update' can refresh the instructions.

<!-- OPENSPEC:END -->

# blokus-step-by-step Development Guidelines

Auto-generated from all feature plans. Last updated: 2025-10-30

## Active Technologies
- Python 3.11+ + tkinter (standard library), pytest (testing) (001-fix-piece-placement)
- N/A (in-memory game state, no persistence required) (001-fix-piece-placement)
- In-memory game state (no persistence required) (003-fix-ai-player)

- Python 3.11+ (portable, rapid prototyping, good game libraries) + tkinter (standard library, no external dependencies, sufficient for 2D board game) (001-blokus-multiplayer)

## Project Structure

```text
src/
tests/
```

## Commands

cd src [ONLY COMMANDS FOR ACTIVE TECHNOLOGIES][ONLY COMMANDS FOR ACTIVE TECHNOLOGIES] pytest [ONLY COMMANDS FOR ACTIVE TECHNOLOGIES][ONLY COMMANDS FOR ACTIVE TECHNOLOGIES] ruff check .

## Code Style

Python 3.11+ (portable, rapid prototyping, good game libraries): Follow standard conventions

## Recent Changes
- 003-fix-ai-player: Added Python 3.11+ + tkinter (standard library), pytest (testing)
- 002-ai-battle-mode: Added Python 3.11+ + tkinter (standard library)
- 001-fix-piece-placement: Added Python 3.11+ + tkinter (standard library), pytest (testing)


<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
