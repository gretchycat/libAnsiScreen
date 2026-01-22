from __future__ import annotations
from typing import Optional, Tuple
from libansiscreen.screen import Screen
from libansiscreen.cell import Cell
from libansiscreen.color.rgb import Color
from libansiscreen.screen_ops import glyph_defs as G
from libansiscreen.color.palette import create_ansi_16_palette
from libansiscreen.color.palette import create_ansi_256_palette

c256=create_ansi_256_palette()

def fill(filldata) -> Cell:
    c=Cell('X', Color(255,0,0), None, 0)
    if isinstance(filldata, Color):
        return Cell(G.BLOCK_FULL, filldata,None,0)
    elif isinstance(filldata, Cell):
        return filldata
    elif isinstance(filldata, int):
        return Cell(G.BLOCK_FULL, c256[abs(filldata)%256],None,0)
    elif isinstance(filldata, dict):
        if all(k in filldata for k in [ 'screen', 'x', 'y' ]):
            s=filldata['screen']
            x=int(filldata['x'])
            y=int(filldata['y'])
            if isinstance(s, Screen):
                w=s.width
                h.s.height()
                return s.get_cell(x%w,y%h)
        if all(k in filldata for k in [ 'gradient','type','x','y','w','h' ]):
            g=filldata['gradient']
            t=filldata['type']
            x=int(filldata['x'])
            y=int(filldata['y'])
            w=int(filldata['w'])
            h=int(filldata['h'])
            c=Color(0,255,0)
            return Cell(G.BLOCK_FULL,c,None,0)
    return c

def block_fill(filldata) -> Color:
    c=Color(255,0,0)
    if isinstance(filldata, Color):
        return filldata
    elif isinstance(filldata, Cell):
        return filldata.fg
    elif isinstance(filldata, int):
        return c256[abs(filldata)%256]
    elif isinstance(filldata, dict):
        if all(k in filldata for k in [ 'screen', 'x', 'y' ]):
            s=filldata['screen']
            x=int(filldata['x'])
            y=int(filldata['y'])
            if isinstance(s, Screen):
                w=s.width
                h.s.height()*2
                return s.pixelget(x%w, y%h)
        if all(k in filldata for k in [ 'gradient','type','x','y','w','h' ]):
            g=filldata['gradient']
            t=filldata['type']
            x=int(filldata['x'])
            y=int(filldata['y'])
            w=int(filldata['w'])
            h=int(filldata['h'])
            c=Color(0,255,0)
            return c
    return c

