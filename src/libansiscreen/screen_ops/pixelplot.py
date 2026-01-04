from __future__ import annotations
from typing import Optional, Tuple
from libansiscreen.screen import Screen
from libansiscreen.cell import Cell
from libansiscreen.color.rgb import Color
from libansiscreen.screen_ops import glyph_defs as G
from libansiscreen.color.palette import create_ansi_16_palette

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

def pixelget(screen, x, y):
    c=screen.get_cell(x, y//2)
    color=Color(0,0,255)
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

def pixel(screen, x, y, color):
    return pixelplot(screen, x, y, color)
plot=pixel

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

import math

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

