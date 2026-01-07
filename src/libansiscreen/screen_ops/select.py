from __future__ import annotations
import math
from typing import Optional, Tuple
from libansiscreen.screen import Screen
from libansiscreen.cell import Cell
from libansiscreen import cell as  C
from libansiscreen.color.rgb import Color
from libansiscreen.screen_ops import glyph_defs as G
from libansiscreen.color.palette import create_ansi_16_palette

_ANSI16 = create_ansi_16_palette()
DEFAULT_FG = _ANSI16.index_to_rgb(7)   # light gray
DEFAULT_BG = _ANSI16.index_to_rgb(0)   # black

def flood_fill_pixel_mask(screen, x_seed, y_seed,):
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
        color = screen.pixelget(x, y)
        # Decide if this pixel is part of fill region
        if color==seed_color:
            mask.pixelplot(x,y,DEFAULT_FG)
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

def flood_fill_char_mask(screen, x_seed, y_seed, ignore_fg_color=False, ignore_bg_color=False,):
    """
    Generate a mask from seed point that is complement of seed,
    respecting block types and optionally color/char matches.
    """
    width, height = screen.width, screen.height
    mask=Screen(width=width)
    stack = [(x_seed, y_seed)]
    seed_cell = screen.get_cell(x_seed, y_seed)
    while stack:
        x, y = stack.pop()
        cell = screen.get_cell(x, y)
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
        else:
            mask.set_cell(x, y, Cell('x', None, None))
            continue
        # Push neighbors
        for nx, ny in [(x+1,y), (x-1,y), (x,y+1), (x,y-1)]:
            if 0 <= nx < width and 0 <= ny < height:
                stack.append((nx, ny))
    return mask

def rect_pixel_mask(x1, y1, x2, y2):
    mask=Screen(width=max(x1, x2)+1)
    for y in range(min(y1,y2), max(y1,y2)):
        for x in range(min(x1,x2),max(x1,x2)):
            mask.pixelplot(x,y,DEFAULT_FG)
    return mask

def rect_char_mask( x1, y1, x2, y2):
    mask=Screen(width=max(x1, x2)+1)
    for y in range(min(y1,y2), max(y1,y2)):
        for x in range(min(x1,x2),max(x1,x2)):
            mask.set_cell(x,y,Cell(G.BLOCK_FULL,None, None))
    return mask

def ellipse_pixel_mask(cx, cy, rx, ry):
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
    return mask

def ellipse_char_mask(cx, cy, rx, ry):
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
        for x in range(x_left,x_right+1):
            mask.set_cell(x,y,Cell(G.BLOCK_FULL,None,None))
    return mask

def stamp_pixel_mask(screen, stamp):
    pass

def stamp_char_mask(screen, stamp):
    pass
