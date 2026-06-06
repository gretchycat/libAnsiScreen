# Class: Cursor

## Description
The `Cursor` class is a lightweight state container that stores the current logical write position (`x`, `y`) within a `Screen` buffer. It also includes an internal mechanism for saving and restoring a single position state, mimicking terminal escape sequence behaviors like DECSC/DECRC.

Importantly, the `Cursor` class does **not** perform bounds checking or enforce wrapping; these responsibilities are handled by the `Screen` class that owns the cursor.

## Constructor (`__init__`)

| Parameter | Type | Default | Description |
|---|---|---|---|
| `x` | `int` | `0` | The horizontal coordinate (column). |
| `y` | `int` | `0` | The vertical coordinate (row). |

## Methods

### `set(x: int, y: int) -> None`
Directly sets the cursor's coordinates.

**Arguments Table:**
| Name | Type | Description |
|---|---|---|
| `x` | `int` | The new horizontal position. |
| `y` | `int` | The new vertical position. |

---

### `move(dx: int = 0, dy: int = 0) -> None`
Moves the cursor relative to its current position.

**Arguments Table:**
| Name | Type | Description |
|---|---|---|
| `dx` | `int` | Relative horizontal shift. |
| `dy` | `int` | Relative vertical shift. |

**Usage Example:**
```python
from libansiscreen.cursor import Cursor
cur = Cursor(10, 5)
cur.move(dx=2, dy=-1)
# cur is now at (12, 4)
```

---

### `save() -> None`
Saves the current `x` and `y` coordinates to an internal buffer.

---

### `restore() -> None`
Restores the cursor position from the previously saved coordinates. If no position was saved, it defaults to the state initialized in the constructor (typically 0, 0).

---

### `reset() -> None`
Resets the current position and the saved position to (0, 0).
