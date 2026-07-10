# libansiscreen/screen.py

from typing import List, Optional

from .cell import Cell
from .framebuffer import frameBuffer
from .cursor import Cursor
from .color.rgb import Color
from .color.palette import create_ansi_16_palette

# ----------------------------------------------------------------------
# Palette-derived defaults (single source of truth)
# ----------------------------------------------------------------------
_ANSI16 = create_ansi_16_palette()

DEFAULT_FG: Color = _ANSI16.index_to_rgb(7)  # light gray
DEFAULT_BG: Color = _ANSI16.index_to_rgb(0)  # black

class Screen(frameBuffer):
    def print(self, s):
        from libansiscreen.parser.ansi_parser import ANSIParser
        parser=ANSIParser(self)
        parser.feed(s)

    def __repr__(self):
        return f'Screen ({self.width}, {self.height})'

    def __strx__(self, box=None, raw=False):
        from libansiscreen.renderer.ansi_emitter import ANSIEmitter
        emitter=ANSIEmitter()
        return emitter.emit(self, box=box, raw=raw )
    
    def emit(self, box=None, raw=False):
        from libansiscreen.renderer.ansi_emitter import ANSIEmitter
        emitter=ANSIEmitter()
        return emitter.emit(self, box=box, raw=raw )

    def emit_diff(self, prev, box=None, raw=False):
        from libansiscreen.renderer.ansi_emitter import ANSIEmitter
        emitter=ANSIEmitter()
        return emitter.emit_diff(self, prev, box=box, raw=raw )

    # ------------------------------------------------------------------
    # Clip stuff
    # ------------------------------------------------------------------
    def copy(self, box = None):
        from libansiscreen.screen_ops.clip import copy
        return copy(self, box=box)

    def clear(self, box = None):
        from libansiscreen.screen_ops.clip import clear
        return clear(self, box=box)

    def paste(dst, src, *, box = None, transparent_char = None,
        transparent_fg = None, transparent_bg = None,
        transparent_attrs = None,) -> None:
        from libansiscreen.screen_ops.clip import paste
        return paste(dst,src,box=box,
                     transparent_char=transparent_char,
                     transparent_fg=transparent_fg,
                     transparent_bg=transparent_bg,
                     transparent_attrs=transparent_attrs)

    def cut(self, box = None):
        from libansiscreen.screen_ops.clip import cut
        return cut(self, box=box)

    # ------------------------------------------------------------------
    # coloring
    # ------------------------------------------------------------------
    def colorize(
        self,
        gradient,
        *,
        mode: str = "hgrad",
        foreground: bool = True,
        background: bool = False,
        only_if_set: bool = True,
        tint: Optional[float] = None,
        direction: str = "tlbr"):
        from libencodescreen.screen_ops.colorize import colorize
        return colorize(self, gradient, mode=mode, foreground=foreground,
                          background=background, only_if_set=only_if_set,
                          tint=tint, direction=direction)

    # ------------------------------------------------------------------
    # block drawing
    # ------------------------------------------------------------------
    def pixel(self, x: int, y: int, color):
        from libansiscreen.screen_ops.pixelplot import pixelplot
        return pixelplot(self, x, y, color)

    def plot(self, x: int, y: int, color):
        from libansiscreen.screen_ops.pixelplot import pixelplot
        return pixelplot(self, x, y, color)

    def pixelplot(self, x: int, y: int, color):
        from libansiscreen.screen_ops.pixelplot import pixelplot
        return pixelplot(self, x, y, color)

    def pixelget(self, x: int, y: int):
        from libansiscreen.screen_ops.pixelplot import pixelget
        return pixelget(self, x, y)

    def line(self, x0: int, y0: int, x1: int, y1: int, color):
        from libansiscreen.screen_ops.pixelplot import draw_line
        return draw_line(self, x0, y0, x1, y1, color)

    def polyline(self, points, color):
        from libansiscreen.screen_ops.pixelplot import draw_polyline
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
        from libansiscreen.screen_ops.pixelplot import draw_regular_polygon
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
        from libansiscreen.screen_ops.pixelplot import draw_regular_star
        return draw_regular_star(
            self, cx, cy, radius, n, k, color, rotation
        )

    def stamp_from_screen(self,transparent_chars=None,box=None,border_bg=None):
        from libansiscreen.screen_ops.prim import stamp_from_screen
        return stamp_from_screen(self,transparent_chars,box,border_bg)

    def flood_fill(self, x_seed, y_seed,fill=None):
        from libansiscreen.screen_ops.pixelplot import flood_fill
        return flood_fill(self, x_seed, y_seed, fill)

    def draw_rectangle(self,x1, y1, x2, y2,fill=None):
        from libansiscreen.screen_ops.pixelplot import draw_rectangle
        return draw_rectangle(self,x1, y1, x2, y2,fill)

    def draw_ellipse(self, cx, cy, rx, ry, fill=None):
        from libansiscreen.screen_ops.pixelplot import draw_ellipse
        return draw_ellipse(self, cx, cy, rx, ry, fill)

    # ------------------------------------------------------------------
    # full-block drawing
    # ------------------------------------------------------------------
    def char_flood_fill(self, x_seed, y_seed, ignore_fg_color=False, ignore_bg_color=False,fill=DEFAULT_FG):
        from libansiscreen.screen_ops.prim import char_flood_fill
        return char_flood_fill(self, x_seed, y_seed, ignore_fg_color, ignore_bg_color, fill=fill)

    def char_rectangle(self,x1, y1, x2, y2,fill=None):
        from libansiscreen.screen_ops.prim import char_rectangle
        return char_rectangle(self,x1, y1, x2, y2,fill)

    def char_ellipse(self, cx, cy, rx, ry, fill=None):
        from libansiscreen.screen_ops.prim import char_ellipse
        return char_ellipse(self, cx, cy, rx, ry, fill)
