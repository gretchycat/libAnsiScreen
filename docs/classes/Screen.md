# Class: Screen

## Description
The `Screen` class is a lossless, document-oriented screen buffer. It acts as the primary interface for terminal content manipulation, maintaining a fixed-width, dynamically-growing grid of `Cell` objects and a `Cursor` instance.

`Screen` provides a high-level API for cursor movement, graphics state management (SGR), writing operations, and advanced graphical functions. Many of its advanced methods are convenience wrappers that delegate to specialized modules in `screen_ops`.

## Constructor (`__init__`)

| Parameter | Type | Default | Description |
|---|---|---|---|
| `width` | `int` | *Required* | Fixed width of the screen in columns. |
| `height` | `int` | `1` | Initial logical height of the screen. |

**Raises:** `ValueError` if `width <= 0`.

## Properties

| Property | Type | Description |
|---|---|---|
| `height` | `int` | Current logical height of the screen. |

## Methods

### Cursor Control (ANSI Semantics)

#### `cursor_goto(x: int, y: int) -> None`
Moves the cursor to the specified coordinates, clamped to the screen width.

#### `cursor_up(n: int = 1) -> None`
Moves the cursor up by `n` rows.

#### `cursor_down(n: int = 1) -> None`
Moves the cursor down by `n` rows.

#### `cursor_forward(n: int = 1) -> None`
Moves the cursor forward by `n` columns.

#### `cursor_back(n: int = 1) -> None`
Moves the cursor back by `n` columns.

#### `cursor_save() -> None`
Saves the current cursor position. See [Cursor](./Cursor.md) for details.

#### `cursor_restore() -> None`
Restores the previously saved cursor position.

---

### Graphics State (SGR)

#### `set_foreground(color: Color) -> None`
Sets the foreground color for future writing operations.

#### `set_background(color: Color) -> None`
Sets the background color for future writing operations.

#### `set_attrs(attrs: int) -> None`
Sets the text attributes bitmask.

#### `reset_graphics() -> None`
Resets foreground, background, and attributes to ANSI defaults.

---

### Writing Operations

#### `put_char(char: str) -> None`
Writes a single character at the current cursor position and advances the cursor.

#### `put_text(text: str) -> None`
Writes a string of text, handling `\n` and `\r`.

#### `print(s: str) -> None`
Parses an ANSI-encoded string and applies it to the screen.
*Orchestration: Invokes [ANSIParser](./ANSIParser.md).*

---

### Rendering

#### `emit(box: Optional[Box] = None, raw: bool = False) -> str`
Renders the screen (or a sub-region) to an ANSI string.
*Orchestration: Invokes [ANSIEmitter](./ANSIEmitter.md).*

#### `emit_diff(prev: Screen, box: Optional[Box] = None, raw: bool = False) -> str`
Renders the difference between this screen and another.
*Orchestration: Invokes [ANSIEmitter](./ANSIEmitter.md).*

---

### Screen Operations (Delegated)

#### `copy(box: Optional[Box] = None) -> Screen`
Copies a region into a new screen.
*Orchestration: Delegated to `screen_ops.clip.copy`. See [clip operations](../screen_ops.md) (conceptual).*

#### `paste(src: Screen, *, box: Optional[Box] = None, ...) -> None`
Pastes another screen into this one.
*Orchestration: Delegated to `screen_ops.clip.paste`.*

#### `colorize(gradient, mode: str = "hgrad", ...) -> None`
Applies a color gradient to the screen.
*Orchestration: Delegated to `screen_ops.colorize.colorize`.*

#### `pixelplot(x: int, y: int, color: Color) -> None`
Plots a "pixel" using half-block characters.
*Orchestration: Delegated to `screen_ops.pixelplot.pixelplot`.*

#### `line(x0: int, y0: int, x1: int, y1: int, color: Color) -> None`
Draws a line using pixels.
*Orchestration: Delegated to `screen_ops.pixelplot.draw_line`.*

#### `regular_star(cx, cy, radius, n, k, color, ...) -> None`
Draws a regular star polygon.
*Orchestration: Delegated to `screen_ops.pixelplot.draw_regular_star`.*

#### `flood_fill(x_seed, y_seed, fill=None) -> Screen`
Performs a pixel-based flood fill.
*Orchestration: Delegated to `screen_ops.pixelplot.flood_fill`.*

#### `char_rectangle(x1, y1, x2, y2, fill=None) -> Screen`
Draws a filled rectangle using full blocks.
*Orchestration: Delegated to `screen_ops.prim.char_rectangle`.*
