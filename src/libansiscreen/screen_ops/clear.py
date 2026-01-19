from typing import Optional, Iterable, Union

from libansiscreen.screen import Screen
from libansiscreen.cell import Cell
from libansiscreen.renderer.ansi_emitter import Box

from .color.rgb import Color

# ------------------------------------------------------------
# Internal helper: normalize legacy tuples to Box
# ------------------------------------------------------------

def _coerce_box(box: Optional[Union[Box, Iterable[int]]]) -> Optional[Box]:
    if box is None:
        return None
    if isinstance(box, Box):
        return box
    if isinstance(box, (tuple, list)) and len(box) == 4:
        return Box(*box)
    raise TypeError(f"Invalid box type: {type(box)}")


# ------------------------------------------------------------
# Clear operation
# ------------------------------------------------------------

def clear(screen: Screen, box: Optional[Union[Box, tuple]] = None) -> None:
    """
    Clear cells in `screen` inside `box`.

    Clearing means:
      - char = None
      - fg   = None
      - bg   = None
      - attrs = 0

    If box is None, clears the entire screen.
    """

    box = _coerce_box(box)

    if box is None:
        x0, y0 = 0, 0
        w, h = screen.width, screen.height
    else:
        x0, y0, w, h = box.x, box.y, box.width, box.height

    for y in range(y0, y0 + h):
        for x in range(x0, x0 + w):
            if screen.get_cell(x, y) is not None:
                screen.set_cell(
                    x, y,
                    Cell(
                        char=None,
                        fg=None,
                        bg=Color(0,0,0),
                        attrs=0,
                    )
                )
