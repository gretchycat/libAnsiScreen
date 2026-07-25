"""
libansiscreen.screen
~~~~~~~~~~~~~~~~~~~~

Primary high-level API module for libAnsiScreen.

Provides the `Screen` class, a document-oriented terminal screen buffer that integrates
ANSI parsing, rendering, color gradients, clipping operations, half-block pixel graphics,
subpixel high-resolution graphics (quadrant, octant, braille), and full-character primitives.
"""

from typing import Any, Iterable, List, Optional, Sequence, Set, Tuple, Union

from .cell import Cell
from .color.palette import create_ansi_16_palette
from .color.rgb import Color
from .framebuffer import frameBuffer
from .parser.ansi_parser import ANSIParser
from .renderer.ansi_emitter import ANSIEmitter
from .screen_ops.clip import clear, copy, cut, paste, tile
from .screen_ops.colorize import Colorize

from .screen_ops.pixel import (
    pixel_ellipse,
    pixel_flood_fill,
    pixel_get,
    pixel_line,
    pixel_plot,
    pixel_polyline,
    pixel_rectangle,
    pixel_regular_polygon,
    pixel_regular_star,
)

from .screen_ops.spixel import (
    spixel_ellipse,
    spixel_flood_fill,
    spixel_get,
    spixel_line,
    spixel_plot,
    spixel_polyline,
    spixel_rectangle,
    spixel_regular_polygon,
    spixel_regular_star,
)

from .screen_ops.prim import (
    char_ellipse,
    char_flood_fill,
    char_rectangle,
    char_tile,
    stamp_from_screen,
)

# ----------------------------------------------------------------------
# Palette-derived defaults (single source of truth)
# ----------------------------------------------------------------------
_ANSI16 = create_ansi_16_palette()

DEFAULT_FG = _ANSI16.index_to_rgb(7)  #: Default light gray foreground color
DEFAULT_BG = _ANSI16.index_to_rgb(0)  #: Default black background color


class Screen(Colorize, frameBuffer):
    """
    Lossless, document-oriented virtual terminal screen buffer.

    `Screen` serves as the central API entry point for `libAnsiScreen`. It combines:
    - Framebuffer storage (`frameBuffer`) for text cells, colors, and attributes.
    - Color gradient and tinting capabilities (`Colorize`).
    - ANSI escape sequence parsing (`ANSIParser`).
    - Optimized differential ANSI sequence emitting (`ANSIEmitter`).
    - Region clip / clipboard operations (`copy`, `clear`, `cut`, `paste`, `tile`).
    - Half-block pixel drawing (2 vertical subpixels per cell).
    - Subpixel monochrome drawing (quadrant, octant, braille modes).
    - High-level universal drawing dispatchers (`plot`, `line`, `polygon`, `star`, etc.).
    - Full-block character graphics primitives (`char_rectangle`, `char_ellipse`, etc.).

    Attributes:
        width (int): Fixed screen width in character columns.
        height (int): Logical screen height in character rows.
        cursor (Cursor): Logical write cursor tracking write position (x, y) and saved states.
        rows (List[List[Cell]]): 2D grid storing individual character cells.
        parser (ANSIParser): ANSI parser instance bound to this screen.
        emitter (ANSIEmitter): ANSI code emitter instance for rendering output.
        current_fg (Color): Active SGR foreground color for subsequent writes.
        current_bg (Color): Active SGR background color for subsequent writes.
        current_attrs (int): Active SGR text attribute bitmask (e.g. bold, underline).
    """

    def __init__(self, width: int, height: int = 1) -> None:
        """
        Initialize a new Screen instance.

        Args:
            width (int): Fixed width of the screen buffer in columns (> 0).
            height (int, optional): Initial height in rows. Defaults to 1.
        """
        super().__init__(width=width, height=height)
        self.parser = ANSIParser(self)
        self.emitter = ANSIEmitter()

    def __repr__(self) -> str:
        return f"Screen ({self.width}, {self.height})"

    # ------------------------------------------------------------------
    # ANSI I/O
    # ------------------------------------------------------------------
    def feed(self, s: Union[str, bytes]) -> None:
        """
        Feed an ANSI-encoded string or bytes sequence into the screen's parser.

        Updates the screen cells, cursor position, and graphics state according to
        the parsed ANSI escape sequences and plain text.

        Args:
            s (Union[str, bytes]): Text string or byte buffer containing ANSI data.
        """
        self.parser.feed(s)

    def print(self, s: Union[str, bytes]) -> None:
        """
        Alias for `feed()`. Parses ANSI text into the screen buffer.

        Args:
            s (Union[str, bytes]): Text string or byte buffer containing ANSI data.
        """
        self.parser.feed(s)

    def emit(self, box: Optional[Tuple[int, int, int, int]] = None, raw: bool = False) -> str:
        """
        Render the screen (or sub-region) into an ANSI escape sequence string.

        Args:
            box (Optional[Tuple[int, int, int, int]], optional): Bounding box `(x, y, w, h)`
                to render. If None, renders the entire screen.
            raw (bool, optional): If True, output absolute cursor position moves (`CSI y;x H`).
                Defaults to False.

        Returns:
            str: ANSI-encoded output string ready for terminal display.
        """
        return self.emitter.emit(self, box=box, raw=raw)

    def emit_diff(
        self,
        prev: frameBuffer,
        box: Optional[Tuple[int, int, int, int]] = None,
        raw: bool = False,
    ) -> str:
        """
        Render only the differences between this screen and a previous frame.

        Minimizes terminal bandwidth by generating differential ANSI SGR and cursor
        movement instructions.

        Args:
            prev (frameBuffer): The previous screen or framebuffer state to compare against.
            box (Optional[Tuple[int, int, int, int]], optional): Bounding box `(x, y, w, h)`
                to limit diff rendering. If None, diffs the entire screen.
            raw (bool, optional): If True, use explicit positioning sequences. Defaults to False.

        Returns:
            str: Differential ANSI escape sequence string.
        """
        return self.emitter.emit_diff(self, prev, box=box, raw=raw)

    # ------------------------------------------------------------------
    # Clip / Clipboard operations
    # ------------------------------------------------------------------
    def copy(self, box: Optional[Tuple[int, int, int, int]] = None) -> frameBuffer:
        """
        Copy a rectangular region of the screen into a new `frameBuffer`.

        Args:
            box (Optional[Tuple[int, int, int, int]], optional): Region to copy `(x, y, w, h)`.
                If None, copies the entire screen.

        Returns:
            frameBuffer: A new framebuffer containing the copied cells.
        """
        return copy(self, box=box)

    def clear(self, box: Optional[Tuple[int, int, int, int]] = None) -> None:
        """
        Clear cells in a specified region or across the entire screen.

        Clearing resets character content, foreground color, background color, and attributes.

        Args:
            box (Optional[Tuple[int, int, int, int]], optional): Region to clear `(x, y, w, h)`.
                If None, clears the whole screen.
        """
        return clear(self, box=box)

    def paste(
        self,
        src: frameBuffer,
        *,
        box: Optional[Tuple[int, int, int, int]] = None,
        transparent_char: Optional[Set[str]] = None,
        transparent_fg: bool = False,
        transparent_bg: bool = False,
        transparent_attrs: bool = False,
    ) -> None:
        """
        Paste another framebuffer onto this screen at a target region.

        Supports transparency rules for characters, foreground/background colors, and attributes.

        Args:
            src (frameBuffer): Source framebuffer to paste from.
            box (Optional[Tuple[int, int, int, int]], optional): Destination origin/box `(x, y, w, h)`.
            transparent_char (Optional[Set[str]], optional): Set of characters to treat as transparent.
            transparent_fg (bool, optional): If True, do not overwrite destination foreground color.
            transparent_bg (bool, optional): If True, do not overwrite destination background color.
            transparent_attrs (bool, optional): If True, do not overwrite destination attributes.
        """
        return paste(
            self,
            src,
            box=box,
            transparent_char=transparent_char,
            transparent_fg=transparent_fg,
            transparent_bg=transparent_bg,
            transparent_attrs=transparent_attrs,
        )

    def cut(self, box: Optional[Tuple[int, int, int, int]] = None) -> frameBuffer:
        """
        Cut a rectangular region: copy it to a new `frameBuffer`, then clear the original area.

        Args:
            box (Optional[Tuple[int, int, int, int]], optional): Region `(x, y, w, h)` to cut.
                If None, cuts the entire screen.

        Returns:
            frameBuffer: A new framebuffer containing the cut content.
        """
        return cut(self, box=box)

    def tile(self, tl: frameBuffer) -> None:
        """
        Repeatedly tile a template framebuffer `tl` across the entire screen dimensions.

        Args:
            tl (frameBuffer): The template framebuffer to repeat across grid.
        """
        return tile(self, tl)

    # ------------------------------------------------------------------
    # Half-block pixel drawing (2 vertical pixels per cell)
    # ------------------------------------------------------------------
    def pixel_plot(self, x: int, y: int, color: Color) -> None:
        """
        Plot a color pixel using half-block characters (upper/lower half block).

        Half-block mode provides 1x2 resolution per character cell (x = column, y = half-row).

        Args:
            x (int): Horizontal subpixel coordinate.
            y (int): Vertical subpixel coordinate (2 units per cell row).
            color (Color): Target pixel color.
        """
        return pixel_plot(self, x, y, color)

    def pixel_get(self, x: int, y: int) -> Optional[Color]:
        """
        Get the color of a half-block subpixel at subpixel coordinates `(x, y)`.

        Args:
            x (int): Horizontal subpixel coordinate.
            y (int): Vertical subpixel coordinate.

        Returns:
            Optional[Color]: Pixel color if set, or None.
        """
        return pixel_get(self, x, y)

    def pixel_line(self, x0: int, y0: int, x1: int, y1: int, color: Color) -> None:
        """
        Draw a straight line using half-block subpixels.

        Args:
            x0 (int): Start X coordinate.
            y0 (int): Start Y subpixel coordinate.
            x1 (int): End X coordinate.
            y1 (int): End Y subpixel coordinate.
            color (Color): Line color.
        """
        return pixel_line(self, x0, y0, x1, y1, color)

    def pixel_polyline(self, points: Sequence[Tuple[int, int]], color: Color) -> None:
        """
        Draw connected line segments through a sequence of subpixel points.

        Args:
            points (Sequence[Tuple[int, int]]): Sequence of `(x, y)` subpixel coordinates.
            color (Color): Polyline color.
        """
        return pixel_polyline(self, points, color)

    def pixel_regular_polygon(
        self,
        cx: int,
        cy: int,
        radius: int,
        sides: int,
        color: Color,
        rotation: float = 0.0,
    ) -> None:
        """
        Draw a regular polygon using half-block subpixels.

        Args:
            cx (int): Center X coordinate.
            cy (int): Center Y subpixel coordinate.
            radius (int): Outer radius in subpixels.
            sides (int): Number of polygon sides (>= 3).
            color (Color): Fill/line color.
            rotation (float, optional): Rotation angle in radians. Defaults to 0.0.
        """
        return pixel_regular_polygon(self, cx, cy, radius, sides, color, rotation=rotation)

    def pixel_regular_star(
        self,
        cx: int,
        cy: int,
        radius: int,
        n: int,
        k: int,
        color: Color,
        rotation: float = 0.0,
    ) -> None:
        """
        Draw a regular star polygon using half-block subpixels.

        Args:
            cx (int): Center X coordinate.
            cy (int): Center Y subpixel coordinate.
            radius (int): Outer radius in subpixels.
            n (int): Number of star points.
            k (int): Star step density / point skip step.
            color (Color): Star color.
            rotation (float, optional): Rotation angle in radians. Defaults to 0.0.
        """
        return pixel_regular_star(self, cx, cy, radius, n, k, color, rotation=rotation)

    def pixel_flood_fill(self, x_seed: int, y_seed: int, fill: Optional[Color] = None) -> frameBuffer:
        """
        Flood fill a connected area using half-block subpixels starting from `(x_seed, y_seed)`.

        Args:
            x_seed (int): Seed point X coordinate.
            y_seed (int): Seed point Y subpixel coordinate.
            fill (Optional[Color], optional): Fill color. If None, uses default foreground.

        Returns:
            frameBuffer: A mask or result framebuffer produced by fill operation.
        """
        return pixel_flood_fill(self, x_seed, y_seed, fill)

    def pixel_rectangle(
        self,
        x1: int,
        y1: int,
        x2: int,
        y2: int,
        fill: Optional[Color] = None,
    ) -> None:
        """
        Draw a filled rectangle using half-block subpixels.

        Args:
            x1 (int): Top-left X coordinate.
            y1 (int): Top-left Y subpixel coordinate.
            x2 (int): Bottom-right X coordinate.
            y2 (int): Bottom-right Y subpixel coordinate.
            fill (Optional[Color], optional): Rectangle fill color.
        """
        return pixel_rectangle(self, x1, y1, x2, y2, fill)

    def pixel_ellipse(
        self,
        cx: int,
        cy: int,
        rx: int,
        ry: int,
        fill: Optional[Color] = None,
    ) -> None:
        """
        Draw a filled ellipse using half-block subpixels.

        Args:
            cx (int): Center X coordinate.
            cy (int): Center Y subpixel coordinate.
            rx (int): Horizontal radius in subpixels.
            ry (int): Vertical radius in subpixels.
            fill (Optional[Color], optional): Ellipse fill color.
        """
        return pixel_ellipse(self, cx, cy, rx, ry, fill)

    # ------------------------------------------------------------------
    # Monochrome subpixel drawing (quadrant, octant, braille)
    # ------------------------------------------------------------------
    def spixel_plot(self, x: int, y: int, state: Any, mode: str = "octant") -> None:
        """
        Plot a subpixel bit in character subpixel mode (quadrant, octant, or braille).

        Args:
            x (int): Horizontal subpixel coordinate.
            y (int): Vertical subpixel coordinate.
            state (Any): Subpixel state (boolean set/clear or color).
            mode (str, optional): Subpixel mode ('quadrant', 'octant', 'braille'). Defaults to 'octant'.
        """
        return spixel_plot(self, x, y, state, mode)

    def spixel_get(self, x: int, y: int, mode: str = "octant") -> Any:
        """
        Retrieve subpixel state at coordinate `(x, y)`.

        Args:
            x (int): Horizontal subpixel coordinate.
            y (int): Vertical subpixel coordinate.
            mode (str, optional): Subpixel mode ('quadrant', 'octant', 'braille'). Defaults to 'octant'.

        Returns:
            Any: Subpixel state value.
        """
        return spixel_get(self, x, y, mode)

    def spixel_line(
        self,
        x0: int,
        y0: int,
        x1: int,
        y1: int,
        state: Any,
        mode: str = "octant",
    ) -> None:
        """
        Draw a subpixel line.

        Args:
            x0 (int): Start X subpixel coordinate.
            y0 (int): Start Y subpixel coordinate.
            x1 (int): End X subpixel coordinate.
            y1 (int): End Y subpixel coordinate.
            state (Any): Subpixel bit state or color.
            mode (str, optional): Drawing subpixel mode. Defaults to 'octant'.
        """
        return spixel_line(self, x0, y0, x1, y1, state, mode=mode)

    def spixel_polyline(
        self,
        points: Sequence[Tuple[int, int]],
        state: Any,
        mode: str = "octant",
    ) -> None:
        """
        Draw connected subpixel line segments.

        Args:
            points (Sequence[Tuple[int, int]]): Subpixel coordinates `[(x0, y0), ...]`.
            state (Any): Subpixel state.
            mode (str, optional): Subpixel mode ('quadrant', 'octant', 'braille'). Defaults to 'octant'.
        """
        return spixel_polyline(self, points, state, mode=mode)

    def spixel_regular_polygon(
        self,
        cx: int,
        cy: int,
        radius: int,
        sides: int,
        state: Any,
        rotation: float = 0.0,
        mode: str = "octant",
    ) -> None:
        """
        Draw a regular polygon using character subpixels.

        Args:
            cx (int): Center X subpixel coordinate.
            cy (int): Center Y subpixel coordinate.
            radius (int): Radius in subpixels.
            sides (int): Number of sides.
            state (Any): Subpixel state.
            rotation (float, optional): Rotation angle in radians. Defaults to 0.0.
            mode (str, optional): Subpixel mode. Defaults to 'octant'.
        """
        return spixel_regular_polygon(self, cx, cy, radius, sides, state, rotation, mode=mode)

    def spixel_regular_star(
        self,
        cx: int,
        cy: int,
        radius: int,
        n: int,
        k: int,
        state: Any,
        rotation: float = 0.0,
        mode: str = "octant",
    ) -> None:
        """
        Draw a regular star polygon using character subpixels.

        Args:
            cx (int): Center X subpixel coordinate.
            cy (int): Center Y subpixel coordinate.
            radius (int): Radius in subpixels.
            n (int): Star point count.
            k (int): Step skip.
            state (Any): Subpixel state.
            rotation (float, optional): Rotation angle in radians. Defaults to 0.0.
            mode (str, optional): Subpixel mode. Defaults to 'octant'.
        """
        return spixel_regular_star(self, cx, cy, radius, n, k, state, rotation, mode=mode)

    def spixel_flood_fill(
        self,
        x_seed: int,
        y_seed: int,
        state: Any,
        mode: str = "octant",
    ) -> frameBuffer:
        """
        Flood fill subpixel area starting at seed point.

        Args:
            x_seed (int): Seed X subpixel.
            y_seed (int): Seed Y subpixel.
            state (Any): Target fill state.
            mode (str, optional): Subpixel mode. Defaults to 'octant'.

        Returns:
            frameBuffer: Resulting mask framebuffer.
        """
        return spixel_flood_fill(self, x_seed, y_seed, state, mode=mode)

    def spixel_rectangle(
        self,
        x1: int,
        y1: int,
        x2: int,
        y2: int,
        state: Any,
        mode: str = "octant",
    ) -> None:
        """
        Draw a subpixel filled rectangle.

        Args:
            x1 (int): Top-left X subpixel.
            y1 (int): Top-left Y subpixel.
            x2 (int): Bottom-right X subpixel.
            y2 (int): Bottom-right Y subpixel.
            state (Any): Subpixel state.
            mode (str, optional): Subpixel mode. Defaults to 'octant'.
        """
        return spixel_rectangle(self, x1, y1, x2, y2, state, mode=mode)

    def spixel_ellipse(
        self,
        cx: int,
        cy: int,
        rx: int,
        ry: int,
        state: Any,
        mode: str = "octant",
    ) -> None:
        """
        Draw a subpixel filled ellipse.

        Args:
            cx (int): Center X subpixel.
            cy (int): Center Y subpixel.
            rx (int): Radius X in subpixels.
            ry (int): Radius Y in subpixels.
            state (Any): Subpixel state.
            mode (str, optional): Subpixel mode. Defaults to 'octant'.
        """
        return spixel_ellipse(self, cx, cy, rx, ry, state, mode=mode)

    # ------------------------------------------------------------------
    # Universal drawing dispatchers
    # ------------------------------------------------------------------
    def plot(self, x: int, y: int, state: Any, mode: Optional[str] = None) -> None:
        """
        Universal plot dispatcher.

        Dispatches to `pixel_plot` when `mode` is None or 'half', or `spixel_plot` for character subpixel modes.

        Args:
            x (int): Horizontal subpixel coordinate.
            y (int): Vertical subpixel coordinate.
            state (Any): Color or subpixel state.
            mode (Optional[str], optional): Drawing mode ('half', 'quadrant', 'octant', 'braille').
        """
        if mode in [None, "half"]:
            return pixel_plot(self, x, y, state)
        return spixel_plot(self, x, y, state, mode)

    def get(self, x: int, y: int, mode: Optional[str] = None) -> Any:
        """
        Universal subpixel getter dispatcher.

        Args:
            x (int): Horizontal subpixel coordinate.
            y (int): Vertical subpixel coordinate.
            mode (Optional[str], optional): Drawing mode.

        Returns:
            Any: Subpixel color or state value.
        """
        if mode in [None, "half"]:
            return pixel_get(self, x, y)
        return spixel_get(self, x, y, mode)

    def line(
        self,
        x0: int,
        y0: int,
        x1: int,
        y1: int,
        state: Any,
        mode: Optional[str] = None,
    ) -> None:
        """
        Universal line drawing dispatcher.

        Args:
            x0 (int): Start X coordinate.
            y0 (int): Start Y coordinate.
            x1 (int): End X coordinate.
            y1 (int): End Y coordinate.
            state (Any): Color or subpixel state.
            mode (Optional[str], optional): Drawing mode ('half', 'quadrant', 'octant', 'braille').
        """
        if mode in [None, "half"]:
            return pixel_line(self, x0, y0, x1, y1, state)
        return spixel_line(self, x0, y0, x1, y1, state, mode=mode)

    def polyline(
        self,
        points: Sequence[Tuple[int, int]],
        state: Any,
        mode: Optional[str] = None,
    ) -> None:
        """
        Universal polyline dispatcher.

        Args:
            points (Sequence[Tuple[int, int]]): Subpixel coordinates.
            state (Any): Color or subpixel state.
            mode (Optional[str], optional): Drawing mode.
        """
        if mode in [None, "half"]:
            return pixel_polyline(self, points, state)
        return spixel_polyline(self, points, state, mode=mode)

    def regular_polygon(
        self,
        cx: int,
        cy: int,
        radius: int,
        sides: int,
        state: Any,
        rotation: float = 0.0,
        mode: Optional[str] = None,
    ) -> None:
        """
        Universal regular polygon dispatcher.

        Args:
            cx (int): Center X coordinate.
            cy (int): Center Y coordinate.
            radius (int): Radius in subpixels.
            sides (int): Number of sides.
            state (Any): Color or subpixel state.
            rotation (float, optional): Rotation angle in radians.
            mode (Optional[str], optional): Drawing mode.
        """
        if mode in [None, "half"]:
            return pixel_regular_polygon(self, cx, cy, radius, sides, state, rotation)
        return spixel_regular_polygon(self, cx, cy, radius, sides, state, rotation, mode=mode)

    def regular_star(
        self,
        cx: int,
        cy: int,
        radius: int,
        n: int,
        k: int,
        state: Any,
        rotation: float = 0.0,
        mode: Optional[str] = None,
    ) -> None:
        """
        Universal regular star polygon dispatcher.

        Args:
            cx (int): Center X coordinate.
            cy (int): Center Y coordinate.
            radius (int): Radius in subpixels.
            n (int): Number of points.
            k (int): Point skip step.
            state (Any): Color or subpixel state.
            rotation (float, optional): Rotation angle in radians.
            mode (Optional[str], optional): Drawing mode.
        """
        if mode in [None, "half"]:
            return pixel_regular_star(self, cx, cy, radius, n, k, state, rotation)
        return spixel_regular_star(self, cx, cy, radius, n, k, state, rotation, mode=mode)

    def flood_fill(
        self,
        x_seed: int,
        y_seed: int,
        state: Any = None,
        mode: Optional[str] = None,
    ) -> frameBuffer:
        """
        Universal flood fill dispatcher.

        Args:
            x_seed (int): Seed X coordinate.
            y_seed (int): Seed Y coordinate.
            state (Any): Fill color or subpixel state.
            mode (Optional[str], optional): Drawing mode.

        Returns:
            frameBuffer: Resulting mask framebuffer.
        """
        if mode in [None, "half"]:
            return pixel_flood_fill(self, x_seed, y_seed, state)
        return spixel_flood_fill(self, x_seed, y_seed, state, mode=mode)

    def rectangle(
        self,
        x1: int,
        y1: int,
        x2: int,
        y2: int,
        state: Any,
        mode: Optional[str] = None,
    ) -> None:
        """
        Universal rectangle dispatcher.

        Args:
            x1 (int): Top-left X coordinate.
            y1 (int): Top-left Y coordinate.
            x2 (int): Bottom-right X coordinate.
            y2 (int): Bottom-right Y coordinate.
            state (Any): Color or subpixel state.
            mode (Optional[str], optional): Drawing mode.
        """
        if mode in [None, "half"]:
            return pixel_rectangle(self, x1, y1, x2, y2, state)
        return spixel_rectangle(self, x1, y1, x2, y2, state, mode=mode)

    def ellipse(
        self,
        cx: int,
        cy: int,
        rx: int,
        ry: int,
        state: Any,
        mode: Optional[str] = None,
    ) -> None:
        """
        Universal ellipse dispatcher.

        Args:
            cx (int): Center X coordinate.
            cy (int): Center Y coordinate.
            rx (int): Radius X in subpixels.
            ry (int): Radius Y in subpixels.
            state (Any): Color or subpixel state.
            mode (Optional[str], optional): Drawing mode.
        """
        if mode in [None, "half"]:
            return pixel_ellipse(self, cx, cy, rx, ry, state)
        return spixel_ellipse(self, cx, cy, rx, ry, state, mode=mode)

    # ------------------------------------------------------------------
    # Full-block character primitives
    # ------------------------------------------------------------------
    def char_flood_fill(
        self,
        x_seed: int,
        y_seed: int,
        ignore_fg_color: bool = False,
        ignore_bg_color: bool = False,
        fill: Optional[Color] = DEFAULT_FG,
    ) -> frameBuffer:
        """
        Perform a full-character flood fill starting from a seed cell `(x_seed, y_seed)`.

        Args:
            x_seed (int): Seed cell column.
            y_seed (int): Seed cell row.
            ignore_fg_color (bool, optional): If True, ignore foreground color when matching cells.
            ignore_bg_color (bool, optional): If True, ignore background color when matching cells.
            fill (Optional[Color], optional): Target fill color. Defaults to DEFAULT_FG.

        Returns:
            frameBuffer: Mask framebuffer indicating filled cells.
        """
        return char_flood_fill(
            self,
            x_seed,
            y_seed,
            ignore_fg_color,
            ignore_bg_color,
            fill=fill,
        )

    def char_rectangle(
        self,
        x1: int,
        y1: int,
        x2: int,
        y2: int,
        fill: Optional[Color] = None,
    ) -> frameBuffer:
        """
        Draw a filled rectangle using full-block character glyphs (`█`).

        Args:
            x1 (int): Top-left column.
            y1 (int): Top-left row.
            x2 (int): Bottom-right column.
            y2 (int): Bottom-right row.
            fill (Optional[Color], optional): Block color.

        Returns:
            frameBuffer: Mask framebuffer of affected cells.
        """
        return char_rectangle(self, x1, y1, x2, y2, fill)

    def char_ellipse(
        self,
        cx: int,
        cy: int,
        rx: int,
        ry: int,
        fill: Optional[Color] = None,
    ) -> frameBuffer:
        """
        Draw a filled ellipse using full-block character glyphs (`█`).

        Args:
            cx (int): Center column.
            cy (int): Center row.
            rx (int): Radius X in columns.
            ry (int): Radius Y in rows.
            fill (Optional[Color], optional): Block color.

        Returns:
            frameBuffer: Mask framebuffer of affected cells.
        """
        return char_ellipse(self, cx, cy, rx, ry, fill)

    def stamp_from_screen(
        self,
        transparent_chars: Optional[Sequence[Optional[str]]] = None,
        box: Optional[Tuple[int, int, int, int]] = None,
        border_bg: Optional[Color] = None,
    ) -> frameBuffer:
        """
        Create a stamp framebuffer from this screen with specified transparency and border.

        Args:
            transparent_chars (Optional[Sequence[Optional[str]]], optional): Sequence of characters
                considered transparent (e.g. `[None, ' ']`).
            box (Optional[Tuple[int, int, int, int]], optional): Bounding region `(x, y, w, h)`.
            border_bg (Optional[Color], optional): Optional background color for stamp border.

        Returns:
            frameBuffer: A stamp framebuffer ready for pasting.
        """
        return stamp_from_screen(
            self,
            transparent_chars=transparent_chars,
            box=box,
            border_bg=border_bg,
        )

    def char_tile(self, text: str) -> None:
        """
        Tile multi-line ASCII text across the entire screen grid cell-by-cell.

        Args:
            text (str): String containing text pattern (can include newline characters).
        """
        return char_tile(self, text)
