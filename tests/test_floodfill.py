import unittest
import math
from libansiscreen.screen import Screen
from libansiscreen.cell import Cell
from libansiscreen.color.rgb import Color
from libansiscreen.renderer.ansi_emitter import ANSIEmitter
from libansiscreen.screen_ops.select import flood_fill_char_mask
from libansiscreen.screen_ops.select import flood_fill_pixel_mask
from libansiscreen.screen_ops import glyph_defs as G
from pathlib import Path
OUT = Path("out")
OUT.mkdir(exist_ok=True)

def emit(screen: Screen, name: str):
    ansi = ANSIEmitter().emit(screen)
    path = OUT / name
    path.write_text(ansi)
    print(f"Wrote {path}")

class FloodFill(unittest.TestCase):
    def setUp(self):
        # Create a small test screen, adjust dimensions as needed
        self.screen = Screen(width=80)

    def test_flood_fill_char_mask(self):
        yellow = Color(255, 255, 0)
        self.screen.regular_polygon(10, 10, 7, 6, yellow)
        emit(self.screen, 'floodfill-src1.ans')

        dst1=flood_fill_char_mask(self.screen,10,5,True,True)
        emit(dst1, 'floodfill-dst1.ans')

    def test_flood_fill_pixel_mask(self):
        cyan=Color(0, 255, 255)
        self.screen.regular_polygon(10, 10, 7, 12, cyan)
        emit(self.screen, 'floodfill-src2.ans')

        dst2=flood_fill_pixel_mask(self.screen,10,10)
        emit(dst2, 'floodfill-dst2.ans')

if __name__ == "__main__":
    unittest.main()
