# Class: ANSIParser

## Description
`ANSIParser` is a streaming state machine designed to parse ANSI escape sequences and mutate a `Screen` buffer accordingly. Unlike a terminal emulator, it treats the input as a document, updating the logical state of the buffer (cursor position, colors, attributes) as it processes data.

The parser handles:
- **Text:** Direct character insertion.
- **Control Characters:** Carriage return (`\r`) and newline (`\n`).
- **CSI (Control Sequence Introducer):** Cursor movement, clearing, and SGR.
- **SGR (Select Graphic Rendition):** Foreground/background colors and text attributes.

## Constructor (`__init__`)

| Parameter | Type | Default | Description |
|---|---|---|---|
| `screen` | `Screen` | *Required* | The `Screen` instance that this parser will mutate. |

## Methods

### `feed(data: Union[str, bytes], encoding: str = 'utf-8') -> None`
Feeds a chunk of data into the parser.

**Arguments Table:**
| Name | Type | Description |
|---|---|---|
| `data` | `str` or `bytes` | The input data to parse. |
| `encoding` | `str` | The encoding to use if `bytes` are provided. |

**Usage Example:**
```python
from libansiscreen.screen import Screen
from libansiscreen.parser.ansi_parser import ANSIParser

screen = Screen(width=80)
parser = ANSIParser(screen)
parser.feed("\x1b[31mHello\x1b[0m")
# Screen now contains 'Hello' in red
```

---

### `_process_char(ch: str) -> None`
Internal method that routes characters to the appropriate state handler based on the current parser state.

---

### `_dispatch_csi(final: str) -> None`
Internal method that executes the logic for a completed CSI sequence.

Supported Final Characters:
- `A`: Cursor Up
- `B`: Cursor Down
- `C`: Cursor Forward
- `D`: Cursor Back
- `H`, `f`: Cursor Position (CUP/HVP)
- `J`: Erase in Display (ED)
- `K`: Erase in Line (EL)
- `m`: SGR (Select Graphic Rendition)

---

### `_handle_sgr(params: List[int]) -> None`
Internal method that processes SGR parameters to update the screen's graphics state.

Supported SGR Codes:
- `0`: Reset
- `1–9`: Set attributes (Bold, Faint, Italic, Underline, Blink, Inverse, Conceal, Strike)
- `22–29`: Clear attributes
- `30–37`, `90–97`: Set ANSI-16 foreground colors
- `40–47`, `100–107`: Set ANSI-16 background colors
- `38;5;n`, `48;5;n`: Set ANSI-256 colors
- `38;2;r;g;b`, `48;2;r;g;b`: Set Truecolor (24-bit) colors
- `39`, `49`: Reset foreground/background to defaults
