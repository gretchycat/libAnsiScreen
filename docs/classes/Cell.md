# Class: Cell

## Description
The `Cell` class represents a single coordinate on the terminal grid. It is the atomic unit of the `Screen` buffer, storing the character to be displayed, its foreground and background colors, and any associated ANSI text attributes (like bold or italic).

`Cell` is implemented as a Python dataclass with `slots=True` for high performance and low memory footprint, which is critical when managing large screen buffers. It supports value-based equality and provides helper methods for diffing and shifting colors.

## Constructor (`__init__`)

| Parameter | Type | Default | Description |
|---|---|---|---|
| `char` | `str` | `None` | The single character to display in this cell. |
| `fg` | `Optional[Color]` | `None` | The foreground color of the character. `None` typically implies inheritance or reset. |
| `bg` | `Optional[Color]` | `None` | The background color of the cell. `None` typically implies inheritance or reset. |
| `attrs` | `int` | `0` | A bitmask of ANSI text attributes (e.g., `ATTR_BOLD`). |

## Methods

### `__eq__(other: object) -> bool`
Performs a value-based equality check against another object.

**Arguments Table:**
| Name | Type | Description |
|---|---|---|
| `other` | `object` | The object to compare against. |

**Returns:** `bool` - `True` if all fields (`char`, `fg`, `bg`, `attrs`) match, `False` otherwise.

**Usage Example:**
```python
from libansiscreen.cell import Cell
from libansiscreen.color.rgb import Color

c1 = Cell('A', Color(255, 0, 0), None, 0)
c2 = Cell('A', Color(255, 0, 0), None, 0)
print(c1 == c2) # True
```

---

### `diff(other: Cell) -> int`
Returns a bitmask indicating which fields differ between this cell and another.

**Arguments Table:**
| Name | Type | Description |
|---|---|---|
| `other` | `Cell` | The cell to compare against. |

**Returns:** `int` - A 4-bit mask where:
- Bit 0: Character differs
- Bit 1: Foreground color differs
- Bit 2: Background color differs
- Bit 3: Attributes differ

**Usage Example:**
```python
from libansiscreen.cell import Cell
c1 = Cell('A')
c2 = Cell('B')
print(bin(c1.diff(c2))) # 0b1 (Bit 0 set)
```

---

### `char_changed(other: Cell) -> bool`
Predicate to check if the character differs from another cell.

**Arguments Table:**
| Name | Type | Description |
|---|---|---|
| `other` | `Cell` | The cell to compare against. |

**Returns:** `bool` - `True` if `char` fields differ.

---

### `fg_changed(other: Cell) -> bool`
Predicate to check if the foreground color differs from another cell.

**Arguments Table:**
| Name | Type | Description |
|---|---|---|
| `other` | `Cell` | The cell to compare against. |

**Returns:** `bool` - `True` if `fg` fields differ.

---

### `bg_changed(other: Cell) -> bool`
Predicate to check if the background color differs from another cell.

**Arguments Table:**
| Name | Type | Description |
|---|---|---|
| `other` | `Cell` | The cell to compare against. |

**Returns:** `bool` - `True` if `bg` fields differ.

---

### `attrs_changed(other: Cell) -> bool`
Predicate to check if the attributes differ from another cell.

**Arguments Table:**
| Name | Type | Description |
|---|---|---|
| `other` | `Cell` | The cell to compare against. |

**Returns:** `bool` - `True` if `attrs` fields differ.

---

### `copy() -> Cell`
Creates a deep copy of the cell.

**Returns:** `Cell` - A new `Cell` instance with identical values.

**Usage Example:**
```python
from libansiscreen.cell import Cell
c1 = Cell('A')
c2 = c1.copy()
```

---

### `shift_hsv(h: float, s: float, v: float) -> Cell`
Shifts both foreground and background colors in HSV space. Mutates the cell's color objects.

**Arguments Table:**
| Name | Type | Description |
|---|---|---|
| `h` | `float` | Hue shift (-1.0 to 1.0). |
| `s` | `float` | Saturation shift (-1.0 to 1.0). |
| `v` | `float` | Value shift (-1.0 to 1.0). |

**Returns:** `Cell` - Returns `self` for chaining.

---

### `shift_rgb(r: int, g: int, b: int) -> Cell`
Shifts both foreground and background colors in RGB space. Mutates the cell's color objects.

**Arguments Table:**
| Name | Type | Description |
|---|---|---|
| `r` | `int` | Red shift (-255 to 255). |
| `g` | `int` | Green shift (-255 to 255). |
| `b` | `int` | Blue shift (-255 to 255). |

**Returns:** `Cell` - Returns `self` for chaining.
