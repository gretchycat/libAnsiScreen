import pytest
from libansiscreen.screen import Screen
from libansiscreen.color.rgb import Color
from libansiscreen.screen_ops.prim import (
    hline,
    vline,
    box,
    stamp_from_screen,
    char_flood_fill,
    char_rectangle,
    char_ellipse,
    char_tile,
)
from libansiscreen.screen_ops.glyph_defs import (
    LINE_SINGLE_HORIZONTAL,
    LINE_SINGLE_VERTICAL,
    BOX_SINGLE,
    BOX_BLOCK,
)
from tests.helpers import save_output


def test_primitives_basic_composition():
    screen = Screen(10)
    box(8, 4, glyphs=BOX_SINGLE, fb=screen)
    hline(1, 6, y=2, glyphs=LINE_SINGLE_HORIZONTAL, fb=screen, merge=True)
    vline(1, 3, x=4, glyphs=LINE_SINGLE_VERTICAL, fb=screen, merge=True)

    # Structural assertions
    assert screen.get_cell(4, 2).char == "┼"
    assert screen.get_cell(0, 0).char == "┌"
    assert screen.get_cell(7, 3).char == "┘"
    assert screen.get_cell(1, 1).char is None

    save_output(screen, "primitives_basic.ans")


def test_block_box_and_stamp():
    src = box(8, 4, glyphs=BOX_BLOCK)
    clr = Color(0, 0, 0)

    stamp = stamp_from_screen(src, transparent_chars=("█",), border_bg=clr)

    assert stamp.get_cell(1, 1).char is None
    c = stamp.get_cell(0, 0)
    assert c.char == " "
    assert c.bg == Color(0, 0, 0)

    save_output(stamp, "primitives_stamp.ans")


def test_char_shapes_and_flood_fill():
    scr_ell = Screen(width=40)
    scr_ell.char_ellipse(20, 12, 8, 8, fill=Color(255, 0, 128))
    save_output(scr_ell, "primitives_ellipse.ans")

    scr_rect = Screen(width=40)
    scr_rect.char_rectangle(5, 2, 30, 8, fill=Color(0, 255, 128))
    save_output(scr_rect, "primitives_rectangle.ans")

    scr_fill = Screen(width=40)
    cyan = Color(0, 255, 192)
    yellow = Color(255, 192, 0)
    scr_fill.regular_polygon(10, 10, 7, 12, cyan)
    scr_fill.char_flood_fill(10, 5, fill=yellow)
    save_output(scr_fill, "primitives_flood_fill.ans")


def test_char_tile():
    scr = Screen(width=10, height=4)
    scr.char_tile("AB\nCD\n")

    assert scr.get_cell(0, 0).char == "A"
    assert scr.get_cell(1, 0).char == "B"
    assert scr.get_cell(0, 1).char == "C"
    assert scr.get_cell(1, 1).char == "D"
    save_output(scr, "primitives_char_tile.ans")
