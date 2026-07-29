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
from .image import ImageRegistry, ImageEntry, load_image

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
    Lossless, document-oriented screen buffer.

    - Defaults to object-based storage (list of lists of Cell objects) for maximum performance.
    - Optional binary mode (`use_binary=True`) using packed cell structs for testing/benchmarking.
    - Width is fixed unless explicitly resized.
    - Height grows dynamically.
    - Cursor represents logical write position.
    - Graphics state (colors + attributes) is explicit.
    - Integrated ImageRegistry for Kitty, Sixel, and iTerm2 graphics.
    """

    # ------------------------------------------------------------------
    # Construction
    # ------------------------------------------------------------------
    def __init__(self, width: int, height: int = 1, use_binary: bool = False) -> None:
        if width <= 0:
            raise ValueError("Screen width must be > 0")
        self.width: int = width
        self.use_binary: bool = use_binary
        self.cursor: Cursor = Cursor()

        # Current graphics state (SGR-like)
        self.current_fg: Optional[Color] = DEFAULT_FG
        self.current_bg: Optional[Color] = DEFAULT_BG
        self.current_attrs: int = 0
        self._pending_wrap: bool = False

        # Image Registry for Terminal Graphics (Kitty, Sixel, etc.)
        self.image_registry: ImageRegistry = ImageRegistry()

        if self.use_binary:
            self._buffer: bytearray = bytearray()
            self._allocated_rows: int = 0
        else:
            self._rows: List[List[Optional[Cell]]] = []

        self._ensure_row(height - 1)

    # ------------------------------------------------------------------
    # Properties & Backward Compatibility Adapters
    # ------------------------------------------------------------------

    @property
    def height(self) -> int:
        """Logical height of the screen in rows."""
        if self.use_binary:
            return self._allocated_rows
        return len(self._rows)

    @property
    def rows(self) -> Any:
        """
        Returns 2D grid of cells.
        When use_binary is False, returns list of lists of Cell objects directly for maximum performance.
        When use_binary is True, returns RowsProxy object to synchronize with binary buffer.
        """
        if self.use_binary:
            return RowsProxy(self)
        return self._rows

    @property
    def buffer(self) -> bytearray:
        """
        Binary bytearray buffer.
        Returns the internal bytearray when use_binary is True, or dynamically packs
        self._rows into a bytearray when use_binary is False.
        """
        if self.use_binary:
            return self._buffer
        buf = bytearray(self.height * self.width * CELL_SIZE)
        for y, row in enumerate(self._rows):
            for x, cell in enumerate(row):
                if cell is not None:
                    pack_cell(buf, (y * self.width + x) * CELL_SIZE, cell)
        return buf

    @buffer.setter
    def buffer(self, val: bytearray) -> None:
        if self.use_binary:
            self._buffer = val
            self._allocated_rows = len(val) // (self.width * CELL_SIZE) if self.width > 0 else 0
        else:
            rows_count = len(val) // (self.width * CELL_SIZE) if self.width > 0 else 0
            self._rows = []
            for y in range(rows_count):
                row = []
                for x in range(self.width):
                    offset = (y * self.width + x) * CELL_SIZE
                    cell = unpack_cell(val, offset)
                    row.append(cell)
                self._rows.append(row)

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
    # Internal Memory Helpers
    # ------------------------------------------------------------------
    def _cell_offset(self, x: int, y: int) -> int:
        return (y * self.width + x) * CELL_SIZE

    def _ensure_row(self, y: int) -> None:
        """Ensure row y exists in buffer."""
        if self.use_binary:
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

                self._buffer.extend(bytes(default_cell_bytes) * (additional_rows * self.width))
                self._allocated_rows = target_rows
        else:
            tpl = Cell(
                char=None,
                fg=self.current_fg,
                bg=self.current_bg,
                attrs=self.current_attrs,
            )
            while len(self._rows) <= y:
                row = [tpl.copy() for _ in range(self.width)]
                self._rows.append(row)

    def _clamp_x(self, x: int) -> int:
        return max(0, min(self.width - 1, x))

    def resize(self, width: int, height: int) -> None:
        """Resize the framebuffer grid."""
        if self.use_binary:
            if height > 0:
                if height < self._allocated_rows:
                    del self._buffer[height * self.width * CELL_SIZE :]
                    self._allocated_rows = height
                else:
                    self._ensure_row(height - 1)

            if width > 0 and width != self.width:
                old_width = self.width
                old_rows = self._allocated_rows
                old_buffer = bytes(self._buffer)

                self.width = width
                self._buffer = bytearray()
                self._allocated_rows = 0
                self._ensure_row(old_rows - 1)

                copy_cols = min(old_width, width)
                for y in range(old_rows):
                    src_offset = (y * old_width) * CELL_SIZE
                    dst_offset = (y * width) * CELL_SIZE
                    self._buffer[dst_offset : dst_offset + copy_cols * CELL_SIZE] = old_buffer[
                        src_offset : src_offset + copy_cols * CELL_SIZE
                    ]
        else:
            if width > 0 and width != self.width:
                old_width = self.width
                self.width = width
                diff = width - old_width
                if diff > 0:
                    tpl = Cell(
                        char=None,
                        fg=self.current_fg,
                        bg=self.current_bg,
                        attrs=self.current_attrs,
                    )
                    row_add = [tpl.copy() for _ in range(diff)]
                    for y in range(len(self._rows)):
                        self._rows[y].extend([c.copy() for c in row_add])
                else:
                    for y in range(len(self._rows)):
                        del self._rows[y][width:]

            if height > 0:
                if height < len(self._rows):
                    del self._rows[height:]
                else:
                    self._ensure_row(height - 1)

    # ------------------------------------------------------------------
    # Cell Access
    # ------------------------------------------------------------------
    def get_cell(self, x: int, y: int) -> Optional[Cell]:
        if x < 0 or x >= self.width or y < 0:
            return None
        self._ensure_row(y)
        if self.use_binary:
            if y >= self._allocated_rows:
                return None
            cell = unpack_cell(self._buffer, self._cell_offset(x, y))
        else:
            if y >= len(self._rows):
                return None
            cell = self._rows[y][x]
        if cell is not None and isinstance(cell.image, int):
            cell.image = self.image_registry.get(cell.image)
        return cell

    def set_cell(self, x: int, y: int, cell: Optional[Cell]) -> None:
        if x < 0 or x >= self.width or y < 0:
            return
        self._ensure_row(y)
        if cell is not None and cell.image is not None and not isinstance(cell.image, (int, ImageEntry)):
            img_id = self.image_registry.register(cell.image)
            cell = cell.copy()
            cell.image = self.image_registry.get(img_id)
        if self.use_binary:
            pack_cell(self._buffer, self._cell_offset(x, y), cell)
        else:
            self._rows[y][x] = cell

    def put_cell(
        self,
        x: int,
        y: int,
        *,
        char: Optional[str] = None,
        fg: Optional[Color] = None,
        bg: Optional[Color] = None,
        attrs: int = 0,
        image: Optional[Any] = None,
    ) -> None:
        self.set_cell(
            x,
            y,
            Cell(
                char=char,
                fg=Color.set(fg),
                bg=Color.set(bg),
                attrs=attrs,
                image=image,
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
        cell_pixel_size: tuple[int, int] = (8, 16),
    ) -> int:
        """
        Loads and resizes an image to fit into width_cells x height_cells.
        Stamps the image into the framebuffer across the specified grid region.
        """
        loaded_img = load_image(image, width_cells=width_cells, height_cells=height_cells, cell_pixel_size=cell_pixel_size)
        img_id = self.image_registry.register(
            loaded_img, width_cells=width_cells, height_cells=height_cells, metadata=metadata
        )
        img_entry = self.image_registry.get(img_id)
        for ry in range(height_cells):
            for rx in range(width_cells):
                target_x = x + rx
                target_y = y + ry
                if 0 <= target_x < self.width:
                    self._ensure_row(target_y)
                    if self.use_binary:
                        offset = self._cell_offset(target_x, target_y)
                        tile_info = (ry << 8) | rx
                        pack_cell_fields(
                            self._buffer,
                            offset,
                            codepoint_or_imgid=IMAGE_FLAG | img_id,
                            tile_info=tile_info,
                        )
                    else:
                        self.set_cell(target_x, target_y, Cell(image=img_entry, tile_x=rx, tile_y=ry))
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
        self._pending_wrap = False
        self.cursor.x = 0

    def line_feed(self) -> None:
        if self._pending_wrap:
            self._pending_wrap = False
            self.cursor.x = 0
            self.cursor.y += 1
        else:
            self.cursor.y += 1

    def new_line(self) -> None:
        self._pending_wrap = False
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
    def put_char(self, char: str, raw=False) -> None:
        def cp437_char(char:str) -> str:
            if len(char) != 1:
                raise ValueError("put_char expects a single character: " + str(char))
            CP437_LOW_GRAPHICS = [
                " ",
                "☺",
                "☻",
                "♥",
                "♦",
                "♣",
                "♠",
                "•",
                "◘",
                "○",
                "◙",
                "♂",
                "♀",
                "♪",
                "♫",
                "☼",
                "►",
                "◄",
                "↕",
                "‼",
                "¶",
                "§",
                "▬",
                "↨",
                "↑",
                "↓",
                "→",
                "←",
                "∟",
                "↔",
                "▲",
                "▼",
            ]
            i=ord(char)
            if i<32:
                char=CP437_LOW_GRAPHICS[i]
            if i==127:
                char="⌂"
            return char
        if len(char) != 1:
            raise ValueError("put_char expects a single character: " + str(char))

        if self._pending_wrap:
            self._pending_wrap = False
            self.cursor.x = 0
            self.cursor.y += 1

        self._ensure_row(self.cursor.y)

        if self.use_binary:
            offset = self._cell_offset(self.cursor.x, self.cursor.y)

            fg_r, fg_g, fg_b, fg_set = 0, 0, 0, False
            if self.current_fg is not None:
                fg_r, fg_g, fg_b, fg_set = self.current_fg.r, self.current_fg.g, self.current_fg.b, True

            bg_r, bg_g, bg_b, bg_set = 0, 0, 0, False
            if self.current_bg is not None:
                bg_r, bg_g, bg_b, bg_set = self.current_bg.r, self.current_bg.g, self.current_bg.b, True

            pack_cell_fields(
                self._buffer,
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
        else:
            if not raw:
                cell = Cell(
                    char=char,
                    fg=self.current_fg,
                    bg=self.current_bg,
                    attrs=self.current_attrs,
                )
                self._rows[self.cursor.y][self.cursor.x] = cell
            else:
                c=self._rows[self.cursor.y][self.cursor.x]
                if not c:
                    c=Cell()
                c.char=cp437_char(char)
                self._rows[self.cursor.y][self.cursor.x] = c

        self._advance_cursor()

    def put_text(self, text: str, raw=False) -> None:
        for ch in text:
            if ch == "\n" and not raw:
                self.new_line()
            elif ch == "\r" and not raw:
                self.carriage_return()
            else:
                self.put_char(ch,raw=raw)

    def _advance_cursor(self) -> None:
        self.cursor.x += 1
        if self.cursor.x >= self.width:
            self.cursor.x = self.width - 1
            self._pending_wrap = True

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
        old_height = max(1, self.height)
        self.cursor.reset()
        if self.use_binary:
            self._buffer.clear()
            self._allocated_rows = 0

            space_cell = Cell(
                char=" ",
                fg=self.current_fg,
                bg=self.current_bg,
                attrs=self.current_attrs,
            )
            space_cell_bytes = bytearray(CELL_SIZE)
            pack_cell(space_cell_bytes, 0, space_cell)

            self._buffer.extend(bytes(space_cell_bytes) * (old_height * self.width))
            self._allocated_rows = old_height
        else:
            self._rows = [
                [
                    Cell(
                        char=" ",
                        fg=self.current_fg,
                        bg=self.current_bg,
                        attrs=self.current_attrs,
                    )
                    for _ in range(self.width)
                ]
                for _ in range(old_height)
            ]

    def clear_row(self, y: int) -> None:
        self._ensure_row(y)
        if self.use_binary:
            offset = self._cell_offset(0, y)
            self._buffer[offset : offset + self.width * CELL_SIZE] = bytes(self.width * CELL_SIZE)
        else:
            self._rows[y] = [Cell() for _ in range(self.width)]

    def clear_to_end_of_line(self) -> None:
        self._ensure_row(self.cursor.y)
        if self.use_binary:
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
                    self._buffer,
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
        else:
            for x in range(self.cursor.x, self.width):
                self._rows[self.cursor.y][x] = Cell(
                    char=" ",
                    fg=self.current_fg,
                    bg=self.current_bg,
                    attrs=self.current_attrs,
                )

    def clear_to_end_of_screen(self) -> None:
        self.clear_to_end_of_line()
        for y in range(self.cursor.y + 1, self.height):
            self.clear_row(y)

    # ------------------------------------------------------------------
    # Color Shift Utilities
    # ------------------------------------------------------------------
    def shift_hsv(self, h: float, s: float, v: float) -> None:
        for y in range(self.height):
            for x in range(self.width):
                cell = self.get_cell(x, y)
                if cell:
                    cell.shift_hsv(h, s, v)
                    self.set_cell(x, y, cell)

    def shift_rgb(self, r: int, g: int, b: int) -> None:
        for y in range(self.height):
            for x in range(self.width):
                cell = self.get_cell(x, y)
                if cell:
                    cell.shift_rgb(r, g, b)
                    self.set_cell(x, y, cell)

