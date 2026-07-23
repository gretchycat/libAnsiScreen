from __future__ import annotations
from ..framebuffer import frameBuffer
from ..cell import Cell
from .pixelplot import regular_polygon, regular_star
import math

# simulated graphic framebuffer
# using the braille characters.
# these functions work on a monochrome pixel grid.
# states are untouched and can be set separately

def is_braille(char):
    if isinstance(char, str) and len(char) == 1:
        return 0x2800 <= ord(char) <= 0x28FF
    return False

def braille_plot(fb:frameBuffer, x, y, state):
    vx = x // 2
    vy = y // 4
    bx = x % 2
    by = y % 4

    bit_masks = [
        [0x01, 0x02, 0x04, 0x40],  # bx = 0
        [0x08, 0x10, 0x20, 0x80]   # bx = 1
    ]
    mask = bit_masks[bx][by]

    current = fb.get_cell(vx, vy)
    
    if not isinstance(current, Cell):
        current=Cell()
    # Convert string char to integer code point (default to U+2800 if not braille)
    if is_braille(current.char):
        code_point = ord(current.char)
    else:
        code_point = 0x2800

    if state:
        code_point |= mask
    else:
        code_point &= ~mask

    # Write back as character string
    current.char = chr(code_point)
    fb.set_cell(vx, vy, current)

def braille_get(fb:frameBuffer, x, y):
    vx = x // 2
    vy = y // 4
    c =''
    current = fb.get_cell(vx, vy)
    if isinstance(current, Cell):
        c=current.char
    else: return False
    if is_braille(c):
        bx = x % 2
        by = y % 4
        bit_masks = [
            [0x01, 0x02, 0x04, 0x40],
            [0x08, 0x10, 0x20, 0x80]
        ]
        code_point = ord(c) if isinstance(c, str) else c
        return bool(code_point & bit_masks[bx][by])
    return False

def braille_draw_line(fb:frameBuffer, x0, y0, x1, y1, state):
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
            braille_plot(fb, x, y, state)
            err -= dy
            if err < 0:
                y += sy
                err += dx
            x += sx
    else:
        err = dy // 2
        while y != y1:
            braille_plot(fb, x, y, state)
            err -= dx
            if err < 0:
                x += sx
                err += dy
            y += sy
    # plot last point
    braille_plot(fb, x1, y1, state)

def braille_draw_polyline(fb:frameBuffer, points, state):
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
        braille_draw_line(fb, x0, y0, x1, y1, state)

def braille_draw_regular_polygon(fb:frameBuffer, cx, cy, radius, sides, state, rotation=0.0):
    """
    Draw a regular convex polygon by generating vertices and drawing a polyline.
    """
    points = regular_polygon(cx, cy, radius, sides, rotation)
    braille_draw_polyline(fb, points, state)

def braille_draw_regular_star(fb:frameBuffer, cx, cy, radius, n, k, state, rotation=0.0):
    """
    Draw a regular star polygon {n/k}.
    """
    points = regular_star(cx, cy, radius, n, k, rotation)
    braille_draw_polyline(fb, points, state)

def braille_flood_fill(fb: frameBuffer, x_seed: int, y_seed: int, state:bool):
    """
    4-way stack-based flood fill on the virtual braille pixel grid.
    Replaces contiguous pixels matching the state at (x_seed, y_seed) with `state`.
    """
    # Max dimensions in virtual braille pixels (2 horizontal, 4 vertical per cell)
    max_x = fb.width * 2
    max_y = fb.height * 4

    # Seed bounds check
    if not (0 <= x_seed < max_x and 0 <= y_seed < max_y):
        return

    # Get initial pixel state at seed point
    target_state = braille_get(fb, x_seed, y_seed)

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
        if braille_get(fb, x, y) == target_state:
            braille_plot(fb, x, y, state)
            
            # Push 4-way adjacent pixels
            stack.append((x + 1, y))
            stack.append((x - 1, y))
            stack.append((x, y + 1))
            stack.append((x, y - 1))

def braille_draw_rectangle(fb:frameBuffer, x1, y1, x2, y2, state, fill=False):
    min_x, max_x = min(x1, x2), max(x1, x2)
    min_y, max_y = min(y1, y2), max(y1, y2)

    if fill:
        for y in range(min_y, max_y + 1):
            braille_draw_line(fb, min_x, y, max_x, y, state)
    else:
        # Top and bottom horizontal edges
        braille_draw_line(fb, min_x, min_y, max_x, min_y, state)
        braille_draw_line(fb, min_x, max_y, max_x, max_y, state)
        # Left and right vertical edges
        braille_draw_line(fb, min_x, min_y, min_x, max_y, state)
        braille_draw_line(fb, max_x, min_y, max_x, max_y, state)

def braille_draw_ellipse(fb:frameBuffer, cx, cy, rx, ry, state, fill=False):
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
                braille_draw_line(fb, x_left, y, x_right, y, state)
            else:
                braille_plot(fb, x_left, y, state)
                braille_plot(fb, x_right, y, state)

