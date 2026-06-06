# Class: Box

## Description
A simple dataclass used to represent a rectangular region on a 2D grid. It is used extensively throughout the library for defining clipping regions, pasting boundaries, and partial rendering.

## Constructor (`__init__`)

| Parameter | Type | Default | Description |
|---|---|---|---|
| `x` | `int` | *Required* | The top-left horizontal coordinate. |
| `y` | `int` | *Required* | The top-left vertical coordinate. |
| `width` | `int` | *Required* | The width of the box. |
| `height` | `int` | *Required* | The height of the box. |

## Methods

### `contains(x: int, y: int) -> bool`
Checks if the specified coordinate is within the boundaries of the box.

**Arguments Table:**
| Name | Type | Description |
|---|---|---|
| `x` | `int` | Horizontal coordinate to check. |
| `y` | `int` | Vertical coordinate to check. |

**Returns:** `bool` - `True` if the point is inside the box, `False` otherwise.
