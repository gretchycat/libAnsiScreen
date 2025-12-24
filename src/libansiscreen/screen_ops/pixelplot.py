from __future__ import annotations
from typing import Optional, Tuple
from libansiscreen.screen import Screen
from libansiscreen.cell import Cell
from libansiscreen.color.rgb import Color
from libansiscreen.screen_ops import glyph_defs as G

# simulated graphic framebuffer
# using the "█", "▀" "▄", " " characters.
# brighter color is solid.
# same bright color is solid fg color. same dim color is ' ' bg color
# if a color/char is set, set both fg/bg intelligently
BLOCK_FULL = "█"
BLOCK_TOP = "▀"
BLOCK_BOTTOM = "▄"

def make_cell(c1, c2):
    if c1==c2:
        return Cell(BLOCK_FULL, c1, None)
    if c1>c2:
        return Cell(BLOCK_TOP, c1, c2)
    return Cell(BLOCK_BOTTOM, c1, c2)

def pixelplot(screen, x, y, color):
    c=screen.get_cell(x, y//2)
    if c:
        if y%2: #bottom block
            if c.char==BLOCK_TOP:
                c=make_cell(c.fg, color)
            elif c.char==BLOCK_FULL:
                c=make_cell(c.fg, color)
            elif c.char==BLOCK_BOTTOM:
                c=make_cell(c.bg, color)
            else:
                c=make_cell(c.bg, color)
        else:   #top block
            if c.char==BLOCK_BOTTOM:
                c=make_cell(color, c.bg)
            elif c.char==BLOCK_FULL:
                c=make_cell(color, c.fg)
            elif c.char==BLOCK_TOP:
                c=make_cell(color, c.fg)
            else:
                c=make_cell(color, c.bg)
        screen.set_cell(x,y//2, c)
