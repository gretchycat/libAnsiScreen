 # libAnsiScreen

**libAnsiScreen** is a character-cell rendering library that treats ANSI as a
*serialization format*, not as a rendering model.

Instead of relying on terminal state, cursor tricks, or partial redraw side
effects, libAnsiScreen maintains an explicit in-memory screen buffer composed of
cells—each with a character, foreground color, background color, and attributes.
ANSI escape sequences are parsed *into* this buffer, and optimized ANSI output is
generated *from* it.

This design makes terminal rendering deterministic, composable, and portable.

---

## Motivation

ANSI terminals were designed for teletypes, not modern interfaces.

Cursor movement is expensive. Partial redraws are fragile. Terminal emulators
vary wildly in behavior. Anyone who has tried to build a game, UI, or compositor
using raw ANSI has eventually discovered the same truth:

> You need a real screen model.

libAnsiScreen exists to provide that model.

---

## Core Concepts

### Screen Buffer

At the heart of libAnsiScreen is a 2D screen buffer with an explicit width and
height. Each cell contains:

- a character
- a foreground color (internally stored as RGB)
- a background color (internally stored as RGB)
- optional attributes (bold, underline, inverse, etc.)

The buffer is the single source of truth. No terminal state is assumed.

---

### ANSI as Input *and* Output

ANSI escape sequences are supported in two directions:

- **Import**: ANSI streams can be parsed into the buffer, starting at any
  `(x, y)` coordinate. Cursor movement, color changes, and erase commands mutate
  the buffer—not the terminal.

- **Export**: The buffer can be rendered back to ANSI using different strategies,
  such as:
  - full-frame scanline output (no cursor positioning)
  - diff-based output with cost-aware cursor movement

This makes ANSI deterministic, replayable, and testable.

---

### Truecolor Internals

Internally, all colors are stored as up to 24-bit RGB.

This allows libAnsiScreen to:

- correctly parse truecolor ANSI (`38;2` / `48;2`)
- downsample deterministically to:
  - 256-color ANSI
  - 16-color ANSI
  - 8-color ANSI
  - monochrome
- apply perceptual quantization and dithering policies

ANSI color depth becomes an output choice, not a limitation.

---

## Intended Use Cases

libAnsiScreen is designed to be a foundational rendering layer for:

- BBS software (e.g. Synchronet external programs)
- terminal games
- ANSI art tools and compositors
- image-to-ANSI pipelines
- terminal UI experiments
- offline ANSI processing and optimization

It is **not** a full terminal emulator. Input modes, keyboard mapping, mouse
tracking, and device queries are intentionally out of scope.

---

## Design Philosophy

- **Deterministic**: Same input buffer → same output ANSI
- **Explicit**: No hidden terminal state
- **Composable**: Multiple sources can render into the same buffer
- **Cost-aware**: Rendering strategies can be chosen based on byte cost
- **Portable**: Works across terminals, SSH, telnet, and BBS environments

---

## Project Status

libAnsiScreen is under active development.

The core buffer model, ANSI parsing, and rendering strategies are being designed
with correctness and long-term reuse in mind. The public API is not yet frozen.

---

## Usage & API

*Coming soon.*

This section will document:
- the `Screen` and `Cell` APIs
- ANSI import and export interfaces
- rendering strategies and cost models
- image and palette integration

---

## License

MIT License. See `LICENSE` for details.
