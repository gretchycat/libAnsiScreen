# Library Purpose: libAnsiScreen

## High-Level Goals
`libAnsiScreen` is a high-performance, document-oriented terminal screen buffer library for Python. Its primary goal is to provide a lossless, programmatic interface for manipulating terminal content as a structured document rather than a transient stream of escape sequences.

The library enables developers to:
- Build complex terminal user interfaces (TUIs) using high-level abstractions.
- Perform advanced graphical operations such as pixel-plotting, gradients, and primitive drawing within a character-based terminal.
- Effortlessly parse existing ANSI-encoded data into a manipulatable buffer.
- Efficiently render buffer changes to ANSI escape sequences using an optimized, state-aware emitter.

## Scope
`libAnsiScreen` focuses strictly on the representation, manipulation, and serialization of screen content. It is designed to be:
- **Renderer-Agnostic:** While it includes a powerful ANSI emitter, the core buffer (`Screen`) can theoretically be rendered to any format.
- **Stateless/Document-Oriented:** It treats the terminal screen as a persistent document that can be queried and modified at any coordinate.
- **Feature-Rich:** Includes built-in support for clipping, pasting, color quantization, and geometry-based operations.

It does **not** handle:
- Input handling (keyboard/mouse).
- Terminal resize events (though it provides a `resize` method for the buffer).
- Direct I/O to the terminal (users are expected to print the emitted strings).

## Core Philosophy

### 1. Lossless Representation
Every cell in a `Screen` buffer is represented by a `Cell` object that explicitly stores its character, foreground color, background color, and attributes (bold, italic, etc.). Unlike traditional terminal emulators that might discard information or rely on implicit state, `libAnsiScreen` maintains a full, explicit state for every coordinate.

### 2. High-Level Orchestration
The `Screen` class acts as the central hub, providing convenience methods for common tasks while delegating complex logic to specialized "Screen Ops" modules. This keeps the API clean and intuitive while allowing the underlying implementation to remain modular and extensible.

### 3. Optimization through Differentiating
The `ANSIEmitter` is designed to be "diff-aware." It can compare the current state of a buffer against a previous state (or a default state) to emit the minimal set of ANSI escape sequences required to update the terminal. This significantly reduces data transfer and improves performance for dynamic TUIs.

### 4. Color Precision
With a dedicated `Color` class and support for Truecolor (24-bit), ANSI-256, and ANSI-16 palettes, the library provides precise control over terminal aesthetics. It includes built-in quantization logic to ensure colors are rendered as accurately as possible within the constraints of the target terminal.
