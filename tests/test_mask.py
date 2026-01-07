import unittest
import math
from libansiscreen.screen import Screen
from libansiscreen.cell import Cell
from libansiscreen.color.rgb import Color
from libansiscreen.renderer.ansi_emitter import ANSIEmitter
from libansiscreen.screen_ops.select import flood_fill_char_mask
from libansiscreen.screen_ops.select import flood_fill_pixel_mask
from libansiscreen.screen_ops.select import rect_pixel_mask
from libansiscreen.screen_ops.select import rect_char_mask
from libansiscreen.screen_ops.select import ellipse_pixel_mask
from libansiscreen.screen_ops.select import ellipse_char_mask
from libansiscreen.screen_ops import glyph_defs as G
from pathlib import Path
OUT = Path("out")
OUT.mkdir(exist_ok=True)

def emit(screen: Screen, name: str):
    ansi = ANSIEmitter().emit(screen)
    path = OUT / name
    path.write_text(ansi)
    print(f"Wrote {path}")

class mask(unittest.TestCase):
    def setUp(self):
        # Create a small test screen, adjust dimensions as needed
        self.screen = Screen(width=80)

    def test_flood_fill_char_mask(self):
        yellow = Color(255, 255, 0)
        self.screen.regular_polygon(10, 10, 7, 6, yellow)
        emit(self.screen, 'mask-floodfill-char-src1.ans')
        dst1=flood_fill_char_mask(self.screen,10,5,True,True)
        emit(dst1, 'mask-floodfill-char-dst1.ans')

    def test_flood_fill_pixel_mask(self):
        cyan=Color(0, 255, 255)
        self.screen.regular_polygon(10, 10, 7, 12, cyan)
        emit(self.screen, 'mask-floodfill-pixel-src2.ans')
        dst2=flood_fill_pixel_mask(self.screen,10,10)
        emit(dst2, 'mask-floodfill-pixel-dst2.ans')

    def test_rect_pixel_mask(self):
        dst=rect_pixel_mask(4, 5, 27, 12)
        emit(dst, 'mask-rect-pixel.ans')

    def test_elipse_pixel_mask(self):
        dst=ellipse_pixel_mask(10, 10, 9, 4)
        emit(dst, 'mask-elipse-pixel.ans')

    def test_rect_char_mask(self):
        dst=rect_char_mask(4, 5, 27, 12)
        emit(dst, 'mask-rect-char.ans')

    def test_elipse_char_mask(self):
        dst=ellipse_char_mask(10, 10, 9, 4)
        emit(dst, 'mask-elipse-char.ans')

if __name__ == "__main__":
    unittest.main()
