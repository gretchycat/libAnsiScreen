import unittest
from libansiscreen.screen import Screen
from libansiscreen.color.rgb import Color
from libansiscreen.renderer.ansi_emitter import ANSIEmitter
from pathlib import Path
OUT = Path("out")
OUT.mkdir(exist_ok=True)

def emit(screen: Screen, name: str):
    ansi = ANSIEmitter().emit(screen)
    path = OUT / name
    path.write_text(ansi)
    print(f"Wrote {path}")

class TestScreenDrawing(unittest.TestCase):
    def setUp(self):
        # Create a small test screen, adjust dimensions as needed
        self.screen = Screen(width=20)

    def test_pixel(self):
        red = Color(255, 0, 0)
        self.screen.pixel(4, 5, red)
        emit(self.screen, 'pixel.ans')
        c = self.screen.get_cell(4, 5 // 2)
        self.assertIsNotNone(c)
        self.assertIn(red, [c.fg, c.bg])

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

if __name__ == "__main__":
    unittest.main()
