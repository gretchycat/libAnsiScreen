from __future__ import annotations
from ..framebuffer import frameBuffer
from ..cell import Cell
from .pixel import regular_polygon, regular_star
import math

# simulated graphic framebuffer
# using the octant characters.
# these functions work on a monochrome pixel grid.
# color and attribute states are untouched and can be set separately

# Modes
MODE_BRAILLE = "braille"
MODE_OCTANT = "octant"
MODE_QUADRANT = "quadrant"

# ==============================================================================
# 1. BRAILLE MODE LOOKUPS (2x4 Grid, U+2800..U+28FF)
# ==============================================================================
# Mapping (bx, by) -> Braille bitmask value
BRAILLE_BIT_MASKS = [
    [0x01, 0x02, 0x04, 0x40],  # bx = 0 (Left column: dots 1, 2, 3, 7)
    [0x08, 0x10, 0x20, 0x80]   # bx = 1 (Right column: dots 4, 5, 6, 8)
]

# ==============================================================================
# 2. BLOCK OCTANT MODE LOOKUPS (2x4 Grid, Symbols for Legacy Computing)
# ==============================================================================
# Mapping (bx, by) -> bit index 0..7
OCTANT_BIT_MASKS = [
    [0x01, 0x04, 0x10, 0x40],  # bx = 0 (Left column: rows 0, 1, 2, 3 -> bits 0, 2, 4, 6)
    [0x02, 0x08, 0x20, 0x80]   # bx = 1 (Right column: rows 0, 1, 2, 3 -> bits 1, 3, 5, 7)
]

# ==============================================================================
# 3. BLOCK QUADRANT MODE LOOKUPS (2x2 Grid, Block Elements)
# ==============================================================================
# Mapping (bx, by) -> bit index 0..3
QUADRANT_BIT_MASKS = [
    [0x01, 0x04],  # bx = 0 (Left column:  rows 0, 1 -> bits 0, 2)
    [0x02, 0x08]   # bx = 1 (Right column: rows 0, 1 -> bits 1, 3)
]

# Map 8-bit mask (0..255) to Unicode code point
# 0 maps to space (' '), 255 to full block ('█')
OCTANT_CHARS = [' '] * 256
OCTANT_CHARS[0] = ' '
OCTANT_CHARS[255] = '\u2588'  # Full block

for mask in range(1, 255):
    # Unicode Legacy Computing Supplement: Block Octants span U+1CD00 to U+1CDE5
    # The code point offset follows the 8-bit binary value directly
    OCTANT_CHARS[mask] = chr(0x1CD00 + mask - 1)

OCTANT_MAP = {char: mask for mask, char in enumerate(OCTANT_CHARS)}

# 4-bit bitmask [TR, TL, BR, BL] -> Quadrant Character Map (16 total states)
# Bit 0 (0x1): Top-Left     (x=0, y=0)
# Bit 1 (0x2): Top-Right    (x=1, y=0)
# Bit 2 (0x4): Bottom-Left  (x=0, y=1)
# Bit 3 (0x8): Bottom-Right (x=1, y=1)
QUADRANT_CHARS = [
    ' ',       # 0b0000 (0)  - Empty space
    '\u2598',  # 0b0001 (1)  - ▘ Top-Left
    '\u259d',  # 0b0010 (2)  - ▝ Top-Right
    '\u2580',  # 0b0011 (3)  - ▀ Upper Half
    '\u2596',  # 0b0100 (4)  - ▖ Bottom-Left
    '\u258c',  # 0b0101 (5)  - ▌ Left Half
    '\u259e',  # 0b0110 (6)  - ▞ Top-Right + Bottom-Left
    '\u259b',  # 0b0111 (7)  - ▛ Top-Left + Top-Right + Bottom-Left
    '\u2597',  # 0b1000 (8)  - ▗ Bottom-Right
    '\u259a',  # 0b1001 (9)  - ▚ Top-Left + Bottom-Right
    '\u2590',  # 0b1010 (10) - ▐ Right Half
    '\u259c',  # 0b1011 (11) - ▜ Top-Left + Top-Right + Bottom-Right
    '\u2584',  # 0b1100 (12) - ▄ Lower Half
    '\u2599',  # 0b1101 (13) - ▙ Top-Left + Bottom-Left + Bottom-Right
    '\u259f',  # 0b1110 (14) - ▟ Top-Right + Bottom-Left + Bottom-Right
    '\u2588',  # 0b1111 (15) - █ Full Block
]

# Fast character -> 4-bit bitmask reverse lookup
QUADRANT_MAP = {char: mask for mask, char in enumerate(QUADRANT_CHARS)}

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
    return False

def spixel_plot(fb: frameBuffer, x, y, state, mode=MODE_OCTANT):
    vx = x // 2
    vy = y // 2
    bx = x % 2
    by = y % 2
    if mode in [ MODE_BRAILLE, MODE_OCTANT]:
        vy = y // 4
        by = y % 4
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
    fb.set_cell(vx,vy, current)

def spixel_get(fb: frameBuffer, x, y, mode=MODE_OCTANT):
    vx = x // 2
    vy = y // 2
    bx = x % 2
    by = y % 2
    if mode in [ MODE_BRAILLE, MODE_OCTANT]:
        vy = y // 4
        by = y % 4
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
    return False

def spixel_draw_line(fb:frameBuffer, x0, y0, x1, y1, state, mode=MODE_OCTANT):
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

def spixel_draw_polyline(fb:frameBuffer, points, state, mode=MODE_OCTANT):
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
        spixel_draw_line(fb, x0, y0, x1, y1, state, mode=mode)

def spixel_draw_regular_polygon(fb:frameBuffer, cx, cy, radius, sides, state, rotation=0.0, mode=MODE_OCTANT):
    """
    Draw a regular convex polygon by generating vertices and drawing a polyline.
    """
    points = regular_polygon(cx, cy, radius, sides, rotation)
    spixel_draw_polyline(fb, points, state, mode=mode)

def spixel_draw_regular_star(fb:frameBuffer, cx, cy, radius, n, k, state, rotation=0.0, mode=MODE_OCTANT):
    """
    Draw a regular star polygon {n/k}.
    """
    points = regular_star(cx, cy, radius, n, k, rotation)
    spixel_draw_polyline(fb, points, state, mode=mode)

def spixel_flood_fill(fb: frameBuffer, x_seed: int, y_seed: int, state:bool, mode=MODE_OCTANT):
    """
    4-way stack-based flood fill on the virtual octant pixel grid.
    Replaces contiguous pixels matching the state at (x_seed, y_seed) with `state`.
    """
    # Max dimensions in virtual octant pixels (2 horizontal, 4 vertical per cell)
    max_x = fb.width * 2
    max_y = fb.height * 4

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

def spixel_draw_rectangle(fb:frameBuffer, x1, y1, x2, y2, state, fill=False, mode=MODE_OCTANT):
    min_x, max_x = min(x1, x2), max(x1, x2)
    min_y, max_y = min(y1, y2), max(y1, y2)

    if fill:
        for y in range(min_y, max_y + 1):
            spixel_draw_line(fb, min_x, y, max_x, y, state, mode=mode)
    else:
        # Top and bottom horizontal edges
        spixel_draw_line(fb, min_x, min_y, max_x, min_y, state, mode=mode)
        spixel_draw_line(fb, min_x, max_y, max_x, max_y, state, mode=mode)
        # Left and right vertical edges
        spixel_draw_line(fb, min_x, min_y, min_x, max_y, state, mode=mode)
        spixel_draw_line(fb, max_x, min_y, max_x, max_y, state, mode=mode)

def spixel_draw_ellipse(fb:frameBuffer, cx, cy, rx, ry, state, fill=False, mode=MODE_OCTANT):
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
                spixel_draw_line(fb, x_left, y, x_right, y, state, mode=mode)
            else:
                spixel_plot(fb, x_left, y, state, mode=mode)
                spixel_plot(fb, x_right, y, state, mode=mode)

