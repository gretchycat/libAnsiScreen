from __future__ import annotations
from typing import Optional, Tuple
from libansiscreen.screen import Screen
from libansiscreen.cell import Cell
from libansiscreen.color.rgb import Color
from libansiscreen.screen_ops import glyph_defs as G

def flood_fill_mask(
    screen, x_seed, y_seed,
    ignore_fg_color=False,
    ignore_bg_color=False,
):
    """
    Generate a mask from seed point that is complement of seed,
    respecting block types and optionally color/char matches.
    """
    width, height = screen.width, screen.height
    mask=Screen(width=width)
    stack = [(x_seed, y_seed)]
    seed_cell = screen.get_cell(x_seed, y_seed)
        match_block_type=False
    if seed_cell==FULL_BLOCK
        match_block_type=True
    while stack:
        x, y = stack.pop()
        cell = screen.get_cell(x, y)
        if mask.get_cell(x, y) is not None:
            continue  # already visited
        # Decide if this pixel is part of fill region
        fill_pixel = False
        color_ok=True
        if not ignore_fg_color:
            if seed_cell.fg!=cell.fg:
                color_ok=False
        if not ignore_bg_color:
            if seed_cell.bg!=cell.bg:
                color_ok=False
        if color_ok:
            if seed_cell.char is not None:
                fill_pixel = (cell.char == seed_cell.char)
            elif match_block_type:
                fill_pixel = (cell.char in (BLOCK_FULL, BLOCK_TOP, BLOCK_BOTTOM, BLOCK_LEFT, BLOCK_RIGHT))
            else:
                fill_pixel = True  # default: any non-blocked pixel
        if fill_pixel:
            # Determine subpixel occupancy
            if(match_block_type):
                elif cell.char == FULL_BLOCK:
                    mask.set_cell(x, y, Cell(FULL_BLOCK , None, None))
                elif cell.char == BLOCK_TOP:
                    mask.set_cell(x, y, Cell(BLOCK_TOP, None, None))
                elif cell.char == BLOCK_BOTTOM:
                    mask.set_cell(x, y, Cell(BLOCK_BOTTOM, None, None))
                elif cell.char == BLOCK_LEFT:
                    mask.set_cell(x, y, Cell(BLOCK_LEFT, None, None))
                elif cell.char == BLOCK_RIGHT:
                    mask.set_cell(x, y, Cell(BLOCK_RIGHT, None, None)) 
            elif cell.char == seed_cell.char:
                mask.set_cell(x, y, Cell(BLOCK_FULL, None, None))
            else:
                mask.set_cell(x, y, Cell('x', None, None))
            # Push neighbors
            for nx, ny in [(x+1,y), (x-1,y), (x,y+1), (x,y-1)]:
                if 0 <= nx < width and 0 <= ny < height:
                    if mask.get_cell(nx, ny) is None:
                        stack.append((nx, ny))
    return mask
