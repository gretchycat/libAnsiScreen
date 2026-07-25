# Screen Operations (`screen_ops`)

The `screen_ops` package contains modular, high-level graphics and utility functions that operate on `frameBuffer` and `Screen` instances. While exposed as methods on the `Screen` class, these functions can also be imported and called independently.

---

## 1. Clipping and Pasting (`libansiscreen.screen_ops.clip`)

### `clear(screen: frameBuffer, box: Optional[Tuple[int, int, int, int]] = None) -> None`
Clears a rectangular region or the entire screen buffer. Resets cells to default state.

### `copy(screen: frameBuffer, box: Optional[Tuple[int, int, int, int]] = None) -> frameBuffer`
Copies a rectangular region into a new `frameBuffer` instance.

### `cut(screen: frameBuffer, box: Optional[Tuple[int, int, int, int]] = None) -> frameBuffer`
Copies a region to a new `frameBuffer` and clears the source region.

### `paste(dst: frameBuffer, src: frameBuffer, *, box: Optional[Tuple[int, int, int, int]] = None, transparent_char: Optional[Set[str]] = None, transparent_fg: bool = False, transparent_bg: bool = False, transparent_attrs: bool = False) -> None`
Pastes `src` framebuffer into `dst` with fine-grained transparency controls for characters, foreground color, background color, and text attributes.

### `tile(screen: frameBuffer, tl: frameBuffer) -> None`
Repeatedly tiles a template framebuffer `tl` across the full dimensions of `screen`.

---

## 2. Colorization & Gradients (`libansiscreen.screen_ops.colorize`)

The `Colorize` class provides gradient application and color manipulation algorithms.

### `colorize(screen: frameBuffer, gradient: Iterable[Color], *, mode: str = "hgrad", foreground: bool = True, background: bool = False, only_if_set: bool = True, tint: Optional[float] = None, direction: str = "tlbr") -> None`
Applies a color gradient across cells in the screen buffer.
- **Modes:**
  - `"hgrad"` / `"horizontal"`: Left to right horizontal gradient.
  - `"vgrad"` / `"vertical"`: Top to bottom vertical gradient.
  - `"dgrad"` / `"diagonal"`: Diagonal gradient (`direction="tlbr"` or `"trbl"`).
  - `"words"`: Applies color sequence word-by-word across non-space text.

---

## 3. Half-Block Pixel Graphics (`libansiscreen.screen_ops.pixel`)

Provides 1x2 subpixel color rendering using half-block Unicode characters (`▀`, `▄`, `█`). Vertical coordinates (`y`) are in half-character units (2 units per cell row).

- `pixel_plot(fb: frameBuffer, x: int, y: int, color: Color) -> None`
- `pixel_get(fb: frameBuffer, x: int, y: int) -> Optional[Color]`
- `pixel_line(fb: frameBuffer, x0: int, y0: int, x1: int, y1: int, color: Color) -> None`
- `pixel_polyline(fb: frameBuffer, points: Sequence[Tuple[int, int]], color: Color) -> None`
- `pixel_regular_polygon(fb: frameBuffer, cx: int, cy: int, radius: int, sides: int, color: Color, rotation: float = 0.0) -> None`
- `pixel_regular_star(fb: frameBuffer, cx: int, cy: int, radius: int, n: int, k: int, color: Color, rotation: float = 0.0) -> None`
- `pixel_flood_fill(fb: frameBuffer, x_seed: int, y_seed: int, fill: Optional[Color] = None) -> frameBuffer`
- `pixel_rectangle(fb: frameBuffer, x1: int, y1: int, x2: int, y2: int, fill: Optional[Color] = None) -> None`
- `pixel_ellipse(fb: frameBuffer, cx: int, cy: int, rx: int, ry: int, fill: Optional[Color] = None) -> None`

---

## 4. Subpixel Character Graphics (`libansiscreen.screen_ops.spixel`)

Provides high-resolution monochrome/character-subpixel drawing modes.

### Modes Supported:
- `"octant"`: 2x4 subpixel grid using Legacy Computing Block Octants (U+1CD00 range).
- `"braille"`: 2x4 subpixel grid using Unicode Braille Patterns (U+2800..U+28FF).
- `"quadrant"`: 2x2 subpixel grid using Block Elements (U+2580 range).

### Subpixel API Functions:
- `spixel_plot(fb: frameBuffer, x: int, y: int, state: Any, mode: str = "octant") -> None`
- `spixel_get(fb: frameBuffer, x: int, y: int, mode: str = "octant") -> Any`
- `spixel_line(fb: frameBuffer, x0: int, y0: int, x1: int, y1: int, state: Any, mode: str = "octant") -> None`
- `spixel_polyline(fb: frameBuffer, points: Sequence[Tuple[int, int]], state: Any, mode: str = "octant") -> None`
- `spixel_regular_polygon(fb: frameBuffer, cx: int, cy: int, radius: int, sides: int, state: Any, rotation: float = 0.0, mode: str = "octant") -> None`
- `spixel_regular_star(fb: frameBuffer, cx: int, cy: int, radius: int, n: int, k: int, state: Any, rotation: float = 0.0, mode: str = "octant") -> None`
- `spixel_flood_fill(fb: frameBuffer, x_seed: int, y_seed: int, state: Any, mode: str = "octant") -> frameBuffer`
- `spixel_rectangle(fb: frameBuffer, x1: int, y1: int, x2: int, y2: int, state: Any, mode: str = "octant") -> None`
- `spixel_ellipse(fb: frameBuffer, cx: int, cy: int, rx: int, ry: int, state: Any, mode: str = "octant") -> None`

---

## 5. Full-Block Character Primitives (`libansiscreen.screen_ops.prim`)

Provides full-character cell graphics using full block glyphs (`█`).

- `char_flood_fill(fb: frameBuffer, x_seed: int, y_seed: int, ignore_fg_color: bool = False, ignore_bg_color: bool = False, fill: Optional[Color] = DEFAULT_FG) -> frameBuffer`
- `char_rectangle(fb: frameBuffer, x1: int, y1: int, x2: int, y2: int, fill: Optional[Color] = None) -> frameBuffer`
- `char_ellipse(fb: frameBuffer, cx: int, cy: int, rx: int, ry: int, fill: Optional[Color] = None) -> frameBuffer`
- `stamp_from_screen(source: frameBuffer, transparent_chars: Optional[Sequence[Optional[str]]] = None, box: Optional[Tuple[int, int, int, int]] = None, border_bg: Optional[Color] = None) -> frameBuffer`
- `char_tile(fb: frameBuffer, text: str) -> None`
