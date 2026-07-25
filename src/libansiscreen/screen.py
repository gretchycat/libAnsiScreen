# ./screen.py

from .framebuffer import frameBuffer
from .color.palette import create_ansi_16_palette
from .parser.ansi_parser import ANSIParser
from .renderer.ansi_emitter import ANSIEmitter
from .screen_ops.colorize import Colorize
from .screen_ops.clip import clear, copy, cut, paste, tile

from .screen_ops.pixel import (
    pixel_ellipse,
    pixel_line,
    pixel_polyline,
    pixel_rectangle,
    pixel_regular_polygon,
    pixel_regular_star,
    pixel_flood_fill,
    pixel_get,
    pixel_plot,
)

from .screen_ops.spixel import (
    spixel_ellipse,
    spixel_line,
    spixel_polyline,
    spixel_rectangle,
    spixel_regular_polygon,
    spixel_regular_star,
    spixel_flood_fill,
    spixel_get,
    spixel_plot,
)

from .screen_ops.prim import (
    char_ellipse,
    char_flood_fill,
    char_rectangle,
    stamp_from_screen,
    char_tile,
)

# ----------------------------------------------------------------------
# Palette-derived defaults (single source of truth)
# ----------------------------------------------------------------------
_ANSI16 = create_ansi_16_palette()

DEFAULT_FG = _ANSI16.index_to_rgb(7)  # light gray
DEFAULT_BG = _ANSI16.index_to_rgb(0)  # black

class Screen(Colorize, frameBuffer):
    def __init__(self, width: int, height=1):
        super().__init__(width=width, height=height)
        self.parser=ANSIParser(self)
        self.emitter=ANSIEmitter()

    def __repr__(self):
       return f'Screen ({self.width}, {self.height})'

    # ------------------------------------------------------------------
    # ANSI I/O
    # ------------------------------------------------------------------
    def feed(self, s):
        self.parser.feed(s)

    def print(self, s):
        self.parser.feed(s)

    def emit(self, box=None, raw=False):
        return self.emitter.emit(self, box=box, raw=raw )

    def emit_diff(self, prev, box=None, raw=False):
        return self.emitter.emit_diff(self, prev, box=box, raw=raw )

    # ------------------------------------------------------------------
    # Clip stuff
    # ------------------------------------------------------------------
    def copy(self, box = None):
        return copy(self, box=box)

    def clear(self, box = None):
        return clear(self, box=box)

    def paste(self, src, *, box = None, transparent_char = None,
        transparent_fg = None, transparent_bg = None,
        transparent_attrs = None,) -> None:
        return paste(self,src,box=box,
                     transparent_char=transparent_char,
                     transparent_fg=transparent_fg,
                     transparent_bg=transparent_bg,
                     transparent_attrs=transparent_attrs)

    def cut(self, box = None):
        return cut(self, box=box)

    def tile(self, tl):
        return tile(self.tl)

    # ------------------------------------------------------------------
    # half block drawing
    # ------------------------------------------------------------------
    def pixel_plot(self, x: int, y: int, color):
        return pixel_plot(self, x, y, color)

    def pixel_get(self, x: int, y: int):
        return pixel_get(self, x, y)

    def line(self, x0: int, y0: int, x1: int, y1: int, color):
        return pixel_line(self, x0, y0, x1, y1, color)

    def pixel_line(self, x0: int, y0: int, x1: int, y1: int, color):
        return pixel_line(self, x0, y0, x1, y1, color)

    def pixel_polyline(self, points, color):
        return pixel_polyline(self, points, color)

    def pixel_regular_polygon(self, cx: int, cy: int, radius: int,\
                        sides: int, color, rotation: float = 0.0):
        return pixel_polygon(self, cx, cy, radius,\
                                    sides, color, rotation)

    def pixel_regular_star(self, cx: int, cy: int, radius: int,n: int,\
                    k: int, color, rotation: float = 0.0):
        return pixel_regular_star(self, cx, cy, radius, n,\
                                 k, color, rotation)

    def pixel_flood_fill(self, x_seed, y_seed,fill=None):
        return pixel_flood_fill(self, x_seed, y_seed, fill)

    def pixel_rectangle(self,x1, y1, x2, y2,fill=None):
        return pixel_rectangle(self,x1, y1, x2, y2,fill)

    def pixel_ellipse(self, cx, cy, rx, ry, fill=None):
        return pixel_ellipse(self, cx, cy, rx, ry, fill)

    # ------------------------------------------------------------------
    # spixel drawing
    # ------------------------------------------------------------------
    def spixel_plot(self, x: int, y: int, state, mode='octant'):
        return spixel_plot(self, x, y, state,mode)

    def spixel_get(self, x: int, y: int, mode='octant'):
        return spixel_get(self, x, y,mode)

    def spixel_line(self, x0: int, y0: int, x1: int, y1: int, state, mode='octant'):
        return spixel_line(self, x0, y0, x1, y1, state, mode=mode)

    def spixel_polyline(self, points, state):
        return spixel_polyline(self, points, state, mode='octant')

    def spixel_regular_polygon(self, cx: int, cy: int, radius: int,\
                        sides: int, state, rotation: float = 0.0, mode='octant'):
        return spixel_regular_polygon(self, cx, cy, radius,\
                                    sides, state, rotation, mode=mode)

    def spixel_regular_star(self, cx: int, cy: int, radius: int,n: int,\
                    k: int, state, rotation: float = 0.0, mode='octant'):
        return spixel_regular_star(self, cx, cy, radius, n,\
                                 k, state, rotation, mode=mode)

    def spixel_flood_fill(self, x_seed, y_seed,state, mode='octant'):
        return spixel_flood_fill(self, x_seed, y_seed, state, mode=mode)

    def spixel_rectangle(self,x1, y1, x2, y2,state, mode='octant'):
        return spixel_rectangle(self,x1, y1, x2, y2,state, mode=mode)

    def spixel_ellipse(self, cx, cy, rx, ry, state, mode='octant'):
        return spixel_ellipse(self, cx, cy, rx, ry, state, mode=mode)

    # ------------------------------------------------------------------
    # block drawing
    # ------------------------------------------------------------------
    def plot(self, x: int, y: int, state, mode=None):
        if mode is None:
            return pixel_plot(self, x, y, state)
        return spixel_plot(self, x, y, state,mode)

    def get(self, x: int, y: int, mode=None):
        if mode is None:
            return pixel_get(self, x, y)
        return spixel_get(self, x, y,mode)

    def line(self, x0: int, y0: int, x1: int, y1: int, state, mode=None):
        if mode is None:
            return pixel_line(self, x0, y0, x1, y1, state)
        return spixel_line(self, x0, y0, x1, y1, state, mode=mode)

    def polyline(self, points, state, mode=None):
        if mode is None:
            return pixel_polyline(self, points, state)
        return spixel_polyline(self, points, state, mode=None)

    def regular_polygon(self, cx: int, cy: int, radius: int,\
                        sides: int, state, rotation: float = 0.0, mode=None):
        if mode is None:
            return pixel_regular_polygon(self, cx, cy, radius,\
                                    sides, state, rotation)
        return spixel_regular_polygon(self, cx, cy, radius,\
                                    sides, state, rotation, mode=mode)

    def regular_star(self, cx: int, cy: int, radius: int,n: int,\
                    k: int, state, rotation: float = 0.0, mode=None):
        if mode is None:
            return pixel_regular_star(self, cx, cy, radius, n,\
                                 k, state, rotation)
        return spixel_regular_star(self, cx, cy, radius, n,\
                                 k, state, rotation, mode=mode)

    def flood_fill(self, x_seed, y_seed,state, mode=None):
        if mode is None:
            return pixel_flood_fill(self, x_seed, y_seed, state)
        return spixel_flood_fill(self, x_seed, y_seed, state, mode=mode)

    def rectangle(self,x1, y1, x2, y2,state, mode=None):
        if mode is None:
            return pixel_rectangle(self,x1, y1, x2, y2,state)
        return spixel_rectangle(self,x1, y1, x2, y2,state, mode=mode)

    def ellipse(self, cx, cy, rx, ry, state, mode=None):
        if mode is None:
            return pixel_ellipse(self, cx, cy, rx, ry, state)
        return spixel_ellipse(self, cx, cy, rx, ry, state, mode=mode)

    # ------------------------------------------------------------------
    # full-block drawing
    # ------------------------------------------------------------------
    def char_flood_fill(self, x_seed, y_seed, ignore_fg_color=False, ignore_bg_color=False,fill=DEFAULT_FG):
        return char_flood_fill(self, x_seed, y_seed, ignore_fg_color, ignore_bg_color, fill=fill)

    def char_rectangle(self,x1, y1, x2, y2,fill=None):
        return char_rectangle(self,x1, y1, x2, y2,fill)

    def char_ellipse(self, cx, cy, rx, ry, fill=None):
        return char_ellipse(self, cx, cy, rx, ry, fill)
    
    def stamp_from_screen(self,transparent_chars=None,box=None,border_bg=None):
        return stamp_from_screen(self,transparent_chars,box,border_bg)

    def char_tile(self, text):
        return char_tile(self, text)

