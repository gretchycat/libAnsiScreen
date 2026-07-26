# libansiscreen/framebuffer.py

from typing import Any, Dict, List, Optional, Iterator
from .cell import Cell
from .cursor import Cursor
from .color.rgb import Color
from .color.palette import create_ansi_16_palette
from .binary_cell import (
    CELL_SIZE,
    pack_cell,
    unpack_cell,
    pack_cell_fields,
    IMAGE_FLAG,
    CODEPOINT_MASK,
)
from .image import ImageRegistry, ImageEntry

# ----------------------------------------------------------------------
# Palette-derived defaults (single source of truth)
# ----------------------------------------------------------------------
_ANSI16 = create_ansi_16_palette()

DEFAULT_FG = _ANSI16.index_to_rgb(7)  # light gray
DEFAULT_BG = _ANSI16.index_to_rgb(0)  # black


# ----------------------------------------------------------------------
# Transparent Proxy Classes for fb.rows backward compatibility
# ----------------------------------------------------------------------
class CellProxy:
    """
    Proxy object wrapping a cell position in a frameBuffer.
    Attribute reads and writes dynamically synchronize with the binary buffer.
    """

    def __init__(self, fb: "frameBuffer", x: int, y: int) -> None:
        object.__setattr__(self, "_fb", fb)
        object.__setattr__(self, "_x", x)
        object.__setattr__(self, "_y", y)

    @property
    def char(self) -> Optional[str]:
        c = self._fb.get_cell(self._x, self._y)
        return c.char if c else None

    @char.setter
    def char(self, value: Optional[str]) -> None:
        c = self._fb.get_cell(self._x, self._y) or Cell()
        c.char = value
        self._fb.set_cell(self._x, self._y, c)

    @property
    def fg(self) -> Optional[Color]:
        c = self._fb.get_cell(self._x, self._y)
        return c.fg if c else None

    @fg.setter
    def fg(self, value: Optional[Color]) -> None:
        c = self._fb.get_cell(self._x, self._y) or Cell()
        c.fg = value
        self._fb.set_cell(self._x, self._y, c)

    @property
    def bg(self) -> Optional[Color]:
        c = self._fb.get_cell(self._x, self._y)
        return c.bg if c else None

    @bg.setter
    def bg(self, value: Optional[Color]) -> None:
        c = self._fb.get_cell(self._x, self._y) or Cell()
        c.bg = value
        self._fb.set_cell(self._x, self._y, c)

    @property
    def attrs(self) -> int:
        c = self._fb.get_cell(self._x, self._y)
        return c.attrs if c else 0

    @attrs.setter
    def attrs(self, value: int) -> None:
        c = self._fb.get_cell(self._x, self._y) or Cell()
        c.attrs = value
        self._fb.set_cell(self._x, self._y, c)

    def copy(self) -> Cell:
        c = self._fb.get_cell(self._x, self._y)
        return c.copy() if c else Cell()

    def __getattr__(self, name: str) -> Any:
        c = self._fb.get_cell(self._x, self._y) or Cell()
        return getattr(c, name)

    def __setattr__(self, name: str, value: Any) -> None:
        if name in ("_fb", "_x", "_y"):
            object.__setattr__(self, name, value)
            return
        c = self._fb.get_cell(self._x, self._y) or Cell()
        setattr(c, name, value)
        self._fb.set_cell(self._x, self._y, c)

    def __repr__(self) -> str:
        c = self._fb.get_cell(self._x, self._y)
        return repr(c) if c else "Cell(char=None, fg=None, bg=None, attrs=0)"

    def __eq__(self, other: object) -> bool:
        c = self._fb.get_cell(self._x, self._y)
        if c is None:
            c = Cell()
        if isinstance(other, CellProxy):
            other = self._fb.get_cell(other._x, other._y) or Cell()
        return c == other


class RowProxy:
    """
    Proxy representing a single row in frameBuffer.
    """

    def __init__(self, fb: "frameBuffer", y: int) -> None:
        self._fb = fb
        self._y = y

    def __getitem__(self, x: int) -> CellProxy:
        return CellProxy(self._fb, x, self._y)

    def __setitem__(self, x: int, cell: Optional[Cell]) -> None:
        self._fb.set_cell(x, self._y, cell)

    def __len__(self) -> int:
        return self._fb.width

    def __iter__(self) -> Iterator[CellProxy]:
        for x in range(self._fb.width):
            yield self[x]

    def __repr__(self) -> str:
        return repr([self[x] for x in range(self._fb.width)])


class RowsProxy:
    """
    Proxy representing fb.rows (2D grid).
    Synchronizes direct indexed mutations with binary buffer.
    """

    def __init__(self, fb: "frameBuffer") -> None:
        self._fb = fb

    def __getitem__(self, y: int) -> RowProxy:
        return RowProxy(self._fb, y)

    def __setitem__(self, y: int, row_cells: List[Optional[Cell]]) -> None:
        self._fb._ensure_row(y)
        for x, cell in enumerate(row_cells):
            if x < self._fb.width:
                self._fb.set_cell(x, y, cell)

    def __len__(self) -> int:
        return self._fb.height

    def __iter__(self) -> Iterator[RowProxy]:
        for y in range(self._fb.height):
            yield RowProxy(self._fb, y)

    def clear(self) -> None:
        self._fb.cls()

    def append(self, row_cells: List[Optional[Cell]]) -> None:
        y = self._fb.height
        self._fb._ensure_row(y)
        for x, cell in enumerate(row_cells):
            if x < self._fb.width:
                self._fb.set_cell(x, y, cell)


class frameBuffer:
    """
    Lossless, document-oriented screen buffer using a high-performance
    binary memory buffer (16-byte packed cell struct).

    - Width is fixed unless explicitly resized.
    - Height grows dynamically via binary buffer expansion.
    - Cursor represents logical write position.
    - Graphics state (colors + attributes) is explicit.
    - Integrated ImageRegistry for Kitty, Sixel, and iTerm2 graphics.
    """

    # ------------------------------------------------------------------
    # Construction
    # ------------------------------------------------------------------
    def __init__(self, width: int, height: int = 1) -> None:
        if width <= 0:
            raise ValueError("Screen width must be > 0")
        self.width: int = width
        self.cursor: Cursor = Cursor()

        # Current graphics state (SGR-like)
        self.current_fg: Optional[Color] = DEFAULT_FG
        self.current_bg: Optional[Color] = DEFAULT_BG
        self.current_attrs: int = 0

        # Binary buffer storage
        self.buffer: bytearray = bytearray()
        self._allocated_rows: int = 0

        # Image Registry for Terminal Graphics (Kitty, Sixel, etc.)
        self.image_registry: ImageRegistry = ImageRegistry()

        self._ensure_row(height - 1)

    # ------------------------------------------------------------------
    # Properties & Backward Compatibility Adapters
    # ------------------------------------------------------------------

    @property
    def height(self) -> int:
        """Logical height of the screen in rows."""
        return self._allocated_rows

    @property
    def rows(self) -> RowsProxy:
        """
        Backward-compatibility property returning a proxy object for 2D cell grid.
        Mutations to rows[y][x] or rows[y][x].char update self.buffer directly.
        """
        return RowsProxy(self)

    @classmethod
    def extend(cls, instance: Any) -> Any:
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
    # Internal Binary Memory Helpers
    # ------------------------------------------------------------------
    def _cell_offset(self, x: int, y: int) -> int:
        return (y * self.width + x) * CELL_SIZE

    def _ensure_row(self, y: int) -> None:
        """Ensure row y exists in binary buffer."""
        if y >= self._allocated_rows:
            target_rows = y + 1
            additional_rows = target_rows - self._allocated_rows

            default_cell = Cell(
                char=None,
                fg=self.current_fg,
                bg=self.current_bg,
                attrs=self.current_attrs,
            )
            default_cell_bytes = bytearray(CELL_SIZE)
            pack_cell(default_cell_bytes, 0, default_cell)

            self.buffer.extend(bytes(default_cell_bytes) * (additional_rows * self.width))
            self._allocated_rows = target_rows

    def _clamp_x(self, x: int) -> int:
        return max(0, min(self.width - 1, x))

    def resize(self, width: int, height: int) -> None:
        """Resize the binary framebuffer grid."""
        if height > 0:
            if height < self._allocated_rows:
                del self.buffer[height * self.width * CELL_SIZE :]
                self._allocated_rows = height
            else:
                self._ensure_row(height - 1)

        if width > 0 and width != self.width:
            old_width = self.width
            old_rows = self._allocated_rows
            old_buffer = bytes(self.buffer)

            self.width = width
            self.buffer = bytearray()
            self._allocated_rows = 0
            self._ensure_row(old_rows - 1)

            copy_cols = min(old_width, width)
            for y in range(old_rows):
                src_offset = (y * old_width) * CELL_SIZE
                dst_offset = (y * width) * CELL_SIZE
                self.buffer[dst_offset : dst_offset + copy_cols * CELL_SIZE] = old_buffer[
                    src_offset : src_offset + copy_cols * CELL_SIZE
                ]

    # ------------------------------------------------------------------
    # Cell Access
    # ------------------------------------------------------------------
    def get_cell(self, x: int, y: int) -> Optional[Cell]:
        self._ensure_row(y)
        if y < 0 or y >= self._allocated_rows:
            return None
        if x < 0 or x >= self.width:
            return None
        return unpack_cell(self.buffer, self._cell_offset(x, y))

    def set_cell(self, x: int, y: int, cell: Optional[Cell]) -> None:
        if x < 0 or x >= self.width:
            return
        self._ensure_row(y)
        pack_cell(self.buffer, self._cell_offset(x, y), cell)

    def put_cell(
        self,
        x: int,
        y: int,
        *,
        char: Optional[str] = None,
        fg: Optional[Color] = None,
        bg: Optional[Color] = None,
        attrs: int = 0,
    ) -> None:
        self.set_cell(
            x,
            y,
            Cell(
                char=char,
                fg=fg,
                bg=bg,
                attrs=attrs,
            ),
        )

    # ------------------------------------------------------------------
    # Terminal Graphics & Image Handles (Kitty, Sixel, iTerm2)
    # ------------------------------------------------------------------
    def put_image(
        self,
        x: int,
        y: int,
        image: Any,
        width_cells: int = 1,
        height_cells: int = 1,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> int:
        """
        Registers an image in the image registry and stamps its Image ID
        into the cell buffer across the specified grid region.
        """
        img_id = self.image_registry.register(
            image, width_cells=width_cells, height_cells=height_cells, metadata=metadata
        )
        for ry in range(height_cells):
            for rx in range(width_cells):
                target_x = x + rx
                target_y = y + ry
                if 0 <= target_x < self.width:
                    self._ensure_row(target_y)
                    offset = self._cell_offset(target_x, target_y)
                    tile_info = (ry << 8) | rx
                    pack_cell_fields(
                        self.buffer,
                        offset,
                        codepoint_or_imgid=IMAGE_FLAG | img_id,
                        tile_info=tile_info,
                    )
        return img_id

    # ------------------------------------------------------------------
    # Cursor Control (ANSI Semantics)
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
    # Line / Carriage Control
    # ------------------------------------------------------------------
    def carriage_return(self) -> None:
        self.cursor.x = 0

    def line_feed(self) -> None:
        self.cursor.y += 1

    def new_line(self) -> None:
        self.cursor.x = 0
        self.cursor.y += 1

    # ------------------------------------------------------------------
    # Graphics State (SGR-like)
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
    # Writing Operations
    # ------------------------------------------------------------------
    def put_char(self, char: str) -> None:
        if len(char) != 1:
            raise ValueError("put_char expects a single character: " + str(char))
        self._ensure_row(self.cursor.y)
        offset = self._cell_offset(self.cursor.x, self.cursor.y)

        fg_r, fg_g, fg_b, fg_set = 0, 0, 0, False
        if self.current_fg is not None:
            fg_r, fg_g, fg_b, fg_set = self.current_fg.r, self.current_fg.g, self.current_fg.b, True

        bg_r, bg_g, bg_b, bg_set = 0, 0, 0, False
        if self.current_bg is not None:
            bg_r, bg_g, bg_b, bg_set = self.current_bg.r, self.current_bg.g, self.current_bg.b, True

        pack_cell_fields(
            self.buffer,
            offset,
            codepoint_or_imgid=ord(char),
            fg_r=fg_r,
            fg_g=fg_g,
            fg_b=fg_b,
            fg_set=fg_set,
            bg_r=bg_r,
            bg_g=bg_g,
            bg_b=bg_b,
            bg_set=bg_set,
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

    def __repr__(self) -> str:
        return f"frameBuffer ({self.width}, {self.height})"

    # ------------------------------------------------------------------
    # Clearing Operations
    # ------------------------------------------------------------------
    def cls(self) -> None:
        """
        Trims down buffer rows, resets cursor to (0,0), and sets each cell
        in the buffer to a space (' ') with current fg, bg, and attrs.
        """
        old_height = max(1, self._allocated_rows)
        self.buffer.clear()
        self.cursor.reset()
        self._allocated_rows = 0

        space_cell = Cell(
            char=" ",
            fg=self.current_fg,
            bg=self.current_bg,
            attrs=self.current_attrs,
        )
        space_cell_bytes = bytearray(CELL_SIZE)
        pack_cell(space_cell_bytes, 0, space_cell)

        self.buffer.extend(bytes(space_cell_bytes) * (old_height * self.width))
        self._allocated_rows = old_height

    def clear_row(self, y: int) -> None:
        self._ensure_row(y)
        offset = self._cell_offset(0, y)
        self.buffer[offset : offset + self.width * CELL_SIZE] = bytes(self.width * CELL_SIZE)

    def clear_to_end_of_line(self) -> None:
        self._ensure_row(self.cursor.y)
        space_cp = ord(" ")

        fg_r, fg_g, fg_b, fg_set = 0, 0, 0, False
        if self.current_fg is not None:
            fg_r, fg_g, fg_b, fg_set = self.current_fg.r, self.current_fg.g, self.current_fg.b, True

        bg_r, bg_g, bg_b, bg_set = 0, 0, 0, False
        if self.current_bg is not None:
            bg_r, bg_g, bg_b, bg_set = self.current_bg.r, self.current_bg.g, self.current_bg.b, True

        for x in range(self.cursor.x, self.width):
            offset = self._cell_offset(x, self.cursor.y)
            pack_cell_fields(
                self.buffer,
                offset,
                codepoint_or_imgid=space_cp,
                fg_r=fg_r,
                fg_g=fg_g,
                fg_b=fg_b,
                fg_set=fg_set,
                bg_r=bg_r,
                bg_g=bg_g,
                bg_b=bg_b,
                bg_set=bg_set,
                attrs=self.current_attrs,
            )

    def clear_to_end_of_screen(self) -> None:
        self.clear_to_end_of_line()
        for y in range(self.cursor.y + 1, self._allocated_rows):
            self.clear_row(y)

    # ------------------------------------------------------------------
    # Color Shift Utilities
    # ------------------------------------------------------------------
    def shift_hsv(self, h: float, s: float, v: float) -> None:
        for y in range(self._allocated_rows):
            for x in range(self.width):
                cell = self.get_cell(x, y)
                if cell:
                    cell.shift_hsv(h, s, v)
                    self.set_cell(x, y, cell)

    def shift_rgb(self, r: int, g: int, b: int) -> None:
        for y in range(self._allocated_rows):
            for x in range(self.width):
                cell = self.get_cell(x, y)
                if cell:
                    cell.shift_rgb(r, g, b)
                    self.set_cell(x, y, cell)
