from __future__ import annotations

from typing import Optional, Tuple

from libansiscreen.screen import Screen
from libansiscreen.cell import Cell


# Box is (x, y, width, height)
Box = Tuple[int, int, int, int]


def copy(screen: Screen, box: Optional[Box] = None) -> Screen:
    """
    Copy a region of a screen into a new screen.

    If box is None, returns a full deep copy of the screen.
    Box is defined as (x, y, width, height).
    """

    if box is None:
        # Full screen copy
        new_screen = Screen(
            width=screen.width
        )

        for y in range(screen.height):
            for x in range(screen.width):
                cell = screen.get_cell(x, y)
                new_screen.set_cell(x, y, cell.copy())

        return new_screen

    x0, y0, w, h = box

    if w <= 0 or h <= 0:
        raise ValueError("Box width and height must be positive")

    new_screen = Screen(
        w
    )

    for dy in range(h):
        sy = y0 + dy
        if sy < 0 or sy >= screen.height:
            continue

        for dx in range(w):
            sx = x0 + dx
            if sx < 0 or sx >= screen.width:
                continue

            cell = screen.get_cell(sx, sy)
            new_screen.set_cell(dx, dy, cell.copy())

    return new_screen
