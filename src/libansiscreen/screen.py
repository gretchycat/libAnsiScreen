# libansiscreen/screen.py

from typing import List, Optional

from .cell import Cell
from .cursor import Cursor
from .color.rgb import Color
from .color.palette import create_ansi_16_palette


# ----------------------------------------------------------------------
# Palette-derived defaults (single source of truth)
# ----------------------------------------------------------------------

_ANSI16 = create_ansi_16_palette()

DEFAULT_FG: Color = _ANSI16.index_to_rgb(7)  # light gray
DEFAULT_BG: Color = _ANSI16.index_to_rgb(0)  # black


class Screen:
    """
    Lossless, document-oriented screen buffer.

    - Width is fixed.
    - Height grows dynamically.
    - Cursor represents write position only.
    - Current graphics state (colors + attributes) is explicit.
    """

    # ------------------------------------------------------------------
    # Construction
    # ------------------------------------------------------------------

    def __init__(self, width: int):
        if width <= 0:
            raise ValueError("Screen width must be > 0")

        self.width: int = width
        self.rows: List[List[Cell]] = []
        self.cursor: Cursor = Cursor()

        # Current graphics state (SGR-like)
        self.current_fg: Color = DEFAULT_FG
        self.current_bg: Color = DEFAULT_BG
        self.current_attrs: int = 0

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def height(self) -> int:
        """Logical height of the screen."""
        return len(self.rows)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _ensure_row(self, y: int) -> None:
        """Ensure row y exists."""
        while y >= len(self.rows):
            self.rows.append([Cell() for _ in range(self.width)])

    def _clamp_x(self, x: int) -> int:
        return max(0, min(self.width - 1, x))

    # ------------------------------------------------------------------
    # Cell access
    # ------------------------------------------------------------------

    def get_cell(self, x: int, y: int) -> Optional[Cell]:
        self._ensure_row(y)
        if y < 0 or y >= len(self.rows):
            return None
        if x < 0 or x >= self.width:
            return None
        return self.rows[y][x]

    def set_cell(self, x: int, y: int, cell: Cell) -> None:
        if x < 0 or x >= self.width:
            return
        self._ensure_row(y)
        self.rows[y][x] = cell

    def put_cell(self, x: int, y: int, *, char=None, fg=None, bg=None, attrs=0,) -> None:
        self.set_cell(
            x, y,
            Cell(
                char=char,
                fg=fg,
                bg=bg,
                attrs=attrs,
            )
        )
    # ------------------------------------------------------------------
    # Cursor control (ANSI semantics)
    # ------------------------------------------------------------------
    def cursor_goto(self, x: int, y: int) -> None:
        self.cursor.x = self._clamp_x(x)
        self.cursor.y = max(0, y)
        self._ensure_row(self.cursor.y)

    def cursor_up(self, n: int = 1) -> None:
        self.cursor.y = max(0, self.cursor.y - n)

    def cursor_down(self, n: int = 1) -> None:
        self.cursor.y += n
        self._ensure_row(self.cursor.y)

    def cursor_forward(self, n: int = 1) -> None:
        self.cursor.x = self._clamp_x(self.cursor.x + n)

    def cursor_back(self, n: int = 1) -> None:
        self.cursor.x = self._clamp_x(self.cursor.x - n)

    def cursor_next_line(self, n: int = 1) -> None:
        self.cursor.x = 0
        self.cursor.y += n
        self._ensure_row(self.cursor.y)

    def cursor_prev_line(self, n: int = 1) -> None:
        self.cursor.x = 0
        self.cursor.y = max(0, self.cursor.y - n)

    def cursor_set_column(self, x: int) -> None:
        self.cursor.x = self._clamp_x(x)

    def cursor_save(self) -> None:
        self.cursor.save()

    def cursor_restore(self) -> None:
        self.cursor.restore()
        self.cursor.x = self._clamp_x(self.cursor.x)
        self._ensure_row(self.cursor.y)

    # ------------------------------------------------------------------
    # Line / carriage control
    # ------------------------------------------------------------------

    def carriage_return(self) -> None:
        self.cursor.x = 0

    def line_feed(self) -> None:
        self.cursor.y += 1
        self._ensure_row(self.cursor.y)

    def newline(self) -> None:
        self.cursor.x = 0
        self.cursor.y += 1
        self._ensure_row(self.cursor.y)

    # ------------------------------------------------------------------
    # Graphics state (SGR-like)
    # ------------------------------------------------------------------

    def set_foreground(self, color: Color) -> None:
        self.current_fg = color

    def set_background(self, color: Color) -> None:
        self.current_bg = color

    def set_attrs(self, attrs: int) -> None:
        self.current_attrs = attrs

    def add_attrs(self, attrs: int) -> None:
        self.current_attrs |= attrs

    def clear_attrs(self, attrs: int) -> None:
        self.current_attrs &= ~attrs

    def reset_graphics(self) -> None:
        """
        Reset foreground, background, and attributes to ANSI defaults.
        Equivalent to SGR 0.
        """
        self.current_fg = DEFAULT_FG
        self.current_bg = DEFAULT_BG
        self.current_attrs = 0

    # ------------------------------------------------------------------
    # Writing operations
    # ------------------------------------------------------------------

    def put_char(self, char: str) -> None:
        #if type(char != str):
        #    raise ValueError("put_char expects a single character" + str(char))
        if len(char) != 1:
            raise ValueError("put_char expects a single character" + char)

        self._ensure_row(self.cursor.y)

        self.rows[self.cursor.y][self.cursor.x] = Cell(
            char=char,
            fg=self.current_fg,
            bg=self.current_bg,
            attrs=self.current_attrs,
        )

        self._advance_cursor()

    def put_text(self, text: str) -> None:
        for ch in text:
            if ch == "\n":
                self.newline()
            elif ch == "\r":
                self.carriage_return()
            else:
                self.put_char(ch)

    def _advance_cursor(self) -> None:
        self.cursor.x += 1
        if self.cursor.x >= self.width:
            self.cursor.x = 0
            self.cursor.y += 1
            self._ensure_row(self.cursor.y)

    # ------------------------------------------------------------------
    # Clearing operations
    # ------------------------------------------------------------------

    def cls(self) -> None:
        """
        Clear screen, reset cursor and graphics state.
        """
        self.rows.clear()
        self.cursor.reset()
        self.reset_graphics()

    def clear_row(self, y: int) -> None:
        self._ensure_row(y)
        self.rows[y] = [Cell() for _ in range(self.width)]

    def clear_to_end_of_line(self) -> None:
        self._ensure_row(self.cursor.y)
        row = self.rows[self.cursor.y]
        for x in range(self.cursor.x, self.width):
            row[x] = Cell(
                char=" ",
                fg=self.current_fg,
                bg=self.current_bg,
                attrs=self.current_attrs,
            )

    def clear_to_end_of_screen(self) -> None:
        self.clear_to_end_of_line()
        for y in range(self.cursor.y + 1, len(self.rows)):
            self.rows[y] = [Cell() for _ in range(self.width)]

    def copy(self, box=None):
        from libansiscreen.screen_ops.copy import copy
        return copy(self, box)

    def clear(self, box=None):
        from libansiscreen.screen_ops.clear import clear
        clear(self, box)

    def paste(self, src, box=None, **kwargs):
        from libansiscreen.screen_ops.paste import paste
        paste(self, src, box=box, **kwargs)

    def cut(self, box=None):
        from libansiscreen.screen_ops.cut import cut
        return cut(self, box)

    def colorize(
        self,
        gradient,
        *,
        mode: str = "hgrad",
        foreground: bool = True,
        background: bool = False,
        only_if_set: bool = True,
        tint: Optional[float] = None,
        direction: str = "tlbr"):
        from libencodescreen.screen_ops.colorize import colorize
        return colorize(self, gradient, mode=mode, foreground=foreground,
                          background=background, only_if_set=only_if_set,
                          tint=tint, direction=direction)

    def pixel(self, x: int, y: int, color):
        from libansiscreen.screen_ops.pixelplot import pixel
        return pixel(self, x, y, color)

    def pixelplot(self, x: int, y: int, color):
        from libansiscreen.screen_ops.pixelplot import pixelplot
        return pixelplot(self, x, y, color)

    def pixelget(self, x: int, y: int):
        from libansiscreen.screen_ops.pixelplot import pixelget
        return pixelget(self, x, y)


    def line(self, x0: int, y0: int, x1: int, y1: int, color):
        from libansiscreen.screen_ops.pixelplot import draw_line
        return draw_line(self, x0, y0, x1, y1, color)

    def polyline(self, points, color):
        from libansiscreen.screen_ops.pixelplot import draw_polyline
        return draw_polyline(self, points, color)

    def regular_polygon(
        self,
        cx: int,
        cy: int,
        radius: int,
        sides: int,
        color,
        rotation: float = 0.0,
    ):
        from libansiscreen.screen_ops.pixelplot import draw_regular_polygon
        return draw_regular_polygon(
            self, cx, cy, radius, sides, color, rotation
        )

    def regular_star(
        self,
        cx: int,
        cy: int,
        radius: int,
        n: int,
        k: int,
        color,
        rotation: float = 0.0,
    ):
        from libansiscreen.screen_ops.pixelplot import draw_regular_star
        return draw_regular_star(
            self, cx, cy, radius, n, k, color, rotation
        )

