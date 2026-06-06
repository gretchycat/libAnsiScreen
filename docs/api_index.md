# API Reference Index

This index provides a complete navigation map to all classes and modules within the `libAnsiScreen` library.

## Core Classes
- [Screen](./classes/Screen.md) - The central screen buffer and orchestrator.
- [Cell](./classes/Cell.md) - The atomic unit of terminal state.
- [Cursor](./classes/Cursor.md) - Logical write position tracker.

## Color Management
- [Color](./classes/Color.md) - Immutable RGB(A) color representation.
- [Palette](./classes/Palette.md) - Indexed color mappings and factory functions.

## Rendering and Parsing
- [ANSIEmitter](./classes/ANSIEmitter.md) - State-aware ANSI rendering engine.
- [ANSIParser](./classes/ANSIParser.md) - Streaming ANSI data processor.
- [Box](./classes/Box.md) - Rectangular region definition.
- [AnsiColorState](./classes/AnsiColorState.md) - Internal ANSI color representation.
- [TerminalState](./classes/TerminalState.md) - Internal terminal graphics state.

## Screen Operations
- [Screen Operations](./screen_ops.md) - High-level utility functions for clipping, geometry, and more.

## Documentation Overview
- [Library Purpose](./purpose.md) - Goals, scope, and philosophy.
- [Library Architecture](./architecture.md) - Conceptual design and data structures.
- [Usage Guide](./usage.md) - Runnable code recipes and examples.
