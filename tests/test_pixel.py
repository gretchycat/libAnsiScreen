import math
import pytest
from libansiscreen.screen import Screen
from libansiscreen.cell import Cell
from libansiscreen.color.rgb import Color
from libansiscreen.screen_ops.pixel import pixel_plot
from tests.helpers import save_output

DARK = Color(10, 10, 10)
MID = Color(128, 128, 128)
BRIGHT = Color(250, 250, 250)


def cell_state(cell):
    if cell is None:
        return None
    return (cell.char, cell.fg, cell.bg)


def run_pixel(initial_cell, plot_y, color):
    screen = Screen(1)
    if initial_cell is not None:
        screen.set_cell(0, 0, initial_cell)
    pixel_plot(screen, 0, plot_y, color)
    return screen.get_cell(0, 0)


def test_pixel_plot_basic():
    screen = Screen(width=20)
    red = Color(255, 0, 0)
    screen.pixel_plot(4, 5, red)

    c = screen.get_cell(4, 5 // 2)
    assert c is not None
    assert red in [c.fg, c.bg]
    save_output(screen, "pixel.ans")


def test_empty_to_top_pixel():
    cell = run_pixel(None, 0, MID)
    assert cell_state(cell) == ("▀", MID, None)


def test_empty_to_bottom_pixel():
    cell = run_pixel(None, 1, MID)
    assert cell_state(cell) == ("▄", MID, None)


def test_top_then_same_bottom_becomes_solid():
    start = Cell("▀", MID, None)
    cell = run_pixel(start, 1, MID)
    assert cell_state(cell) == ("█", MID, None)


def test_bottom_then_same_top_becomes_solid():
    start = Cell("▄", MID, None)
    cell = run_pixel(start, 0, MID)
    assert cell_state(cell) == ("█", MID, None)


def test_top_brighter_than_bottom():
    start = Cell("▀", BRIGHT, None)
    cell = run_pixel(start, 1, DARK)
    assert cell_state(cell) == ("▀", BRIGHT, DARK)


def test_bottom_brighter_than_top():
    start = Cell("▀", DARK, None)
    cell = run_pixel(start, 1, BRIGHT)
    assert cell_state(cell) == ("▄", BRIGHT, DARK)


def test_solid_overwritten_on_top():
    start = Cell("█", MID, None)
    cell = run_pixel(start, 0, BRIGHT)
    assert cell.char in ("▀", "█")
    assert cell.fg == BRIGHT


def test_solid_overwritten_on_bottom():
    start = Cell("█", MID, None)
    cell = run_pixel(start, 1, BRIGHT)
    assert cell.char in ("▄", "█")
    assert cell.fg == BRIGHT


def test_non_block_glyph_is_overwritten():
    start = Cell("X", DARK, None)
    cell = run_pixel(start, 0, MID)
    assert cell.char in ("▀", "█")
    assert cell.fg == MID


def test_line_slopes():
    screen = Screen(width=80)
    for a in range(0, 360, 15):
        r = math.radians(a)
        w = screen.width // 2
        screen.pixel_line(
            w,
            w,
            w + round(math.sin(r) * w),
            w + round(math.cos(r) * w),
            Color.hsv(a / 360, 1.0, 1.0),
        )
    save_output(screen, "line_slope.ans")


def test_pixel_line_and_polyline():
    screen = Screen(width=40)
    green = Color(0, 255, 0)
    blue = Color(0, 0, 255)

    screen.pixel_line(0, 0, 10, 5, green)
    save_output(screen, "line.ans")

    points = [(0, 0), (5, 5), (10, 0)]
    screen.pixel_polyline(points, blue)
    save_output(screen, "polyline.ans")


def test_pixel_regular_polygon_and_star():
    screen = Screen(width=40)
    yellow = Color(255, 255, 0)
    cyan = Color(0, 255, 255)

    screen.pixel_regular_polygon(10, 10, 7, 6, yellow)
    save_output(screen, "polygon.ans")

    screen.pixel_regular_star(10, 10, 6, 5, 2, cyan)
    save_output(screen, "star.ans")


def test_pixel_flood_fill_rectangle_ellipse():
    screen = Screen(width=40)
    cyan = Color(0, 255, 255)
    yellow = Color(255, 255, 0)
    green = Color(0, 255, 0)
    red = Color(255, 0, 0)

    screen.pixel_regular_polygon(10, 10, 7, 12, cyan)
    save_output(screen, "pixel_floodfill-src2.ans")

    screen.pixel_flood_fill(10, 10, yellow)
    save_output(screen, "pixel_floodfill-dst2.ans")

    scr_rect = Screen(width=40)
    scr_rect.pixel_rectangle(4, 5, 27, 12, green)
    save_output(scr_rect, "pixel_rectangle.ans")

    scr_ell = Screen(width=40)
    scr_ell.pixel_ellipse(10, 10, 9, 4, red)
    save_output(scr_ell, "pixel_ellipse.ans")
