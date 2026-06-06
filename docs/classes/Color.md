# Class: Color

## Description
The `Color` class represents an immutable RGB(A) color. It provides a robust set of factory methods for creating colors from various formats (RGB, HSV, Hex, integer indices) and includes utility methods for color manipulation, distance measurement, and space conversion.

Colors are implemented as frozen dataclasses, making them hashable and safe for use as dictionary keys or in sets.

## Constructor (`__init__`)

| Parameter | Type | Default | Description |
|---|---|---|---|
| `r` | `int` | *Required* | Red component (0–255). |
| `g` | `int` | *Required* | Green component (0–255). |
| `b` | `int` | *Required* | Blue component (0–255). |
| `a` | `int` | `255` | Alpha component (0–255). |

## Static / Factory Methods

### `rgb(r: int, g: int, b: int) -> Color`
Creates a Color instance from RGB integers.

**Usage Example:**
```python
from libansiscreen.color.rgb import Color
red = Color.rgb(255, 0, 0)
```

---

### `hsv(h: float, s: float, v: float) -> Color`
Creates a Color instance from HSV values (0.0–1.0).

**Arguments Table:**
| Name | Type | Description |
|---|---|---|
| `h` | `float` | Hue (0.0 to 1.0). |
| `s` | `float` | Saturation (0.0 to 1.0). |
| `v` | `float` | Value (0.0 to 1.0). |

**Raises:** `ValueError` if any parameter is outside the range 0.0–1.0.

---

### `hex(value: str) -> Color`
Creates a Color instance from a hex string (e.g., "#FF0000" or "F00").

---

### `set(v: Any) -> Color`
Polymorphic factory method that attempts to create a Color from various input types:
- `int`: Interpreted as an ANSI-256 palette index.
- `str`: Interpreted as a hex string.
- `tuple`: Interpreted as `(r, g, b)`.
- `dict`: Interpreted as `{'r': r, 'g': g, 'b': b}`.
- `Color`: Returns a copy of the color.
- `None`: Returns black (0, 0, 0).

---

## Instance Methods

### `luminance() -> float`
Calculates the relative luminance of the color using standard coefficients.

---

### `to_tuple() -> Tuple[int, int, int]`
Returns the color as an `(r, g, b)` tuple.

---

### `to_float_tuple() -> Tuple[float, float, float]`
Returns the color as an `(r, g, b)` tuple of floats (0.0–1.0).

---

### `to_hsv() -> Tuple[float, float, float]`
Converts the color to HSV space.

**Returns:** `(h, s, v)` tuple.

---

### `distance_rgb(other: Color) -> int`
Calculates the squared Euclidean distance in RGB space between this color and another.

---

### `distance_hsv(other: Color) -> float`
Calculates the squared distance in HSV space. Hue is treated circularly.

---

### `blend(other: Color, amount: float) -> Color`
Blends this color toward `other` by the specified `amount` (0.0 to 1.0).

**Arguments Table:**
| Name | Type | Description |
|---|---|---|
| `other` | `Color` | The target color to blend toward. |
| `amount` | `float` | The blending factor (0.0 = self, 1.0 = other). |

**Returns:** `Color` - A new blended `Color` instance.

---

### `shift_hsv(h: float, s: float, v: float) -> Color`
Returns a new Color instance shifted in HSV space.

---

### `shift_rgb(r: int, g: int, b: int) -> Color`
Returns a new Color instance shifted in RGB space (clamped to 0–255).
