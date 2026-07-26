# Screen Operations (`screen_ops`)

The `screen_ops` package contains modular, high-level graphics and utility functions that operate on `frameBuffer` and `Screen` instances. While exposed as methods on the `Screen` class, these functions can also be imported and called independently.

---

## 1. Clipping and Pasting (`libansiscreen.screen_ops.clip`)

### `clear(screen: frameBuffer, box: Optional[Tuple[int, int, int, int]] = None) -> None`
Clears a rectangular region or the entire screen buffer. Resets target cells in binary memory.

### `copy(screen: frameBuffer, box: Optional[Tuple[int, int, int, int]] = None) -> frameBuffer`
Copies a rectangular region into a new `frameBuffer` instance using fast binary memory slice transfers. All cell attributes (characters, foreground, background, text attributes, and `None` states) are preserved exactly as defined.

### `cut(screen: frameBuffer, box: Optional[Tuple[int, int, int, int]] = None) -> frameBuffer`
Copies a region to a new `frameBuffer` and clears the source region.

### `paste(dst: frameBuffer, src: frameBuffer, *, box: Optional[Tuple[int, int, int, int]] = None, transparent_char: Optional[Set[str]] = None, transparent_fg: bool = False, transparent_bg: bool = False, transparent_attrs: bool = False) -> None`
Pastes `src` framebuffer into `dst` with fine-grained transparency and non-overwriting controls.

### `tile(screen: frameBuffer, tl: frameBuffer) -> None`
Repeatedly tiles a template framebuffer `tl` across the full dimensions of `screen`.

---

## Detailed Copy & Paste Non-Overwriting (Transparency) Rules

When pasting a source framebuffer (`src`) onto a destination framebuffer (`dst`), `libAnsiScreen` follows strict non-overwriting rules for each cell component. Unset (`None`) properties or active transparency flags instruct `paste` to **preserve destination cell attributes** rather than replacing them.

### 1. Character Non-Overwriting Rules
- **Unset Source Characters (`char = None`):** If a cell in `src` has no character set (`char=None`), `paste` will **not overwrite** `dst_cell.char`. The underlying destination character is preserved intact.
- **`transparent_char` Filtering:** If a set of characters is supplied to `transparent_char` (e.g., `transparent_char={' '}`), any cell in `src` containing a character in that set is treated as transparent and will **not overwrite** `dst_cell.char`.

### 2. Foreground Color Non-Overwriting Rules
- **Unset Source Foreground (`fg = None`):** In `libAnsiScreen`, `fg=None` indicates an uncolored/inherited foreground. When pasting a cell where `src_cell.fg` is `None`, `paste` will **not overwrite** `dst_cell.fg`. The destination cell retains its existing foreground color.
- **`transparent_fg = True` Flag:** When `transparent_fg` is set to `True`, all source foreground colors are ignored during paste, preserving `dst_cell.fg` across all cells in the pasted region.

### 3. Background Color Non-Overwriting Rules
- **Unset Source Background (`bg = None`):** When `src_cell.bg` is `None`, `paste` will **not overwrite** `dst_cell.bg`. The destination cell retains its existing background color.
- **`transparent_bg = True` Flag:** When `transparent_bg` is set to `True`, all source background colors are ignored during paste, preserving `dst_cell.bg` across all cells in the pasted region.

### 4. Text Attribute Non-Overwriting Rules
- **`transparent_attrs = True` Flag:** When `transparent_attrs` is set to `True`, text formatting attributes (such as bold, italic, or underline bitmasks) from `src` are ignored, preserving `dst_cell.attrs`.

---

### Non-Overwriting Behavior Matrix

| Source Cell Property (`src`) | Paste Condition / Flag | Action on Destination (`dst`) |
|---|---|---|
| `char = 'A'` | `char not in transparent_char` | Overwrites `dst_cell.char` with `'A'` |
| `char = ' '` | `transparent_char = {' '}` | **Preserves `dst_cell.char`** (Transparent Space) |
| `char = None` | Any | **Preserves `dst_cell.char`** (Unset Character) |
| `fg = Color(255, 0, 0)` | `transparent_fg = False` | Overwrites `dst_cell.fg` with Red |
| `fg = Color(255, 0, 0)` | `transparent_fg = True` | **Preserves `dst_cell.fg`** |
| `fg = None` | Any | **Preserves `dst_cell.fg`** (Transparent Foreground) |
| `bg = Color(0, 0, 255)` | `transparent_bg = False` | Overwrites `dst_cell.bg` with Blue |
| `bg = Color(0, 0, 255)` | `transparent_bg = True` | **Preserves `dst_cell.bg`** |
| `bg = None` | Any | **Preserves `dst_cell.bg`** (Transparent Background) |

---

### Practical Usage Code Examples

#### Example 1: Layering Text Overlay onto a Colored Background Panel
```python
from libansiscreen.screen import Screen
from libansiscreen.color.rgb import Color

# 1. Create a background panel with blue background
panel = Screen(width=40, height=10)
panel.set_background(Color(0, 0, 200))
panel.cls()

# 2. Create text label with red text and None (transparent) background
label = Screen(width=20, height=1)
label.set_foreground(Color(255, 255, 0))
label.set_background(None)  # Transparent background
label.put_text("Status: Active")

# 3. Paste label onto panel
panel.paste(label, box=(2, 2, 20, 1))

# Result: Characters and yellow text color are stamped onto panel, 
# while the panel's blue background is preserved!
```

#### Example 2: Non-Destructive Floating Sprite Stamping
```python
# Passing transparent_char={' '} ensures spaces inside the sprite box 
# do not erase underlying characters or graphics in the destination:
destination.paste(sprite_screen, box=(x, y, 10, 5), transparent_char={' '})
```

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
