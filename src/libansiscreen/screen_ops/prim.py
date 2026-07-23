from __future__ import annotations

from typing import Optional, Dict, Callable, Tuple, Iterable

from ..framebuffer import frameBuffer
from ..cell import Cell
from ..screen_ops import glyph_defs as G

import math
from typing import Optional, Tuple
from ..cell import Cell as C
from ..color.rgb import Color
from ..screen_ops import glyph_defs as G
from ..color.palette import create_ansi_16_palette
from ..screen_ops.fill import fill as cell_fill
_ANSI16 = create_ansi_16_palette()
DEFAULT_FG = _ANSI16.index_to_rgb(7)   # light gray
DEFAULT_BG = _ANSI16.index_to_rgb(0)   # black
DEFAULT_CELL = Cell('X', DEFAULT_FG, DEFAULT_BG, 0)

# ============================================================
# Line merge support (explicit, opt-in)
# ============================================================

UP, DOWN, LEFT, RIGHT = 1, 2, 4, 8

GLYPH_CONNECTIONS = {
    G.LINE_SINGLE_H: LEFT | RIGHT,
    G.LINE_SINGLE_V: UP | DOWN,
    G.LINE_SINGLE_TL: DOWN | RIGHT,
    G.LINE_SINGLE_TR: DOWN | LEFT,
    G.LINE_SINGLE_BL: UP | RIGHT,
    G.LINE_SINGLE_BR: UP | LEFT,
    "├": UP | DOWN | RIGHT,
    "┤": UP | DOWN | LEFT,
    "┬": LEFT | RIGHT | DOWN,
    "┴": LEFT | RIGHT | UP,
    "┼": UP | DOWN | LEFT | RIGHT,
}

CONNECTIONS_TO_GLYPH = {v: k for k, v in GLYPH_CONNECTIONS.items()}


def merge_glyph(existing: Optional[str], new: Optional[str]) -> Optional[str]:
    if existing is None or new is None:
        return new
    a = GLYPH_CONNECTIONS.get(existing, 0)
    b = GLYPH_CONNECTIONS.get(new, 0)
    if not (a or b):
        return new
    return CONNECTIONS_TO_GLYPH.get(a | b, new)


def resolve_glyph(g):
    if callable(g):
        return g()
    return g

# ============================================================
# Horizontal line
# ============================================================

def hline(
    x1: int,
    x2: int,
    *,
    glyphs: Dict[str, Optional[str]],
    y: int = 0,
    fb: Optional[frameBuffer] = None,
    merge: bool = False,
) -> frameBuffer:
    if x2 < x1:
        x1, x2 = x2, x1
    width = x2 - x1 + 1
    scr = fb or frameBuffer(width)
    yy = y if fb else 0
    for i, x in enumerate(range(x1, x2 + 1)):
        role = "start" if i == 0 else "end" if i == width - 1 else "segment"
        g = resolve_glyph(glyphs.get(role))
        if g is None:
            continue
        cell = scr.get_cell(x, yy)
        char = merge_glyph(cell.char, g) if merge else g
        scr.set_cell(x, yy, Cell(char=char))
    return scr

# ============================================================
# Vertical line
# ============================================================

def vline(
    y1: int,
    y2: int,
    *,
    glyphs: Dict[str, Optional[str]],
    x: int = 0,
    fb: Optional[frameBuffer] = None,
    merge: bool = False,
) -> frameBuffer:
    if y2 < y1:
        y1, y2 = y2, y1
    height = y2 - y1 + 1
    scr = fb or frameBuffer(1)
    xx = x if fb else 0
    for i, y in enumerate(range(y1, y2 + 1)):
        role = "start" if i == 0 else "end" if i == height - 1 else "segment"
        g = resolve_glyph(glyphs.get(role))
        if g is None:
            continue
        cell = scr.get_cell(xx, y)
        char = merge_glyph(cell.char, g) if merge else g
        scr.set_cell(xx, y, Cell(char=char))
    return scr

# ============================================================
# Box (glyph-driven, transparency-aware)
# ============================================================

def box(
    w: int,
    h: int,
    *,
    glyphs: Dict[str, Optional[str]],
    fb: Optional[frameBuffer] = None,
) -> frameBuffer:
    scr = fb or frameBuffer(w)
    for y in range(h):
        for x in range(w):
            is_top = y == 0
            is_bottom = y == h - 1
            is_left = x == 0
            is_right = x == w - 1
            if is_top and is_left:
                key = "tl"
            elif is_top and is_right:
                key = "tr"
            elif is_bottom and is_left:
                key = "bl"
            elif is_bottom and is_right:
                key = "br"
            elif is_top or is_bottom:
                key = "h"
            elif is_left or is_right:
                key = "v"
            else:
                key = "fill"
            g = resolve_glyph(glyphs.get(key))
            if g is None:
                continue
            scr.set_cell(x, y, Cell(char=g))
    return scr

# ============================================================
# Stamp from screen
# ============================================================

def stamp_from_screen(
    source: frameBuffer,
    *,
    transparent_chars = [None,' '],
    box: Optional[Tuple[int, int, int, int]] = None,
    border_bg=None,
) -> frameBuffer:
    if box:
        x0, y0, w, h = box
    else:
        x0, y0 = 0, 0
        w, h = source.width, source.height
    out = frameBuffer(w)
    # Copy / punch transparency
    for y in range(h):
        for x in range(w):
            src = source.get_cell(x + x0, y + y0)
            if src.char in transparent_chars:
                continue
            out.set_cell(x, y, src.copy())
    # Optional border
    if border_bg:
        bg = border_bg  # default: black, passed explicitly
        def border_cell():
            return Cell(char=" ", bg=bg)
        for x in range(w):
            out.set_cell(x, 0, border_cell())
            out.set_cell(x, h - 1, border_cell())
        for y in range(h):
            out.set_cell(0, y, border_cell())
            out.set_cell(w - 1, y, border_cell())
    return out

def char_flood_fill(fb, x_seed, y_seed, ignore_fg_color=False, ignore_bg_color=False,fill=DEFAULT_FG):
    """
    Generate a mask from seed point that is complement of seed,
    respecting block types and optionally color/char matches.
    """
    width, height = fb.width, fb.height
    mask=frameBuffer(width=width)
    stack = [(x_seed, y_seed)]
    seed_cell = fb.get_cell(x_seed, y_seed)
    while stack:
        x, y = stack.pop()
        cell = fb.get_cell(x, y)
        if mask.get_cell(x, y).char is not None:
            continue  # already visited
        fill_pixel = False
        color_ok=True
        if not ignore_fg_color:
            if seed_cell.fg!=cell.fg:
                color_ok=False
        if not ignore_bg_color:
            if seed_cell.bg!=cell.bg:
                color_ok=False
        if color_ok:
            fill_pixel = (cell.char == seed_cell.char)
        if fill_pixel and color_ok:
            mask.set_cell(x, y, Cell(G.BLOCK_FULL, None, None))
            fb.set_cell(x, y, cell_fill(fill))
        else:
            mask.set_cell(x, y, Cell('x', None, None))
            continue
        # Push neighbors
        for nx, ny in [(x+1,y), (x-1,y), (x,y+1), (x,y-1)]:
            if 0 <= nx < width and 0 <= ny < height:
                stack.append((nx, ny))
    return mask

def char_rectangle(fb,x1, y1, x2, y2, fill=DEFAULT_FG):
    mask=frameBuffer(width=max(x1, x2)+1)
    for y in range(min(y1,y2), max(y1,y2)):
        for x in range(min(x1,x2),max(x1,x2)):
            mask.set_cell(x,y,Cell(G.BLOCK_FULL,None, None))
            fb.set_cell(x, y, cell_fill(fill))
    return mask

def char_ellipse(fb,cx, cy, rx, ry,fill=DEFAULT_FG):
    # Use fb dimensions for safe clamping
    fb_w = cx+rx+1
    fb_h = cy+ry+1
    mask = frameBuffer(width=fb_w)
    # Iterate from the top of the ellipse to the bottom
    for y in range(cy - ry, cy + ry + 1):
        # Skip rows outside the fb vertical bounds
        if y < 0 or y >= fb_h:
            continue
        # Standardize y relative to center
        dy = y - cy
        # Calculate the ratio of how far we are from the vertical center
        # We use float division to find the horizontal spread (dx)
        h_ratio = 1 - (dy**2 / ry**2)
        if h_ratio >= 0:
            dx = int(rx * math.sqrt(h_ratio))
            # Clamp to fb boundaries
            x_left = max(0, cx - dx)
            x_right = min(fb_w - 1, cx + dx) 
        for x in range(x_left,x_right+1):
            mask.set_cell(x,y,Cell(G.BLOCK_FULL,None,None))
            fb.set_cell(x, y, cell_fill(fill))
    return mask

def char_tile(fb, text):
    txt=' '
    if type(text)==str and len(text)>0:
        txt=text
    t=txt.split('\n')
    h=len(t)
    for y in range(fb.height):
        s=t[y%h]
        w=len(s)
        if w:
            for x in range(fb.width):
                c=fb.get_cell(x,y)
                fb.put_cell(x,y,char=t[y%h][x%w], fg=c.fg,bg=c.bg,attrs=0)

