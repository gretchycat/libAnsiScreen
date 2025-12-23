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

def pixelplot(screen, x, y, color):
    c=screen.get_cell(x, y/2)
    if c:
        if y%2: #bottom block
            pass
        else:   #top block
            pass
        screen.set_cell(x,y/2, c)
