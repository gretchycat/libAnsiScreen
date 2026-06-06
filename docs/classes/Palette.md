# Class: Palette

## Description
The `Palette` class represents an indexed color palette, providing exact mappings between integer indices and `Color` instances. It is used to define representable color spaces (like ANSI-16 or ANSI-256) and perform lossless conversions between indices and RGB values.

The class does not perform nearest-color matching internally; it is strictly a lookup table.

## Constructor (`__init__`)

| Parameter | Type | Default | Description |
|---|---|---|---|
| `index_to_color` | `Dict[int, Color]` | *Required* | A dictionary mapping integer indices to `Color` objects. |

## Methods

### `get_colors() -> Dict[int, Color]`
Returns a copy of the internal index-to-color mapping.

---

### `set_colors(index_to_color: Dict[int, Color]) -> None`
Replaces the palette data with a new mapping. Performs validation on the input dictionary.

**Raises:**
- `ValueError`: If the dictionary is empty or contains invalid indices.
- `TypeError`: If values are not `Color` instances.

---

### `index_to_rgb(index: int) -> Optional[Color]`
Converts a palette index to its associated `Color`.

**Returns:** `Optional[Color]` - The color at the index, or `None` if not found.

---

### `rgb_to_index_exact(color: Color) -> Optional[int]`
Finds the palette index that exactly matches the provided `Color`.

**Returns:** `Optional[int]` - The index, or `None` if no exact match exists.

---

### `choose_index(color: Color, strategy: str = "exact") -> Optional[int]`
Selects an index for a color based on a strategy. Currently, only the "exact" strategy is supported.

---

### `from_list(colors: list[Color]) -> Palette`
**@classmethod**
Creates a palette from a list of colors, using the list indices as the palette indices.

---

## Factory Functions
These functions are defined in the `palette` module and return pre-configured `Palette` instances.

### `create_ansi_16_palette() -> Palette`
Returns the standard 16-color ANSI/CGA palette (indices 0–15).

### `create_ansi_256_palette() -> Palette`
Returns the standard xterm 256-color palette, which includes the 16 ANSI colors, a 6x6x6 color cube, and a 24-step grayscale ramp.
