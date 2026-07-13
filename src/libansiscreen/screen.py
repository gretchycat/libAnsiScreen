# ./screen.py

from typing import List, Optional

from .cell import Cell
from .framebuffer import frameBuffer
from .cursor import Cursor
from .color.rgb import Color
from .color.palette import create_ansi_16_palette

from .parser.ansi_parser import ANSIParser
from .renderer.ansi_emitter import ANSIEmitter
#TODO :make each file into a framebuffer class
from .screen_ops.colorize import Colorize
from .screen_ops.clip import clear, copy, cut, paste
from .screen_ops.pixelplot import (
    draw_ellipse,
    draw_line,
    draw_polyline,
    draw_rectangle,
    draw_regular_polygon,
    draw_regular_star,
    flood_fill,
    pixelget,
    pixelplot,
)
from .screen_ops.prim import (
    char_ellipse,
    char_flood_fill,
    char_rectangle,
    stamp_from_screen,
)

# ----------------------------------------------------------------------
# Palette-derived defaults (single source of truth)
# ----------------------------------------------------------------------
_ANSI16 = create_ansi_16_palette()

DEFAULT_FG: Color = _ANSI16.index_to_rgb(7)  # light gray
DEFAULT_BG: Color = _ANSI16.index_to_rgb(0)  # black

class Screen(Colorize, frameBuffer):
    def __init__(self, width: int, height=1):
        super().__init__(width=width, height=height)
        self.parser=ANSIParser(self)
        self.emitter=ANSIEmitter()

    def __repr__(self):
       return f'Screen ({self.width}, {self.height})'

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

    def paste(dst, src, *, box = None, transparent_char = None,
        transparent_fg = None, transparent_bg = None,
        transparent_attrs = None,) -> None:
        return paste(dst,src,box=box,
                     transparent_char=transparent_char,
                     transparent_fg=transparent_fg,
                     transparent_bg=transparent_bg,
                     transparent_attrs=transparent_attrs)

    def cut(self, box = None):
        return cut(self, box=box)

    # ------------------------------------------------------------------
    # coloring
    # ------------------------------------------------------------------
    def colorizex(
        self,
        gradient,
        *,
        mode: str = "hgrad",
        foreground: bool = True,
        background: bool = False,
        only_if_set: bool = True,
        tint: Optional[float] = None,
        direction: str = "tlbr"):
        return self.colorize(gradient, mode=mode, foreground=foreground,
                          background=background, only_if_set=only_if_set,
                         tint=tint, direction=direction)

    # ------------------------------------------------------------------
    # block drawing
    # ------------------------------------------------------------------
    def pixel(self, x: int, y: int, color):
        return pixelplot(self, x, y, color)

    def plot(self, x: int, y: int, color):
        return pixelplot(self, x, y, color)

    def pixelplot(self, x: int, y: int, color):
        return pixelplot(self, x, y, color)

    def pixelget(self, x: int, y: int):
        return pixelget(self, x, y)

    def line(self, x0: int, y0: int, x1: int, y1: int, color):
        return draw_line(self, x0, y0, x1, y1, color)

    def polyline(self, points, color):
        return draw_polyline(self, points, color)

    def regular_polygon(
        self,
        cx: int,
        cy: int,
        radius: int,
        sides: int,
        color,
        rotation: float = 0.0,
    ):
        return draw_regular_polygon(
            self, cx, cy, radius, sides, color, rotation
        )

    def regular_star(
        self,
        cx: int,
        cy: int,
        radius: int,
        n: int,
        k: int,
        color,
        rotation: float = 0.0,
    ):
        return draw_regular_star(
            self, cx, cy, radius, n, k, color, rotation
        )

    def flood_fill(self, x_seed, y_seed,fill=None):
        return flood_fill(self, x_seed, y_seed, fill)

    def draw_rectangle(self,x1, y1, x2, y2,fill=None):
        return draw_rectangle(self,x1, y1, x2, y2,fill)

    def draw_ellipse(self, cx, cy, rx, ry, fill=None):
        return draw_ellipse(self, cx, cy, rx, ry, fill)

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

