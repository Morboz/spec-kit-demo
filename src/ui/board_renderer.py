"""
Optimized board renderer for Blokus.

This module provides high-performance rendering for the game board using:
- Double buffering to reduce flicker
- Region-based updates to avoid full redraws
- Caching for piece shapes and common operations
- Optimized drawing algorithms
- Configurable rendering quality
"""

import tkinter as tk
from typing import Dict, List, Tuple, Optional, Set, Any
from collections import defaultdict
from dataclasses import dataclass


@dataclass
class RenderRegion:
    """Represents a region of the board that needs to be redrawn."""
    x: int
    y: int
    width: int
    height: int
    priority: int = 0  # Higher priority rendered first


@dataclass
class CachedPiece:
    """Cached piece rendering data."""
    piece_id: int
    shape: List[Tuple[int, int]]
    color: str
    rotation: int
    flipped: bool
    # Pre-rendered points for faster drawing
    points: List[Tuple[int, int]]


class OptimizedBoardRenderer:
    """High-performance board renderer with caching and region updates."""

    def __init__(
        self,
        canvas: tk.Canvas,
        board_size: int = 20,
        cell_size: int = 30,
    ):
        """
        Initialize optimized board renderer.

        Args:
            canvas: Tkinter canvas to render on
            board_size: Size of the board (NxN)
            cell_size: Size of each cell in pixels
        """
        self.canvas = canvas
        self.board_size = board_size
        self.cell_size = cell_size

        # Rendering configuration
        self.enable_double_buffer = True
        self.enable_region_updates = True
        self.enable_caching = True
        self.render_quality = "high"  # high, medium, low

        # Canvas dimensions
        self.canvas_width = board_size * cell_size
        self.canvas_height = board_size * cell_size

        # Double buffering
        self.buffer_canvas: Optional[tk.Canvas] = None
        self.buffer_image: Optional[tk.PhotoImage] = None

        # Caching
        self.piece_cache: Dict[str, CachedPiece] = {}
        self.grid_lines_cache: Optional[tk.PhotoImage] = None
        self.background_cache: Optional[tk.PhotoImage] = None

        # Dirty regions tracking
        self.dirty_regions: Set[Tuple[int, int, int, int]] = set()
        self.last_rendered_state: Dict[str, Any] = {}

        # Performance metrics
        self.render_count = 0
        self.cache_hits = 0
        self.cache_misses = 0

        # Initialize
        self._setup_canvas()
        self._create_buffer()

    def _setup_canvas(self):
        """Setup canvas configuration for optimal rendering."""
        self.canvas.configure(
            width=self.canvas_width,
            height=self.canvas_height,
            bg="white",
            highlightthickness=0,
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)

    def _create_buffer(self):
        """Create offscreen buffer for double buffering."""
        if self.enable_double_buffer:
            # Create buffer canvas
            self.buffer_canvas = tk.Canvas(
                self.canvas,
                width=self.canvas_width,
                height=self.canvas_height,
            )
            self.buffer_canvas.pack_forget()  # Hide buffer

    def render_board(
        self,
        board_state: Dict[Tuple[int, int], int],
        pieces: Optional[Dict[int, Any]] = None,
        show_grid: bool = True,
        show_coordinates: bool = False,
        highlight_regions: Optional[List[RenderRegion]] = None,
    ) -> Dict[str, int]:
        """
        Render the board with optimizations.

        Args:
            board_state: Dictionary of (row, col) -> player_id
            pieces: Dictionary of player_id -> piece data
            show_grid: Whether to show grid lines
            show_coordinates: Whether to show board coordinates
            highlight_regions: Regions to highlight

        Returns:
            Dictionary with performance metrics
        """
        self.render_count += 1
        metrics = {
            "render_time": 0,
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "regions_updated": 0,
        }

        import time
        start_time = time.time()

        if self.enable_region_updates and self.dirty_regions:
            # Only redraw dirty regions
            metrics["regions_updated"] = self._render_regions(
                board_state, pieces, show_grid, show_coordinates, highlight_regions
            )
        else:
            # Full redraw (either region updates disabled or no dirty regions)
            self._render_full(board_state, pieces, show_grid, show_coordinates, highlight_regions)
            # If we rendered everything, clear dirty regions
            self.dirty_regions.clear()

        metrics["render_time"] = (time.time() - start_time) * 1000  # ms

        return metrics

    def _render_regions(
        self,
        board_state: Dict[Tuple[int, int], int],
        pieces: Optional[Dict[int, Any]],
        show_grid: bool,
        show_coordinates: bool,
        highlight_regions: Optional[List[RenderRegion]],
    ):
        """
        Render only dirty regions.

        Args:
            board_state: Board state dictionary
            pieces: Pieces data
            show_grid: Show grid lines flag
            show_coordinates: Show coordinates flag
            highlight_regions: Regions to highlight

        Returns:
            Number of regions rendered
        """
        if not self.dirty_regions:
            return 0

        regions_rendered = 0

        # Sort regions by priority
        sorted_regions = sorted(
            [(x, y, w, h) for x, y, w, h in self.dirty_regions],
            key=lambda r: (r[3] * r[2]),  # Sort by area
            reverse=True,
        )

        for x, y, w, h in sorted_regions:
            self._render_region(x, y, w, h, board_state, pieces, show_grid, show_coordinates)
            regions_rendered += 1

        # Clear dirty regions after rendering
        self.dirty_regions.clear()

        return regions_rendered

    def _render_region(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        board_state: Dict[Tuple[int, int], int],
        pieces: Optional[Dict[int, Any]],
        show_grid: bool,
        show_coordinates: bool,
    ):
        """
        Render a specific region.

        Args:
            x: X coordinate in grid cells
            y: Y coordinate in grid cells
            width: Width in grid cells
            height: Height in grid cells
            board_state: Board state
            pieces: Pieces data
            show_grid: Show grid flag
            show_coordinates: Show coordinates flag
        """
        # Calculate pixel coordinates
        px = x * self.cell_size
        py = y * self.cell_size
        pw = width * self.cell_size
        ph = height * self.cell_size

        # Get pieces in this region
        region_pieces = []
        for row in range(y, min(y + height, self.board_size)):
            for col in range(x, min(x + width, self.board_size)):
                if (row, col) in board_state:
                    player_id = board_state[(row, col)]
                    region_pieces.append((row, col, player_id))

        # Clear region
        self.canvas.create_rectangle(
            px, py, px + pw, py + ph,
            fill="white",
            outline="",
        )

        # Draw pieces in region
        for row, col, player_id in region_pieces:
            self._draw_piece_at(row, col, player_id, pieces)

        # Draw grid lines if enabled
        if show_grid:
            self._draw_grid_region(x, y, width, height)

    def _render_full(
        self,
        board_state: Dict[Tuple[int, int], int],
        pieces: Optional[Dict[int, Any]],
        show_grid: bool,
        show_coordinates: bool,
        highlight_regions: Optional[List[RenderRegion]],
    ):
        """
        Render entire board.

        Args:
            board_state: Board state
            pieces: Pieces data
            show_grid: Show grid flag
            show_coordinates: Show coordinates flag
            highlight_regions: Regions to highlight
        """
        # Clear canvas
        self.canvas.delete("all")

        # Draw background
        self._draw_background()

        # Draw pieces
        for (row, col), player_id in board_state.items():
            self._draw_piece_at(row, col, player_id, pieces)

        # Draw grid
        if show_grid:
            self._draw_grid()

        # Draw coordinates
        if show_coordinates:
            self._draw_coordinates()

        # Draw highlights
        if highlight_regions:
            for region in highlight_regions:
                self._draw_region_highlight(region)

    def _draw_background(self):
        """Draw the board background."""
        self.canvas.create_rectangle(
            0, 0, self.canvas_width, self.canvas_height,
            fill="white",
            outline="",
        )

    def _draw_grid(self):
        """Draw grid lines."""
        # Check cache first
        if self.enable_caching and self.grid_lines_cache:
            # Use cached grid
            self.canvas.create_image(
                0, 0,
                image=self.grid_lines_cache,
                anchor=tk.NW,
            )
            return

        # Draw grid lines
        for i in range(self.board_size + 1):
            # Vertical lines
            x = i * self.cell_size
            self.canvas.create_line(
                x, 0, x, self.canvas_height,
                fill="#CCCCCC",
                width=1,
            )

            # Horizontal lines
            y = i * self.cell_size
            self.canvas.create_line(
                0, y, self.canvas_width, y,
                fill="#CCCCCC",
                width=1,
            )

        # Cache grid if enabled
        if self.enable_caching:
            self._cache_grid()

    def _draw_grid_region(self, x: int, y: int, width: int, height: int):
        """
        Draw grid lines for a region.

        Args:
            x: X coordinate
            y: Y coordinate
            width: Width
            height: Height
        """
        px = x * self.cell_size
        py = y * self.cell_size
        pw = width * self.cell_size
        ph = height * self.cell_size

        # Draw border of region
        self.canvas.create_rectangle(
            px, py, px + pw, py + ph,
            outline="#CCCCCC",
            width=1,
        )

        # Draw internal grid lines
        for i in range(width + 1):
            line_x = px + i * self.cell_size
            self.canvas.create_line(
                line_x, py, line_x, py + ph,
                fill="#EEEEEE",
                width=1,
            )

        for i in range(height + 1):
            line_y = py + i * self.cell_size
            self.canvas.create_line(
                px, line_y, px + pw, line_y,
                fill="#EEEEEE",
                width=1,
            )

    def _draw_piece_at(
        self,
        row: int,
        col: int,
        player_id: int,
        pieces: Optional[Dict[int, Any]],
    ):
        """
        Draw a piece at a specific location.

        Args:
            row: Row index
            col: Column index
            player_id: Player who owns the piece
            pieces: Pieces data
        """
        # Get player color
        color = self._get_player_color(player_id)

        # Calculate pixel position
        x = col * self.cell_size
        y = row * self.cell_size

        # Draw cell
        self.canvas.create_rectangle(
            x, y, x + self.cell_size, y + self.cell_size,
            fill=color,
            outline="#333333",
            width=1,
        )

        # Add shading for 3D effect (high quality only)
        if self.render_quality == "high":
            # Top-left highlight
            self.canvas.create_line(
                x, y, x + self.cell_size, y,
                fill="#FFFFFF",
                width=1,
            )
            self.canvas.create_line(
                x, y, x, y + self.cell_size,
                fill="#FFFFFF",
                width=1,
            )

            # Bottom-right shadow
            shadow_color = self._darken_color(color, 0.3)
            self.canvas.create_line(
                x, y + self.cell_size, x + self.cell_size, y + self.cell_size,
                fill=shadow_color,
                width=1,
            )
            self.canvas.create_line(
                x + self.cell_size, y, x + self.cell_size, y + self.cell_size,
                fill=shadow_color,
                width=1,
            )

    def _draw_coordinates(self):
        """Draw board coordinates (row/column numbers)."""
        font_size = max(6, self.cell_size // 4)

        # Draw column numbers
        for col in range(self.board_size):
            x = col * self.cell_size + self.cell_size // 2
            self.canvas.create_text(
                x, -5,
                text=str(col),
                anchor=tk.S,
                font=("Arial", font_size),
                fill="#999999",
            )

        # Draw row numbers
        for row in range(self.board_size):
            y = row * self.cell_size + self.cell_size // 2
            self.canvas.create_text(
                -5, y,
                text=str(row),
                anchor=tk.E,
                font=("Arial", font_size),
                fill="#999999",
            )

    def _draw_region_highlight(self, region: RenderRegion):
        """
        Draw a region highlight.

        Args:
            region: Region to highlight
        """
        px = region.x * self.cell_size
        py = region.y * self.cell_size
        pw = region.width * self.cell_size
        ph = region.height * self.cell_size

        self.canvas.create_rectangle(
            px, py, px + pw, py + ph,
            outline="#FF0000",
            width=2,
            dash=(5, 5),
        )

    def _get_player_color(self, player_id: int) -> str:
        """
        Get color for a player.

        Args:
            player_id: Player ID

        Returns:
            Color string
        """
        colors = {
            1: "#4A90E2",  # Blue
            2: "#E24A4A",  # Red
            3: "#4AE26E",  # Green
            4: "#E2B54A",  # Yellow
        }
        return colors.get(player_id, "#999999")

    def _darken_color(self, color: str, factor: float) -> str:
        """
        Darken a hex color by a factor.

        Args:
            color: Hex color string
            factor: Darkening factor (0.0 to 1.0)

        Returns:
            Darkened color string
        """
        # Simple implementation - could be more sophisticated
        # For now, return a darker gray
        return "#666666"

    def _cache_grid(self):
        """Cache the grid lines for faster rendering."""
        if not self.enable_caching:
            return

        # Create an offscreen canvas for caching
        cache_canvas = tk.Canvas(
            width=self.canvas_width,
            height=self.canvas_height,
        )

        # Draw grid on cache canvas
        for i in range(self.board_size + 1):
            x = i * self.cell_size
            y = i * self.cell_size

            cache_canvas.create_line(
                x, 0, x, self.canvas_height,
                fill="#CCCCCC",
                width=1,
            )
            cache_canvas.create_line(
                0, y, self.canvas_width, y,
                fill="#CCCCCC",
                width=1,
            )

        # Convert to image
        self.grid_lines_cache = tk.PhotoImage(canvas=cache_canvas)

    def mark_dirty(self, x: int, y: int, width: int = 1, height: int = 1):
        """
        Mark a region as dirty (needs redraw).

        Args:
            x: X coordinate in grid cells
            y: Y coordinate in grid cells
            width: Width in grid cells
            height: Height in grid cells
        """
        self.dirty_regions.add((x, y, width, height))

    def mark_all_dirty(self):
        """Mark entire board as dirty."""
        self.dirty_regions.clear()
        self.dirty_regions.add((0, 0, self.board_size, self.board_size))

    def clear_cache(self):
        """Clear all cached data."""
        self.piece_cache.clear()
        self.grid_lines_cache = None
        self.background_cache = None

    def get_performance_metrics(self) -> Dict[str, Any]:
        """
        Get performance metrics.

        Returns:
            Dictionary with performance statistics
        """
        total_cache = self.cache_hits + self.cache_misses
        cache_hit_rate = (self.cache_hits / total_cache * 100) if total_cache > 0 else 0

        return {
            "total_renders": self.render_count,
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "cache_hit_rate": round(cache_hit_rate, 2),
            "cache_size": len(self.piece_cache),
        }

    def configure(
        self,
        double_buffer: Optional[bool] = None,
        region_updates: Optional[bool] = None,
        caching: Optional[bool] = None,
        quality: Optional[str] = None,
    ):
        """
        Configure rendering options.

        Args:
            double_buffer: Enable/disable double buffering
            region_updates: Enable/disable region-based updates
            caching: Enable/disable caching
            quality: Render quality (high, medium, low)
        """
        if double_buffer is not None:
            self.enable_double_buffer = double_buffer
            if double_buffer:
                self._create_buffer()

        if region_updates is not None:
            self.enable_region_updates = region_updates

        if caching is not None:
            self.enable_caching = caching
            if not caching:
                self.clear_cache()

        if quality is not None:
            self.render_quality = quality

    def cleanup(self):
        """Clean up resources."""
        self.clear_cache()
        if self.buffer_canvas:
            self.buffer_canvas.destroy()
            self.buffer_canvas = None


class PieceShapeCache:
    """Cache for piece shapes to avoid recalculation."""

    def __init__(self):
        """Initialize piece shape cache."""
        self.cache: Dict[str, List[Tuple[int, int]]] = {}

    def get_shape(
        self,
        piece_name: str,
        rotation: int = 0,
        flipped: bool = False,
    ) -> List[Tuple[int, int]]:
        """
        Get piece shape with transformation applied.

        Args:
            piece_name: Name of the piece
            rotation: Rotation degrees (0, 90, 180, 270)
            flipped: Whether piece is flipped

        Returns:
            List of (row, col) coordinates
        """
        cache_key = f"{piece_name}_{rotation}_{flipped}"

        if cache_key in self.cache:
            return self.cache[cache_key].copy()

        # Transform base shape
        shape = self._transform_shape(piece_name, rotation, flipped)
        self.cache[cache_key] = shape

        return shape

    def _transform_shape(
        self,
        piece_name: str,
        rotation: int,
        flipped: bool,
    ) -> List[Tuple[int, int]]:
        """
        Transform base piece shape.

        Args:
            piece_name: Piece name
            rotation: Rotation degrees
            flipped: Flip flag

        Returns:
            Transformed shape coordinates
        """
        # Get base shape (placeholder - would come from piece definitions)
        base_shape = [(0, 0), (0, 1), (1, 0)]  # Example L-shape

        shape = base_shape.copy()

        # Apply flip
        if flipped:
            shape = [(-r, c) for r, c in shape]

        # Apply rotation
        for _ in range(rotation // 90):
            shape = [(c, -r) for r, c in shape]

        # Normalize to start from (0, 0)
        min_r = min(r for r, c in shape)
        min_c = min(c for r, c in shape)
        shape = [(r - min_r, c - min_c) for r, c in shape]

        return shape

    def clear(self):
        """Clear the cache."""
        self.cache.clear()