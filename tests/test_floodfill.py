import unittest
import math
from libansiscreen.screen import Screen
from libansiscreen.cell import Cell
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

class FloodFill(unittest.TestCase):
    def setUp(self):
        # Create a small test screen, adjust dimensions as needed
        self.screen = Screen(width=80)

    def test_pixel(self):
        pass
