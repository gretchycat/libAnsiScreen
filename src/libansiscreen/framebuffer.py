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

class frameBuffer():
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
    def __init__(self, width: int, height=1):
        if width <= 0:
            raise ValueError("Screen width must be > 0")
        self.width: int = width
        self.rows: List[List[Cell]] = []
        self.cursor: Cursor = Cursor()
        # Current graphics state (SGR-like)
        self.current_fg: Color = DEFAULT_FG
        self.current_bg: Color = DEFAULT_BG
        self.current_attrs: int = 0
        self._ensure_row(height)
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
            #self.rows.append([Cell() for _ in range(self.width)])
            self.rows.append([Cell(
                char=' ',
                fg=self.current_fg,
                bg=self.current_bg,
                attrs=self.current_attrs,) for _ in range(500)]) #FIXME

    def _clamp_x(self, x: int) -> int:
        return max(0, min(self.width - 1, x))

    def resize(self, width, height):
        if height>0:
            while len(self.rows)>height:
                self.rows.pop()
            self._ensure_row(height)
        if width>0:
            addCells=width-self.width
            self.width=width
            if addCells>0:
                for y in range(height): #TODO fix me
                    for _ in range(addCells):
                        self.rows[y].append(Cell(
                                char=' ',
                                fg=self.current_fg,
                                bg=self.current_bg,
                                attrs=self.current_attrs))

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
        if cell:
            self.rows[y][x] = cell.copy()
        else:
            self.rows[y][x] = None

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

    def cursor_up(self, n: int = 1) -> None:
        self.cursor.y = max(0, self.cursor.y - n)

    def cursor_down(self, n: int = 1) -> None:
        self.cursor.y += n

    def cursor_forward(self, n: int = 1) -> None:
        self.cursor.x = self._clamp_x(self.cursor.x + n)

    def cursor_back(self, n: int = 1) -> None:
        self.cursor.x = self._clamp_x(self.cursor.x - n)

    def cursor_next_line(self, n: int = 1) -> None:
        self.cursor.x = 0
        self.cursor.y += n

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

    # ------------------------------------------------------------------
    # Line / carriage control
    # ------------------------------------------------------------------
    def carriage_return(self) -> None:
        self.cursor.x = 0

    def line_feed(self) -> None:
        self.cursor.y += 1

    def newline(self) -> None:
        self.cursor.x = 0
        self.cursor.y += 1

    # ------------------------------------------------------------------
    # Graphics state (SGR-like)
    # ------------------------------------------------------------------
    def set_foreground(self, color: Color) -> None:
        self.current_fg = Color.set(color)

    def set_background(self, color: Color) -> None:
        self.current_bg = Color.set(color)

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

    def __repr__(self):
        return f'frameBuffer ({self.width}, {self.height})'

    # ------------------------------------------------------------------
    # Clearing operations
    # ------------------------------------------------------------------
    def cls(self) -> None:
        """
        Clear screen, reset cursor and graphics state.
        """
        y=len(self.rows)-1
        self.rows.clear()
        self.cursor.reset()
        self._ensure_row(y)

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

    # ------------------------------------------------------------------
    # coloring
    # ------------------------------------------------------------------
    def shift_hsv(self, h: float, s:float,v:float):
        for r in self.rows:
            for c in r:
                c.shift_hsv(h,s,v)

    def shift_rgb(self, r: int, g:int, b:int):
        for row in self.rows:
            for c in row:
                c.shift_rgb(r,g,b)

