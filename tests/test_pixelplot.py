import unittest
import math
from libansiscreen.screen import Screen
from libansiscreen.cell import Cell
from libansiscreen.color.rgb import Color
from libansiscreen.renderer.ansi_emitter import ANSIEmitter
from pathlib import Path
OUT = Path("out")
OUT.mkdir(exist_ok=True)

def cell_state(cell):
    if cell is None:
        return None
    return (cell.char, cell.fg, cell.bg)

from libansiscreen.color.rgb import Color

DARK = Color(10, 10, 10)
MID  = Color(128, 128, 128)
BRIGHT = Color(250, 250, 250)

from libansiscreen.screen import Screen
from libansiscreen.screen_ops.pixelplot import pixel

def run_pixel(initial_cell, plot_y, color):
    """
    initial_cell: Cell or None
    plot_y: logical y (even=top, odd=bottom)
    color: Color to plot
    """
    screen = Screen(1)

    if initial_cell is not None:
        screen.set_cell(0, 0, initial_cell)

    pixel(screen, 0, plot_y, color)
    return screen.get_cell(0, 0)

def emit(screen: Screen, name: str):
    ansi = ANSIEmitter().emit(screen)
    path = OUT / name
    path.write_text(ansi)
    print(f"Wrote {path}")

class TestScreenDrawing(unittest.TestCase):
    def setUp(self):
        # Create a small test screen, adjust dimensions as needed
        self.screen = Screen(width=80)

    def test_pixel(self):
        red = Color(255, 0, 0)
        self.screen.pixel(4, 5, red)
        emit(self.screen, 'pixel.ans')
        c = self.screen.get_cell(4, 5 // 2)
        self.assertIsNotNone(c)
        self.assertIn(red, [c.fg, c.bg])

    def test_line_slopes(self):
        for a in range(0, 360, 15):
            r=math.radians(a)
            w=self.screen.width//2
            self.screen.line(w,w,
                             w+round(math.sin(r)*w),
                             w+round(math.cos(r)*w),
                             Color.hsv(a/360, 1.0, 1.0))
        emit(self.screen, 'line_slope.ans')

    def test_empty_to_top_pixel(self):
        cell = run_pixel(None, 0, MID)
        assert cell_state(cell) == ("▀", MID, None)

    def test_empty_to_bottom_pixel(self):
        cell = run_pixel(None, 1, MID)
        assert cell_state(cell) == ("▄", MID, None)

    def test_top_then_same_bottom_becomes_solid(self):
        start = Cell("▀", MID, None)
        cell = run_pixel(start, 1, MID)
        assert cell_state(cell) == ("█", MID, None)

    def test_bottom_then_same_top_becomes_solid(self):
        start = Cell("▄", MID, None)
        cell = run_pixel(start, 0, MID)
        assert cell_state(cell) == ("█", MID, None)

    def test_top_brighter_than_bottom(self):
        start = Cell("▀", BRIGHT, None)
        cell = run_pixel(start, 1, DARK)
        assert cell_state(cell) == ("▀", BRIGHT, DARK)

    def test_bottom_brighter_than_top(self):
        start = Cell("▀", DARK, None)
        cell = run_pixel(start, 1, BRIGHT)
        assert cell_state(cell) == ("▄", BRIGHT, DARK)

    def test_solid_overwritten_on_top(self):
        start = Cell("█", MID, None)
        cell = run_pixel(start, 0, BRIGHT)
        assert cell.char in ("▀", "█")
        assert cell.fg == BRIGHT

    def test_solid_overwritten_on_bottom(self):
        start = Cell("█", MID, None)
        cell = run_pixel(start, 1, BRIGHT)
        assert cell.char in ("▄", "█")
        assert cell.fg == BRIGHT

    def test_non_block_glyph_is_overwritten(self):
        start = Cell("X", DARK, None)
        cell = run_pixel(start, 0, MID)
        assert cell.char in ("▀", "█")
        assert cell.fg == MID

    def test_no_pixelplot_drops_color(self):
        start = Cell("▀", DARK, None)
        cell = run_pixel(start, 1, BRIGHT)
        colors = {cell.fg, cell.bg}
        assert BRIGHT in colors

    def test_line(self):
        green = Color(0, 255, 0)
        self.screen.line(0, 0, 10, 5, green)
        emit(self.screen, 'line.ans')
        # check a few points along expected path
        for x, y in [(0,0), (5,2), (10,5)]:
            c = self.screen.get_cell(x, y // 2)
            self.assertIsNotNone(c)
            self.assertIn(green, [c.fg, c.bg])

    def test_polyline(self):
        blue = Color(0, 0, 255)
        points = [(0,0), (5,5), (10,0)]
        self.screen.polyline(points, blue)
        emit(self.screen, 'polyline.ans')
        # verify start, middle, end
        for x, y in [(0,0), (5,5), (10,0)]:
            c = self.screen.get_cell(x, y // 2)
            self.assertIsNotNone(c)
            self.assertIn(blue, [c.fg, c.bg])

    def test_regular_polygon(self):
        yellow = Color(255, 255, 0)
        self.screen.regular_polygon(10, 10, 7, 6, yellow)
        emit(self.screen, 'polygon.ans')
        # check center vicinity
        for x, y in [(3,10), (17,10), (10,4)]:
            c = self.screen.get_cell(x, y // 2)
            self.assertIsNotNone(c)
            self.assertIn(yellow, [c.fg, c.bg])

    def test_regular_star(self):
        cyan = Color(0, 255, 255)
        self.screen.regular_star(10, 10, 6, 5, 2, cyan)
        emit(self.screen, 'star.ans')
        # verify approximate star points
        for x, y in [(16,10), (12,4), (12,16)]:
            c = self.screen.get_cell(x, y // 2)
            self.assertIsNotNone(c)
            self.assertIn(cyan, [c.fg, c.bg])

    def test_flood_fill(self):
        cyan=Color(0, 255, 255)
        yellow = Color(255, 255, 0)
        self.screen.regular_polygon(10, 10, 7, 12, cyan)
        emit(self.screen, 'pixel-floodfill-src2.ans')
        self.screen.flood_fill(10,10, yellow)
        emit(self.screen, 'pixel-floodfill-dst2.ans')

    def test_draw_rectangle(self):
        green = Color(0, 255, 0)
        self.screen.draw_rectangle(4, 5, 27, 12,green)
        emit(self.screen, 'pixel_draw_rectangle.ans')

    def test_draw_ellipse(self):
        red= Color(255, 0,0)
        self.screen.draw_ellipse(10, 10, 9, 4,red)
        emit(self.screen, 'pixel_draw_ellipse.ans')

 


if __name__ == "__main__":
    unittest.main()
