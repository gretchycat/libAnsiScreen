# Library Architecture: libAnsiScreen

## Conceptual Design
`libAnsiScreen` is designed around a decoupled architecture that separates in-memory screen representation from ANSI parsing and differential output rendering. The system consists of four primary layers:

1. **Foundational Data Layer:** `Cell`, `Color`, and `Palette` classes define atomic units of terminal state and color spaces.
2. **Buffer Management Layer:** `frameBuffer` and `Screen` manage the document-oriented grid, row allocation, graphics state (SGR), and write position tracking (`Cursor`).
3. **Operational Layer (`screen_ops`):** Modular utility functions for high-level operations:
   - `screen_ops.clip`: Clipping, cutting, copying, pasting, transparent overlay, and tiling.
   - `screen_ops.colorize`: Color gradients (`hgrad`, `vgrad`, `dgrad`, `words`) and RGB/HSV color shifting.
   - `screen_ops.pixel`: Half-block pixel drawing (1x2 resolution per character cell).
   - `screen_ops.spixel`: Subpixel monochrome graphics (`quadrant`, `octant`, `braille` modes).
   - `screen_ops.prim`: Full-character block primitives (`█`) and screen stamping.
4. **Translation Layer:** `ANSIParser` (streaming parser) and `ANSIEmitter` (differential cost-aware rendering engine).

---

## Core Component Interactions

### 1. The Screen Orchestrator
The `Screen` class serves as the main high-level API. It inherits from `Colorize` and `frameBuffer` and delegates drawing and region operations to specialized functions within `screen_ops`.

```
                     +-------------------+
                     |      Screen       |
                     +---------+---------+
                               |
         +---------------------+---------------------+
         |                     |                     |
+--------v--------+   +--------v--------+   +--------v--------+
|   frameBuffer   |   |   ANSIParser    |   |   ANSIEmitter   |
+--------+--------+   +-----------------+   +-----------------+
         |
+--------v--------+
|  Cell / Cursor  |
+-----------------+
```

### 2. Cell, Color, and Truecolor Internals
- A `Cell` is a lightweight Python dataclass (`slots=True`) containing a single character `char`, `fg` (`Color`), `bg` (`Color`), and an integer bitmask `attrs`.
- `Color` objects are immutable RGB(A) instances stored internally as 24-bit RGB.
- Colors can be quantized to 16-color ANSI, 256-color ANSI, or emitted as Truecolor (24-bit) escape sequences by the `ANSIEmitter`.

### 3. Parsing and Emission Pipeline
- **`ANSIParser`:** A streaming state machine that reads ANSI sequence characters (`\x1b[...]`), updates the screen's graphics state (`current_fg`, `current_bg`, `current_attrs`), and writes characters to the cell grid at the current `Cursor` position.
- **`ANSIEmitter`:** Scans the `Screen` buffer, compares target cell states against tracked terminal state (`TerminalState`), and emits cost-aware, differential ANSI escape codes.

---

## Data Structures

### Dynamic Grid Allocation
The `frameBuffer` stores rows as `List[List[Cell]]`. The width is fixed at screen creation, while height grows dynamically row-by-row as content or cursor movement extends past the existing vertical range.

### Bitmasks for Text Attributes
Text attributes (Bold, Italic, Underline, Blink, Inverse, Conceal, Strikethrough) are represented as bit flags on integer bitmasks (e.g. `ATTR_BOLD = 0b00000001` in `cell.py`).

### Rectangular Boundaries (`Box`)
Region operations use `Box` objects or `(x, y, width, height)` tuples to define clipping boundaries and partial frame emission limits.

---

## Extension Points

- **New Screen Operations:** Add custom modules to `screen_ops` that manipulate `frameBuffer` or `Screen` instances.
- **Custom Color Palettes:** Instantiate custom `Palette` lookup tables for specific terminal target platforms.
- **Alternative Renderers:** Implement renderers that consume `Screen` buffers to output HTML, SVG, or image bitmaps.
