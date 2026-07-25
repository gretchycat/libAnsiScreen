# API Reference Index

This index provides a complete sitemap for all modules, classes, and documentation guides within `libAnsiScreen`.

---

## Core Classes
- [Screen](./classes/Screen.md) - Primary high-level virtual terminal screen orchestrator.
- [Cell](./classes/Cell.md) - Atomic unit of terminal grid state (character, colors, attributes).
- [Cursor](./classes/Cursor.md) - Logical write position tracker (`x`, `y`) and position save/restore state.

---

## Color & Palette Management
- [Color](./classes/Color.md) - Immutable RGB(A) color representation, conversions, and blending.
- [Palette](./classes/Palette.md) - Indexed color lookups and ANSI palette factories.

---

## Rendering & Parsing
- [ANSIEmitter](./classes/ANSIEmitter.md) - State-aware differential ANSI rendering engine.
- [ANSIParser](./classes/ANSIParser.md) - Streaming ANSI escape sequence processor.
- [Box](./classes/Box.md) - Rectangular region bounding box `(x, y, w, h)`.
- [AnsiColorState](./classes/AnsiColorState.md) - Internal ANSI color representation tracking.
- [TerminalState](./classes/TerminalState.md) - Internal terminal graphics state tracking.

---

## Screen Operations (`screen_ops`)
- [Screen Operations](./screen_ops.md) - High-level utilities for clipping (`clip`), gradients (`colorize`), half-block pixels (`pixel`), subpixel graphics (`spixel`), and full-block primitives (`prim`).

---

## Overview & User Guides
- [Library Purpose](./purpose.md) - Motivation, design goals, and philosophy.
- [Library Architecture](./architecture.md) - Conceptual design, data structures, and pipeline.
- [Usage Guide](./usage.md) - Tested code recipes and runnable examples.
