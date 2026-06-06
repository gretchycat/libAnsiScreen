# Library Architecture: libAnsiScreen

## Conceptual Design
`libAnsiScreen` is designed around a decoupled architecture that separates screen representation from input parsing and output rendering. The system is divided into four primary layers:

1. **Foundational Data Layer:** `Cell`, `Color`, and `Palette` classes define the atomic units of terminal state.
2. **Buffer Management Layer:** The `Screen` and `Cursor` classes manage the document-oriented grid and logical write position.
3. **Operational Layer (Screen Ops):** Specialized modules (e.g., `clip`, `colorize`, `pixelplot`) perform high-level manipulations on the `Screen` buffer.
4. **Translation Layer:** The `ANSIParser` and `ANSIEmitter` handle the conversion between the internal buffer state and external ANSI escape sequences.

---

## Core Component Interactions

### 1. The Screen Orchestrator
The `Screen` class is the central point of interaction. It maintains a 2D grid of `Cell` objects and a `Cursor` instance. While it provides a wide range of methods, many of them are convenience wrappers that delegate to the Operational Layer.

**Interaction Flow:**
- When `screen.pixelplot(x, y, color)` is called, it invokes `libansiscreen.screen_ops.pixelplot.pixelplot`.
- The op function queries or modifies the `Cell` objects within the `Screen`.
- If the `Screen` needs to grow vertically to accommodate a coordinate, it uses its internal `_ensure_row` helper.

### 2. Cell and Color
A `Cell` is a lightweight data container (using `__slots__` and `@dataclass`) that holds a character and two `Color` instances (FG and BG). `Color` objects are immutable and represent RGB values. The use of `None` for FG/BG in a `Cell` typically signifies inheritance or a reset state, depending on the context.

### 3. Parsing and Ejection
- **ANSIParser:** A streaming state machine that reads characters. When it encounters an escape sequence (CSI, SGR, etc.), it updates the `Screen`'s graphics state (e.g., `current_fg`) or calls movement methods (e.g., `cursor_goto`).
- **ANSIEmitter:** Analyzes the `Screen` buffer (or a specific `Box` region). It maintains an internal `TerminalState` and `AnsiColorState` to track what the terminal *currently* displays. It only generates SGR codes when the intended state in the buffer differs from the tracked terminal state.

---

## Data Structures

### The Grid
The `Screen` stores its content in `self.rows`, which is a `List[List[Cell]]`. This allows for efficient row-based access and dynamic vertical growth. Each row is pre-allocated with a fixed width.

### Bitmasks for Attributes
Terminal attributes (Bold, Italic, etc.) are handled using a bitmask integer. Constants like `ATTR_BOLD = 0b00000001` are defined in `cell.py` and used throughout the library for efficient attribute checking and manipulation.

### Box Regions
A `Box` (defined in `renderer/ansi_emitter.py` and aliased in `screen_ops/clip.py`) is a simple dataclass or tuple `(x, y, width, height)` used to define rectangular regions for operations like clipping, pasting, or partial rendering.

---

## Extension Points
The library is designed for extension in the following areas:

- **New Screen Ops:** Developers can create new modules in `screen_ops` that take a `Screen` object and perform arbitrary manipulations on its cells.
- **Custom Palettes:** The `Palette` class can be instantiated with any mapping of indices to `Color` objects, allowing for custom terminal color schemes.
- **Alternative Renderers:** While only an ANSI emitter is provided, the structured nature of the `Screen` buffer makes it straightforward to implement renderers for other formats like HTML, SVG, or image buffers.
