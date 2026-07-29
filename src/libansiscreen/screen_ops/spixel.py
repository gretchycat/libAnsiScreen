from __future__ import annotations
from ..framebuffer import frameBuffer
from ..cell import Cell
from .pixel import regular_polygon, regular_star
from .quadrants import get_quadrant_array
from .sextants import get_sextant_array
from .octants import get_octant_array
import math

# simulated graphic framebuffer
# using the octant characters.
# these functions work on a monochrome pixel grid.
# color and attribute states are untouched and can be set separately

# Modes
MODE_BRAILLE = "braille"
MODE_QUADRANT = "quadrant"
MODE_SEXTANT = "sextant"
MODE_OCTANT = "octant"

# ==============================================================================
# BRAILLE MODE LOOKUPS (2x4 Grid, U+2800..U+28FF)
# ==============================================================================
# Mapping (bx, by) -> Braille bitmask value
BRAILLE_BIT_MASKS = [
    [0x01, 0x02, 0x04, 0x40],  # bx = 0 (Left column: dots 1, 2, 3, 7)
    [0x08, 0x10, 0x20, 0x80]   # bx = 1 (Right column: dots 4, 5, 6, 8)
]

# ==============================================================================
# BLOCK QUADRANT MODE LOOKUPS (2x2 Grid, Block Elements)
# ==============================================================================
QUADRANT_BIT_MASKS = [
    [0x01, 0x04],  # bx = 0 (Left column:  rows 0, 1 -> bits 0, 2)
    [0x02, 0x08]   # bx = 1 (Right column: rows 0, 1 -> bits 1, 3)
]
QUADRANT_CHARS = get_quadrant_array()
QUADRANT_MAP = {char: mask for mask, char in enumerate(QUADRANT_CHARS)}

# ==============================================================================
# BLOCK SEXTANT MODE LOOKUPS (2x3 Grid, Symbols for Legacy Computing)
# ==============================================================================
SEXTANT_BIT_MASKS = [
    [0x01, 0x04, 0x10],  # bx = 0 (Left column:  subpixels 1, 3, 5)
    [0x02, 0x08, 0x20]   # bx = 1 (Right column: subpixels 2, 4, 6)
]
SEXTANT_CHARS = get_sextant_array()
SEXTANT_MAP = {char: mask for mask, char in enumerate(SEXTANT_CHARS)}

# ==============================================================================
# BLOCK OCTANT MODE LOOKUPS (2x4 Grid, Symbols for Legacy Computing)
# ==============================================================================
OCTANT_BIT_MASKS = [
    [0x01, 0x04, 0x10, 0x40],  # bx = 0 (Left column:  Octants 1, 3, 5, 7)
    [0x02, 0x08, 0x20, 0x80]   # bx = 1 (Right column: Octants 2, 4, 6, 8)
]
OCTANT_CHARS = get_octant_array()
OCTANT_MAP = {char: mask for mask, char in enumerate(OCTANT_CHARS)}

# ==============================================================================
# HELPERS & PLOTTING FUNCTIONS
# ==============================================================================
def is_subpixel_char(char, mode=MODE_OCTANT):
    if not (isinstance(char, str) and len(char) == 1):
        return False
    if mode == MODE_BRAILLE:
        return 0x2800 <= ord(char) <= 0x28FF
    elif mode == MODE_OCTANT:
        return char in OCTANT_MAP
    elif mode == MODE_QUADRANT:
        return char in QUADRANT_MAP
    elif mode == MODE_SEXTANT:
        return char in SEXTANT_MAP or (0x1FB00 <= ord(char) <= 0x1FB3F)
    return False

def spixel_plot(fb: frameBuffer, x, y, state, mode=MODE_OCTANT):
    vx = x // 2
    vy = y // 2
    bx = x % 2
    by = y % 2
    if mode in [ MODE_BRAILLE, MODE_OCTANT]:
        vy = y // 4
        by = y % 4
    elif mode == MODE_SEXTANT:
        vy = y // 3
        by = y % 3
    current = fb.get_cell(vx, vy)
    if not isinstance(current, Cell):
        current = Cell()
    if mode == MODE_BRAILLE:
        mask = BRAILLE_BIT_MASKS[bx][by]
        code_point = ord(current.char) if is_subpixel_char(current.char, MODE_BRAILLE) else 0x2800
        if state:
            code_point |= mask
        else:
            code_point &= ~mask
        current.char = chr(code_point)
    elif mode == MODE_OCTANT:
        mask = OCTANT_BIT_MASKS[bx][by]
        bitmask = OCTANT_MAP[current.char] if is_subpixel_char(current.char, MODE_OCTANT) else 0
        if state:
            bitmask |= mask
        else:
            bitmask &= ~mask
        current.char = OCTANT_CHARS[bitmask]
    elif mode == MODE_QUADRANT:
        mask = QUADRANT_BIT_MASKS[bx][by]
        bitmask = QUADRANT_MAP[current.char] if is_subpixel_char(current.char, MODE_QUADRANT) else 0
        if state:
            bitmask |= mask
        else:
            bitmask &= ~mask
        current.char = QUADRANT_CHARS[bitmask]
    elif mode == MODE_SEXTANT:
        mask = SEXTANT_BIT_MASKS[bx][by]
        bitmask = SEXTANT_MAP[current.char] if is_subpixel_char(current.char, MODE_SEXTANT) else 0
        if state:
            bitmask |= mask
        else:
            bitmask &= ~mask
        current.char = SEXTANT_CHARS[bitmask]
    fb.set_cell(vx,vy, current)

def spixel_get(fb: frameBuffer, x, y, mode=MODE_OCTANT):
    vx = x // 2
    vy = y // 2
    bx = x % 2
    by = y % 2
    if mode in [ MODE_BRAILLE, MODE_OCTANT]:
        vy = y // 4
        by = y % 4
    elif mode == MODE_SEXTANT:
        vy = y // 3
        by = y % 3
    current = fb.get_cell(vx, vy)
    if not isinstance(current, Cell):
        return False
    if mode == MODE_BRAILLE and is_subpixel_char(current.char, MODE_BRAILLE):
        mask = BRAILLE_BIT_MASKS[bx][by]
        return bool(ord(current.char) & mask)
    elif mode == MODE_OCTANT and is_subpixel_char(current.char, MODE_OCTANT):
        mask = OCTANT_BIT_MASKS[bx][by]
        bitmask = OCTANT_MAP[current.char]
        return bool(bitmask & mask)
    elif mode == MODE_QUADRANT and is_subpixel_char(current.char, MODE_QUADRANT):
        mask = QUADRANT_BIT_MASKS[bx][by]
        bitmask = QUADRANT_MAP[current.char]
        return bool(bitmask & mask)
    elif mode == MODE_SEXTANT and is_subpixel_char(current.char, MODE_SEXTANT):
        mask = SEXTANT_BIT_MASKS[bx][by]
        bitmask = SEXTANT_MAP[current.char]
        return bool(bitmask & mask)
    return False

def spixel_line(fb:frameBuffer, x0, y0, x1, y1, state, mode=MODE_OCTANT):
    """
    Draw a line from (x0, y0) to (x1, y1) using pixelplot.
    Works for all slopes, arbitrary start/end.
    """
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    x, y = x0, y0

    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1

    if dx > dy:
        err = dx // 2
        while x != x1:
            spixel_plot(fb, x, y, state, mode=mode)
            err -= dy
            if err < 0:
                y += sy
                err += dx
            x += sx
    else:
        err = dy // 2
        while y != y1:
            spixel_plot(fb, x, y, state, mode=mode)
            err -= dx
            if err < 0:
                x += sx
                err += dy
            y += sy
    # plot last point
    spixel_plot(fb, x1, y1, state, mode=mode)

def spixel_polyline(fb:frameBuffer, points, state, mode=MODE_OCTANT):
    """
    Draw multiple connected lines.
    points: list of (x, y) tuples
    state: state object
    """
    if len(points) < 2:
        return  # nothing to draw

    for i in range(len(points) - 1):
        x0, y0 = points[i]
        x1, y1 = points[i + 1]
        spixel_line(fb, x0, y0, x1, y1, state, mode=mode)

def spixel_regular_polygon(fb:frameBuffer, cx, cy, radius, sides, state, rotation=0.0, mode=MODE_OCTANT):
    """
    Draw a regular convex polygon by generating vertices and drawing a polyline.
    """
    points = regular_polygon(cx, cy, radius, sides, rotation)
    spixel_polyline(fb, points, state, mode=mode)

def spixel_regular_star(fb:frameBuffer, cx, cy, radius, n, k, state, rotation=0.0, mode=MODE_OCTANT):
    """
    Draw a regular star polygon {n/k}.
    """
    points = regular_star(cx, cy, radius, n, k, rotation)
    spixel_polyline(fb, points, state, mode=mode)

def spixel_flood_fill(fb: frameBuffer, x_seed: int, y_seed: int, state:bool, mode=MODE_OCTANT):
    """
    4-way stack-based flood fill on the virtual octant pixel grid.
    Replaces contiguous pixels matching the state at (x_seed, y_seed) with `state`.
    """
    # Max dimensions in virtual subpixels depending on mode
    max_x = fb.width * 2
    if mode in [MODE_BRAILLE, MODE_OCTANT]:
        max_y = fb.height * 4
    elif mode == MODE_SEXTANT:
        max_y = fb.height * 3
    else:
        max_y = fb.height * 2

    # Seed bounds check
    if not (0 <= x_seed < max_x and 0 <= y_seed < max_y):
        return

    # Get initial pixel state at seed point
    target_state = spixel_get(fb, x_seed, y_seed, mode=mode)

    # Nothing to fill if seed pixel is already set to target fill state
    if target_state == state:
        return

    stack = [(x_seed, y_seed)]
    visited = set()

    while stack:
        x, y = stack.pop()

        if (x, y) in visited:
            continue
        visited.add((x, y))

        # Check bounds
        if not (0 <= x < max_x and 0 <= y < max_y):
            continue

        # Match pixel state to target_state
        if spixel_get(fb, x, y, mode=mode) == target_state:
            spixel_plot(fb, x, y, state, mode=mode)

            # Push 4-way adjacent pixels
            stack.append((x + 1, y))
            stack.append((x - 1, y))
            stack.append((x, y + 1))
            stack.append((x, y - 1))

def spixel_rectangle(fb:frameBuffer, x1, y1, x2, y2, state, fill=False, mode=MODE_OCTANT):
    min_x, max_x = min(x1, x2), max(x1, x2)
    min_y, max_y = min(y1, y2), max(y1, y2)

    if fill:
        for y in range(min_y, max_y + 1):
            spixel_line(fb, min_x, y, max_x, y, state, mode=mode)
    else:
        # Top and bottom horizontal edges
        spixel_line(fb, min_x, min_y, max_x, min_y, state, mode=mode)
        spixel_line(fb, min_x, max_y, max_x, max_y, state, mode=mode)
        # Left and right vertical edges
        spixel_line(fb, min_x, min_y, min_x, max_y, state, mode=mode)
        spixel_line(fb, max_x, min_y, max_x, max_y, state, mode=mode)

def spixel_ellipse(fb:frameBuffer, cx, cy, rx, ry, state, fill=False, mode=MODE_OCTANT):
    if rx <= 0 or ry <= 0:
        return

    for y in range(cy - ry, cy + ry + 1):
        dy = y - cy
        h_ratio = 1 - (dy**2 / ry**2)
        if h_ratio >= 0:
            dx = int(rx * math.sqrt(h_ratio))
            x_left = cx - dx
            x_right = cx + dx

            if fill:
                spixel_line(fb, x_left, y, x_right, y, state, mode=mode)
            else:
                spixel_plot(fb, x_left, y, state, mode=mode)
                spixel_plot(fb, x_right, y, state, mode=mode)

