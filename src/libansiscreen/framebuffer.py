# libansiscreen/framebuffer.py

from typing import List, Optional
from .cell import Cell
from .cursor import Cursor
from .color.rgb import Color
from .color.palette import create_ansi_16_palette

# ----------------------------------------------------------------------
# Palette-derived defaults (single source of truth)
# ----------------------------------------------------------------------
_ANSI16 = create_ansi_16_palette()

DEFAULT_FG = _ANSI16.index_to_rgb(7)  # light gray
DEFAULT_BG = _ANSI16.index_to_rgb(0)  # black

class frameBuffer():
    """
    Lossless, document-oriented screen buffer.

    - Width is fixed unless explicitly resized.
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

    @classmethod
    def extend(cls, instance):
        """
        Dynamically extends an existing instance with this mixin class.
        """
        base_class = instance.__class__
        if issubclass(base_class, cls):
            return instance
        new_class_name = f"{cls.__name__}ed{base_class.__name__}"
        ExtendedClass = type(new_class_name, (cls, base_class), {})
        instance.__class__ = ExtendedClass
        return instance

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _ensure_row(self, y: int) -> None:
        """Ensure row y exists and is allocated to the current width."""
        while y >= len(self.rows):
            self.rows.append([Cell(
                char=None,
                fg=self.current_fg,
                bg=self.current_bg,
                attrs=self.current_attrs,
            ) for _ in range(self.width)])

    def _ensure_columns(self, row_idx: int, target_width: int) -> None:
        """Ensure a specific row matches the target width by expanding or truncating."""
        row = self.rows[row_idx]
        current_len = len(row)
        if current_len < target_width:
            # Pad missing cells up to target_width
            row.extend(Cell(
                char=None,
                fg=self.current_fg,
                bg=self.current_bg,
                attrs=self.current_attrs,
            ) for _ in range(target_width - current_len))
        elif current_len > target_width:
            # Truncate excess cells down to target_width
            del row[target_width:]

    def _clamp_x(self, x: int) -> int:
        return max(0, min(self.width - 1, x))

    def resize(self, width: int, height: int) -> None:
        """Resize the framebuffer grid to the specified width and height."""
        # 1. Handle height structural changes
        if height > 0:
            if height < len(self.rows):
                del self.rows[height+1:]
            else:
                self._ensure_row(height)
        # 2. Update width tracking and normalize all existing rows
        if width > 0:
            self.width = width
            for y in range(len(self.rows)):
                self._ensure_columns(y, width)

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

    def set_cell(self, x: int, y: int, cell: Cell|None) -> None:
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

    def new_line(self) -> None:
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
                self.new_line()
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

