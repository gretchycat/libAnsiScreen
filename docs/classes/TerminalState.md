# Class: TerminalState

## Description
`TerminalState` is an internal immutable dataclass used by the `ANSIEmitter` to represent the complete graphics state of the terminal (foreground, background, and attributes) at a specific coordinate or point in the emission stream.

## Constructor (`__init__`)

| Parameter | Type | Default | Description |
|---|---|---|---|
| `fg` | `AnsiColorState` | *Required* | The current foreground color state. |
| `bg` | `AnsiColorState` | *Required* | The current background color state. |
| `attrs` | `int` | *Required* | The current text attributes bitmask. |
