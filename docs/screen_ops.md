# Screen Operations (screen_ops)

The `screen_ops` modules contain high-level utility functions that perform complex manipulations on `Screen` buffers. While many are exposed as convenience methods on the `Screen` class, they can also be used independently.

## Clipping and Pasting (`screen_ops.clip`)

### `clear(screen: Screen, box: Optional[Box] = None) -> None`
Clears a rectangular region of the screen. Clearing resets characters to `None`, background to black, and attributes to 0.

---

### `copy(screen: Screen, box: Optional[Box] = None) -> Screen`
Copies a region into a new `Screen` instance.

---

### `cut(screen: Screen, box: Optional[Box] = None) -> Screen`
Copies a region and then clears it in the source screen.

---

### `paste(dst: Screen, src: Screen, *, box: Optional[Box] = None, transparent_char: Optional[Set[str]] = None, ...) -> None`
Pastes the `src` screen into `dst` with optional transparency rules for characters, foreground, background, and attributes.

---

## Colorization (`screen_ops.colorize`)

### `colorize(screen: Screen, gradient: Iterable[Color], *, mode: str = "hgrad", ...) -> None`
Applies a color gradient across the screen.
- **Modes:** `hgrad` (horizontal), `vgrad` (vertical), `dgrad` (diagonal), `words` (sequential per word).

---

## Pixel Plotting (`screen_ops.pixelplot`)

### `pixelplot(screen: Screen, x: int, y: int, color: Color) -> None`
Plots a virtual pixel at `(x, y)` where `y` is in half-character units. Automatically manages half-block characters (▀, ▄, █).

---

### `draw_line(screen: Screen, x0: int, y0: int, x1: int, y1: int, color: Color) -> None`
Draws a line between two points using pixel plotting.

---

### `draw_regular_star(screen: Screen, cx: int, cy: int, radius: int, n: int, k: int, color: Color, ...) -> None`
Draws a regular star polygon `{n/k}`.

---

### `flood_fill(screen: Screen, x_seed: int, y_seed: int, fill: Any = None) -> Screen`
Performs a pixel-based flood fill starting from a seed point.

---

## Drawing Primitives (`screen_ops.prim`)

### `char_rectangle(screen: Screen, x1: int, y1: int, x2: int, y2: int, fill: Any = None) -> Screen`
Draws a filled rectangle using full-character blocks.

---

### `char_ellipse(screen: Screen, cx: int, cy: int, rx: int, ry: int, fill: Any = None) -> Screen`
Draws a filled ellipse using full-character blocks.

---

### `stamp_from_screen(source: Screen, ...) -> Screen`
Creates a "stamp" from a screen region, treating specified characters as transparent.
