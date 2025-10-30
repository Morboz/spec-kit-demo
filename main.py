"""
Blokus Game - Main Application Entry Point

This is the main entry point for the Blokus local multiplayer game.
The game supports 2-4 players on a single device.
"""

import sys


def main() -> int:
    """
    Main entry point for the Blokus game application.

    Returns:
        Exit code (0 for success, non-zero for error)
    """
    print("=" * 60)
    print("Welcome to Blokus - Local Multiplayer Game")
    print("=" * 60)
    print()
    print("Features:")
    print("  • Support for 2-4 players")
    print("  • 20x20 game board")
    print("  • 21 unique Blokus pieces per player")
    print("  • Full rule validation")
    print("  • Score tracking")
    print()
    print("Status: Game not yet implemented (Phase 1 setup complete)")
    print()
    print("Next Steps:")
    print("  1. Phase 2: Implement foundational components")
    print("  2. Phase 3: Game setup functionality")
    print("  3. Phase 4: Piece placement mechanics")
    print("  4. Phase 5: Game state visibility")
    print("  5. Phase 6: Game end detection")
    print()
    print("For more information, see: /specs/001-blokus-multiplayer/")
    print("=" * 60)

    return 0


if __name__ == "__main__":
    sys.exit(main())
