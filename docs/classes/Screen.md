# Class: Screen

## Description
The `Screen` class is the central, document-oriented virtual terminal screen buffer for `libAnsiScreen`. It inherits from `Colorize` and `frameBuffer`, combining:
- **Framebuffer Storage (`frameBuffer`):** Cell storage, color/attribute graphics state, and cursor tracking.
- **Color Gradients & Tinting (`Colorize`):** Advanced gradient fills, tinting, HSV/RGB color shifts.
- **ANSI Stream Parsing (`ANSIParser`):** State-machine parsing of ANSI escape sequences into buffer cells.
- **Optimized Output Emitter (`ANSIEmitter`):** Differential and state-aware ANSI escape string rendering.
- **Clip & Clipboard Operations:** Region copying, clearing, cutting, pasting, and tiling.
- **Half-Block Pixel Graphics (`pixel_*`):** 1x2 subpixel color drawing using half-block glyphs (`▀`, `▄`, `█`).
- **Monochrome Subpixel Graphics (`spixel_*`):** High-resolution drawing via quadrant (2x2), octant (2x4), or braille (2x4) subpixels.
- **Universal Drawing Dispatchers:** Mode-agnostic drawing methods dispatching to half-block or subpixel renderers.
- **Full-Block Character Primitives (`char_*`):** Full-cell shape rendering (`█`) and screen stamping.

---

## Class Hierarchy
`Screen` -> `Colorize` -> `frameBuffer`

---

## Constructor (`__init__`)

```python
Screen(width: int, height: int = 1)
```

| Parameter | Type | Default | Description |
|---|---|---|---|
| `width` | `int` | *Required* | Fixed screen width in character columns (> 0). |
| `height` | `int` | `1` | Initial logical screen height in rows. |

**Raises:** `ValueError` if `width <= 0`.

---

## Attributes & Properties

| Attribute / Property | Type | Description |
|---|---|---|
| `width` | `int` | Fixed screen width in character columns. |
| `height` | `int` | Current logical screen height in character rows. |
| `cursor` | `Cursor` | Logical write position tracker (`x`, `y`) and position save/restore state. |
| `rows` | `List[List[Cell]]` | 2D cell grid (`rows[y][x]`). |
| `parser` | `ANSIParser` | ANSI parser instance bound to this screen buffer. |
| `emitter` | `ANSIEmitter` | ANSI emitter instance for rendering buffer contents to strings. |
| `current_fg` | `Color` | Active SGR foreground color applied to new writes. |
| `current_bg` | `Color` | Active SGR background color applied to new writes. |
| `current_attrs` | `int` | Active text attribute bitmask (e.g., `ATTR_BOLD`). |

---

## Methods

### 1. ANSI I/O

#### `feed(s: Union[str, bytes]) -> None`
Feeds ANSI-encoded text or raw bytes into the screen's parser, updating cells, cursor position, and graphics state.

#### `print(s: Union[str, bytes]) -> None`
Alias for `feed()`. Parses ANSI text into the screen buffer.

#### `emit(box: Optional[Tuple[int, int, int, int]] = None, raw: bool = False) -> str`
Renders the entire screen (or a sub-region `box=(x, y, w, h)`) to an optimized ANSI escape sequence string.

#### `emit_diff(prev: frameBuffer, box: Optional[Tuple[int, int, int, int]] = None, raw: bool = False) -> str`
Renders only the changed cells between this screen and a previous framebuffer frame `prev`.

---

### 2. Cursor Control (ANSI Semantics)

#### `cursor_goto(x: int, y: int) -> None`
Moves the cursor to `(x, y)`, clamping `x` within `[0, width - 1]` and `y >= 0`.

#### `cursor_up(n: int = 1) -> None`
Moves the cursor up by `n` rows (clamped to `y = 0`).

#### `cursor_down(n: int = 1) -> None`
Moves the cursor down by `n` rows.

#### `cursor_forward(n: int = 1) -> None`
Moves the cursor right by `n` columns (clamped to `width - 1`).

#### `cursor_back(n: int = 1) -> None`
Moves the cursor left by `n` columns (clamped to `x = 0`).

#### `cursor_next_line(n: int = 1) -> None`
Moves cursor to column 0 of `n` rows down.

#### `cursor_prev_line(n: int = 1) -> None`
Moves cursor to column 0 of `n` rows up.

#### `cursor_set_column(x: int) -> None`
Sets cursor horizontal column `x`.

#### `cursor_save() -> None`
Saves current cursor position `(x, y)`.

#### `cursor_restore() -> None`
Restores previously saved cursor position.

#### `carriage_return() -> None`
Sets cursor `x = 0`.

#### `line_feed() -> None`
Increments cursor `y += 1`.

#### `new_line() -> None`
Resets cursor `x = 0` and increments `y += 1`.

---

### 3. Graphics State (SGR)

#### `set_foreground(color: Color) -> None`
Sets current foreground color for future character writes.

#### `set_background(color: Color) -> None`
Sets current background color for future character writes.

#### `set_attrs(attrs: int) -> None`
Sets text attribute bitmask (e.g., `ATTR_BOLD | ATTR_UNDERLINE`).

#### `add_attrs(attrs: int) -> None`
Enables specific attribute bits without clearing existing attributes.

#### `clear_attrs(attrs: int) -> None`
Disables specific attribute bits.

#### `reset_graphics() -> None`
Resets foreground, background, and attributes to library ANSI defaults.

---

### 4. Writing & Cell Access

#### `put_char(char: str) -> None`
Writes a single character at current cursor position and advances cursor.

#### `put_text(text: str) -> None`
Writes text string, processing newlines (`\n`) and carriage returns (`\r`).

#### `get_cell(x: int, y: int) -> Optional[Cell]`
Returns the cell at `(x, y)`, or `None` if out of bounds.

#### `set_cell(x: int, y: int, cell: Optional[Cell]) -> None`
Sets cell at `(x, y)` to a copy of `cell`.

#### `put_cell(x: int, y: int, *, char=None, fg=None, bg=None, attrs=0) -> None`
Creates and assigns a new cell at `(x, y)`.

#### `resize(width: int, height: int) -> None`
Resizes screen grid width and height.

#### `cls() -> None`
Clears screen rows and resets cursor position.

#### `clear_row(y: int) -> None`
Clears all cells in row `y`.

#### `clear_to_end_of_line() -> None`
Fills cells from cursor position to end of line with spaces.

#### `clear_to_end_of_screen() -> None`
Clears from cursor position to bottom of screen.

---

### 5. Clip & Clipboard Operations

#### `copy(box: Optional[Tuple[int, int, int, int]] = None) -> frameBuffer`
Copies a rectangular region into a new `frameBuffer`.

#### `clear(box: Optional[Tuple[int, int, int, int]] = None) -> None`
Clears cells in a specified region or full screen.

#### `paste(src: frameBuffer, *, box: Optional[Tuple[int, int, int, int]] = None, transparent_char: Optional[Set[str]] = None, transparent_fg: bool = False, transparent_bg: bool = False, transparent_attrs: bool = False) -> None`
Pastes `src` framebuffer at target region `box=(x, y, w, h)` with transparency rules.

#### `cut(box: Optional[Tuple[int, int, int, int]] = None) -> frameBuffer`
Copies region to a new `frameBuffer` and clears source region.

#### `tile(tl: frameBuffer) -> None`
Tiles template framebuffer `tl` repeatedly across screen.

---

### 6. Colorization & Gradients (Inherited from `Colorize`)

#### `colorize(gradient: Iterable[Color], *, mode: str = "hgrad", foreground: bool = True, background: bool = False, only_if_set: bool = True, tint: Optional[float] = None, direction: str = "tlbr") -> None`
Applies a color gradient across screen cells. Modes: `"hgrad"`, `"vgrad"`, `"dgrad"`, `"words"`.

#### `shift_hsv(h: float, s: float, v: float) -> None`
Shifts all screen cell colors in HSV space.

#### `shift_rgb(r: int, g: int, b: int) -> None`
Shifts all screen cell colors in RGB space.

---

### 7. Half-Block Pixel Graphics (`pixel_*`)
Operates on half-block subpixel grid (2 vertical subpixels per character cell, where `y` coordinate is in half-rows).

- `pixel_plot(x: int, y: int, color: Color) -> None`
- `pixel_get(x: int, y: int) -> Optional[Color]`
- `pixel_line(x0: int, y0: int, x1: int, y1: int, color: Color) -> None`
- `pixel_polyline(points: Sequence[Tuple[int, int]], color: Color) -> None`
- `pixel_regular_polygon(cx: int, cy: int, radius: int, sides: int, color: Color, rotation: float = 0.0) -> None`
- `pixel_regular_star(cx: int, cy: int, radius: int, n: int, k: int, color: Color, rotation: float = 0.0) -> None`
- `pixel_flood_fill(x_seed: int, y_seed: int, fill: Optional[Color] = None) -> frameBuffer`
- `pixel_rectangle(x1: int, y1: int, x2: int, y2: int, fill: Optional[Color] = None) -> None`
- `pixel_ellipse(cx: int, cy: int, rx: int, ry: int, fill: Optional[Color] = None) -> None`

---

### 8. Subpixel Character Graphics (`spixel_*`)
Operates on high-resolution character subpixel grids (`mode` parameter accepts `'quadrant'`, `'octant'`, or `'braille'`).

- `spixel_plot(x: int, y: int, state: Any, mode: str = "octant") -> None`
- `spixel_get(x: int, y: int, mode: str = "octant") -> Any`
- `spixel_line(x0: int, y0: int, x1: int, y1: int, state: Any, mode: str = "octant") -> None`
- `spixel_polyline(points: Sequence[Tuple[int, int]], state: Any, mode: str = "octant") -> None`
- `spixel_regular_polygon(cx: int, cy: int, radius: int, sides: int, state: Any, rotation: float = 0.0, mode: str = "octant") -> None`
- `spixel_regular_star(cx: int, cy: int, radius: int, n: int, k: int, state: Any, rotation: float = 0.0, mode: str = "octant") -> None`
- `spixel_flood_fill(x_seed: int, y_seed: int, state: Any, mode: str = "octant") -> frameBuffer`
- `spixel_rectangle(x1: int, y1: int, x2: int, y2: int, state: Any, mode: str = "octant") -> None`
- `spixel_ellipse(cx: int, cy: int, rx: int, ry: int, state: Any, mode: str = "octant") -> None`

---

### 9. Universal Drawing Dispatchers
High-level drawing methods that automatically route to half-block mode when `mode` is `None` or `'half'`, or subpixel mode when `mode` is `'quadrant'`, `'octant'`, or `'braille'`.

- `plot(x: int, y: int, state: Any, mode: Optional[str] = None) -> None`
- `get(x: int, y: int, mode: Optional[str] = None) -> Any`
- `line(x0: int, y0: int, x1: int, y1: int, state: Any, mode: Optional[str] = None) -> None`
- `polyline(points: Sequence[Tuple[int, int]], state: Any, mode: Optional[str] = None) -> None`
- `regular_polygon(cx: int, cy: int, radius: int, sides: int, state: Any, rotation: float = 0.0, mode: Optional[str] = None) -> None`
- `regular_star(cx: int, cy: int, radius: int, n: int, k: int, state: Any, rotation: float = 0.0, mode: Optional[str] = None) -> None`
- `flood_fill(x_seed: int, y_seed: int, state: Any = None, mode: Optional[str] = None) -> frameBuffer`
- `rectangle(x1: int, y1: int, x2: int, y2: int, state: Any, mode: Optional[str] = None) -> None`
- `ellipse(cx: int, cy: int, rx: int, ry: int, state: Any, mode: Optional[str] = None) -> None`

---

### 10. Full-Block Character Primitives (`char_*`)
Operates directly on character cell blocks (`█`).

#### `char_flood_fill(x_seed: int, y_seed: int, ignore_fg_color: bool = False, ignore_bg_color: bool = False, fill: Optional[Color] = DEFAULT_FG) -> frameBuffer`
Full-character flood fill starting from seed cell `(x_seed, y_seed)`.

#### `char_rectangle(x1: int, y1: int, x2: int, y2: int, fill: Optional[Color] = None) -> frameBuffer`
Draws a filled rectangle using full-block characters (`█`).

#### `char_ellipse(cx: int, cy: int, rx: int, ry: int, fill: Optional[Color] = None) -> frameBuffer`
Draws a filled ellipse using full-block characters (`█`).

#### `stamp_from_screen(transparent_chars: Optional[Sequence[Optional[str]]] = None, box: Optional[Tuple[int, int, int, int]] = None, border_bg: Optional[Color] = None) -> frameBuffer`
Creates a stamp framebuffer from screen region with specified transparency and border color.

#### `char_tile(text: str) -> None`
Tiles multi-line text pattern across screen grid cells.
