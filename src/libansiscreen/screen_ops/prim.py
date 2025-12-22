from __future__ import annotations

from typing import Optional, Dict, Callable, Tuple, Iterable

from libansiscreen.screen import Screen
from libansiscreen.cell import Cell
from libansiscreen.screen_ops import glyph_defs as G


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
    screen: Optional[Screen] = None,
    merge: bool = False,
) -> Screen:
    if x2 < x1:
        x1, x2 = x2, x1

    width = x2 - x1 + 1
    scr = screen or Screen(width)
    yy = y if screen else 0

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
    screen: Optional[Screen] = None,
    merge: bool = False,
) -> Screen:
    if y2 < y1:
        y1, y2 = y2, y1

    height = y2 - y1 + 1
    scr = screen or Screen(1)
    xx = x if screen else 0

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
    screen: Optional[Screen] = None,
) -> Screen:
    scr = screen or Screen(w)

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
    source: Screen,
    *,
    transparent_chars: Iterable[str] = (" ",),
    box: Optional[Tuple[int, int, int, int]] = None,
    add_border: bool = False,
    border_bg=None,
) -> Screen:
    if box:
        x0, y0, w, h = box
    else:
        x0, y0 = 0, 0
        w, h = source.width, source.height

    out = Screen(w)

    # Copy / punch transparency
    for y in range(h):
        for x in range(w):
            src = source.get_cell(x + x0, y + y0)
            if src.char in transparent_chars:
                continue
            out.set_cell(x, y, src.copy())

    # Optional border
    if add_border:
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
