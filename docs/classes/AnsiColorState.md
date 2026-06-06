# Class: AnsiColorState

## Description
`AnsiColorState` is an internal immutable dataclass used by the `ANSIEmitter` to track how a color is currently represented in the terminal's state. It distinguishes between different ANSI encoding methods (e.g., ANSI-16, ANSI-256, Truecolor) and stores the corresponding indices or RGB values.

## Constructor (`__init__`)

| Parameter | Type | Default | Description |
|---|---|---|---|
| `kind` | `str` | *Required* | The encoding method: "default", "ansi16", "ansi256", "truecolor", or "dos". |
| `value` | `Tuple[int, ...]` | *Required* | The underlying representation (e.g., `(idx,)` or `(r, g, b)`). |
