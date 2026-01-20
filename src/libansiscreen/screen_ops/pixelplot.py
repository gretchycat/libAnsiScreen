from __future__ import annotations
from typing import Optional, Tuple
from libansiscreen.screen import Screen
from libansiscreen.cell import Cell
from libansiscreen import cell as C
from libansiscreen.color.rgb import Color
from libansiscreen.screen_ops import glyph_defs as G
from libansiscreen.screen_ops.fill import block_fill
from libansiscreen.color.palette import create_ansi_16_palette
import math

_ANSI16 = create_ansi_16_palette()
DEFAULT_FG = _ANSI16.index_to_rgb(7)   # light gray
DEFAULT_BG = _ANSI16.index_to_rgb(0)   # black

# simulated graphic framebuffer
# using the "█", "▀" "▄", " " characters.
# brighter color is solid.
# same bright color is solid fg color. same dim color is ' ' bg color
# if a color/char is set, set both fg/bg intelligently

def make_cell(c1, c2):
    if c1 is None:
        c1=DEFAULT_BG
    if c2 is None:
        c2=DEFAULT_BG
    if c1==c2:
        if c1==DEFAULT_BG:
            return Cell(' ', c1, c2)
        return Cell(G.BLOCK_FULL, c1, None)
    if c1>c2:
        return Cell(G.BLOCK_TOP, c1, c2)
    return Cell(G.BLOCK_BOTTOM, c2, c1)

def pixelplot(screen, x, y, color):
    c=screen.get_cell(x, y//2)
    if c:
        if y%2==0: #top block
            if c.char==G.BLOCK_BOTTOM:
                c=make_cell(color, c.fg)
            elif c.char==G.BLOCK_FULL:
                c=make_cell(color, c.fg)
            elif c.char==G.BLOCK_TOP:
                c=make_cell(color, c.bg)
            else:
                c=make_cell(color, c.bg)
        else:   #bottom block
            if c.char==G.BLOCK_TOP:
                c=make_cell(c.fg, color)
            elif c.char==G.BLOCK_FULL:
                c=make_cell(c.fg, color)
            elif c.char==G.BLOCK_BOTTOM:
                c=make_cell(c.bg, color)
            else:
                c=make_cell(c.bg, color)
        screen.set_cell(x,y//2, c)

pixel=pixelplot
plot=pixel

def pixelget(screen, x, y):
    c=screen.get_cell(x, y//2)
    color=DEFAULT_BG
    if c:
        if y%2==0: #top block
            if c.char==G.BLOCK_BOTTOM:
                color=c.bg or DEFAULT_BG
            elif c.char==G.BLOCK_FULL:
                color=c.fg or DEFAULT_FG
            elif c.char==G.BLOCK_TOP:
                color=c.fg or DEFAULT_FG
            else:
                color=c.bg or DEFAULT_BG
        else:   #bottom block
            if c.char==G.BLOCK_TOP:
                color=c.bg or DEFAULT_BG
            elif c.char==G.BLOCK_FULL:
                color=c.fg or DEFAULT_FG
            elif c.char==G.BLOCK_BOTTOM:
                color=c.fg or DEFAULT_FG
            else:
                color=c.bg or DEFAULT_BG
    return color

def draw_line(screen, x0, y0, x1, y1, color):
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
            pixelplot(screen, x, y, color)
            err -= dy
            if err < 0:
                y += sy
                err += dx
            x += sx
    else:
        err = dy // 2
        while y != y1:
            pixelplot(screen, x, y, color)
            err -= dx
            if err < 0:
                x += sx
                err += dy
            y += sy
    # plot last point
    pixelplot(screen, x1, y1, color)

def draw_polyline(screen, points, color):
    """
    Draw multiple connected lines.
    points: list of (x, y) tuples
    color: Color object
    """
    if len(points) < 2:
        return  # nothing to draw

    for i in range(len(points) - 1):
        x0, y0 = points[i]
        x1, y1 = points[i + 1]
        draw_line(screen, x0, y0, x1, y1, color)

def regular_polygon(cx, cy, radius, sides, rotation=0.0):
    points = []
    step = 2 * math.pi / sides

    for i in range(sides):
        angle = rotation + i * step
        x = int(round(cx + radius * math.cos(angle)))
        y = int(round(cy + radius * math.sin(angle)))
        points.append((x, y))

    points.append(points[0])  # close the shape
    return points

def draw_regular_polygon(screen, cx, cy, radius, sides, color, rotation=0.0):
    """
    Draw a regular convex polygon by generating vertices and drawing a polyline.
    """
    points = regular_polygon(cx, cy, radius, sides, rotation)
    draw_polyline(screen, points, color)

def regular_star(cx, cy, radius, n, k, rotation=0.0):
    import math

    if k <= 0 or k >= n:
        raise ValueError("k must satisfy 0 < k < n")

    # Precompute circle points
    circle = []
    step = 2 * math.pi / n

    for i in range(n):
        angle = rotation + i * step
        x = int(round(cx + radius * math.cos(angle)))
        y = int(round(cy + radius * math.sin(angle)))
        circle.append((x, y))

    # Generate star order
    points = []
    index = 0
    visited = set()

    while index not in visited:
        visited.add(index)
        points.append(circle[index])
        index = (index + k) % n

    points.append(points[0])  # close
    return points

def draw_regular_star(screen, cx, cy, radius, n, k, color, rotation=0.0):
    """
    Draw a regular star polygon {n/k}.
    """
    points = regular_star(cx, cy, radius, n, k, rotation)
    draw_polyline(screen, points, color)

def flood_fill(screen, x_seed, y_seed,color=None):
    """
    Generate a mask from seed point that is complement of seed,
    respecting block types and optionally color/char matches.
    """
    width, height = screen.width, screen.height*2
    mask=Screen(width=width)
    stack = [(x_seed, y_seed)]
    seed_color = screen.pixelget(x_seed,y_seed)
    while stack:
        x, y = stack.pop()
        mcell=mask.get_cell(x, y//2)
        if mask.pixelget(x, y) == DEFAULT_FG:
            continue    # already visited
        mcell=mask.get_cell(x, y//2)
        if y%2==1:
            if mcell.attrs & C.ATTR_UNDERLINE:
                continue  # already visited
        else:
            if mcell.attrs & C.ATTR_STRIKE:
                continue  # already visited
        colorx = screen.pixelget(x, y)
        # Decide if this pixel is part of fill region
        if colorx==seed_color:
            mask.pixelplot(x,y,DEFAULT_FG)
            if color:
                screen.pixelplot(x,y,color)
        else:
            mcell=mask.get_cell(x, y//2)
            a=mcell.attrs or 0
            if y%2==1:
                mask.set_cell(x,y//2, Cell(mcell.char, mcell.fg, mcell.bg, a | C.ATTR_UNDERLINE))
            else:
                mask.set_cell(x,y//2, Cell(mcell.char, mcell.fg, mcell.bg, a | C.ATTR_STRIKE))
            continue
        # Push neighbors
        for nx, ny in [(x+1,y), (x-1,y), (x,y+1), (x,y-1)]:
            if 0 <= nx < width and 0 <= ny < height:
                stack.append((nx, ny))
    return mask

def draw_rectangle(screen,x1, y1, x2, y2,color=None):
    mask=Screen(width=max(x1, x2)+1)
    for y in range(min(y1,y2), max(y1,y2)):
        for x in range(min(x1,x2),max(x1,x2)):
            mask.pixelplot(x,y,DEFAULT_FG)
            if screen and color:
                screen.pixelplot(x,y,color)
    return mask

def draw_ellipse(screen, cx, cy, rx, ry, color=None):
    # Use screen dimensions for safe clamping
    screen_w = cx+rx+1
    screen_h = cy+ry+1
    mask = Screen(width=screen_w)
    # Iterate from the top of the ellipse to the bottom
    for y in range(cy - ry, cy + ry + 1):
        # Skip rows outside the screen vertical bounds
        if y < 0 or y >= screen_h:
            continue
        # Standardize y relative to center
        dy = y - cy
        # Calculate the ratio of how far we are from the vertical center
        # We use float division to find the horizontal spread (dx)
        h_ratio = 1 - (dy**2 / ry**2)
        if h_ratio >= 0:
            dx = int(rx * math.sqrt(h_ratio))
            # Clamp to screen boundaries
            x_left = max(0, cx - dx)
            x_right = min(screen_w - 1, cx + dx)
            mask.line(x_left, y, x_right, y, DEFAULT_FG)
            if screen and color:
                screen.line(x_left,y,x_right, y, color)
    return mask

